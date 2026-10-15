#!/usr/bin/env python
"""Run the test suite with Django's test runner.

All arguments are passed to ``manage.py test``, for example:

    uv run runtests.py
    uv run runtests.py tests.test_validation --failfast
    uv run runtests.py --shuffle --parallel auto
    DB_BACKEND=postgres uv run runtests.py
"""

import os
import sys

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
    execute_from_command_line([sys.argv[0], "test", *sys.argv[1:]])
