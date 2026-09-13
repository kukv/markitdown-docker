.PHONY: build convert test clean

DEV := docker compose -f compose.dev.yaml

build:
	$(DEV) build

convert:
	$(DEV) run --rm markitdown

test:
	$(DEV) run --rm --entrypoint python markitdown -m pytest -v

clean:
	$(DEV) run --rm --entrypoint sh markitdown -c 'rm -f /data/output/*.md'
