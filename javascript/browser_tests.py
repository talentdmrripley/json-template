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

"""Browser tests generator.

Outputs HTML which refers to JavaScript.
"""

__author__ = 'Andy Chu'

import os
import sys

from pan.core import json
from pan.test import testy

from python import formatters
from python import jsontemplate

__author__ = 'Andy Chu'


# Load the thing being tested.
# Load the test framework.
# Then generate the test bodies.
# And output logs into a div.

_HTML_TEMPLATE = """\
<html>
  <head>
    <script type="text/javascript"
      src="http://jsunity.googlecode.com/files/jsunity-0.6.js">
    </script>
    <script type="text/javascript" src="../javascript/json-template.js">
    </script>
    <script type="text/javascript">
      jsUnity.log = function (s) {
        document.write("<div>" + s + "</div>");
      };

      var results = jsUnity.run({
        [.repeated section test-bodies]
          [name]: function() {
            var t = jsontemplate.Template([template_str|js-string],
                                          [compile_options|json]);
            jsUnity.assertions.assertEqual(
                t.expand([data_dict|json]), // left
                [expected|js-string]);  // right
          }
        [.alternates with],[.end]
      });           
    </script>
  </head>
  <body onload="">
    <b>Tests for [test-name|html]</b>

    <pre id="console">Console</pre>
  </body>
</html>
"""


class TestGenerator(testy.StandardVerifier):

  def __init__(self, output_dir):
    testy.StandardVerifier.__init__(self)
    self.output_dir = output_dir

    self.assertions = []

    def ToJson(x):
      return json.dumps(x, indent=2)

    self.js_template = jsontemplate.Template(
        _HTML_TEMPLATE, default_formatter='raw', meta='[]',
        more_formatters=formatters.Json(ToJson))

  def setUpOnce(self):
    if self.assertions:
      raise RuntimeError(
          'Non-empty assertions on setUpOnce: %r' % self.assertions)

  def tearDownOnce(self):
    """Called after the whole test has been run, and all verification made."""
    filename = os.path.join(self.output_dir, 'browser_test.html')
    html_file = open(filename, 'w')

    data = {
        # TODO: Automatic way of inserting class name
        'test-name': 'JSON Template',
        'test-bodies': self.assertions
        }

    self.js_template.render(data, html_file.write)
    html_file.close()

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
    self.assertions.append({
        'name': self.current_method.__name__,
        'template_str': template_def.args[0],
        'data_dict': dictionary,
        'compile_options': template_def.kwargs,
        'expected': expected,
        })

  # TODO:

  def EvaluationError(self, exception, template_def, data_dict):
    pass

  def CompilationError(self, exception, *args, **kwargs):
    pass

  def _WriteFile(self, filename, contents):
    filename = os.path.join(self.output_dir, filename)

    f = open(filename, 'w')
    f.write(contents)
    f.close()

    # TODO: Need a logger?
    print 'Wrote %s' % filename
