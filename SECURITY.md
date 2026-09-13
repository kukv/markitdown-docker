# Security Policy

## Supported versions

Only the latest release is supported. No `latest` tag is published: pin the image to a released
version (`ghcr.io/kukv/markitdown-docker:vX.Y.Z`, or to its digest) and update that pin when a new
release comes out. Fixes are not backported to older tags.

## Reporting a vulnerability

Report privately through GitHub: open the **Security** tab of this repository and choose
**Report a vulnerability**. Please do not open a public issue, and do not attach a working
payload to anything public.

Include the image tag or digest you ran, the command you used, and a description of what the
crafted input achieves. If a sample file is needed to reproduce it, say so in the report rather
than attaching it anywhere public.

## What counts as a security issue

- **A crafted input file that affects anything outside `/data/output`.** `convert.py` derives the
  output path from the input file name; an input that makes it write outside the mounted output
  directory, read the rest of the container, or execute code is a vulnerability.
- **Tampering with what is distributed** — the published GHCR image, the release workflow
  (`.github/workflows/release.yml`), or anything that would let a build other than a maintainer's
  signed tag be published under this name.
- **Credentials or other secrets baked into the image**, or leaked into the build log.
- **A known vulnerable dependency shipped in the image.** The pinned set in
  `docker/markitdown/requirements.txt` is what users actually run; `sca` scans it on every pull
  request and weekly, but a report is welcome if something is missed.

Not a security issue:

- A file that fails to convert, or converts into wrong or garbled Markdown. That is an ordinary
  issue — and usually an upstream one, see
  [microsoft/markitdown](https://github.com/microsoft/markitdown).
- Vulnerabilities in markitdown itself or in the parsers it uses. Report those upstream; this
  repository will pick up the fixed version.
- Secrets contained in your own documents. They are your input files; the tool writes what it
  reads into `/data/output`.

Note that the container runs as root and gets whatever you mount into it. Mount only the
directories you intend to convert.

## Handling

Reports are acknowledged and triaged by the maintainer. Once a fix is released, the advisory is
published with credit to the reporter unless anonymity is requested.
