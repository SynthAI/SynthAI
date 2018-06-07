.PHONY: update docs quality tests clean

upload:
	rm -rf dist
	python setup.py sdist
	twine upload dist/*

package_data:
	( echo vendor/zbar-0.10/zbar/.libs/libzbar.a && echo package_data.txt && cd src/fastzbarlight && git ls-files vendor ) > src/fastzbarlight/package_data.txt

update:
	pip install -r requirements-dev.txt
	python setup.py build_ext --inplace
	pip install -e .

docs:
	sphinx-build -W -n -b html docs ./build/sphinx/html

quality:
	python setup.py check --strict --metadata --restructuredtext
	check-manifest
	flake8 src tests setup.py

tests:
	py.test tests

clean:
	find src "(" -name '*.so' -or -name '*.egg' -or -name '*.pyc' -or -name '*.pyo' ")" -delete
	find src -type d -name __pycache__ -exec rm -r {} \; || :
	make -C src/fastzbarlight/vendor/zbar-0.10 clean
	rm -rf .tox .cache build dist
