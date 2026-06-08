
export PYTHONPATH=src
export DJANGO_SETTINGS_MODULE=propylon_document_manager.site.settings.local

IN_ENV = uv run

# ======================
# Testing and Linting
# ======================
test: build plain-test

plain-test:
	$(IN_ENV) py.test

# ====================
# Clean
# ====================
clean:
	- @rm -rf src/*.egg-info
	- @rm -rf build
	- @rm -rf dist
	- @rm -f .coverage
	- @rm -f test_results.xml
	- @rm -f coverage.xml
	- @find ./src -name '*.pyc' | xargs -r rm
	- @find ./ -name '__pycache__' | xargs rm -rf


env_clean: clean
	- @rm -rf $(ENV_DIR)

# ====================
# Developer Utilities
# ====================
shell:
	$(IN_ENV) django-admin shell

collectstatic:
	$(IN_ENV) django-admin collectstatic

build:
	uv sync --locked

plain-serve:
	$(IN_ENV) django-admin runserver 0.0.0.0:8001

serve: build makemigrations migrate plain-serve

# ============================
# Database & Fixture Utilities
# ============================
makemigrations:
	$(IN_ENV) django-admin makemigrations

migrate:
	$(IN_ENV) django-admin migrate

fixture: build makemigrations migrate plain-fixture

plain-fixture:
	$(IN_ENV) django-admin load_file_fixtures
