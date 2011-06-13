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

"""Bridge to run Python unit tests against Java code."""

__author__ = 'Andy Chu, William Shallum'

import os
import tempfile
try:
  import json
except ImportError:
  import simplejson as json

from pan.core import os_process
from pan.core import records
from pan.test import testy


class JavaVerifier(testy.StandardVerifier):
  """
  Verifies template behavior by running the java test class.
  """

  LABELS = ['java']

  def __init__(self, java_interpreter_path, impl_path, test_classes_path):
    testy.StandardVerifier.__init__(self)
    self.java_interpreter_path = java_interpreter_path
    self.impl_path = impl_path
    self.test_classes_path = test_classes_path
    self.runner = os_process.Runner()

  def CheckIfRunnable(self):
    if not os.path.exists(self.java_interpreter_path):
      raise testy.TestPrequisiteMissing(
          '%r is missing' % self.java_interpreter_path)

  def _RunScript(self, template_def, dictionary):
    template_str = template_def.args[0]
    options = template_def.kwargs

    test_json = json.dumps(dict(
          template=template_str,
          options=options,
          dictionary=dictionary,
        ))

    temp_json_file = tempfile.NamedTemporaryFile(suffix='.json')
    temp_json_file.write(test_json)
    temp_json_file.flush()

    argv = [
        self.java_interpreter_path, '-cp', 
        # pathset is : or ;
        self.impl_path + os.path.pathsep + self.test_classes_path, 
        'jsontemplate_test.Test', temp_json_file.name]

    result = self.runner.Result(argv)

    temp_json_file.close()  # deletes the file

    # Important: keep line breaks
    lines = result.stderr.splitlines(True)

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

    # The tests specify are written for whitespace_mode='smart-indent'.
    # JavaScript only implement whitespace_mode='any' now, so just ignore all
    # whitespace, and we can use the same tests.
    self.LongStringsEqual(
        expected, result.stdout, ignore_whitespace=ignore_whitespace,
        ignore_all_whitespace=ignore_all_whitespace)

  def EvaluationError(self, exception, template_def, data_dict):
    result = self._RunScript(template_def, data_dict)
    self.In(
        'EXCEPTION: ' + exception.__name__,
        'stderr: %r\nstdout: %s' % (result.stderr, result.stdout))

  def CompilationError(self, exception, *args, **kwargs):
    template_def = testy.ClassDef(*args, **kwargs)
    result = self._RunScript(template_def, {})
    self.In(
        'EXCEPTION: ' + exception.__name__,
        'stderr: %r\nstdout: %s' % (result.stderr, result.stdout))
