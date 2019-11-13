lint:
	flake8 *.py
	pylint -disable=C0114,C0115,C0116,C0103,W0703,C0114 *.py
	mypy --ignore-missing-imports *.py

test:
	python -m unittest discover -s tests
