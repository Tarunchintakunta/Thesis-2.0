"""The one log parser of the study: Drain (He et al., 2017) via drain3.

The configuration comes from configs/drain.yaml and is fingerprinted
(SHA-256 of the file + drain3 version) into results/parser_fingerprint.json
the first time the pipeline runs. Later runs check the fingerprint and refuse
to continue if the parser config changed (Khan et al., 2024 - the parser must
be fixed, not tuned between arms).

Parsing is online and chronological (A -> B -> C), like a deployed parser:
the template recorded for a line is the template *at the time it was parsed*,
so no information from later logs leaks into earlier windows.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from importlib.metadata import version
from pathlib import Path

from drain3 import TemplateMiner
from drain3.masking import MaskingInstruction
from drain3.template_miner_config import TemplateMinerConfig

from logad.config import CONFIG_DIR, PROJECT_ROOT, file_sha256, load_yaml

DRAIN_CONFIG = CONFIG_DIR / "drain.yaml"
FINGERPRINT = PROJECT_ROOT / "results" / "parser_fingerprint.json"


class ParserChanged(RuntimeError):
    pass


def build_miner(cfg: dict) -> TemplateMiner:
    c = TemplateMinerConfig()
    c.drain_depth = int(cfg["depth"])
    c.drain_sim_th = float(cfg["sim_th"])
    c.drain_max_children = int(cfg["max_children"])
    c.drain_max_clusters = int(cfg["max_clusters"])
    c.parametrize_numeric_tokens = bool(cfg["parametrize_numeric_tokens"])
    c.masking_instructions = [MaskingInstruction(m["pattern"], m["name"]) for m in cfg.get("masking", [])]
    c.profiling_enabled = False
    return TemplateMiner(config=c)


def fingerprint(config_path: Path = DRAIN_CONFIG) -> dict:
    cfg = load_yaml(config_path)
    return {
        "parser": cfg["parser"],
        "parser_version_pinned": cfg["parser_version"],
        "parser_version_installed": version("drain3"),
        "config_file": str(config_path.relative_to(PROJECT_ROOT)) if config_path.is_relative_to(PROJECT_ROOT) else str(config_path),
        "config_sha256": file_sha256(config_path),
    }


def check_or_write_fingerprint(path: Path = FINGERPRINT, config_path: Path = DRAIN_CONFIG) -> dict:
    """First run writes the fingerprint; later runs must match it exactly."""
    current = fingerprint(config_path)
    if current["parser_version_installed"] != current["parser_version_pinned"]:
        raise ParserChanged(f"drain3 {current['parser_version_installed']} installed, "
                            f"config pins {current['parser_version_pinned']}")
    if path.exists():
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved.get("config_sha256") != current["config_sha256"]:
            raise ParserChanged("configs/drain.yaml changed after the fingerprint was written - "
                                "the parser must stay fixed. Restore it (or start a new study).")
        return saved
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
    return current


@dataclass
class ParsedLog:
    """Per-line parse result, kept in memory (arrays of equal length)."""

    ts: list[float] = field(default_factory=list)
    cluster_id: list[int] = field(default_factory=list)
    template: list[str] = field(default_factory=list)
    message: list[str] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.ts)


class FixedDrainParser:
    def __init__(self, cfg: dict | None = None) -> None:
        self.cfg = cfg or load_yaml(DRAIN_CONFIG)
        self.miner = build_miner(self.cfg)

    def parse(self, messages, timestamps=None) -> ParsedLog:
        out = ParsedLog()
        for i, message in enumerate(messages):
            result = self.miner.add_log_message(message)
            out.cluster_id.append(int(result["cluster_id"]))
            out.template.append(result["template_mined"])
            out.message.append(message)
            out.ts.append(float(timestamps[i]) if timestamps is not None else float(i))
        return out

    def templates(self) -> list[dict]:
        return [{"cluster_id": c.cluster_id, "size": c.size, "template": c.get_template()}
                for c in self.miner.drain.clusters]
