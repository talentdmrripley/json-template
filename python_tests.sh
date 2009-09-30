#!/bin/bash
#
# python_tests.sh
# Author: Andy Chu
#
# Quick and dirty script to run all Python tests.  TODO: replace this

python jsontemplate_test.py
python python/jsontemplate/jsontemplate_unittest.py
python python/jsontemplate/formatters_test.py
