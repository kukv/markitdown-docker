"""markitdown batch converter — converts documents in /data/input to Markdown in /data/output."""
from __future__ import annotations

from dataclasses import dataclass
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


def main() -> int:
    print("convert.py: not implemented yet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
