# djangocms-no-versioning

[//]: # ([![CI]&#40;https://github.com/bnzk/djangocms-no-versioning/actions/workflows/ci.yml/badge.svg&#41;]&#40;https://github.com/bnzk/djangocms-no-versioning/actions/workflows/ci.yml&#41;)

[//]: # ()
[//]: # ([![Version]&#40;https://img.shields.io/pypi/v/djangocms-no-versioning.svg?style=flat-square "Version"&#41;]&#40;https://pypi.python.org/pypi/djangocms-no-versioning/&#41;)

[//]: # ()
[//]: # ([![Licence]&#40;https://img.shields.io/github/license/bnzk/djangocms-no-versioning.svg?style=flat-square "Licence"&#41;]&#40;https://pypi.python.org/pypi/djangocms-no-versioning/&#41;)

[//]: # ()
[//]: # ([![PyPI Downloads]&#40;https://img.shields.io/pypi/dm/djangocms-no-versioning?style=flat-square "PyPi Downloads"&#41;]&#40;https://pypistats.org/packages/djangocms-no-versioning&#41;)

This is a proof of concept, to enable published/unpublished pages in django-cms v4+, without versioning. As without
djangocms-versioning, all pages are immediatly published, and cannot be hidden.

## Features



## Development


### Getting started

- there is test app, available with `./manage.py runserver`.
- to run tests: `./manage.py test`
- to run tests with many django and cms version combinations: `tox`


### Contributions

If you want to contribute to this project, please perform the following steps

    # Fork this repository
    # Clone your fork
    mkvirtualenv djangocms-no-versioning
    pip install -r dev_requirements.txt
    git checkout -b feature_branch
    ...