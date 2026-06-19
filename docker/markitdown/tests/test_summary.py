from pathlib import Path

import convert


def test_format_summary_counts():
    result = convert.ConversionResult(
        succeeded=[Path("a.docx"), Path("b.pdf")],
        failed=[(Path("bad.pdf"), "boom")],
        skipped=[Path("note.txt")],
    )

    text = convert.format_summary(result)

    assert "成功 2 件" in text
    assert "非対応 1 件" in text
    assert "失敗 1 件" in text
    assert "bad.pdf: boom" in text


def test_format_summary_no_failures_omits_failure_block():
    result = convert.ConversionResult(
        succeeded=[Path("a.docx")], failed=[], skipped=[]
    )

    text = convert.format_summary(result)

    assert "失敗 0 件" in text
    assert "失敗:" not in text
