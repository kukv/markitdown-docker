# Contributing

## 開発環境

Docker があれば動く。ローカルに Python は不要。

```bash
make build   # イメージをビルド
make test    # コンテナ内で pytest を実行
```

## Pull Request

- main ブランチへの直接 push はできない。ブランチを切って PR を出す。
- CI（test / hidden-content / secrets / sca / workflow-audit / actionlint）が
  すべて通る必要がある。
- コミットには署名が必要（`git config commit.gpgsign true`）。
- fork からの PR では `GITHUB_TOKEN` が read-only になるため、一部のジョブが
  コメントを書けない。検査自体は動く。

## Issue

バグ報告・機能要望はテンプレートを使ってほしい。
