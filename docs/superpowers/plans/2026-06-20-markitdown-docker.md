# markitdown-docker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Microsoft markitdown を Docker 上で動かし、`data/input` に置いたドキュメントを `make convert` 一発で `data/output` に Markdown 変換するツールを作る。

**Architecture:** `docker/markitdown/convert.py` が markitdown をライブラリとして呼び出すバッチドライバ。純粋関数（探索・パス変換・一括変換・サマリ整形）に分割し、変換本体を `converter` 引数として注入することで、実ファイルや実 markitdown なしに pytest で検証する。テストはコンテナ内で `python -m pytest` 実行（ローカル Python 不要）。実行は compose の `run --rm`、操作は Makefile で隠蔽。

**Tech Stack:** Python 3.12 (slim), markitdown[docx,pptx,xlsx,xls,pdf], pytest, Docker Compose, GNU Make

## Global Constraints

以下は全タスク共通の制約。各タスクの要件は暗黙的にこれを含む。

- ベースイメージ: `python:3.12-slim`
- 依存は `docker/markitdown/requirements.txt` で**バージョン固定**: `markitdown[docx,pptx,xlsx,xls,pdf]`（＋ `pytest`）
- コンテナ内パスは固定: 入力 `/data/input` / 出力 `/data/output` / 作業ディレクトリ `/app`
- 対応拡張子（大文字小文字を無視）: `.pdf` `.docx` `.pptx` `.xlsx` `.xls`
- 出力命名: `<元ファイル名のstem>.md`。同名が既にあれば**常に上書き**
- エラー方針: 1件失敗してもスキップして続行。プロセスの終了コードは `0`
- 入力はフラット構成（サブディレクトリは処理しない）
- ファイル名/配置の固定値: compose は `compose.yaml`、Dockerfile は `docker/Dockerfile`、イメージに焼く中身は `docker/markitdown/` 配下
- すべての出力メッセージ・サマリは日本語

---

## File Structure

| パス | 役割 |
|------|------|
| `docker/Dockerfile` | python:3.12-slim ベースのイメージ定義。依存インストール＋ソースコピー |
| `docker/markitdown/requirements.txt` | 固定バージョンの依存リスト |
| `docker/markitdown/convert.py` | 変換ドライバ（純粋関数群 + `main()`） |
| `docker/markitdown/tests/test_smoke.py` | 依存導入のスモークテスト |
| `docker/markitdown/tests/test_helpers.py` | 探索・出力パスのテスト |
| `docker/markitdown/tests/test_convert_all.py` | 一括変換・エラー継続・衝突のテスト |
| `docker/markitdown/tests/test_summary.py` | サマリ整形のテスト |
| `compose.yaml` | サービス定義。data マウント + 開発用ソースマウント |
| `Makefile` | `build` / `convert` / `test` / `clean` |
| `.gitignore` | data 配下の中身・キャッシュを除外 |
| `data/input/.gitkeep` `data/output/.gitkeep` | 空フォルダ維持 |
| `README.md` | 使い方（更新） |

各タスクは独立してテスト可能な成果物で終わる。

---

### Task 1: プロジェクト雛形と Docker イメージ（ビルド + スモークテスト）

イメージがビルドでき、`make test` が回り、markitdown が import できる状態を作る。

**Files:**
- Create: `docker/Dockerfile`
- Create: `docker/markitdown/requirements.txt`
- Create: `docker/markitdown/convert.py`（最小スタブ）
- Create: `docker/markitdown/tests/test_smoke.py`
- Create: `compose.yaml`
- Create: `Makefile`
- Create: `.gitignore`
- Create: `data/input/.gitkeep`（空ファイル）
- Create: `data/output/.gitkeep`（空ファイル）

**Interfaces:**
- Consumes: なし（最初のタスク）
- Produces: ビルド済みイメージ `markitdown-docker:local`、`make build` / `make test` コマンド、`/app` 作業ディレクトリ、`INPUT_DIR` / `OUTPUT_DIR` 定数（後続タスクが利用）

- [ ] **Step 1: ディレクトリと空ファイルを作成**

```bash
mkdir -p docker/markitdown/tests data/input data/output
: > data/input/.gitkeep
: > data/output/.gitkeep
```

- [ ] **Step 2: `.gitignore` を作成**

`.gitignore`:
```gitignore
__pycache__/
*.pyc
.pytest_cache/
data/input/*
data/output/*
!data/input/.gitkeep
!data/output/.gitkeep
```

- [ ] **Step 3: `docker/markitdown/requirements.txt` を作成**

```text
markitdown[docx,pptx,xlsx,xls,pdf]==0.1.2
pytest==8.3.4
```

> 注: `0.1.2` は基準値。Step 7 のビルドが「バージョン解決不可」で失敗したら、PyPI または `docker run --rm python:3.12-slim pip index versions markitdown` で最新を確認し、この行を更新してから再ビルドすること。`pytest` も同様。

- [ ] **Step 4: 最小スタブ `docker/markitdown/convert.py` を作成**

```python
"""markitdown batch converter — converts documents in /data/input to Markdown in /data/output."""
from __future__ import annotations

from pathlib import Path

INPUT_DIR = Path("/data/input")
OUTPUT_DIR = Path("/data/output")


def main() -> int:
    print("convert.py: not implemented yet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: スモークテスト `docker/markitdown/tests/test_smoke.py` を作成**

```python
def test_markitdown_importable():
    import markitdown

    assert hasattr(markitdown, "MarkItDown")
```

- [ ] **Step 6: `docker/Dockerfile` を作成**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY markitdown/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY markitdown/ /app/

ENTRYPOINT ["python", "/app/convert.py"]
```

- [ ] **Step 7: `compose.yaml` を作成**

```yaml
services:
  markitdown:
    build:
      context: ./docker
      dockerfile: Dockerfile
    image: markitdown-docker:local
    volumes:
      - ./data/input:/data/input
      - ./data/output:/data/output
      - ./docker/markitdown:/app
```

> `./docker/markitdown:/app` のマウントにより、`convert.py` を編集してもリビルド不要でテスト/変換に反映される（TDD 高速化）。

- [ ] **Step 8: `Makefile` を作成**（各レシピ行の先頭は**タブ**）

```makefile
.PHONY: build convert test clean

build:
	docker compose build

convert:
	docker compose run --rm markitdown

test:
	docker compose run --rm --entrypoint python markitdown -m pytest -v

clean:
	rm -f data/output/*.md
```

> `make test` は `--entrypoint python ... -m pytest` で実行する。`python -m pytest` は作業ディレクトリ `/app` を `sys.path` に入れるため、テストから `import convert` が解決できる。

- [ ] **Step 9: イメージをビルド**

Run: `make build`
Expected: ビルド成功。失敗時は Step 3 の注記に従いバージョンを修正して再実行。

- [ ] **Step 10: スモークテストを実行**

Run: `make test`
Expected: PASS（`test_markitdown_importable` が 1 件成功）

- [ ] **Step 11: Commit**

```bash
git add docker compose.yaml Makefile .gitignore data/input/.gitkeep data/output/.gitkeep
git commit -m "chore: scaffold markitdown-docker image and compose setup"
```

---

### Task 2: 純粋ヘルパー（対象ファイル探索 + 出力パス変換）

入力ディレクトリから対象ファイルを抽出する関数と、出力パスを決める関数を TDD で実装する。

**Files:**
- Modify: `docker/markitdown/convert.py`
- Create: `docker/markitdown/tests/test_helpers.py`

**Interfaces:**
- Consumes: `INPUT_DIR` / `OUTPUT_DIR`（Task 1）
- Produces:
  - `SUPPORTED_EXTENSIONS: set[str]` = `{".pdf", ".docx", ".pptx", ".xlsx", ".xls"}`
  - `find_target_files(input_dir: Path) -> list[Path]`（トップレベルの対応ファイルを名前順）
  - `output_path_for(input_path: Path, output_dir: Path) -> Path`（`output_dir / "<stem>.md"`）

- [ ] **Step 1: 失敗するテストを書く** — `docker/markitdown/tests/test_helpers.py`

```python
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
```

- [ ] **Step 2: テストを実行して失敗を確認**

Run: `make test`
Expected: FAIL（`AttributeError: module 'convert' has no attribute 'find_target_files'`）

- [ ] **Step 3: 最小実装を追加** — `docker/markitdown/convert.py` の `INPUT_DIR`/`OUTPUT_DIR` 定義の直後に追記

```python
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx", ".xls"}


def find_target_files(input_dir: Path) -> list[Path]:
    """input_dir 直下の対応拡張子ファイルを名前順で返す。"""
    return sorted(
        p
        for p in input_dir.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def output_path_for(input_path: Path, output_dir: Path) -> Path:
    """入力ファイルを Markdown 出力パス（<stem>.md）に変換する。"""
    return output_dir / f"{input_path.stem}.md"
```

- [ ] **Step 4: テストを実行して成功を確認**

Run: `make test`
Expected: PASS（スモーク + helpers 計 3 件）

- [ ] **Step 5: Commit**

```bash
git add docker/markitdown/convert.py docker/markitdown/tests/test_helpers.py
git commit -m "feat: add input file discovery and output path mapping"
```

---

### Task 3: 一括変換（エラー継続 + 非対応スキップ + 上書き + 衝突警告）

`converter` を注入して一括変換するコア関数を TDD で実装する。

**Files:**
- Modify: `docker/markitdown/convert.py`
- Create: `docker/markitdown/tests/test_convert_all.py`

**Interfaces:**
- Consumes: `find_target_files`, `output_path_for`, `SUPPORTED_EXTENSIONS`（Task 2）
- Produces:
  - `ConversionResult`（dataclass）フィールド: `succeeded: list[Path]`, `failed: list[tuple[Path, str]]`, `skipped: list[Path]`
  - `convert_all(input_dir: Path, output_dir: Path, converter) -> ConversionResult`
    - `converter` は `Callable[[Path], str]`（Markdown 文字列を返す）。例外を投げた場合はその要素を `failed` に記録して続行
    - 出力先 `<stem>.md` を**上書き**で書き出す。出力名が同一実行内で衝突したら警告を `print` する
    - 非対応拡張子のファイルは `skipped` に記録（変換しない）

- [ ] **Step 1: 失敗するテストを書く** — `docker/markitdown/tests/test_convert_all.py`

```python
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
```

- [ ] **Step 2: テストを実行して失敗を確認**

Run: `make test`
Expected: FAIL（`AttributeError: module 'convert' has no attribute 'convert_all'`）

- [ ] **Step 3: 最小実装を追加** — まずファイル先頭の import を更新

`docker/markitdown/convert.py` の先頭付近を以下に変更:

```python
"""markitdown batch converter — converts documents in /data/input to Markdown in /data/output."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
```

続けて `output_path_for` の下に追記:

```python
@dataclass
class ConversionResult:
    succeeded: list[Path]
    failed: list[tuple[Path, str]]
    skipped: list[Path]


def convert_all(input_dir: Path, output_dir: Path, converter) -> ConversionResult:
    """input_dir の対応ファイルを converter(path) -> markdown で変換し output_dir に書き出す。

    非対応ファイルはスキップ、変換例外は記録して続行する（バッチを止めない）。
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    all_files = [p for p in input_dir.iterdir() if p.is_file()]
    targets = find_target_files(input_dir)
    skipped = sorted(
        p for p in all_files if p.suffix.lower() not in SUPPORTED_EXTENSIONS
    )

    succeeded: list[Path] = []
    failed: list[tuple[Path, str]] = []
    written: set[Path] = set()

    for path in targets:
        out = output_path_for(path, output_dir)
        if out in written:
            print(f"⚠️  出力名が衝突しています: {path.name} → {out.name}（上書きします）")
        try:
            markdown = converter(path)
            out.write_text(markdown, encoding="utf-8")
            written.add(out)
            succeeded.append(path)
        except Exception as exc:  # noqa: BLE001 - 1件の失敗で全体を止めない
            failed.append((path, str(exc)))

    return ConversionResult(succeeded=succeeded, failed=failed, skipped=skipped)
```

- [ ] **Step 4: テストを実行して成功を確認**

Run: `make test`
Expected: PASS（スモーク + helpers + convert_all 計 8 件）

- [ ] **Step 5: Commit**

```bash
git add docker/markitdown/convert.py docker/markitdown/tests/test_convert_all.py
git commit -m "feat: add batch conversion with skip-on-error and collision warning"
```

---

### Task 4: サマリ整形

変換結果を人間向けサマリ文字列にする関数を TDD で実装する。

**Files:**
- Modify: `docker/markitdown/convert.py`
- Create: `docker/markitdown/tests/test_summary.py`

**Interfaces:**
- Consumes: `ConversionResult`（Task 3）
- Produces: `format_summary(result: ConversionResult) -> str`
  - 1 行目: `✅ 成功 N 件 / ⏭ 非対応 K 件 / ❌ 失敗 M 件`
  - 失敗が 1 件以上あるときのみ続けて `失敗:` 見出しと `  - <ファイル名>: <理由>` を列挙

- [ ] **Step 1: 失敗するテストを書く** — `docker/markitdown/tests/test_summary.py`

```python
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
```

- [ ] **Step 2: テストを実行して失敗を確認**

Run: `make test`
Expected: FAIL（`AttributeError: module 'convert' has no attribute 'format_summary'`）

- [ ] **Step 3: 最小実装を追加** — `convert_all` の下に追記

```python
def format_summary(result: ConversionResult) -> str:
    lines = [
        f"✅ 成功 {len(result.succeeded)} 件 / "
        f"⏭ 非対応 {len(result.skipped)} 件 / "
        f"❌ 失敗 {len(result.failed)} 件"
    ]
    if result.failed:
        lines.append("失敗:")
        for path, reason in result.failed:
            lines.append(f"  - {path.name}: {reason}")
    return "\n".join(lines)
```

- [ ] **Step 4: テストを実行して成功を確認**

Run: `make test`
Expected: PASS（計 10 件）

- [ ] **Step 5: Commit**

```bash
git add docker/markitdown/convert.py docker/markitdown/tests/test_summary.py
git commit -m "feat: add conversion summary formatting"
```

---

### Task 5: `main()` 結線 + README + 実地確認（E2E）

実 markitdown を使う `main()` を結線し、実ファイルでエンドツーエンド確認し、README を整える。

**Files:**
- Modify: `docker/markitdown/convert.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: `convert_all`, `format_summary`, `INPUT_DIR`, `OUTPUT_DIR`（Task 2-4）
- Produces: 実行可能な CLI（`make convert`）。`main() -> int`（常に 0 を返す）

- [ ] **Step 1: `main()` を実装** — `docker/markitdown/convert.py` の先頭 import に `sys` を追加

先頭の import ブロックを以下に更新:

```python
"""markitdown batch converter — converts documents in /data/input to Markdown in /data/output."""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
```

ファイル末尾の既存スタブ（`def main()` と `if __name__ == "__main__":` ブロック）を以下で**置き換える**:

```python
def main() -> int:
    from markitdown import MarkItDown

    md = MarkItDown()

    def converter(path: Path) -> str:
        return md.convert(str(path)).text_content

    result = convert_all(INPUT_DIR, OUTPUT_DIR, converter)
    print(format_summary(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: 既存ユニットテストが壊れていないことを確認**

Run: `make test`
Expected: PASS（計 10 件のまま。`main()` は実 markitdown を使うのでユニットテスト対象外）

- [ ] **Step 3: 実ファイルで E2E 確認用のサンプル .xlsx を生成**

markitdown[xlsx] が同梱する openpyxl を使い、コンテナ内で実ファイルを生成する:

```bash
docker compose run --rm --entrypoint python markitdown -c "import openpyxl; wb=openpyxl.Workbook(); ws=wb.active; ws['A1']='hello markitdown'; wb.save('/data/input/sample.xlsx')"
```

Expected: ホスト側に `data/input/sample.xlsx` が生成される。
（openpyxl が無い環境なら、代わりに手持ちの実 `.docx`/`.pdf`/`.pptx` を `data/input/` に置いて以降を実施する）

- [ ] **Step 4: 変換を実行**

Run: `make convert`
Expected: 標準出力に `✅ 成功 1 件 / ⏭ 非対応 0 件 / ❌ 失敗 0 件` 相当が表示される。

- [ ] **Step 5: 出力を確認**

Run: `cat data/output/sample.md`
Expected: ファイルが存在し、本文に `hello markitdown` を含む。

- [ ] **Step 6: 確認用サンプルを片付ける**

```bash
rm -f data/input/sample.xlsx
make clean
```

- [ ] **Step 7: README を更新** — `README.md` を以下で置き換える

```markdown
# markitdown-docker

Microsoft [markitdown](https://github.com/microsoft/markitdown) を Docker で動かし、
各種ドキュメント（PDF / Word / Excel / PowerPoint）を Markdown に一括変換するツール。
ローカル環境に Python や依存を入れずに使える。

## 必要要件

- Docker / Docker Compose
- GNU Make

## 使い方

1. イメージをビルド:

   ```bash
   make build
   ```

2. 変換したいファイルを `data/input/` に置く（対応形式: `.pdf` `.docx` `.pptx` `.xlsx` `.xls`）

3. 変換を実行:

   ```bash
   make convert
   ```

4. `data/output/` に Markdown が出力される（例: `report.docx` → `report.md`）

## 挙動

- 出力名は元ファイルの名前 + `.md`。**同名が既にあれば上書き**する。
- 非対応形式や壊れたファイルが混ざっていても**止まらず**、最後に
  `✅ 成功 N 件 / ⏭ 非対応 K 件 / ❌ 失敗 M 件` のサマリを表示する。
- 入力はフラット構成（`data/input` 直下のみ）。サブフォルダ内は処理しない。

> ⚠️ 注意: `report.docx` と `report.pdf` のように拡張子違いで同名のファイルがあると、
> 出力 `report.md` が衝突し後勝ちで上書きされます（警告ログを表示）。

## 開発

テスト（コンテナ内で実行。ローカル Python 不要）:

```bash
make test
```

| ファイル | 役割 |
|----------|------|
| `docker/Dockerfile` | イメージ定義 |
| `docker/markitdown/convert.py` | 変換ドライバ |
| `docker/markitdown/tests/` | pytest テスト |
| `compose.yaml` | サービス定義・マウント |
| `Makefile` | `build` / `convert` / `test` / `clean` |
```

- [ ] **Step 8: 最終確認 — 出力ディレクトリがクリーンで git 状態が想定通りか**

Run: `git status`
Expected: 変更は `docker/markitdown/convert.py` と `README.md` のみ（`data/` 配下の生成物は .gitignore 済み）。

- [ ] **Step 9: Commit**

```bash
git add docker/markitdown/convert.py README.md
git commit -m "feat: wire up main() entrypoint and document usage"
```

---

## Self-Review

**1. Spec coverage（spec の各要件 → 実装タスク）**

- 目的（input → docker → markdown 出力）: Task 5（main + e2e）✅
- 対応形式 PDF/Word/Excel/PowerPoint: Task 2（`SUPPORTED_EXTENSIONS`）+ Task 1（extras）✅
- ディレクトリ構成（docker/ / docker/markitdown/ / data/ / compose.yaml）: Task 1 ✅
- Dockerfile（slim / requirements 固定 / ENTRYPOINT / 固定パス）: Task 1 ✅
- convert.py（フラット走査 / 拡張子フィルタ / 上書き / スキップ継続 / サマリ / 終了コード0）: Task 2-5 ✅
- compose.yaml（build context ./docker / data マウント）: Task 1 ✅
- Makefile（build/convert/clean、+ test）: Task 1 ✅
- README（概要/要件/使い方/形式/出力ルール/衝突注意）: Task 5 ✅
- エラーハンドリング表（非対応スキップ/例外継続/空入力/上書き）: Task 3（空入力は targets 空 → 成功0のサマリで自然に処理）✅
- 衝突エッジケース（警告ログ）: Task 3 ✅

ギャップなし。

**2. Placeholder scan:** すべてのコード・コマンドは実体入り。バージョンは基準値＋確認手順を明記（プレースホルダではなく検証可能な指示）。✅

**3. Type consistency:** `find_target_files`/`output_path_for`/`convert_all`/`format_summary`/`ConversionResult`（フィールド `succeeded`/`failed`/`skipped`）/`converter` シグネチャは全タスクで一貫。`make test` は全タスク共通で `python -m pytest`。✅
