import pytest

from logad.source.loghub_bgl import SourceMissing, line_windows, read_bgl, window_labels, window_line_index

# made-up lines in the BGL field layout (not copied from the dataset)
SAMPLE = """- 1000 2005.01.01 N1 2005-01-01-00.00.00.000000 N1 RAS KERNEL INFO cache parity error corrected
- 1001 2005.01.01 N1 2005-01-01-00.00.01.000000 N1 RAS KERNEL INFO generating core
KERNDTLB 1002 2005.01.01 N2 2005-01-01-00.00.02.000000 N2 RAS KERNEL FATAL data TLB error interrupt
- 1003 2005.01.01 N1 2005-01-01-00.00.03.000000 N1 RAS APP INFO ciod: message received
"""


def test_read_bgl(tmp_path):
    path = tmp_path / "bgl.log"
    path.write_text(SAMPLE)
    bgl = read_bgl(path)
    assert bgl.labels.tolist() == [False, False, True, False]
    assert bgl.contents[2] == "data TLB error interrupt"


def test_missing_file_says_how_to_fetch_it(tmp_path):
    with pytest.raises(SourceMissing, match="fetch_loghub"):
        read_bgl(tmp_path / "nope.log")


def test_line_windows_and_labels():
    assert line_windows(10, 4, 3) == [(0, 4), (3, 7), (6, 10)]
    labels = [False] * 10
    labels[5] = True
    assert window_labels(labels, 4, 3).tolist() == [False, True, False]
    rows, cols = window_line_index(10, 4, 3)
    assert len(rows) == 12 and cols.max() == 2
