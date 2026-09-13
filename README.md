# markitdown-docker

[日本語](README.ja.md)

A Docker image that wraps Microsoft's [markitdown](https://github.com/microsoft/markitdown) and
converts documents (PDF / Word / Excel / PowerPoint) to Markdown in batch. Nothing has to be
installed locally — no Python, no dependencies.

> This is not an official Microsoft project. It is an unofficial wrapper that distributes
> [markitdown](https://github.com/microsoft/markitdown) as a Docker image.

## Requirements

- Docker

## Usage

1. Create the input and output directories:

   ```bash
   mkdir -p data/input data/output
   ```

2. Put the files to convert into `data/input/` (supported: `.pdf` `.docx` `.pptx` `.xlsx` `.xls`)

3. Run the conversion:

   ```bash
   docker run --rm \
     -v "$PWD/data/input:/data/input" \
     -v "$PWD/data/output:/data/output" \
     ghcr.io/kukv/markitdown-docker:v0.1.0
   ```

4. The Markdown is written to `data/output/` (for example `report.docx` → `report.md`)

### With Docker Compose

Fetch `compose.yaml` and the same run becomes `docker compose run --rm markitdown`
(the Docker Compose plugin is required).

```bash
curl -O https://raw.githubusercontent.com/kukv/markitdown-docker/main/compose.yaml
```

## Behavior

- The output name is the input file name with its extension replaced by `.md`. **An existing
  file of that name is overwritten.**
- Unsupported formats and broken files **do not stop the batch**. A summary is printed at the
  end: `✅ 成功 N 件 / ⏭ 非対応 K 件 / ❌ 失敗 M 件` (succeeded / unsupported / failed — the
  program prints it in Japanese).
- The input is flat: only the files directly under `data/input` are read; subdirectories are not.

> ⚠️ Note: files that differ only by extension, such as `report.docx` and `report.pdf`, both map
> to `report.md`. The output collides and the one converted later wins (a warning is logged).

## Development

Clone the repository and run the locally built image. Python is not needed locally; Docker, the
Docker Compose plugin and GNU Make are.

```bash
make build   # build the image from compose.dev.yaml
make test    # run pytest inside the container
```

| File | Role |
|------|------|
| `docker/Dockerfile` | Image definition |
| `docker/markitdown/convert.py` | Conversion driver |
| `docker/markitdown/tests/` | pytest tests |
| `compose.yaml` | Definition for users running the distributed image |
| `compose.dev.yaml` | Development definition: local build plus a source bind mount |
| `Makefile` | `build` / `convert` / `test` / `clean` |

## What is included

- [markitdown](https://github.com/microsoft/markitdown) 0.1.7 (MIT, Microsoft)

Every dependency is under a permissive license (MIT / BSD / Apache-2.0 and similar), and the full
license text of each package ships inside the image in each package's `*.dist-info/` directory.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Report vulnerabilities through the process in
[SECURITY.md](SECURITY.md). Everyone taking part is expected to follow the
[Code of Conduct](CODE_OF_CONDUCT.md).

## License

[MIT](LICENSE)
