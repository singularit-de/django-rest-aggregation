# Installation

```bash
uv add django-rest-aggregation
```

This also installs the runtime dependencies: Django ≥ 4.2, Django REST Framework ≥ 3.14 and
django-filter ≥ 23.5.

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
