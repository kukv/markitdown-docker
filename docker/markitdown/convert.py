"""markitdown batch converter — converts documents in /data/input to Markdown in /data/output."""
from __future__ import annotations

from pathlib import Path

INPUT_DIR = Path("/data/input")
OUTPUT_DIR = Path("/data/output")

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


def main() -> int:
    print("convert.py: not implemented yet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
