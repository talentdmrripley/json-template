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

import os
import sys
import tempfile

if __name__ == '__main__':
  sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), '..'))

from pan.core import json
from pan.core import os_process
from pan.core import records
from pan.test import testy


_TEST_JS = """
try {
  var t = jsontemplate.Template(%(template)s, %(options)s);
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
var t = jsontemplate.Template(%(template)s, %(options)s);
var s = t.expand(%(dictionary)s);
print(s);
"""

class JavaScriptVerifier(testy.StandardVerifier):
  """Abstract base class."""

  LABELS = ['javascript']

  def __init__(self, script_path, helpers_path, debug_mode=False):
    if not os.path.exists(helpers_path):
      raise RuntimeError(
          "%s doesn't exist; need to check out the 'pan' repository.  See "
          "DevelopingJsonTemplate" % helpers_path)
    # Path of json-template.js
    self.script_path = script_path
    self.helpers_path = helpers_path
    self.debug_mode = debug_mode

    self.runner = os_process.Runner()

  def _MakeTestJs(self, template_def, dictionary):
    template_str = template_def.args[0]
    options = template_def.kwargs

    js_template = _TEST_JS
    if self.debug_mode:
      js_template = _DEBUG_JS

    return js_template % dict(
        template=json.dumps(template_str),
        options=json.dumps(options),
        dictionary=json.dumps(dictionary),
        )


  def _RunScript(self, template_def, dictionary):
    """
    Abstract method to run json-template.js with the given template and
    dictionary.
    """
    raise NotImplementedError

  def Expansion(
      self, template_def, dictionary, expected, ignore_whitespace=False,
      ignore_all_whitespace=False):
    """
    Args:
      template_def: _TemplateDef instance.
    """
    result = self._RunScript(template_def, dictionary)

    # The print() function in shell.cc adds a newline, so compensate for it
    if result.stdout.endswith('\n'):
      result.stdout = result.stdout[:-1]

    self.Equal(result.exit_code, 0, 'stderr: %r' % result.stderr)

    # The tests specify are written for whitespace_mode='smart-indent'.
    # JavaScript only implement whitespace_mode='any' now, so just ignore all
    # whitespace, and we can use the same tests.
    self.LongStringsEqual(
        expected, result.stdout, ignore_whitespace=ignore_whitespace,
        ignore_all_whitespace=ignore_all_whitespace)

  def EvaluationError(self, exception, template_def, data_dict):
    result = self._RunScript(template_def, data_dict)
    if result.exception is None:
      self.fail('No exception found in output')
    self.In(exception.__name__, result.exception)

  def CompilationError(self, exception, *args, **kwargs):
    template_def = testy.ClassDef(*args, **kwargs)
    result = self._RunScript(template_def, {})
    if result.exception is None:
      self.fail('No exception found in output')
    self.In(exception.__name__, result.exception)


class V8ShellVerifier(JavaScriptVerifier):
  """
  Verifies template behavior by calling out to the shell.cc sample included with
  the v8 source tree.
  """

  def __init__(self, v8_path, script_path, helpers_path, debug_mode=False):
    JavaScriptVerifier.__init__(
        self, script_path, helpers_path, debug_mode=debug_mode)
    self.v8_path = v8_path

    # Flip this when you can't figure out what's going on in v8!
    #self.debug_mode = True

  def CheckIfRunnable(self):
    if not os.path.exists(self.v8_path):
      raise testy.TestPrequisiteMissing('%r is missing' % self.v8_path)

  def _RunScript(self, template_def, dictionary):
    test_js = self._MakeTestJs(template_def, dictionary)

    if self.debug_mode:
      print test_js

    temp_js_file = tempfile.NamedTemporaryFile(suffix='.js')
    temp_js_file.write(test_js)
    temp_js_file.flush()

    argv = [
        self.v8_path, self.script_path, self.helpers_path, temp_js_file.name]

    p = self.runner.Pipes(argv)

    # Read the lines one at a time.  This makes it possible to see if we have an
    # infinite loop.
    exception = None
    stdout_lines = []
    for line in p.stdout:
      if line.startswith('V8LOG: '):
        sys.stdout.write(line)
      elif line.startswith('EXCEPTION: '):
        exception = line[len('EXCEPTION: '):]
      else:
        stdout_lines.append(line)

    stderr = p.stderr.read()

    p.stdout.close()
    p.stderr.close()
    exit_code = p.wait()
    temp_js_file.close()  # deletes the file

    stdout = ''.join(stdout_lines)
    if self.debug_mode:
      print stdout

    # There's no support for anything else in shell.cc
    self.Equal(exit_code, 0)
    self.Equal(stderr, '')

    return records.Record(
        stderr=stderr, stdout=stdout, exit_code=exit_code,
        exception=exception)


class CScriptVerifier(JavaScriptVerifier):
  """
  Verifies template behavior by calling out to the shell.cc sample included with
  the v8 source tree.
  """

  LABELS = ['javascript']

  def __init__(self, script_path, helpers_path, debug_mode=False):
    JavaScriptVerifier.__init__(
        self, script_path, helpers_path, debug_mode=debug_mode)

    # Read the script into a string so we can write it to stdin
    self.script_contents = open(script_path).read()

  def _RunScript(self, template_def, dictionary):
    test_js = self._MakeTestJs(template_def, dictionary)

    if self.debug_mode:
      print test_js

    code = self.script_contents + test_js
    exit_code, stdout, stderr = RunWithCScript(self.runner, code)

    if self.debug_mode:
      print 'STDOUT', repr(stdout)

    exception = None
    stdout_lines = []
    for line in stdout.splitlines(True):
      if line.startswith('V8LOG: '):
        sys.stdout.write(line)
      elif line.startswith('EXCEPTION: '):
        exception = line[len('EXCEPTION: '):]
      else:
        stdout_lines.append(line)

    return records.Record(
        stdout=''.join(stdout_lines), stderr=stderr, exit_code=exit_code,
        exception=exception)


def RunWithCScript(runner, code):
  """Runs JavaScript code with the Windows cscript interpreter.

  Returns:
    A 3 tuple of (exit code, stdout string, stderr string)
  """
  argv = ['cscript', '//Nologo', 'javascript/cscript-shell.js']
  p = runner.Pipes(argv, 'OEI')
  p.stdin.write(code)
  p.stdin.close()
  stdout = p.stdout.read()

  # Strip an extra newline from cscript
  if stdout.endswith('\n'):
    stdout = stdout[:-1]

  stderr = p.stderr.read()
  exit_code = p.wait()
  return exit_code, stdout, stderr


def main(argv):
  code = open('javascript/json-template.js').read()
  #code += 'WScript.StdOut.WriteLine(jsontemplate.Template)'
  code += """
var t = jsontemplate.Template('{foo}');
WScript.StdOut.Writeline(t.expand({'foo': 'Hello'}));
"""
  RunWithCScript(code)


if __name__ == '__main__':
  main(sys.argv[1:])
  
