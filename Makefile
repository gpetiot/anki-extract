.PHONY: format lint

format:
	black .

lint:
	pylint *.py

docs:
	sphinx-quickstart docs --sep --project 'anki-extract' --author 'Guillaume Petiot' --release '0.1.0' --quiet --makefile --batchfile

publish-docs:
	$(MAKE) -C docs html
	git checkout gh-pages || git checkout --orphan gh-pages
	rsync -av docs/build/html/* .
	git add .
	git commit -m "Update docs"
	git push origin gh-pages
	git checkout main
