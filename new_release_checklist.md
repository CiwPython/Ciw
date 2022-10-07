# To draft a new release

Requirements:
  + pip install build
  + pip install twine

1) Update `ciw/version.py`
2) Update CHANGES.rst
3) Push to GitHub and draft new release on GitHub
4) Build distribution with: `python -m build`
5) Push to PyPI with: `twine upload --repository-url https://upload.pypi.org/legacy/ dist/*`