#!/bin/bash
#
# jsont-test.sh

# TODO: is there a simpler way to do this?
jsont() {
  bin/jsont "$@"
}

test-inline() {
  echo '{"foo": "bar"}' | jsont --template '[{foo}]'
}

test-formatter() {
  echo '{"num": 0.0000012345}' | jsont --template '[{num|printf %.3f}]'
}

"$@"
