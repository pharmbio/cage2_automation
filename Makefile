CODE_PATHS := lab_adaption

.PHONY: build test serve generate-docs publish-gitlab clean

help:	## Prints this help/overview message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-z0-9_-]+:.*?## / {printf "\033[36m%-17s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

test:	## run the test suite
	pytest tests/

# cleaning up --------------------------------------------------------
clean: clean__py clean__reports

clean__py:	## clean python temp files
	find . -iname *.pyc -delete
	find . -iname __pycache__ -delete
	find . -iname .cache -delete

clean__reports:
	rm -rf ${PATH_REPORTS}


serve: generate-docs
	mkdocs serve --livereload

generate-docs:
	python generate_docs.py

build: generate-docs
	mkdocs build

publish-gitlab: generate-docs	## build MkDocs site into public/ for GitLab Pages
	mkdocs build --site-dir public
