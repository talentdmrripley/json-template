#!/bin/bash
#
# Scripts for JSON Template
#
# Usage:
#   ./do.sh <action> <args>

TASTE_DIR=~/hg/taste

pygrep() {
  find . -name \*.py | xargs grep "$@"
}

py-tests() {
  # Run Python unit tests
  export PYTHONPATH=$TASTE_DIR
  set -o errexit
  ./jsontemplate_test.py "$@"
  python/jsontemplate/jsontemplate_unittest.py
  python/jsontemplate/formatters_test.py
}

js-tests() {
  set -o errexit
  ./js_tests.sh
  export PYTHONPATH=$TASTE_DIR
  ./jsontemplate_test.py --javascript
}

all-tests() {
  # Run all unit tests
  export PYTHONPATH=$TASTE_DIR
  set -o errexit
  ./jsontemplate_test.py --all
}

"$@"
