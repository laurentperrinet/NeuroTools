default: publish

publish:
	python setup.py sdist bdist_wininst upload
