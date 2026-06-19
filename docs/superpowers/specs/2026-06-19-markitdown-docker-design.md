# markitdown-docker 設計書

- 作成日: 2026-06-19
- ステータス: 承認済み（実装プラン作成へ）

## 1. 目的

Microsoft の [markitdown](https://github.com/microsoft/markitdown) を Docker 上で動かし、
ローカル環境を汚さずに各種ドキュメントを Markdown へ一括変換するツールを作る。

利用イメージ:

1. 変換したいドキュメントを `data/input/` に置く
2. `make convert` を実行する
3. `data/output/` に Markdown ファイルが出力される

## 2. スコープ

### 対象

- 入力: Office 系ドキュメント + PDF（`.pdf` / `.docx` / `.pptx` / `.xlsx` / `.xls`）
- 出力: Markdown（`.md`）
- 実行: Docker / Docker Compose 上でのバッチ変換（1回実行して終了）

### 非対象（YAGNI）

- Markdown → PDF などの逆変換
- 画像内テキスト抽出（OCR）や音声文字起こし、LLM による画像説明生成
- サブディレクトリの再帰処理（入力はフラット構成を前提）
- Docker Hub 等へのイメージ公開

将来必要になれば markitdown の追加 extras（`az-doc-intel`, `audio-transcription` 等）で拡張可能。

## 3. ディレクトリ構成

```
markitdown-docker/
├── docker/
│   ├── Dockerfile               # Dockerfile は docker/ 直下
│   └── markitdown/              # イメージに焼き込む中身
│       ├── convert.py           # 変換ドライバ
│       └── requirements.txt     # markitdown をバージョン固定
├── data/
│   ├── input/                   # 変換したいドキュメントを置く（.gitkeep で空フォルダ維持）
│   └── output/                  # .md が出力される（.gitkeep で空フォルダ維持）
├── compose.yaml
├── Makefile
└── README.md
```

- `data/input/` `data/output/` は中身を git 管理せず、フォルダのみ残す（`.gitkeep`、`.gitignore` で中身を無視）。

## 4. コンポーネント設計

### 4.1 Dockerfile（`docker/Dockerfile`）

- ベースイメージ: `python:3.12-slim`
- `docker/markitdown/requirements.txt` を使って依存をインストール
  - `markitdown[docx,pptx,xlsx,xls,pdf]` を**バージョン固定**（実装時の最新安定版でピン留め）
- `docker/markitdown/convert.py` をイメージ内 `/app/convert.py` にコピー
- `ENTRYPOINT ["python", "/app/convert.py"]`
- コンテナ内の入出力パスは固定: `/data/input` → `/data/output`

ビルドコンテキストは `./docker`。よって Dockerfile からは `markitdown/convert.py` /
`markitdown/requirements.txt` を相対パスでコピーする。

### 4.2 変換ドライバ（`docker/markitdown/convert.py`）

markitdown を**ライブラリとして**呼び出す Python スクリプト（案1）。

処理フロー:

1. `/data/input` 直下を走査（フラット構成。サブディレクトリは対象外）
2. 対象拡張子のみ処理: `.pdf` `.docx` `.pptx` `.xlsx` `.xls`（大文字小文字は無視）
3. 各ファイルを `try/except` で 1 件ずつ変換し、`/data/output/<stem>.md` に書き出す
   - 例: `report.docx` → `report.md`
4. **上書きポリシー**: 出力先に同名 `.md` があっても**常に上書き**する
5. **エラーポリシー**: 変換に失敗したファイルは**スキップして続行**し、失敗として記録する
6. 最後にサマリを標準出力に表示:
   - `✅ 成功 N 件 / ⏭ 非対応 K 件 / ❌ 失敗 M 件`
   - 失敗したファイル名と理由の一覧
7. 終了コードは `0`（失敗ファイルがあっても、バッチ処理自体は完了扱い）

### 4.3 compose.yaml

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
```

常駐サービスではなくバッチ実行のため、`up` ではなく `run --rm` で都度実行する。

### 4.4 Makefile

```makefile
.PHONY: build convert clean

build:               ## イメージをビルド
	docker compose build

convert:             ## data/input を変換して data/output に出力
	docker compose run --rm markitdown

clean:               ## 出力をクリア
	rm -f data/output/*.md
```

基本フロー: `make build` → `data/input` にファイル投入 → `make convert`。

### 4.5 README

以下を記載する:

- 概要
- 必要要件（Docker / Docker Compose）
- 使い方（`make build` / ファイル配置 / `make convert`）
- 対応形式（PDF / Word / Excel / PowerPoint）
- 出力ルール（`name.ext → name.md`、上書き、エラースキップ＋サマリ）
- 出力ファイル名の衝突に関する注意（下記エッジケース）

## 5. データフロー

```
data/input/*.{pdf,docx,pptx,xlsx,xls}
        │  (bind mount: ./data/input → /data/input)
        ▼
  convert.py (markitdown ライブラリ)
        │
        ▼
data/output/*.md
        ▲
        │  (bind mount: ./data/output → /data/output)
```

## 6. エラーハンドリング

| ケース | 挙動 |
|--------|------|
| 非対応拡張子のファイル | スキップ（「非対応」としてカウント） |
| 変換中に例外 | スキップして続行、失敗として記録 |
| `data/input` が空 | 「対象ファイルなし」を表示して正常終了 |
| 出力先に同名 `.md` 既存 | 上書き |

## 7. エッジケース / 既知の制限

- **出力ファイル名の衝突**: `report.docx` と `report.pdf` が両方あると、出力先の
  `report.md` が衝突し**後勝ちで上書き**される。発生時は警告ログを出す。
  必要になれば `report.docx.md` のように元拡張子を含めた命名へ変更可能（現時点では未採用）。
- 入力はフラット構成前提。サブディレクトリ内のファイルは処理しない。
- レガシーバイナリ形式（`.doc` / `.ppt` 等）は markitdown の対応状況に依存する。

## 8. 受け入れ基準

- `make build` でイメージがビルドできる。
- `data/input` に Office/PDF ファイルを置いて `make convert` すると、対応する `.md` が
  `data/output` に生成される。
- 壊れたファイルや非対応ファイルが混ざっていても処理が止まらず、最後にサマリが表示される。
- 同名出力が既に存在する場合は上書きされる。
