#!/bin/sh
# The Pages build fails before upload if any delivery check fails.
set -eu
python3 -m pip install -r requirements-test.txt
python3 build.py
python3 -m unittest discover -s tests -v
