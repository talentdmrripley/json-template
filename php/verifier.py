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
try:
  import json
except ImportError:
  import simplejson as json

from pan.core import os_process
from pan.test import testy


class PhpVerifier(testy.StandardVerifier):
  """
  Verifies template behavior by executing the PHP file from command line
  """

  LABELS = ['php']

  def __init__(self, php_interpreter_path, script_path):
    testy.StandardVerifier.__init__(self)
    self.php_interpreter_path = php_interpreter_path
    self.script_path = script_path
    self.runner = os_process.Runner()

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
    result = self.runner.Result(argv)

    # Important: keep line breaks
    lines = result.stdout.splitlines(True)

    exception = None
    for line in lines:
      if line.startswith('EXCEPTION: '):
        exception = line[len('EXCEPTION: '):]

    result.exception = exception

    return result

  def Expansion(
      self, template_def, dictionary, expected, ignore_whitespace=False,
      ignore_all_whitespace=False):
    """
    Args:
      template_def: _TemplateDef instance.
    """
    result = self._RunScript(template_def, dictionary)

    self.Equal(result.exit_code, 0, 'stderr: %r' % result.stderr)

    # In PHP, I think there are some number-of-newline differences that should
    # be cleaned up (i.e. not just leading/trailing whitespace).
    self.LongStringsEqual(
        expected, result.stdout, ignore_all_whitespace=True)
    #self.LongStringsEqual(
    #    expected, result.stdout, ignore_whitespace=ignore_whitespace,
    #    ignore_all_whitespace=ignore_all_whitespace)

  def EvaluationError(self, exception, template_def, data_dict):
    result = self._RunScript(template_def, data_dict)
    self.In('EXCEPTION: ' + exception.__name__, result.stdout)

  def CompilationError(self, exception, *args, **kwargs):
    template_def = testy.ClassDef(*args, **kwargs)
    result = self._RunScript(template_def, {})
    self.In('EXCEPTION: ' + exception.__name__, result.stdout)
