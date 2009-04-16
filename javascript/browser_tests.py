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

import datetime
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
        document.write("<code>" + jsontemplate.HtmlEscape(s) + "</code><br>");
      };

      // TODO: May not be necessary
      function _NormalizeWhitespace(s) {
        var lines = s.split(/\\n/);
        var normalizedLines = [.meta-left][.meta-right];
        for (var i = 0; i < lines.length; i++) {
          normalizedLines.push(lines[.meta-left]i[.meta-right].replace(/(^\s+|\s+$)/g, ""));
        }
        return normalizedLines.join('\\n');
      };

      // TODO: This isn't used, but we might want it for ignore_all_whitespace
      function _StripAllWhitespace(s) {
        return s.replace(/\s+/g, "");
      };

      var results = jsUnity.run({
        [.repeated section test-bodies]
          [name]: function() {
            var t = jsontemplate.Template([template_str|js-string],
                                          [compile_options|json]);
            var actual = t.expand([data_dict|json]);  // left
            var expected = [expected|js-string];  // right
            [.section ignore_whitespace]
              actual = _NormalizeWhitespace(actual);
              expected = _NormalizeWhitespace(expected);
            [.end]

            // For now, strip all whitespace.  The JavaScript version doesn't do
            // smart-indent, and ignore_whitespace doesn't make tests pass,
            // since it only strips at the beginning and end of lines.
            actual = _StripAllWhitespace(actual);
            expected = _StripAllWhitespace(expected);

            jsUnity.assertions.assertEqual(actual, expected);
          }
        [.alternates with],[.end]
      });           
    </script>
  </head>
  <body onload="">
    <p>Tests for [test-name|html] generated on [timestamp|html]</p>
  </body>
</html>
"""


class TestGenerator(testy.StandardVerifier):

  def __init__(self):
    testy.StandardVerifier.__init__(self)

    # Counter for unique method names
    self.counter = 1

    self.assertions = []

    def ToJson(x):
      return json.dumps(x, indent=2)

    self.js_template = jsontemplate.Template(
        _HTML_TEMPLATE, default_formatter='raw', meta='[]',
        more_formatters=formatters.Json(ToJson))

  def WriteHtml(self, output_dir):
    """Called after the whole test has been run, and all verifications made."""
    filename = os.path.join(output_dir, 'browser_test.html')
    html_file = open(filename, 'w')

    data = {
        # TODO: Automatic way of inserting class name
        'test-name': 'JSON Template',
        'timestamp': datetime.datetime.now().isoformat(),
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
        'name': '%s_%s' % (self.current_method.__name__, self.counter),
        'template_str': template_def.args[0],
        'data_dict': dictionary,
        'compile_options': template_def.kwargs,
        'expected': expected,
        'ignore_whitespace': ignore_whitespace,
        })

    self.counter += 1

  # TODO: Test exceptions too!

  def EvaluationError(self, exception, template_def, data_dict):
    pass

  def CompilationError(self, exception, *args, **kwargs):
    pass
