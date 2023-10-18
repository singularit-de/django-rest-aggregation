#!/usr/bin/env python
import os
import sys

import django
from coverage import coverage, Coverage
from django.conf import settings
from django.test.utils import get_runner

from tests.test_data import BASIC_TESTING, GROUP_TESTING

if __name__ == "__main__":
    print(BASIC_TESTING + GROUP_TESTING)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
    django.setup()

    cov = Coverage(source=["src"])
    cov.start()

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests"])

    cov.stop()
    cov.save()
    cov.report()

    sys.exit(bool(failures))
