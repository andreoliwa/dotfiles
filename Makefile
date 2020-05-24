.PHONY: Makefile

help:
	@echo 'Choose one of the following commands:'
	@cat Makefile | egrep '^[a-z-]+: *[./a-z-]* +#' | sed -E -e 's/:.+# */@ /g' | sort | awk -F@ '{printf "%-11s %s\n", $$1, $$2}'
.PHONY: help

clean: # Clean all temporary files
	rm -rf .cache .mypy_cache
.PHONY: clean

.cache/make/pre-commit-autoupdate:
	pre-commit autoupdate
	@mkdir -p .cache/make && touch .cache/make/pre-commit-autoupdate

hooks: .cache/make/pre-commit-autoupdate # Install pre-commit hooks
	pre-commit install --install-hooks
	pre-commit install --hook-type commit-msg
.PHONY: hooks

lint: # Lint all files with pre-commit
	pre-commit run --all-files $(hook)
.PHONY: lint
