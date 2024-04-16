#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"
    django.setup()

    # cov = Coverage(source=["src"])
    # cov.start()

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests"])

    # cov.stop()
    # cov.save()
    # cov.report()
    # cov.html_report()

    sys.exit(bool(failures))
