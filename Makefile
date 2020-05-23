.PHONY: help build install hooks lint

help:
	@echo 'Choose one of the following commands:'
	@cat Makefile | egrep '^[a-z-]+: *[a-z-]* +#' | sed -E -e 's/:.+# */@ /g' | sort | awk -F@ '{printf "%-11s %s\n", $$1, $$2}'

hooks: # Install pre-commit hooks
	pre-commit install --install-hooks
	pre-commit install --hook-type commit-msg

lint: # Lint all files with pre-commit
	pre-commit run --all-files $(hook)
