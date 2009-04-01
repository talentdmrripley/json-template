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
<style type=text/css>
tr td {
  background-color: #DDD;
  padding: 0.5em;
}
</style>
<table width="100%" cellspacing="10">
  <tr>
    <td>
      <b>Template</b>
    </td>
    <td>
      <b>Data Dictionary</b>
    </td>
    <td>
      <b>Output</b>
    </td>
  </tr>
  <tr class="literal">
    <td>
      {highlighted_template|raw}
    </td>
    <td>
      <pre>{dictionary}</pre>
    </td>
    <td>
      <pre>{expanded}</pre>
    </td>
</table>

<p><i>This HTML fragment was automatically generated from the <a
href="http://json-template.googlecode.com/svn/trunk/jsontemplate_test.py">test
cases</a> for <a href="http://code.google.com/p/json-template">JSON
Template</a>.  </p>
"""


_BLOG_HTML = """
<p><b>A template string ...</b></p>

<div class="literal">
{highlighted_template|raw}
</div>

<p><b>... combined with a data dictionary ...</b></p>

<pre class="literal">{dictionary}</pre>

<p><b>... gives output:</b></p>

<pre class="literal">{expanded}</pre>

<p><b>Here is the rendered output:</b></p>

<div class="literal">
{expanded|raw}
</div>
"""


_JS_EXAMPLE = """\
<html>
  <head>
    <script type="text/javascript" src="../javascript/json-template.js">
    </script>
    <script type="text/javascript">
    function write() {
      var t = jsontemplate.Template({template_str});
      var s = t.expand({json_str});
      document.getElementById("replace").innerHTML = s;
    }
    </script>
  </head>
  <body onload="write();">
    <h4>Here is the same example rendered in JavaScript.  <b>View Source</b> to
    see how it works.</h4>
    <div id="replace"></div>
    <p><i>(Um, for some reason this example doesn't work in IE6, but does in
    Firefox and Chrome.  Help with that is appreciated...)</i></p>
  </body>
</html>
"""


class DocGenerator(testy.StandardVerifier):

  def __init__(self, output_dir):
    testy.StandardVerifier.__init__(self)
    self.output_dir = output_dir

    # Counter for unique filenames
    self.counter = 1

    self.blog_template = jsontemplate.Template(
        _BLOG_HTML, default_formatter='html')

    self.html_template = jsontemplate.Template(
        _TEST_CASE_HTML, default_formatter='html')

    # Don't need any escaping here.
    self.js_template = jsontemplate.Template(
        _JS_EXAMPLE, default_formatter='raw')

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
    json_str = json.dumps(dictionary, indent=2)

    self.WriteHighlightedHtml(template_def, json_str, expanded)

    # Mark test methods with the live-js label to generate the Live JavaScript
    # example.
    if testy.HasLabel(self.current_method, 'live-js'):
      self.WriteLiveJavaScriptExample(template_def, json_str, expanded)

    self.counter += 1

  def WriteLiveJavaScriptExample(self, template_def, json_str, expanded):
    """Write a working JavaScript example that can be loaded in the browser."""

    # TODO: Could use expanded to verify the server side against the client side
    # expansion?  But I already have working unit tests for both.

    html = self.js_template.expand({
        'template_str': json.dumps(template_def.args[0]),
        'json_str': json_str,
        })

    filename = '%s-%02d.js.html' % (self.current_method.__name__, self.counter)
    self._WriteFile(filename, html)

  def WriteHighlightedHtml(self, template_def, json_str, expanded):
    """Write a fragment of HTML to document this test case."""

    kwargs = {}

    meta = template_def.kwargs.get('meta')
    if meta:
      kwargs['meta'] = meta

    format_char = template_def.kwargs.get('format_char')
    if format_char:
      kwargs['format_char'] = format_char

    highlighted_template = highlight.AsHtml(template_def.args[0], **kwargs)

    if testy.HasLabel(self.current_method, 'blog-format'):
      template = self.blog_template
    else:
      template = self.html_template

    html = template.expand({
        'highlighted_template': highlighted_template,
        'dictionary': json_str,
        'expanded': expanded})

    filename = '%s-%02d.html' % (self.current_method.__name__, self.counter)
    self._WriteFile(filename, html)

  def _WriteFile(self, filename, contents):
    filename = os.path.join(self.output_dir, filename)

    f = open(filename, 'w')
    f.write(contents)
    f.close()

    # TODO: Need a logger?
    print 'Wrote %s' % filename


  # For now, we don't need anything for errors

  def EvaluationError(self, exception, template_def, data_dict):
    pass

  def CompilationError(self, exception, *args, **kwargs):
    pass
