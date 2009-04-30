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

import subprocess
import sys
import tempfile
import os

from pan.core import json
from pan.core import records
from pan.test import testy


class JavaVerifier(testy.StandardVerifier):
  """
  Verifies template behavior by running the java test class.
  """

  LABELS = ['javascript']

  def __init__(self, java_interpreter_path, impl_path, test_classes_path):
    testy.StandardVerifier.__init__(self)
    self.java_interpreter_path = java_interpreter_path
    self.impl_path = impl_path
    self.test_classes_path = test_classes_path

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
        self.java_interpreter_path, '-cp', self.impl_path + os.path.pathsep + self.test_classes_path, 'jsontemplate_test.Test', temp_json_file.name]
    p = subprocess.Popen(
        argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True)  # for Windows too

    stdout = p.stdout.read()
    print stdout
    stderr = p.stderr.read()
    p.stdout.close()
    p.stderr.close()
    exit_code = p.wait()
    temp_json_file.close()  # deletes the file

    # Important: keep line breaks
    lines = stdout.splitlines(True)
    # Filter out log messages
    stdout = ''.join(lines)

    exception = None
    for line in stderr.splitlines(True):
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

    # The tests specify are written for whitespace_mode='smart-indent'.
    # JavaScript only implement whitespace_mode='any' now, so just ignore all
    # whitespace, and we can use the same tests.
    self.LongStringsEqual(
        expected, result.stdout, ignore_all_whitespace=True)

  def EvaluationError(self, exception, template_def, data_dict):
    result = self._RunScript(template_def, data_dict)
    self.In('EXCEPTION: ' + exception.__name__, 'stderr: %r\nstdout: %s' % (result.stderr, result.stdout))

  def CompilationError(self, exception, *args, **kwargs):
    template_def = testy.ClassDef(*args, **kwargs)
    result = self._RunScript(template_def, {})
    self.In('EXCEPTION: ' + exception.__name__, 'stderr: %r\nstdout: %s' % (result.stderr, result.stdout))
