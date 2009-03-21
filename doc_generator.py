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
      {highlighted_template|raw}
    </td>
    <td>
      <pre>{dictionary}</pre>
    </td>
    <td>
      <pre>{expanded}</pre>
    </td>
  </tr>
</table>
"""


class DocGenerator(testy.StandardVerifier):

  def __init__(self, output_dir):
    testy.StandardVerifier.__init__(self)
    self.output_dir = output_dir

    # Counter for unique filenames
    self.counter = 1

    self.html_template = jsontemplate.Template(
        _TEST_CASE_HTML, default_formatter='html')

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

    filename = os.path.join(self.output_dir, '%03d.html' % self.counter)
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
