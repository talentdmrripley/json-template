#!/bin/bash
#
# Misc utilities

action=$1
shift

PAN_DIR=~/svn/pan/trunk

case $action in

  pygrep)
    find . -name \*.py | xargs grep "$@"
    ;;

  py-tests)
    # Run Python unit tests
    export PYTHONPATH=$PAN_DIR
    set -o errexit
    ./jsontemplate_test.py
    python/jsontemplate/jsontemplate_unittest.py
    ;;

  js-tests)
    set -o errexit
    ./js_tests.sh
    export PYTHONPATH=$PAN_DIR
    ./jsontemplate_test.py --javascript
    ;;

  all-tests)
    # Run all unit tests
    export PYTHONPATH=$PAN_DIR
    set -o errexit
    ./jsontemplate_test.py --all
    ;;

  *)
    echo "Invalid action '$action'"
    exit 1
    ;;
esac
