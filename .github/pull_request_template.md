**A pull request that does not fill this in is closed without review.** See
[CONTRIBUTING.md](https://github.com/kukv/markitdown-docker/blob/main/CONTRIBUTING.md) before
opening one. Commits must be signed and use a `feat:` / `fix:` / `docs:` / `chore:` / `ci:`
prefix; CI must pass.

## What and why

<!-- What changes, and why. "Why" is required — a diff without a reason is closed. -->

## Verification

<!-- The exact commands you ran (e.g. `make test`) and what they printed. "I tested it" is not
     enough on its own. -->

## Scope (packaging only?)

<!-- This repository only packages upstream markitdown: `convert.py` stays a single file with no
     dependency beyond markitdown and the standard library, conversion errors never stop a batch,
     and conversion quality itself belongs to microsoft/markitdown. Confirm this change stays
     inside that line, or say why it needs to cross it. If you touched a workflow, confirm any
     new or changed action is pinned to a full commit SHA with a `# vX.Y.Z` comment. -->

## New dependency (delete this section if none)

<!-- Why it's needed, that its license is permissive (MIT / BSD / Apache-2.0 or similar), and that
     you edited `requirements.in` and regenerated `requirements.txt` with
     `uv pip compile requirements.in -o requirements.txt`. -->

## Release notes label

<!-- Which label from .github/release.yaml applies to this change, so the maintainer can attach
     it: Kind: Feature, Kind: Bug Fix, Kind: Enhancement, Impact: Breaking, or Kind: Dependencies. -->

## AI use (verified?)

<!-- If AI assisted this submission, confirm per
     [Use of AI](https://github.com/kukv/markitdown-docker/blob/main/CONTRIBUTING.md#use-of-ai)
     that you've read, verified and can defend the output. -->
