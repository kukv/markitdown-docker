from pathlib import Path

import convert


def test_find_target_files_filters_and_sorts(tmp_path):
    (tmp_path / "a.docx").write_bytes(b"")
    (tmp_path / "b.pdf").write_bytes(b"")
    (tmp_path / "c.txt").write_bytes(b"")           # 非対応
    (tmp_path / "d.PPTX").write_bytes(b"")          # 大文字拡張子
    (tmp_path / "sub").mkdir()                       # ディレクトリは無視
    (tmp_path / "sub" / "e.docx").write_bytes(b"")  # ネストは無視

    result = convert.find_target_files(tmp_path)

    assert result == [tmp_path / "a.docx", tmp_path / "b.pdf", tmp_path / "d.PPTX"]


def test_output_path_for_uses_stem_and_md(tmp_path):
    out = convert.output_path_for(Path("/data/input/report.docx"), tmp_path)
    assert out == tmp_path / "report.md"
