"""Load and validate a study config. TOML, parsed with stdlib tomllib.

A config is the whole difference between one disease and another: the label vocabulary, the
query bank, what counts as a target, and which labels are out of scope. Nothing about the
disease is in the code.
"""

import tomllib
from pathlib import Path

REQUIRED = ("study", "labels", "extraction", "paths", "queries")


class Config:
    def __init__(self, data, path):
        self.path = Path(path)
        self.data = data
        self.study = data["study"]["name"]
        self.description = data["study"].get("description", "")
        self.diseases = list(data["labels"]["diseases"])
        self.manifestations = list(data["labels"]["manifestations"])
        self.entity = data["extraction"]["entity"]
        self.exclude_guidance = data["extraction"].get("exclude_guidance", "")
        self.roles = list(data["extraction"].get("roles",
                          ["driver", "modifier", "therapeutic target", "biomarker"]))
        self.systems = list(data["extraction"].get("study_systems",
                            ["human tissue", "clinical trial", "mouse model", "cell line",
                             "computational", "review"]))
        scope = data.get("scope", {})
        self.exclude_labels = set(scope.get("exclude_labels", []))
        self.exclude_labels_reason = scope.get("exclude_labels_reason", "out of scope")
        self.excluded_tiers = list(scope.get("excluded_tiers", ["full text - not supported"]))
        self.derive_module = scope.get("derive_module")
        paths = data["paths"]
        self.workdir = Path(paths["workdir"])
        self.baseline = Path(paths["baseline"]) if paths.get("baseline") else None
        self.frozen = list(paths.get("frozen", []))
        self.queries = [dict(q) for q in data["queries"]]

    @property
    def tier_rank(self):
        return {"abstract only": 0, "full text - not supported": 1,
                "full text - partial": 2, "full text - supported": 3}

    def check(self):
        problems = []
        if "Other" not in self.manifestations:
            problems.append("labels.manifestations should include a catch-all 'Other'; "
                            "without one, claims outside the vocabulary have nowhere legitimate to go")
        if len(set(self.manifestations)) != len(self.manifestations):
            problems.append("labels.manifestations contains duplicates")
        for i, q in enumerate(self.queries):
            for field in ("disease", "query"):
                if field not in q:
                    problems.append("queries[%d] is missing %r" % (i, field))
            if q.get("disease") not in self.diseases:
                problems.append("queries[%d] disease %r is not in labels.diseases"
                                % (i, q.get("disease")))
        if self.baseline and not self.baseline.exists():
            problems.append("paths.baseline %s does not exist; omit it for a cold start"
                            % self.baseline)
        return problems


def load(path):
    with open(path, "rb") as fh:
        data = tomllib.load(fh)
    missing = [k for k in REQUIRED if k not in data]
    if missing:
        raise ValueError("%s is missing section(s): %s" % (path, ", ".join(missing)))
    cfg = Config(data, path)
    problems = cfg.check()
    if problems:
        raise ValueError("%s:\n  - %s" % (path, "\n  - ".join(problems)))
    return cfg
