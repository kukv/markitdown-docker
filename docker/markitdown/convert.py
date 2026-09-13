"""markitdown batch converter — converts documents in /data/input to Markdown in /data/output."""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

INPUT_DIR = Path("/data/input")
OUTPUT_DIR = Path("/data/output")

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx", ".xls"}


def _is_user_file(path: Path) -> bool:
    """直下の通常ファイルで、ドットファイル（.gitkeep など）を除外する。"""
    return path.is_file() and not path.name.startswith(".")


def find_target_files(input_dir: Path) -> list[Path]:
    """input_dir 直下の対応拡張子ファイルを名前順で返す。"""
    return sorted(
        p
        for p in input_dir.iterdir()
        if _is_user_file(p) and p.suffix.lower() in SUPPORTED_EXTENSIONS
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
    all_files = [p for p in input_dir.iterdir() if _is_user_file(p)]
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
    if not result.succeeded and not result.skipped and not result.failed:
        lines.append(
            "ℹ️  data/input に対象ファイルが見つかりませんでした。"
            "マウントのパスが正しいか確認してください。"
        )
    return "\n".join(lines)


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
