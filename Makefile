

.Phony: test

test: pipenv
	pipenv run nosetests -vv tests/*.py

