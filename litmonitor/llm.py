"""Minimal Anthropic Messages client. One file, stdlib only.

Swapping provider means rewriting this file and nothing else. Model ids are resolved at
runtime from /v1/models rather than hardcoded, because a pinned id silently routes to an
older model once it is retired.
"""

import json
import os
import re
import time
import urllib.error
import urllib.request

API = "https://api.anthropic.com/v1"
VERSION = "2023-06-01"
DEFAULT_PREFERENCE = r"^claude-(opus|sonnet)-"


def _headers():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    return {"x-api-key": key, "anthropic-version": VERSION, "content-type": "application/json"}


def list_models(timeout=30):
    req = urllib.request.Request(API + "/models?limit=100", headers=_headers())
    return json.load(urllib.request.urlopen(req, timeout=timeout)).get("data", [])


def resolve_model(preference=None, env_var="NF_MONITOR_MODEL"):
    """Pin via env var, else newest model matching the preference pattern.

    The verdict step is where a weaker model costs you a fabricated mechanism, so the
    default preference deliberately excludes the small models.
    """
    if preference is None:
        preference = DEFAULT_PREFERENCE
    pinned = os.environ.get(env_var)
    if pinned:
        return pinned
    models = sorted(list_models(), key=lambda m: m.get("created_at", ""), reverse=True)
    for m in models:
        if re.match(preference, m["id"]):
            return m["id"]
    raise RuntimeError("no model matched %r; set %s" % (preference, env_var))


def complete(prompt, system=None, model=None, max_tokens=2000, temperature=0.0,
             retries=4, timeout=180):
    """One completion. Returns {text, usage, model, stop_reason}."""
    body = {"model": model or resolve_model(), "max_tokens": max_tokens,
            "temperature": temperature, "messages": [{"role": "user", "content": prompt}]}
    if system:
        body["system"] = system
    req = urllib.request.Request(API + "/messages", data=json.dumps(body).encode(),
                                 headers=_headers())
    for attempt in range(retries):
        try:
            d = json.load(urllib.request.urlopen(req, timeout=timeout))
            text = "".join(b.get("text", "") for b in d.get("content", []))
            return {"text": text, "usage": d.get("usage", {}), "model": d.get("model"),
                    "stop_reason": d.get("stop_reason")}
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 529) and attempt < retries - 1:
                time.sleep(2 ** attempt * 5)
                continue
            raise RuntimeError("anthropic %s: %s" % (exc.code, exc.read()[:300].decode())) from None
        except urllib.error.URLError:
            if attempt < retries - 1:
                time.sleep(2 ** attempt * 5)
                continue
            raise


def complete_json(prompt, system=None, salvage_key=None, **kw):
    """Completion parsed as JSON, with salvage for truncated replies.

    Long article bodies make truncation routine, and a dropped reply is a silently missing
    verdict, so partial objects are recovered rather than discarded.
    """
    out = complete(prompt, system=system, **kw)
    text = out["text"]
    try:
        m = re.search(r"\{.*\}", text, re.S)
        out["data"] = json.loads(m.group(0)) if m else None
    except Exception:
        out["data"] = None
    if out["data"] is None and salvage_key:
        objs = []
        for frag in re.findall(r"\{[^{}]*\"" + salvage_key + r"\"[^{}]*\}", text, re.S):
            try:
                objs.append(json.loads(frag))
            except Exception:
                pass
        out["data"] = {"salvaged": objs} if objs else None
    return out


def cost_note(usages):
    """Token totals for the run log. Prices change, so report tokens, not dollars."""
    tot = {"input_tokens": 0, "output_tokens": 0}
    for u in usages:
        tot["input_tokens"] += u.get("input_tokens", 0)
        tot["output_tokens"] += u.get("output_tokens", 0)
    tot["calls"] = len(usages)
    return tot
