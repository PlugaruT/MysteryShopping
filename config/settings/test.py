from .common import *  # noqa
import logging

SECRET_KEY = env("DJANGO_SECRET_KEY", default='&xc!toi_e027v29qxjw8medhv-fz!%36en=w=1@e9ug@9b_)*4')

# TESTING
# ------------------------------------------------------------------------------
# Use nose to run all tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Tell nose to measure coverage on the apps
NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=mystery_shopping',
]
# Deactivate logging information for factory_boy module
logging.getLogger("factory").setLevel(logging.INFO)

