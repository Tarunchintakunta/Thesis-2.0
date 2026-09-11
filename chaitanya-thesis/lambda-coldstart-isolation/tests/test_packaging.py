import zipfile

from coldstart.localbench import command, schedule
from coldstart.packaging import build_manifest, deterministic_zip, sha256_file


def make_pkg(root):
    (root / "lib").mkdir(parents=True)
    (root / "handler.py").write_text("def lambda_handler(e, c=None):\n    return e\n")
    (root / "lib" / "big.py").write_text("x = 1\n" * 1000)
    return root


def test_zip_is_deterministic(tmp_path):
    src = make_pkg(tmp_path / "pkg")
    a = deterministic_zip(src, tmp_path / "a.zip")
    b = deterministic_zip(src, tmp_path / "b.zip")
    assert sha256_file(a) == sha256_file(b)


def test_bytecode_is_never_shipped(tmp_path):
    src = make_pkg(tmp_path / "pkg")
    (src / "__pycache__").mkdir()
    (src / "__pycache__" / "handler.cpython-312.pyc").write_bytes(b"\x00" * 100)
    (src / "stray.pyc").write_bytes(b"\x00")
    names = zipfile.ZipFile(deterministic_zip(src, tmp_path / "p.zip")).namelist()
    assert sorted(names) == ["handler.py", "lib/big.py"]


def test_manifest_describes_zips_and_jars(tmp_path):
    build = tmp_path / "build"
    make_pkg(build / "python-optimised")
    (build / "java-default").mkdir(parents=True)
    with zipfile.ZipFile(build / "java-default" / "function.jar", "w") as zf:
        zf.writestr("coldstart/Handler.class", b"\xca\xfe\xba\xbe")
    m = build_manifest(build)
    by = {(e["runtime"], e["variant"]): e for e in m["variants"]}
    assert set(by) == {("python", "optimised"), ("java", "default")}
    assert by[("java", "default")]["artifact"] == "function.jar" and by[("java", "default")]["files"] == 1
    assert by[("python", "optimised")]["files"] == 2
    assert (build / "package_manifest.json").exists()


def test_python_bench_never_writes_bytecode():
    assert "-B" in command("python", "default")


def test_bench_schedule_is_interleaved_blocks():
    variants = [("python", "default"), ("python", "optimised"), ("nodejs", "default")]
    order = schedule(4, variants, seed=1)
    assert len(order) == 12
    for rep in range(4):
        assert sorted((r, v) for k, r, v in order if k == rep) == sorted(variants)
