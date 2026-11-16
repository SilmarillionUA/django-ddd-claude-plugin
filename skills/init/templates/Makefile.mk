PYTHON = $(if $(VIRTUAL_ENV),python,$(firstword $(wildcard .venv/bin/python)))

test:
	$(PYTHON) -m pytest

format:
	$(PYTHON) -m isort {source_root}
	$(PYTHON) -m black {source_root}
	find {source_root} -type f -name "*.html" -exec $(PYTHON) -m djade {} --target-version {django_target_version} \;

architecture:
	$(PYTHON) scripts/ddd_layer_guard.py --all

lint: architecture
	$(PYTHON) -m flake8 {source_root}
	$(PYTHON) -m black --check {source_root}
	$(PYTHON) -m isort --check-only {source_root}
