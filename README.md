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
