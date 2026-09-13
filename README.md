# markitdown-docker

Microsoft [markitdown](https://github.com/microsoft/markitdown) を Docker で動かし、
各種ドキュメント（PDF / Word / Excel / PowerPoint）を Markdown に一括変換するツール。
ローカル環境に Python や依存を入れずに使える。

> Microsoft 公式のプロジェクトではありません。[markitdown](https://github.com/microsoft/markitdown)
> を Docker イメージとして配布する非公式のラッパーです。

## 必要要件

- Docker

## 使い方

1. 入出力ディレクトリを作る:

   ```bash
   mkdir -p data/input data/output
   ```

2. 変換したいファイルを `data/input/` に置く（対応形式: `.pdf` `.docx` `.pptx` `.xlsx` `.xls`）

3. 変換を実行:

   ```bash
   docker run --rm \
     -v "$PWD/data/input:/data/input" \
     -v "$PWD/data/output:/data/output" \
     ghcr.io/kukv/markitdown-docker:v0.1.0
   ```

4. `data/output/` に Markdown が出力される（例: `report.docx` → `report.md`）

### Docker Compose を使う場合

このリポジトリの `compose.yaml` を手元に置けば `docker compose run --rm markitdown`
でも実行できる。

## 挙動

- 出力名は元ファイルの名前 + `.md`。**同名が既にあれば上書き**する。
- 非対応形式や壊れたファイルが混ざっていても**止まらず**、最後に
  `✅ 成功 N 件 / ⏭ 非対応 K 件 / ❌ 失敗 M 件` のサマリを表示する。
- 入力はフラット構成（`data/input` 直下のみ）。サブフォルダ内は処理しない。

> ⚠️ 注意: `report.docx` と `report.pdf` のように拡張子違いで同名のファイルがあると、
> 出力 `report.md` が衝突し後勝ちで上書きされます（警告ログを表示）。

## 開発

clone して、ローカルビルドしたイメージで動かす。ローカルに Python は不要。
GNU Make と Docker Compose が必要。

```bash
make build   # compose.dev.yaml でイメージをビルド
make test    # コンテナ内で pytest を実行
```

| ファイル | 役割 |
|----------|------|
| `docker/Dockerfile` | イメージ定義 |
| `docker/markitdown/convert.py` | 変換ドライバ |
| `docker/markitdown/tests/` | pytest テスト |
| `compose.yaml` | 配布イメージを使う利用者向け定義 |
| `compose.dev.yaml` | ローカルビルド + ソース bind mount の開発用定義 |
| `Makefile` | `build` / `convert` / `test` / `clean` |

## 同梱しているもの

- [markitdown](https://github.com/microsoft/markitdown) 0.1.7 (MIT, Microsoft)

依存パッケージはすべて permissive ライセンス（MIT / BSD / Apache-2.0 ほか）で、
各パッケージのライセンス全文はイメージ内の `*.dist-info/LICENSE` に同梱されている。

## ライセンス

[MIT](LICENSE)
