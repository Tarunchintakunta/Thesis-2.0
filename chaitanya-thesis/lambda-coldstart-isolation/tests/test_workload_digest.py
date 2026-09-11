"""Part of the runtime gate: all variants do the same work and give the same answer."""
import ast
import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = json.loads((ROOT / "payloads/fixed_payload.json").read_text())
EXPECTED = json.loads((ROOT / "payloads/expected_output.json").read_text())


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _functions(path):
    tree = ast.parse(Path(path).read_text())
    return {n.name: ast.dump(n) for n in tree.body if isinstance(n, ast.FunctionDef)}


def _node_body(path):
    text = Path(path).read_text()
    return text[text.index("export function digest"):]


def test_expected_output_shape():
    assert EXPECTED["ok"] is True and EXPECTED["n"] == PAYLOAD["iterations"]
    assert EXPECTED["items"] == len(PAYLOAD["items"]) and EXPECTED["items_total"] == sum(PAYLOAD["items"])
    assert re.fullmatch(r"[0-9a-f]{64}", EXPECTED["digest"])


def test_python_optimised_matches_expected():
    mod = _load(ROOT / "functions/python/optimised/handler.py", "py_opt")
    assert mod.lambda_handler(PAYLOAD) == EXPECTED


def test_python_default_and_optimised_share_the_code():
    # only the import block may differ between the two variants
    assert _functions(ROOT / "functions/python/default/handler.py") == \
        _functions(ROOT / "functions/python/optimised/handler.py")


def test_node_default_and_optimised_share_the_code():
    assert _node_body(ROOT / "functions/nodejs/default/index.mjs") == \
        _node_body(ROOT / "functions/nodejs/optimised/index.mjs")


def test_warmer_ping_short_circuits():
    mod = _load(ROOT / "functions/python/optimised/handler.py", "py_opt2")
    assert mod.lambda_handler({"warmer": True}) == {"ok": True, "warmer": True}


def test_digest_is_iterated_sha256():
    import hashlib
    mod = _load(ROOT / "functions/python/optimised/handler.py", "py_opt3")
    h = hashlib.sha256(hashlib.sha256(b"abc").digest()).digest().hex()
    assert mod.digest("abc", 2) == h
    assert mod.digest("abc", 0) == b"abc".hex()


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_node_optimised_matches_python():
    uri = (ROOT / "functions/nodejs/optimised/index.mjs").as_uri()
    js = (f"import('{uri}').then(async m => "
          "console.log(JSON.stringify(await m.handler(JSON.parse(process.argv[1])))))")
    out = subprocess.run(["node", "-e", js, json.dumps(PAYLOAD)], capture_output=True, text=True,
                         check=True, timeout=60)
    assert json.loads(out.stdout) == EXPECTED


def test_java_variants_have_the_same_digest_and_handler_code():
    def region(path):
        text = Path(path).read_text()
        start = text.index("public static String digest")
        end = text.index("return out;\n    }\n", text.index("public Map<String, Object> handleRequest"))
        return text[start:end]
    assert region(ROOT / "functions/java/default/src/main/java/coldstart/Handler.java") == \
        region(ROOT / "functions/java/optimised/src/main/java/coldstart/Handler.java")
