PYTHON	= python3
MAIN 	= fly_in.py
MAP		?= maps/example.txt

.PHONY: install run debug clean lint lint-strict test errors

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) $(MAIN) $(MAP)

debug:
	$(PYTHON) -m pdb $(MAIN) $(MAP)

clean:
	rm -rf __pycache__ */__pycache__ .mypy_cache .pytest_cache

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

test:
	$(PYTHON) -m pytest -q tests

errors:
	@for f in maps/errors/*.txt; do \
		echo "== $$f"; $(PYTHON) $(MAIN) $$f 2>&1 || true; \
	done
