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

"""Testy Verifier for json-template.lua"""

__author__ = 'Andy Chu'

import os

from pan.core import json
from pan.core import records
from pan.core import os_process
from pan.test import testy

import base_verifier  # TODO: Move this into a package


class LuaVerifier(base_verifier.JsonTemplateVerifier):
  """Verifies template behavior by running the Lua interpreter."""

  LABELS = ['lua']

  def __init__(self, lua_exe, lua_dir):
    base_verifier.JsonTemplateVerifier.__init__(self)
    self.lua_exe = lua_exe
    # Set the working directory to where verifier.lua and Json.lua live --
    # otherwise require doesn't work
    self.runner = os_process.Runner(cwd=lua_dir)
    self.script_path = os.path.join(lua_dir, 'verifier.lua')

  def _RunScript(self, template_def, dictionary, all_formatters=False):
    template_str = template_def.args[0]
    options = template_def.kwargs
    argv = [
        self.lua_exe, self.script_path, template_str, json.dumps(dictionary),
        json.dumps(options)]
    print argv
    return self.runner.Result(argv)

  def Expansion(
      self, template_def, dictionary, expected, ignore_whitespace=False,
      ignore_all_whitespace=False, all_formatters=False):
    """
    Args:
      template_def: ClassDef instance that defines a Template.
    """
    result = self._RunScript(
        template_def, dictionary, all_formatters=all_formatters)

    self.Equal(result.exit_code, 0, 'stderr: %s' % result.stderr)
    self.LongStringsEqual(
        result.stdout, expected, ignore_whitespace=ignore_whitespace,
        ignore_all_whitespace=ignore_all_whitespace)

  def EvaluationError(self, exception, template_def, data_dict):
    result = self._RunScript(template_def, data_dict)

    self.Equal(result.exit_code, 1)
    print exception.__name__
    self.In(exception.__name__, result.stderr)

  def CompilationError(self, exception, *args, **kwargs):
    template_def = testy.ClassDef(*args, **kwargs)
    result = self._RunScript(template_def, {})
    self.Equal(result.exit_code, 1)
    print exception.__name__
    self.In(exception.__name__, result.stderr)
