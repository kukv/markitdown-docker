.PHONY: build convert test clean

build:
	docker compose build

convert:
	docker compose run --rm markitdown

test:
	docker compose run --rm --entrypoint python markitdown -m pytest -v

clean:
	rm -f data/output/*.md
