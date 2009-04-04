#!/usr/bin/python -S
"""reusing_the_outside.py

Example of reusing the "outside" of a web page.
"""

import cgi
import os
import sys

try:
  import jsontemplate
except ImportError:
  # For development
  sys.path.insert(0, '..')
  import jsontemplate


# Page 1 and 2 have *different* data dictionaries ...

PAGE_ONE_DATA = {
    'title': "Itchy & Scratchy",
    'desc': 'jerks',
    }

PAGE_TWO_DATA = {
    'title': 'Page Two',
    'verb': 'bites',
    }

# ... and *different* templates

PAGE_ONE_TEMPLATE = jsontemplate.Template(
    '<b>{title}</b> are {desc}', default_formatter='html')

PAGE_TWO_TEMPLATE = jsontemplate.Template(
    '{title} <i>{verb}</i>', default_formatter='html')


# This is the skeleton we want to share between them.  Notice that we use
# {body|raw} to prevent double-escaping, because 'body' is *already HTML*.
# 'title' is plain text.

HTML_TEMPLATE = jsontemplate.Template("""
<html>
  <head>
    <title>{title}</title>
  </head>
  <body>{body|raw}</body>
</html>
""", default_formatter='html')


# Now the pattern is simple:
# 
# 1. Just expand each specific page template with its own specific dictionary.
# 2. And then expand the result of that into the shared HTML template.

def Site(path_info):
  """Returns an HTML page."""

  if path_info == '/one':
    body = PAGE_ONE_TEMPLATE.expand(PAGE_ONE_DATA)
    title = PAGE_ONE_DATA['title']
  elif path_info == '/two':
    body = PAGE_TWO_TEMPLATE.expand(PAGE_TWO_DATA)
    title = PAGE_TWO_DATA['title']
  else:
    # Note: Request it with trailing slash: cgi-bin/reusing_the_outside.py/
    body = """
    <p><a href="one">Page One</a> <a href="two">Page Two</a></p>
    <p>(<b>View Source</b> to see that both have the same outside "shell")</p>
    """
    title = 'Index'

  return HTML_TEMPLATE.expand({'body': body, 'title': title})


# Now go back to the 'Design Minimalism' blog post (linked from
# http://code.google.com/p/json-template/).

def main():
  """Returns an exit code."""

  print 'Content-Type: text/html'
  print
  print Site(os.getenv('PATH_INFO'))


if __name__ == '__main__':
  main()
