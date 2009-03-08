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

"""Bridge to run Python unit tests against JavaScript code."""

__author__ = 'Andy Chu'

import subprocess
import sys
import tempfile

from pan.core import json
from pan.core import records
from pan.test import testy


_TEST_JS = """
try {
  var t = Template(%(template)s, %(options)s);
  var s = t.expand(%(dictionary)s);
  print(s);
} catch(e) {
  // Damn, why is there no native JSON?
  if (typeof(e) == 'object') {
    print('EXCEPTION: ' + e.name + ': ' + e.message);
  } else {
    print('EXCEPTION:', e);
  }
}
"""


# Don't catch exceptions so you can tell where the hell they came from (v8
# prints the line number)
_DEBUG_JS = """
var t = Template(%(template)s, %(options)s);
var s = t.expand(%(dictionary)s);
print(s);
"""


class V8ShellVerifier(testy.StandardVerifier):
  """
  Verifies template behavior by calling out to the shell.cc sample included with
  the v8 source tree.
  """

  def __init__(self, v8_path, script_path, helpers_path):
    testy.StandardVerifier.__init__(self)
    self.v8_path = v8_path
    self.helpers_path = helpers_path
    self.script_path = script_path

  def _RunScript(self, template_def, dictionary):
    template_str = template_def.args[0]
    options = template_def.kwargs

    js_template = _TEST_JS
    if 0:  # flip this as necessary
      js_template = _DEBUG_JS

    test_js = js_template % dict(
        template=json.dumps(template_str),
        options=json.dumps(options),
        dictionary=json.dumps(dictionary),
        )
    #print test_js

    temp_js_file = tempfile.NamedTemporaryFile(suffix='.js')
    temp_js_file.write(test_js)
    temp_js_file.flush()

    argv = [
        self.v8_path, self.script_path, self.helpers_path, temp_js_file.name]
    print argv
    p = subprocess.Popen(
        argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True)  # for Windows too

    stdout = p.stdout.read()
    print stdout
    stderr = p.stderr.read()
    p.stdout.close()
    p.stderr.close()
    exit_code = p.wait()
    temp_js_file.close()  # deletes the file

    # Important: keep line breaks
    lines = stdout.splitlines(True)
    # Filter out log messages
    stdout = ''.join(
        line for line in lines if not line.startswith('V8LOG: '))

    exception = None
    for line in lines:
      if line.startswith('EXCEPTION: '):
        exception = line[len('EXCEPTION: '):]

    # There's no support for anything else in shell.cc
    self.Equal(exit_code, 0)  
    self.Equal(stderr, '')  

    return records.Record(
        stderr=stderr, stdout=stdout, exit_code=exit_code,
        exception=exception)

  def Expansion(
      self, template_def, dictionary, expected, ignore_whitespace=False):
    """
    Args:
      template_def: _TemplateDef instance.
    """
    result = self._RunScript(template_def, dictionary)

    # The print() function in shell.cc adds a newline, so compensate for it
    if result.stdout.endswith('\n'):
      result.stdout = result.stdout[:-1]

    self.Equal(result.exit_code, 0, 'stderr: %r' % result.stderr)
    self.LongStringsEqual(
        expected, result.stdout, ignore_whitespace=ignore_whitespace)

  def EvaluationError(self, exception, template_def, data_dict):
    result = self._RunScript(template_def, data_dict)
    self.In('EXCEPTION: ' + exception.__name__, result.stdout)

  def CompilationError(self, exception, *args, **kwargs):
    template_def = testy.ClassDef(*args, **kwargs)
    result = self._RunScript(template_def, {})
    self.In('EXCEPTION: ' + exception.__name__, result.stdout)
