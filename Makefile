.PHONY: format lint

format:
	black .

lint:
	pylint *.py
