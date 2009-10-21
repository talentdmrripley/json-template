#!/usr/bin/python -S
#
# Copyright (C) 2009 Andy Chu
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Expand a JSON template, given a data dictionary.

Usage:
  expand.py 'a is {a}' '{"a": 1}'
"""

__author__ = 'Andy Chu'


import os
import sys

if __name__ == '__main__':
  sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), '..'))

from pan.core import cmdapp
from pan.core import params
from pan.core import json

import jsontemplate
from jsontemplate import formatters

PARAMS = [
    params.OptionalBoolean(
        'files', shortcut='f',
        help='Read from the named files.  The default is to use the arguments '
        'as strings'),
    params.RequiredString(
        'template', shortcut='t', pos=1,
        help='The template (filename or string)'),
    params.RequiredString(
        'json', shortcut='j', pos=2,
        help='The JSON data dictionary to expand the template with '
        '(filename or string)'),
    params.OptionalBoolean(
        'more-formatters', shortcut='m',
        help='Use all formatters that exist in the Python implementation'),
    # TODO: Argh, this doesn't work for command line parsing; only URL parsing.
    # It would be nice to be able to substitute small values as flags.
    params.UNDECLARED,
    ]

def main(argv):
  """Returns an exit code."""

  options = cmdapp.ParseArgv(argv[1:], PARAMS)

  if options.files:
    template_str = open(options.template).read()
    dictionary = open(options.json).read()
  else:
    template_str = options.template
    dictionary = options.json

  dictionary = json.loads(dictionary)

  if options.more_formatters:
    more_formatters = formatters.PythonPercentFormat
  else:
    more_formatters = lambda x: None

  t = jsontemplate.FromString(template_str, more_formatters=more_formatters)
  sys.stdout.write(t.expand(dictionary))


if __name__ == '__main__':
  sys.exit(main(sys.argv))
