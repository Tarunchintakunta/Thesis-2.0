from scripts import check_bib


def entries():
    return check_bib.parse_bib(check_bib.BIB.read_text())


def test_bibliography_matches_the_master_prompt_pack():
    assert check_bib.check(entries()) == []


def test_missing_baseline_is_flagged():
    rest = [e for e in entries() if e.get("doi", "").lower() != check_bib.BASELINE_DOI]
    assert any("baseline" in p for p in check_bib.check(rest))


def test_an_entry_without_doi_or_url_is_flagged():
    es = entries()
    es[0] = {k: v for k, v in es[0].items() if k not in ("doi", "url")}
    assert any("no DOI or URL" in p for p in check_bib.check(es))
