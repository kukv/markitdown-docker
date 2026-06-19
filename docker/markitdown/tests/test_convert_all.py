import convert


def make_files(folder, names):
    folder.mkdir(parents=True, exist_ok=True)
    for n in names:
        (folder / n).write_bytes(b"")


def test_convert_all_writes_markdown(tmp_path):
    inp, out = tmp_path / "in", tmp_path / "out"
    make_files(inp, ["a.docx", "b.pdf"])

    result = convert.convert_all(inp, out, lambda path: f"# {path.name}")

    assert (out / "a.md").read_text(encoding="utf-8") == "# a.docx"
    assert (out / "b.md").read_text(encoding="utf-8") == "# b.pdf"
    assert set(result.succeeded) == {inp / "a.docx", inp / "b.pdf"}
    assert result.failed == []


def test_convert_all_continues_on_error(tmp_path):
    inp, out = tmp_path / "in", tmp_path / "out"
    make_files(inp, ["good.docx", "bad.pdf"])

    def fake(path):
        if path.name == "bad.pdf":
            raise ValueError("boom")
        return "ok"

    result = convert.convert_all(inp, out, fake)

    assert result.succeeded == [inp / "good.docx"]
    assert len(result.failed) == 1
    assert result.failed[0][0] == inp / "bad.pdf"
    assert "boom" in result.failed[0][1]
    assert (out / "good.md").read_text(encoding="utf-8") == "ok"


def test_convert_all_records_unsupported_as_skipped(tmp_path):
    inp, out = tmp_path / "in", tmp_path / "out"
    make_files(inp, ["a.docx", "note.txt", "image.png"])

    result = convert.convert_all(inp, out, lambda p: "x")

    assert sorted(p.name for p in result.skipped) == ["image.png", "note.txt"]


def test_convert_all_overwrites_existing(tmp_path):
    inp, out = tmp_path / "in", tmp_path / "out"
    make_files(inp, ["a.docx"])
    out.mkdir(parents=True, exist_ok=True)
    (out / "a.md").write_text("OLD", encoding="utf-8")

    convert.convert_all(inp, out, lambda p: "NEW")

    assert (out / "a.md").read_text(encoding="utf-8") == "NEW"


def test_convert_all_warns_on_output_collision(tmp_path, capsys):
    inp, out = tmp_path / "in", tmp_path / "out"
    make_files(inp, ["report.docx", "report.pdf"])

    convert.convert_all(inp, out, lambda p: p.suffix)

    captured = capsys.readouterr()
    assert "衝突" in captured.out
    # 名前順で report.docx → report.pdf の順に処理され、後勝ちで .pdf が残る
    assert (out / "report.md").read_text(encoding="utf-8") == ".pdf"


def test_convert_all_ignores_dotfiles(tmp_path):
    """ドットファイル（.gitkeep など）はスキップ件数に含まれない。"""
    inp, out = tmp_path / "in", tmp_path / "out"
    make_files(inp, [".gitkeep"])

    result = convert.convert_all(inp, out, lambda p: "x")

    assert result.skipped == []
    assert result.succeeded == []
    assert result.failed == []


def test_convert_all_ignores_dotfiles_alongside_real_file(tmp_path):
    """.gitkeep がある場合でも、実ファイルは正常に変換される。"""
    inp, out = tmp_path / "in", tmp_path / "out"
    make_files(inp, [".gitkeep", "a.docx"])

    result = convert.convert_all(inp, out, lambda p: f"# {p.name}")

    assert result.skipped == []
    assert result.succeeded == [inp / "a.docx"]
    assert (out / "a.md").read_text(encoding="utf-8") == "# a.docx"
