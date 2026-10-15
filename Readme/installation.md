# Installation

```bash
pip install django-rest-aggregation
```

The package needs Django, Django REST Framework and django-filter at runtime.
These are currently **not** declared as dependencies in `pyproject.toml`, so install them yourself
(see [PKG-1 in the issues note](issues.md#pkg-1-runtime-dependencies-are-not-declared)):

```bash
pip install django djangorestframework django-filter
```

Add `django_filters` to `INSTALLED_APPS`, because aggregated value filtering uses it:

```python
INSTALLED_APPS = [
    ...,
    "rest_framework",
    "django_filters",
]
```

No app entry for `django_rest_aggregation` is needed; it has no models.

Next: [Quickstart](quickstart.md)
