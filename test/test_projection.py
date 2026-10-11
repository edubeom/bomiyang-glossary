"""terms.json projection must not depend on PYTHONHASHSEED (same input -> same output)."""
import json
import os
import subprocess
import sys
from pathlib import Path

from glossary import generate_glossary as gg

WORDS = [
    {"id": "apply", "status": "active", "domain": ["system", "general", "trading", "system"],
     "lang": {"en": "apply", "ko": "적용"}, "variants": [{"types": ["plural"], "value": "applies"}]},
]


def _domains(active):
    return [t["domain"] for t in active["terms"] if t["term_type"] == "base"]


def test_unroll_domains_keeps_declared_order():
    active, _legacy, _skipped = gg.build_terms_json(WORDS, [])
    assert _domains(active) == ["system", "general", "trading"]


def test_projection_same_across_hash_seeds():
    root = Path(__file__).resolve().parents[2]
    code = (
        "import json, sys; from glossary import generate_glossary as gg; "
        "a, _, _ = gg.build_terms_json(json.loads(sys.argv[1]), []); "
        "print(json.dumps([[t['id'], t['domain']] for t in a['terms']]))"
    )
    outs = set()
    for seed in ("0", "1", "2", "3", "4"):
        env = {**os.environ, "PYTHONHASHSEED": seed, "PYTHONPATH": str(root)}
        r = subprocess.run([sys.executable, "-c", code, json.dumps(WORDS)], capture_output=True, text=True,
                           encoding="utf-8", env=env, cwd=str(root), check=True)
        outs.add(r.stdout)
    assert len(outs) == 1
