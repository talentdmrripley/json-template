#!/usr/bin/python -S
"""
base_verifier.py
"""

__author__ = 'Andy Chu'


import taste


class JsonTemplateVerifier(taste.StandardVerifier):
  """Abstract base class for all language-specific verifiers."""

  def Expansion(
      self, template_def, dictionary, expected, ignore_whitespace=False,
      ignore_all_whitespace=False, all_formatters=False):
    """Verifies a normal expansion."""
    raise NotImplementedError

  def ExpansionWithAllFormatters(
      self, template_def, dictionary, expected):
    """Verifies an expansion with all formatters implemented in the language."""
    self.Expansion(template_def, dictionary, expected, all_formatters=True)

  def CompilationError(self, exception, *args, **kwargs):
    """Verifiers an error that occurs when compiling the template."""
    raise NotImplementedError

  def EvaluationError(self, exception, template_def, data_dict):
    """
    Verifies an error that occurs when expanding a template with a data
    dictionary.
    """
    raise NotImplementedError
