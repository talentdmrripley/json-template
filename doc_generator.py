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

"""Documentation generator.

This takes test cases assertions and outputs HTML for publishing.
"""

__author__ = 'Andy Chu'

import os
import sys

from pan.core import json
from pan.core import records
from pan.test import testy

from python import highlight
from python import jsontemplate

__author__ = 'Andy Chu'


# Use jsontemplate to document itself!
_TEST_CASE_HTML = """
<table border="1" width="100%">
  <tr>
    <td>
      <b>Template</b>
    </td>
    <td>
      <b>Data Dictionary</b>
    </td>
  </tr>
  <tr>
    <td>
      {highlighted_template|raw}
    </td>
    <td>
      <pre>{dictionary}</pre>
    </td>
  </tr>
  <tr>
    <td>
      <b>Output</b>
    </td>
    <td>
      <b>Rendered Output</b>
    </td>
  </tr>
  <tr>
    <td>
      <pre>{expanded}</pre>
    </td>
    <td>
      {expanded|raw}
    </td>
  </tr>
</table>
"""


_BLOG_HTML = """
<p><b>A template string ...</b></p>

<span class="literal">
{highlighted_template|raw}
</span>

<p><b>... Combined with a data dictionary ...</b></p>

<pre class="literal">{dictionary}</pre>

<p><b>... Gives output:</b></p>

<pre class="literal">{expanded}</pre>

<p><b>Here is the rendered output:</b></p>

<span class="literal">
{expanded|raw}
</span>
"""


class DocGenerator(testy.StandardVerifier):

  def __init__(self, output_dir):
    testy.StandardVerifier.__init__(self)
    self.output_dir = output_dir

    # Counter for unique filenames
    self.counter = 1

    if 1:
      template = _BLOG_HTML
    else:
      template = _TEST_CASE_HTML
    self.html_template = jsontemplate.Template(
        template, default_formatter='html')

  def BeforeMethod(self, method):
    testy.StandardVerifier.BeforeMethod(self, method)
    # Reset the counter every time we get a method
    self.counter = 1

  def Expansion(
      self, template_def, dictionary, expected, ignore_whitespace=False):
    """
    Args:
      template_def: ClassDef instance that defines a Template.
    """
    tested_template = jsontemplate.Template(
        *template_def.args, **template_def.kwargs)

    expanded = tested_template.expand(dictionary)

    kwargs = {}

    meta = template_def.kwargs.get('meta')
    if meta:
      kwargs['meta'] = meta

    format_char = template_def.kwargs.get('format_char')
    if format_char:
      kwargs['format_char'] = format_char

    highlighted_template = highlight.AsHtml(template_def.args[0], **kwargs)
    html = self.html_template.expand({
        'highlighted_template': highlighted_template,
        'dictionary': json.dumps(dictionary, indent=2),
        'expanded': expanded})

    filename = '%s-%03d.html' % (self.current_method.__name__, self.counter)
    filename = os.path.join(self.output_dir, filename)

    f = open(filename, 'w')
    f.write(html)
    f.close()

    # TODO: Need a logger?
    print 'Wrote %s' % filename
    self.counter += 1

  # For now, we don't need anything for errors

  def EvaluationError(self, exception, template_def, data_dict):
    pass

  def CompilationError(self, exception, *args, **kwargs):
    pass
