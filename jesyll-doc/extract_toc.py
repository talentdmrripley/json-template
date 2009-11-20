#!/usr/bin/python -S
"""
extract_toc.py

Custom script to extract a table of contents from my posts.
"""

__author__ = 'Andy Chu'

import os
import re
import sys

if __name__ == '__main__':
  sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

import jsontemplate


class Error(Exception):
  pass


TOC_TEMPLATE = """\
{.repeated section headings}
  <a href="#{target}">{name}</a><br>
{.end}
"""

_HEADING_RE = re.compile(
  '<a name="(?P<target>[^"]+)"><h3>(?P<name>[^<]+)</h3></a>')

def MakeToc(blog_template):
  """
  """
  headings = []
  for match in _HEADING_RE.finditer(blog_template):
    headings.append(
        dict(target=match.group('target'), name=match.group('name')))

  toc = jsontemplate.expand(TOC_TEMPLATE, {'headings': headings})
  return toc


def main(argv):
  try:
    contents = open(argv[1]).read()
  except IndexError:
    raise Error('Usage: %s <filename>' % sys.argv[0])

  sys.stdout.write(MakeToc(contents))


if __name__ == '__main__':
  try:
    sys.exit(main(sys.argv))
  except Error, e:
    print >> sys.stderr, e.args[0]
    sys.exit(1)
