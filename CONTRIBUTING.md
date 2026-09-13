# Contributing

Thanks for taking the time to improve markitdown-docker.

## Getting started

This repository is a Docker image around Microsoft's
[markitdown](https://github.com/microsoft/markitdown). `docker/Dockerfile` installs the pinned
dependencies and `docker/markitdown/convert.py` — one file — is the whole driver: it walks
`/data/input`, converts every supported file, writes `<stem>.md` into `/data/output`, and prints
a summary. The tests live in `docker/markitdown/tests/` and run with pytest inside the container.

You do **not** need Python locally. Docker, the Docker Compose plugin and GNU Make are enough.

```bash
make build     # build the image from compose.dev.yaml
make test      # run pytest inside the container
make convert   # convert whatever is in data/input into data/output
make clean     # remove the generated *.md from data/output
```

There are two compose files and they are not interchangeable. `compose.dev.yaml` builds the image
locally and bind-mounts `./docker/markitdown` onto `/app`, so `make test` and `make convert` run
against your working tree. `compose.yaml` is what users download on its own: it pulls the pinned
`ghcr.io/kukv/markitdown-docker:vX.Y.Z` image and mounts only `data/input` and `data/output`.
Never add the `/app` mount there — a user who fetched just `compose.yaml` has no
`docker/markitdown/` directory, so Docker would create an empty one and shadow the `convert.py`
inside the image.

Please keep the following in mind.

1. `convert.py` stays a single file with no dependency beyond `markitdown` and the standard
   library. It is the only thing this project ships on top of upstream; a driver that needs its
   own library is a sign the change belongs upstream instead.
2. A batch must never be stopped by one bad file. Conversion errors are collected and reported in
   the summary; unsupported extensions are skipped. Keep both behaviors, and cover any change to
   them in `docker/markitdown/tests/`.
3. Bugs and missing formats in the conversion itself belong to
   [microsoft/markitdown](https://github.com/microsoft/markitdown), not here. This repository only
   packages it. `SUPPORTED_EXTENSIONS` in `convert.py` may be extended once upstream supports the
   format and the extra is added to `requirements.in`.
4. Think twice before adding a dependency. Every one of them lands in the distributed image and
   grows both its size and its license surface — everything shipped today is permissive
   (MIT / BSD / Apache-2.0 and similar), and that must stay true. `requirements.txt` is generated,
   so edit `requirements.in` and regenerate it with
   `uv pip compile requirements.in -o requirements.txt`.
5. Pin any GitHub Action you add to a full commit SHA with a `# vX.Y.Z` comment, and pin Docker
   images by digest. Renovate keeps those pins current.

## Pull requests

- `main` is protected; branch off and open a pull request.
- CI must pass: `test` (`ci.yml`, which is `make build` and `make test`) plus `hidden-content`,
  `secrets`, `sca`, `workflow-audit` and `actionlint` (`security.yml`).
- Commits must be signed (`git config commit.gpgsign true`).
- On a pull request from a fork the `GITHUB_TOKEN` is read-only, so the jobs that comment back
  cannot post. The checks themselves still run and still fail the build.
- Commit messages use a `feat:` / `fix:` / `docs:` / `chore:` / `ci:` prefix.
- Label the pull request so it lands in the right section of the release notes — see the
  categories in `.github/release.yaml` (`Kind: Feature`, `Kind: Bug Fix`, `Kind: Enhancement`,
  `Impact: Breaking`, `Kind: Dependencies`).
- Review by the maintainer (`.github/CODEOWNERS`) is required before merge.

## Releases

Creating a tag is blocked by the `protect-tags` ruleset and `GITHUB_TOKEN` cannot bypass it, so
the maintainer always pushes the tag from a local clone.

1. Update `main`, then create and push a signed tag.

   ```bash
   git tag -s vX.Y.Z -m "vX.Y.Z"
   git push origin vX.Y.Z
   ```

2. `release.yml` builds the `linux/amd64` and `linux/arm64` image, pushes it to GHCR with
   provenance and SBOM attestations, and creates the GitHub Release with notes generated from the
   labels of the pull requests included (a tag containing a `-` is published as a prerelease).
3. **First release only**: a package pushed to GHCR is created private. Switch it to Public by
   hand in the package settings, otherwise `docker run` fails for everyone else.
4. Update the image tag in the three places it is pinned:
   - `compose.yaml`
   - `README.md`
   - `.github/ISSUE_TEMPLATE/bug_report.yml` (the placeholder)

No `latest` tag is published. `vX.Y.Z` and `X.Y.Z` are never moved once pushed; `X.Y` follows the
latest patch release.

## Use of AI

AI assistance is fine. Submitting what an AI produced without understanding it is not.

Generating a submission takes seconds; verifying one takes a person's time. Sending
unverified output moves that cost onto the maintainer and takes time away from the review
this project actually needs.

Before you open an issue or a pull request, you are expected to have read the output,
verified it against this repository, and be able to explain and defend it. You are the
author of what you submit, whatever tool helped you write it.

Issues and pull requests that appear to be unreviewed AI output — invented inputs that do not
exist, a diff that does not follow from the description, boilerplate that does not engage with
this project — are **closed without notice and without individual explanation**. That judgment
is the maintainer's, and there is no appeal process; you are welcome to open a new issue or
pull request that shows your own reasoning.

Closing one does not mean the underlying point was worthless. If a closed issue or pull
request contains something useful, the maintainer may take it up — as an issue raised by
the maintainer, or by merging or rewriting the change — without notice and without credit
to the original submitter. Anything you submit is licensed under the
[MIT License](LICENSE), and opening an issue or pull request here means you accept this
handling.

## Reporting problems

- A security-relevant issue: see [SECURITY.md](SECURITY.md).
- Anything else: open an issue with the image tag you ran, the exact command, and the summary
  line or log you got. A small file that reproduces it helps — do not attach a confidential
  document.
- A file that converts into wrong or poor Markdown is an upstream problem; report it to
  [microsoft/markitdown](https://github.com/microsoft/markitdown).

Everyone taking part is expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

By contributing you agree that your contributions are licensed under the
[MIT License](LICENSE).
