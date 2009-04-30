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

"""Bridge to run Python unit tests against PHP code."""

__author__ = 'Miguel Ibero'

import os
import subprocess
import sys
import tempfile

from pan.core import json
from pan.core import records
from pan.test import testy


class PhpVerifier(testy.StandardVerifier):
  """
  Verifies template behavior by executing the PHP file from command line
  """

  def __init__(self, php_interpreter_path, script_path):
    testy.StandardVerifier.__init__(self)
    self.php_interpreter_path = php_interpreter_path
    self.script_path = script_path

  def CheckIfRunnable(self):
    if not os.path.exists(self.php_interpreter_path):
      raise testy.TestPrequisiteMissing(
          '%r is missing' % self.php_interpreter_path)

  def _RunScript(self, template_def, dictionary):
    template_str = template_def.args[0]
    options = template_def.kwargs

    argv = [
        self.php_interpreter_path, self.script_path,
        template_str, json.dumps(dictionary), json.dumps(options)]
    p = subprocess.Popen(
        argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True)  # for Windows too

    stdout = p.stdout.read()
    print stdout
    stderr = p.stderr.read()
    p.stdout.close()
    p.stderr.close()
    exit_code = p.wait()

    # Important: keep line breaks
    lines = stdout.splitlines(True)
    # Filter out log messages
    stdout = ''.join(lines)

    exception = None
    for line in lines:
      if line.startswith('EXCEPTION: '):
        exception = line[len('EXCEPTION: '):]

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

    self.Equal(result.exit_code, 0, 'stderr: %r' % result.stderr)
    self.LongStringsEqual(
        expected, result.stdout, ignore_all_whitespace=True)

  def EvaluationError(self, exception, template_def, data_dict):
    result = self._RunScript(template_def, data_dict)
    self.In('EXCEPTION: ' + exception.__name__, result.stdout)

  def CompilationError(self, exception, *args, **kwargs):
    template_def = testy.ClassDef(*args, **kwargs)
    result = self._RunScript(template_def, {})
    self.In('EXCEPTION: ' + exception.__name__, result.stdout)
