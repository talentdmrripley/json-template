#!/bin/bash
#
# Misc utilities

action=$1
shift

TASTE_DIR=~/hg/taste

case $action in

  pygrep)
    find . -name \*.py | xargs grep "$@"
    ;;

  py-tests)
    # Run Python unit tests
    export PYTHONPATH=$TASTE_DIR
    set -o errexit
    ./jsontemplate_test.py
    python/jsontemplate/jsontemplate_unittest.py
    python/jsontemplate/formatters_test.py
    ;;

  js-tests)
    set -o errexit
    ./js_tests.sh
    export PYTHONPATH=$TASTE_DIR
    ./jsontemplate_test.py --javascript
    ;;

  all-tests)
    # Run all unit tests
    export PYTHONPATH=$TASTE_DIR
    set -o errexit
    ./jsontemplate_test.py --all
    ;;

  *)
    echo "Invalid action '$action'"
    exit 1
    ;;
esac
