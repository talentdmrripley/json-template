#!/usr/bin/python
"""Expand a JSON template.

Usage:
  jsont [options] [<template-file>]
  jsont -h | --help
  jsont --version

Options:
  --format=FORMAT
      Read input as either JSON or TNET.  (TODO: autodetect it?)

  --template=TEMPLATE
      Inline template, rather than reading it from a file.
"""

import sys
try:
  import json
except ImportError:
  from simplejson import json

import jsontemplate
from jsontemplate import formatters

import docopt

class UsageError(Exception):
  pass


def main(argv):
  """Returns an exit code."""

  opts = docopt.docopt(__doc__, version='jsont 0.1')

  if opts['--template']:
    # TODO: Could provide an option to suppress this newline.
    template_str = opts['--template'] + '\n'
  else:
    template_file = opts['<template-file>']
    if template_file:
      try:
        f = open(template_file)
      except IOError, e:
        raise RuntimeError(e)
      template_str = f.read()
    else:
      raise UsageError("A template file or inline template is required.")

  # TODO: add more?
  more_formatters = formatters.PythonPercentFormat
  t = jsontemplate.FromString(template_str,
                              more_formatters=more_formatters,
                              # TODO: add more?
                              more_predicates=None)

  dictionary = json.load(sys.stdin)
  s = t.expand(dictionary)
  sys.stdout.write(s.encode('utf-8'))
  return 0


if __name__ == '__main__':
  try:
    sys.exit(main(sys.argv))
  except RuntimeError, e:
    print >>sys.stderr, 'jsont: %s' % e.args[0]
    sys.exit(1)
  except UsageError, e:
    print >>sys.stderr, 'jsont: %s' % e.args[0]
    sys.exit(2)
