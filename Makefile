# fmesh
# Makefile: Ian Dennis Miller

help:
	@grep -e '^\w\S\+\:' Makefile | sed 's/://g' | cut -d ' ' -f 1

run:
	./scripts/fmesh-tui

install:
	pip install -e .

configuration:
	cp example-env.conf .env
