# Contributing

## 開発環境

Docker / Docker Compose / GNU Make があれば動く。ローカルに Python は不要。

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

## リリース手順

1. main を最新にして、署名タグを作って push する。タグ作成はリポジトリの
   ルールセットでブロックされており `GITHUB_TOKEN` では bypass できないため、
   必ず手元から push する。

   ```bash
   git tag -s vX.Y.Z -m "vX.Y.Z"
   git push origin vX.Y.Z
   ```

2. `release` ワークフローが GHCR へ multi-arch イメージを publish し、
   GitHub Release を作成する。
3. **初回リリース時のみ**: GHCR パッケージは push 時 private で作られるため、
   Package settings から手動で Public に変更する。
4. 以下のイメージタグを新しいバージョンに更新する。
   - `compose.yaml`
   - `README.md`
   - `.github/ISSUE_TEMPLATE/bug_report.yml`（placeholder）
