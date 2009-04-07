#!/usr/bin/python -S
"""
formatters.py

This module should implement the standard list of formatters.

TODO: Specify language-independent formatters.

It also provides a method for *composing lookup chains* for formatters.  Not to
be confused with plain formatter chaining, e.g.

  {variable|html|json}
"""

__author__ = 'Andy Chu'


import os
import sys

from python import jsontemplate  # For TemplateFileInclude


def PythonPercentFormat(format_str):
  """Use Python % format strings as template format specifiers."""

  if format_str.startswith('printf '):
    fmt = format_str[len('printf '):]
    return lambda value: fmt % value
  else:
    return None


class TemplateFileInclude(object):
  """Template include mechanism.

  The relative path is specified as an argument to the template.
  """

  def __init__(self, root_dir):
    self.root_dir = root_dir

  def __call__(self, format_str):
    """Returns a formatter function."""

    if format_str.startswith('template '):
      relative_path = format_str[len('template '):]
      full_path = os.path.join(self.root_dir, relative_path)
      f = open(full_path)
      template = jsontemplate.FromFile(f)
      f.close()
      return template.expand  # a 'bound method'

    else:
      return None  # this lookup is not applicable


if __name__ == '__main__':
  try:
    sys.exit(main(sys.argv))
  except Error, e:
    print >> sys.stderr, e.args[0]
    sys.exit(1)
