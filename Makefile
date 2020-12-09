.PHONY: clean compile_translations coverage diff_cover docs dummy_translations \
        extract_translations fake_translations help pii_check pull_translations push_translations \
        quality requirements selfcheck test test-all upgrade validate

.DEFAULT_GOAL := help

# For opening files in a browser. Use like: $(BROWSER)relative/path/to/file.html
BROWSER := python -m webbrowser file://$(CURDIR)/

help: ## display this help message
	@echo "Please use \`make <target>' where <target> is one of"
	@perl -nle'print $& if m{^[a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

clean: ## remove generated byte code, coverage reports, and build artifacts
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	coverage erase
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

coverage: clean ## generate and view HTML coverage report
	pytest --cov-report html
	$(BROWSER)htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	tox -e docs
	$(BROWSER)docs/_build/html/index.html

upgrade: export CUSTOM_COMPILE_COMMAND=make upgrade
upgrade: ## update the requirements/*.txt files with the latest packages satisfying requirements/*.in
	pip install -qr requirements/pip-tools.txt
	# Make sure to compile files after any other files they include!
	pip-compile --upgrade -o requirements/pip-tools.txt requirements/pip-tools.in
	pip-compile --upgrade -o requirements/base.txt requirements/base.in
	pip-compile --upgrade -o requirements/test.txt requirements/test.in
	pip-compile --upgrade -o requirements/doc.txt requirements/doc.in
	pip-compile --upgrade -o requirements/quality.txt requirements/quality.in
	pip-compile --upgrade -o requirements/travis.txt requirements/travis.in
	pip-compile --upgrade -o requirements/dev.txt requirements/dev.in
	grep -e "^amqp==\|^anyjson==\|^billiard==\|^celery==\|^kombu==\|^click-didyoumean==\|^click-repl==\|^click==\|^prompt-toolkit==\|^vine==" requirements/base.txt > requirements/celery44.txt
	# Let tox control the versions for Django, DRF and celery for testing
	sed -i.tmp '/^django==/d' requirements/test.txt
	sed -i.tmp '/^djangorestframework==/d' requirements/test.txt
	sed -i.tmp '/^amqp==/d' requirements/test.txt
	sed -i.tmp '/^anyjson==/d' requirements/test.txt
	sed -i.tmp '/^billiard==/d' requirements/test.txt
	sed -i.tmp '/^celery==/d' requirements/test.txt
	sed -i.tmp '/^kombu==/d' requirements/test.txt
	sed -i.tmp '/^vine==/d' requirements/test.txt
	rm requirements/test.txt.tmp

quality: ## check coding style with pycodestyle and pylint
	tox -e quality

pii_check: ## check for PII annotations on all Django models
	tox -e pii_check

requirements: ## install development environment requirements
	pip install -qr requirements/pip-tools.txt
	pip-sync requirements/dev.txt requirements/private.*

test: clean ## run tests in the current virtualenv
	pytest

diff_cover: test ## find diff lines that need test coverage
	diff-cover coverage.xml

test-all: quality pii_check ## run tests on every supported Python/Django combination
	tox

validate: quality pii_check test ## run tests and quality checks

selfcheck: ## check that the Makefile is well-formed
	@echo "The Makefile is well-formed."

## Localization targets

extract_translations: ## extract strings to be translated, outputting .mo files
	rm -rf docs/_build
	cd super-csv && ../manage.py makemessages -l en -v1 -d django
	cd super-csv && ../manage.py makemessages -l en -v1 -d djangojs

compile_translations: ## compile translation files, outputting .po files for each supported language
	cd super-csv && ../manage.py compilemessages

detect_changed_source_translations:
	cd super-csv && i18n_tool changed

pull_translations: ## pull translations from Transifex
	tx pull -af --mode reviewed

push_translations: ## push source translation files (.po) from Transifex
	tx push -s

dummy_translations: ## generate dummy translation (.po) files
	cd super_csv && i18n_tool dummy

build_dummy_translations: extract_translations dummy_translations compile_translations ## generate and compile dummy translation files

validate_translations: build_dummy_translations detect_changed_source_translations ## validate translations
