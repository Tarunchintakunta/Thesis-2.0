from scripts.check_bib import BIB, main, parse_bib

ENTRIES = parse_bib(BIB.read_text())


def test_exactly_the_master_prompt_corpus():
    scholarly = [e for e in ENTRIES if not e["key"].startswith("aws")]
    aws = [e for e in ENTRIES if e["key"].startswith("aws")]
    assert len(scholarly) == 21 and len(aws) == 3
    assert all(2022 <= int(e["year"]) <= 2026 for e in scholarly)


def test_baseline_and_traceability():
    base = [e for e in ENTRIES if e.get("doi", "").lower() == "10.3390/fi18010053"]
    assert len(base) == 1 and "Pantelić" in base[0]["author"] or "Panteli" in base[0]["author"]
    assert all(e.get("doi") or e.get("url") for e in ENTRIES)


def test_no_html_left_in_titles():
    assert not any("<" in e["title"] for e in ENTRIES)


def test_offline_check_passes():
    assert main(["--offline"]) == 0
