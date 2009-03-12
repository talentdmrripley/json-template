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

import sys

from pan.core import json
from pan.core import records
from pan.test import testy

__author__ = 'Andy Chu'


class DocGenerator(testy.StandardVerifier):

  def __init__(self, output_dir):
    testy.StandardVerifier.__init__(self)
    self.output_dir = output_dir

  def Expansion(
      self, template_def, dictionary, expected, ignore_whitespace=False):
    """
    Args:
      template_def: ClassDef instance that defines a Template.
    """
    print 'Expand to %s' % self.output_dir

  # For now, we don't need anything for errors

  def EvaluationError(self, exception, template_def, data_dict):
    pass

  def CompilationError(self, exception, *args, **kwargs):
    pass
