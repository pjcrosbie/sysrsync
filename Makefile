

.Phony: test

test:
	pipenv run nosetests -vv test_sysrsync.py

