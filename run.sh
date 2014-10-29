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

make-docs() {
  PYTHONPATH=.:$TASTE_DIR doc/makedocs.py "$@"
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

google-code-upload() {
  wget http://support.googlecode.com/svn/trunk/scripts/googlecode_upload.py
  chmod +x googlecode_upload.py
}

# Make release zip with Python and JavaScript versions
# I am doing it this way because Google Code only lets you upload versioned
# files (which is a good thing).  But I don't want people to have to rename
# jsontemplate-0.8.py to jsontemplate.py, etc.

release() {
  local version=$1
  if test -z "$version"; then
    echo "Version required"
    exit 1
  fi

  set -o errexit

  rm -rf release-tmp
  mkdir -p release-tmp
  cd release-tmp
  # remove underscore
  cp ../python/jsontemplate/_jsontemplate.py jsontemplate.py
  cp ../javascript/json-template.js .
  zip json-template-$version.zip json*
  ls *.zip
}

# First run python3/do.sh to create the file to release!
release-python3() {
  local version=$1
  if test -z "$version"; then
    echo "Version required"
    exit 1
  fi
  local outname=json-template-py3k-$version.zip
  rm $outname

  set -o errexit

  rm -rf release-tmp
  mkdir -p release-tmp
  pushd release-tmp
  cp ../python3/jsontemplate.py ../python3/README .
  zip $outname jsontemplate.py README
  ls *.zip
  popd
}

# To run an individual test with the environment
unit() {
  export PYTHONPATH=$TASTE_DIR
  "$@"
}

_link() { ln -s -f -v "$@"; }

install() {
  _link $PWD/bin/jsont ~/bin
}

"$@"
