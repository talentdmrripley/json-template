#!/bin/bash
#
# This directory contains a patch to convert Python 2.x jsontemplate.py to Python
# 3.
#
# For now we are maintaining this patch in the source repo.  When
# python/jsontemplate/_jsontemplate.py is updated, this patch can be regenerated
# if necessary.
#
# python3/jsontemplate.py should not be checked in -- only the patch should be.
#
# Patch by kevin.steves@gmail.com.

#
# Usage:
#   ./do.sh <action>


die() {
  echo 1>&2 "$@"
  exit 1
}

# Create the python3 version
make() {
  cp ../python/jsontemplate/_jsontemplate.py jsontemplate.py
  patch -p0 < py3k.patch
}

tests() {
  which python3 || die "Python 3 not installed"

  # Really cheap test: just run it with python3
  python3 jsontemplate.py

  echo "TODO: run language independent tests in jsontemplate_test.py on it"
}

"$@"
