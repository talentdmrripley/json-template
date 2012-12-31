#!/bin/bash
#
# jsont-test.sh

# TODO: Shouldn't need do.sh?  Maybe just bin/jsont.
jsont() {
  ./do.sh jsont "$@"
}

test-inline() {
  echo '{"foo": "bar"}' | jsont --template '[{foo}]'
}

test-formatter() {
  echo '{"num": 0.0000012345}' | jsont --template '[{num|printf %.3f}]'
}

"$@"
