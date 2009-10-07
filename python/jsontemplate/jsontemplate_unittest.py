#!/usr/bin/python -S
"""
jsontemplate_unittest.py
"""

__author__ = 'Andy Chu'


import os
import sys

if __name__ == '__main__':
  # for jsontemplate and pan, respectively
  sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
  sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from pan.core import json
from pan.test import testy
from pan.core import util

# We need access to the internals here
from jsontemplate import _jsontemplate as jsontemplate
import verifier as python_verifier

B = util.BlockStr


class TokenizeTest(testy.Test):

  def testMakeTokenRegex(self):
    token_re = jsontemplate.MakeTokenRegex('[', ']')
    tokens = token_re.split("""
[# Comment#]

[# Comment !@#234 with all ...\\\ sorts of bad characters??]

[# Multi ]
[# Line ]
[# Comment ]
text
[!!]
text

[foo|fmt]
[bar|fmt]
""")
    self.verify.Equal(len(tokens), 17)

  def testSectionRegex(self):

    # Section names are required
    self.verify.Equal(
        jsontemplate._SECTION_RE.match('section'),
        None)
    self.verify.Equal(
        jsontemplate._SECTION_RE.match('repeated section'),
        None)

    self.verify.Equal(
        jsontemplate._SECTION_RE.match('section Foo').groups(),
        (None, 'Foo'))
    self.verify.Equal(
        jsontemplate._SECTION_RE.match('repeated section @').groups(),
        ('repeated', '@'))


class FromStringTest(testy.Test):

  def testEmpty(self):
    s = """\
Format-Char: |
Meta: <>
"""
    t = jsontemplate.FromString(s, _constructor=testy.ClassDef)
    self.verify.Equal(t.args[0], '')
    self.verify.Equal(t.kwargs['meta'], '<>')
    self.verify.Equal(t.kwargs['format_char'], '|')

    # Empty template
    t = jsontemplate.FromString('', _constructor=testy.ClassDef)
    self.verify.Equal(t.args[0], '')
    self.verify.Equal(t.kwargs.get('meta'), None)
    self.verify.Equal(t.kwargs.get('format_char'), None)

  def testBadOptions(self):
    f = """\
Format-Char: |
Meta: <>
BAD STUFF
"""
    self.verify.Raises(
        jsontemplate.CompilationError, jsontemplate.FromString, f)

  def testTemplate(self):
    f = """\
format-char: :
meta: <>

Hello <there>
"""
    t = jsontemplate.FromString(f, _constructor=testy.ClassDef)
    self.verify.Equal(t.args[0], 'Hello <there>\n')
    self.verify.Equal(t.kwargs['meta'], '<>')
    self.verify.Equal(t.kwargs['format_char'], ':')

  def testNoOptions(self):
    # Bug fix
    f = """Hello {dude}"""
    t = jsontemplate.FromString(f)
    self.verify.Equal(t.expand({'dude': 'Andy'}), 'Hello Andy')

  def testEncoding(self):
    # Bug fix: Templates that are Unicode strings should expand as Unicode
    # strings
    t = jsontemplate.FromString(u'\u00FF')
    self.verify.Equal(t.expand({}), u'\u00FF')

    t = jsontemplate.FromString(u'\uFF00')
    self.verify.Equal(t.expand({}), u'\uFF00')


class ScopedContextTest(testy.Test):

  def testScopedContext(self):
    data = {'foo': [1,2,3]}
    s = jsontemplate._ScopedContext(data, '')
    self.verify.Equal(s.Lookup('@'), data)
    self.verify.Equal(s.Lookup('foo'), data['foo'])
    self.verify.Equal(s.Lookup('@'), data)

    print s.PushSection('foo')
    self.verify.Equal(s.Lookup('@'), data['foo'])
    s.Next()
    self.verify.Equal(s.Lookup('@'), 1)
    s.Next()
    self.verify.Equal(s.Lookup('@'), 2)
    s.Next()
    self.verify.Equal(s.Lookup('@'), 3)
    self.verify.Raises(StopIteration, s.Next)

  def testEmptyList(self):
    s = jsontemplate._ScopedContext([], '')
    self.verify.Raises(StopIteration, s.Next)


class InternalTemplateTest(testy.Test):
  """Tests that can only be run internally."""

  VERIFIERS = [python_verifier.InternalTemplateVerifier]

  def testFormatterRaisesException(self):

    # For now, integers can't be formatted directly as html.  Just omit the
    # formatter.
    t = jsontemplate.Template('There are {num|html} ways to do it')
    try:
      t.expand({'num': 5})
    except jsontemplate.EvaluationError, e:
      self.verify.IsTrue(e.args[0].startswith('Formatting value 5'), e.args[0])
      self.verify.Equal(e.original_exception.__class__, AttributeError)
    else:
      self.fail('Expected EvaluationError')

  def testMultipleFormatters(self):
    # TODO: This could have a version in the external test too, just not with
    # 'url-params', which is not the same across platforms because of dictionary
    # iteration order

    # Single formatter
    t = testy.ClassDef(
        'http://example.com?{params:url-params}',
        format_char=':')
    self.verify.Expansion(
        t,
        {'params': {'foo': 1, 'bar': 'String with spaces', 'baz': '!@#$%^&*('}},
        'http://example.com?baz=%21%40%23%24%25%5E%26%2A%28&foo=1&bar=String+with+spaces')

    # Multiple
    t = testy.ClassDef(
        'http://example.com?{params|url-params|html}',
        format_char='|')
    self.verify.Expansion(
        t,
        {'params': {'foo': 1, 'bar': 'String with spaces', 'baz': '!@#$%^&*('}},
        'http://example.com?baz=%21%40%23%24%25%5E%26%2A%28&amp;foo=1&amp;bar=String+with+spaces')

  def testExpandingDictionary(self):
    # This isn't strictly necessary, but it should make it easier for people to
    # develop templates iteratively.  They can see what the context is without
    # writing the whole template.

    def _More(format_str):
      if format_str == 'str':
        return lambda x: json.dumps(x, indent=2)
      else:
        return None

    t = testy.ClassDef('{@}', more_formatters=_More)
    d = {
        u'url': u'http://example.com',
        u'person': {
            u'name': u'Andy',
            u'age': 30,
            }
        }

    expected = """\
{
  "url": "http://example.com",
  "person": {
    "age": 30,
    "name": "Andy"
  }
}
"""
    # simplejson emits some extra whitespace
    self.verify.Expansion(t, d, expected, ignore_whitespace=True)

  def testScope(self):
    # From the wiki

    t = jsontemplate.Template("""
  {internal_link_prefix|htmltag}
  <p>
    <b>HTML Source</b>
    <ul>
      {.repeated section html-source-links}
        <p>
          <a
          href="{internal_link_prefix|htmltag}raw-html/data/wiki/columns-{num-cols}/{url-name}">
            {anchor|html}
          </a>
        <p>
      {.end}
    </ul>
  </p>
  """)
    d = {
        'internal_link_prefix': 'http://',
        'url-name': 'Wiki',
        'html-source-links': [
            {'num-cols': 1, 'anchor': '1'},
            {'num-cols': 2, 'anchor': '2'},
            ],
        }

    # Bug fix
    t.expand(d)

  #
  # Tests for public functions
  #

  def testExpand(self):
    """Test the free function expand."""
    self.verify.Equal(
        jsontemplate.expand('Hello {name}', {'name': 'World'}),
        'Hello World')

  def testTemplateExpand(self):
    t = jsontemplate.Template('Hello {name}')

    self.verify.Equal(
        t.expand({'name': 'World'}),
        'Hello World')

    # Test the kwarg syntax
    self.verify.Equal(
        t.expand(name='World'),
        'Hello World')

    # Only accepts one argument
    self.verify.Raises(TypeError, t.expand, {'name': 'world'}, 'extra')

  def testCompileTemplate(self):
    program = jsontemplate.CompileTemplate('{}')
    # If no builder is passed, them CompileTemplate should return a _Section
    # instance (the root of the program)
    self.verify.Equal(type(program), jsontemplate._Section)

  def testSimpleUnicodeSubstitution(self):
    t = jsontemplate.Template(u'Hello {name}')

    self.verify.Equal(t.expand({u'name': u'World'}), u'Hello World')

    # TODO: Need a lot more comprehensive *external* unicode tests, as well as
    # ones for the internal API.  Need to test mixing of unicode() and str()
    # instances (or declare it undefined).


class FunctionsApiTest(testy.Test):
  """Tests that can only be run internally."""

  def testMoreFormattersAsDict(self):
    t = jsontemplate.Template(
        'Hello {name|lower} {name|upper}',
        more_formatters={
            'lower': lambda v: v.lower(),
            'upper': lambda v: v.upper(),
            })

    self.verify.Equal(t.expand({'name': 'World'}), 'Hello world WORLD')

  def testMoreFormattersAsFunction(self):
    def MyFormatters(name):
      return {
        'lower': lambda v: v.lower(),
        'upper': lambda v: v.upper(),
        }.get(name)

    t = jsontemplate.Template(
        'Hello {name|lower} {name|upper}', more_formatters=MyFormatters)

    self.verify.Equal(t.expand({'name': 'World'}), 'Hello world WORLD')


class AdvancedTemplateTest(testy.Test):

  VERIFIERS = [python_verifier.InternalTemplateVerifier]

  def testRecursiveTemplates(self):
    # TODO: This doesn't work yet, since I can't pass child_template.expand as a
    # formatter to child_template.
    # 
    # Probably need a TemplateSet abstraction.  And that may need some awareness
    # of the 'template-file' formatter name.
    child_template = jsontemplate.Template(
        B("""
        - {@}
        """))

    top = jsontemplate.Template(
        B("""
        Directory listing for {root}

        {.repeated section children}
          {@|child}
        {.end}
        """), more_formatters={'child': child_template.expand})

    data = {
      'root': '/home',
      'children': [
        'bin',
        'work',
        ],
      }

    s = top.expand(data)
    #print s


if __name__ == '__main__':
  testy.RunThisModule()
