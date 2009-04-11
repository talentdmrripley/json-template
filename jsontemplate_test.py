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

"""Language-independent tests for json-template.

Uses the testy test framework.
"""

__author__ = 'Andy Chu'


import os
from pprint import pprint
import subprocess
import sys
import unittest

if __name__ == '__main__':
  sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), '..'))

from pan.core import cmdapp
from pan.core import params
from pan.core import json
from pan.test import testy

from python import jsontemplate  # module under *direct* test

# External verifiers:
from javascript import verifier as javascript_verifier
from javascript import browser_tests
from python import verifier as python_verifier
from java import verifier as java_verifier
import doc_generator

# Backward-compatible naming
template2 = jsontemplate


class TokenizeTest(testy.Test):

  def testMakeTokenRegex(self):
    token_re = template2.MakeTokenRegex('[', ']')
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
        template2._SECTION_RE.match('section'),
        None)
    self.verify.Equal(
        template2._SECTION_RE.match('repeated section'),
        None)

    self.verify.Equal(
        template2._SECTION_RE.match('section Foo').groups(),
        (None, 'section', 'Foo'))
    self.verify.Equal(
        template2._SECTION_RE.match('repeated section @').groups(),
        ('repeated', 'section', '@'))


class FromStringTest(testy.Test):

  def testEmpty(self):
    s = """\
Format-Char: |
Meta: <>
"""
    t = template2.FromString(s, _constructor=testy.ClassDef)
    self.verify.Equal(t.args[0], '')
    self.verify.Equal(t.kwargs['meta'], '<>')
    self.verify.Equal(t.kwargs['format_char'], '|')

    # Empty template
    t = template2.FromString('', _constructor=testy.ClassDef)
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
        template2.CompilationError, template2.FromString, f)

  def testTemplate(self):
    f = """\
format-char: :
meta: <>

Hello <there>
"""
    t = template2.FromString(f, _constructor=testy.ClassDef)
    self.verify.Equal(t.args[0], 'Hello <there>\n')
    self.verify.Equal(t.kwargs['meta'], '<>')
    self.verify.Equal(t.kwargs['format_char'], ':')

  def testNoOptions(self):
    # Bug fix
    f = """Hello {dude}"""
    t = template2.FromString(f)
    self.verify.Equal(t.expand({'dude': 'Andy'}), 'Hello Andy')


class _InternalTemplateVerifier(testy.StandardVerifier):
  """Verifies template behavior in-process."""

  def Expansion(
      self, template_def, dictionary, expected, ignore_whitespace=False):
    """
    Args:
      template_def: _TemplateDef instance.
    """
    template = template2.Template(*template_def.args, **template_def.kwargs)
    # TODO: Consider reversing left and right here and throughout
    left = template.expand(dictionary)
    right = expected

    self.LongStringsEqual(left, right, ignore_whitespace=ignore_whitespace)

  def EvaluationError(self, exception, template_def, data_dict):
    template = template2.Template(*template_def.args, **template_def.kwargs)
    self.Raises(exception, template.expand, data_dict)

  def CompilationError(self, exception, *args, **kwargs):
    self.Raises(exception, template2.Template, *args, **kwargs)


_TemplateDef = testy.ClassDef


class JsonTemplateTest(testy.PyUnitCompatibleTest):
  """Language-independent tests for JSON Template."""

  LABELS = ['multilanguage']

  # TODO: This isn't sed
  VERIFIERS = [_InternalTemplateVerifier, python_verifier.ExternalVerifier]

  def __init__(self, verifier):
    testy.PyUnitCompatibleTest.__init__(self, verifier)
    self.Template = _TemplateDef  # TODO: Replace _TemplateDef everywhere

  def testConfigurationErrors(self):
    self.verify.CompilationError(
        template2.ConfigurationError, '', format_char='!')
    self.verify.CompilationError(
        template2.ConfigurationError, '', meta='m')

    # Should I assert that meta is not something crazy?  Max length of 4 and
    # containing {}, [], <> or () is liberal.

  def testTrivial(self):
    t = self.Template('Hello')
    self.verify.Expansion(t, {}, 'Hello')

  def testComment(self):
    t = self.Template('Hello {# Comment} There')
    self.verify.Expansion(t, {}, 'Hello  There')

  def testSpace(self):
    t = self.Template('{.space}{.space}')
    self.verify.Expansion(t, {}, '  ')

  def testOnlyDeclaration(self):
    t = self.Template('{# Comment}')
    self.verify.Expansion(t, {}, '')

  def testSimpleData(self):
    t = self.Template('Hello {name}, how are you')
    self.verify.Expansion(t, {'name': 'Andy'}, 'Hello Andy, how are you')

    self.verify.EvaluationError(template2.UndefinedVariable, t, {})

  def testExpandingInteger(self):
    t = self.Template('There are {num} ways to do it')
    self.verify.Expansion(t, {'num': 5}, 'There are 5 ways to do it')

  def testExpandingNull(self):
    # None/null is considered undefined.  Typically, a null value should be
    # wrapped in section instead.
    t = self.Template('There are {num} ways to do it')
    self.verify.EvaluationError(template2.UndefinedVariable, t, {'num': None})

  def testVariableFormat(self):
    t = self.Template('Where is your {name|html}')
    self.verify.Expansion(t, {'name': '<head>'}, 'Where is your &lt;head&gt;')

  def testDefaultFormatter(self):
    t = self.Template('{name} {val|raw}', default_formatter='html')
    self.verify.Expansion(t, {'name': '<head>', 'val': '<>'}, '&lt;head&gt; <>')

  def testUndefinedVariable(self):
    t = self.Template('Where is your {name|html}')
    self.verify.EvaluationError(template2.UndefinedVariable, t, {})

  def testFormattingCharacter(self):
    t = self.Template('Where is your {name:html}', format_char=':')
    self.verify.Expansion(t, {'name': '<head>'}, 'Where is your &lt;head&gt;')

  def testBadFormatters(self):
    self.verify.CompilationError(
        template2.BadFormatter, 'Where is your {name|BAD}')

    self.verify.CompilationError(
        template2.BadFormatter, 'Where is your {name|really|bad}')

  def testMissingFormatter(self):
    self.verify.CompilationError(
        template2.MissingFormatter, 'What is your {name}',
        default_formatter=None)

  def testEscapeMetacharacter(self):
    t = self.Template('[.meta-left]Hello[.meta-right]', meta='[]')
    self.verify.Expansion(t, {}, '[Hello]')

  def testMeta(self):
    t = self.Template('Hello {{# Comment}} There', meta='{{}}')
    self.verify.Expansion(t, {}, 'Hello  There')

  def testSubstituteCursor(self):
    t = self.Template('{.section is-new}New since {@} ! {.end}')
    self.verify.Expansion(t, {}, '')
    self.verify.Expansion(t, {'is-new': 123}, 'New since 123 ! ')

  def testSimpleSection(self):
    # Has some newlines too
    t = self.Template("""\
{.section is-new}
  Hello there
  New since {date}!
  {date}
{.end}""")
    self.verify.Expansion(t, {}, '')
    d = {'is-new': {'date': 'Monday'}}
    self.verify.Expansion(t, d , """\
  Hello there
  New since Monday!
  Monday
""")

  def testRepeatedSection(self):
    t = self.Template("""
[header]
---------
[.repeated section people]
  [name] [age]
[.end]
""", meta='[]')

    d = {
        'header': 'People',
        'people': [
            {'name': 'Andy', 'age': '20'},
            {'name': 'Bob', 'age': '25'},
            ],
        }

    self.verify.Expansion(t, d, """
People
---------
  Andy 20
  Bob 25
""")

    # Now test a missing section

    self.verify.Expansion(t, {'header': 'Header'}, """
Header
---------
""")

    # people=None is the same
    self.verify.Expansion(t, {'header': 'Header', 'people': None}, """
Header
---------
""")

  def testRepeatedSectionWithDot(self):
    t = self.Template("""
[header]
---------
[.repeated section people]
  [greeting] [@]
[.end]
""", meta='[]')

    d = {
        'greeting': 'Hello',
        'header': 'People',
        'people': [
            'Andy',
            'Bob',
            ],
        }

    self.verify.Expansion(t, d, """
People
---------
  Hello Andy
  Hello Bob
""")

  def testNestedRepeatedSections(self):
    t = self.Template("""
[header]
---------
[.repeated section people]
  [name]: [.repeated section attributes][@] [.end]

[.end]
""", meta='[]')

    d = {
        'header': 'People',
        'people': [
            {'name': 'Andy', 'attributes': ['jerk', 'cool']},
            {'name': 'Bob', 'attributes': ['nice', 'mean', 'fun']},
            ],
        }

    self.verify.Expansion(t, d, """
People
---------
  Andy: jerk cool 
  Bob: nice mean fun 
""")

  def testRepeatedSectionAtRoot(self):
    # This tests expansion of a JSON *list* -- no dictionary in sight

    t = self.Template('[.repeated section @][@] [.end]', meta='[]')
    self.verify.Expansion(t, ['Andy', 'Bob'], 'Andy Bob ')

  def testAlternatesWith(self):
    t = self.Template("""
[header]
---------
[.repeated section people]
  Name: [name] Age: [age]
[.alternates with]
  *****
[.end]
""", meta='[]')
    d = {
        'header': 'People',
        'people': [
            {'name': 'Andy', 'age': '20'},
            {'name': 'Bob', 'age': '25'},
            {'name': 'Carol', 'age': '30'},
            ],
        }

    self.verify.Expansion(t, d, """
People
---------
  Name: Andy Age: 20
  *****
  Name: Bob Age: 25
  *****
  Name: Carol Age: 30
""")

  def testSection(self):

    # TODO: Should the *leading* whitespace before [.end] be removed too?
    t = self.Template("""
[header]
---------
[.section people]
There are [summary] here:
  [.repeated section entries]
    [name] [age]
  [.end]
  [footer]
[.end]
""", meta='[]')

    d = {
        'header': 'People',
        'people': {
            'summary': '2 dudes',
            'footer': 'Footer',
            'entries': [
                {'name': 'Andy', 'age': '20'},
                {'name': 'Bob', 'age': '25'},
                ],
            }
        }

    expected = """
People
---------
There are 2 dudes here:
      Andy 20
      Bob 25
    Footer
"""
    self.verify.Expansion(t, d, expected)
    #return

    self.verify.Expansion(t, {'header': 'People'}, """
People
---------
""")

    # Now test with people=None.  This is the same as omitting the key.
    self.verify.Expansion(t, {'header': 'People', 'people': None}, """
People
---------
""")

  def testExpansionInInnerScope(self):
    t = self.Template("""
[url]
[.section person]
  [name] [age] [url]
[.end]
""", meta='[]')

    d = {
        'url': 'http://example.com',
        'person': {
            'name': 'Andy',
            'age': 30,
            }
        }

    expected = """
http://example.com
  Andy 30 http://example.com
"""
    self.verify.Expansion(t, d, expected)

    d = {
        'person': {
            'name': 'Andy',
            'age': 30,
            }
        }
    self.verify.EvaluationError(template2.UndefinedVariable, t, d)

  def testTooManyEndBlocks(self):
    self.verify.CompilationError(template2.TemplateSyntaxError, """
{.section people}
{.end}
{.end}
""")

  def testTooFewEndBlocks(self):
    self.verify.CompilationError(template2.TemplateSyntaxError, """
{.section people}
  {.section cars}
  {.end}
""")

  def testSectionAndRepeatedSection(self):
    """A repeated section within a section."""
    t = self.Template("""
[header]
---------
[.section people]
  <table>
  [.repeated section @]
    <tr>
      <td>[name]</td>
      <td>[age]</td>
    </tr>
  [.end]
  </table>
[.end]
""", meta='[]')

    d = {
        'header': 'People',
        'people': [
            {'name': 'Andy', 'age': '20'},
            {'name': 'Bob', 'age': '25'},
            ],
        }

    expected = """
People
---------
  <table>
    <tr>
      <td>Andy</td>
      <td>20</td>
    </tr>
    <tr>
      <td>Bob</td>
      <td>25</td>
    </tr>
  </table>
"""

    self.verify.Expansion(t, d, expected, ignore_whitespace=True)

    self.verify.Expansion(t, {'header': 'People'}, """
People
---------
""")

  def testBadContext(self):
    # Note: A list isn't really a valid top level context, but this case should
    # be some kind of error.
    t = self.Template("{foo}")
    self.verify.EvaluationError(template2.UndefinedVariable, t, [])

  def testSectionOr(self):
    t = self.Template("""
Hello there.
{.section person}
  {name} {age} {url}
{.or}
  No person.
{.end}
{url}
""")

    d = {
        'url': 'http://example.com',
        'person': {
            'name': 'Andy',
            'age': 30,
            }
        }

    expected = """
Hello there.
  Andy 30 http://example.com
http://example.com
"""
    self.verify.Expansion(t, d, expected)

    d = { 'url': 'http://example.com' }

    expected = """
Hello there.
  No person.
http://example.com
"""
    self.verify.Expansion(t, d, expected)

  @testy.labels('documentation')
  def testRepeatedSectionOr(self):
    t = self.Template("""
{header}
---------
{.repeated section people}
  {name} {age}
{.or}
  No people.
{.end}
""")

    with_people = {
        'header': 'People',
        'people': [
            {'name': 'Andy', 'age': '20'},
            {'name': 'Bob', 'age': '25'},
            ],
        }

    self.verify.Expansion(t, with_people, """
People
---------
  Andy 20
  Bob 25
""")

    # Empty list
    without_people = {
        'header': 'People',
        'people': [],
        }

    self.verify.Expansion(t, without_people, """
People
---------
  No people.
""")

    # Null
    d = {
        'header': 'People',
        'people': None,
        }

    self.verify.Expansion(t, d, """
People
---------
  No people.
""")

    # Now there are 3 clauses
    t = self.Template("""
{header}
---------
{.repeated section people}
  {name} {age}
{.alternates with}
  --
{.or}
  No people.
{.end}
""")

    self.verify.Expansion(t, with_people, """
People
---------
  Andy 20
  --
  Bob 25
""")

    # Empty list
    d = {
        'header': 'People',
        'people': [],
        }

    self.verify.Expansion(t, without_people, """
People
---------
  No people.
""")

  def testEmptyListWithSection(self):
    # From the wiki

    t = self.Template("""
{.section title-results}
  Results.
  {.repeated section @}
    {num}. {line}
  {.end}
{.end}
""")
    d = {
        'title-results': [
            {'num': 1, 'line': 'one'},
            {'num': 2, 'line': 'two'},
            ]
        }

    self.verify.Expansion(t, d, """
  Results.
      1. one
      2. two
  """)

    d = { 'title-results': [] }

    self.verify.Expansion(t, d, '\n')


class StandardFormattersTest(testy.Test):
  """Test that each implementation implements the standard formatters."""

  LABELS = ['multilanguage']

  def testHtmlFormatter(self):
    t = testy.ClassDef('<b>{name|html}</b>')
    self.verify.Expansion(
        t, {'name': '"<tag>"'}, '<b>"&lt;tag&gt;"</b>')

  def testHtmlAttrValueFormatter(self):
    t = testy.ClassDef('<a href="{url|html-attr-value}">')
    self.verify.Expansion(
        t, {'url': '"<>&'}, '<a href="&quot;&lt;&gt;&amp;">')



# TODO: This can be an example in the documentation about how to use custom
# formatters.
def _PythonFormat(format_str):
  """Use Python % format strings as template format specifiers."""
  # A little hack for now
  if format_str.startswith('%'):
    return lambda value: format_str % value
  else:
    return None


class InternalTemplateTest(testy.PyUnitCompatibleTest):
  """Tests that can only be run internally."""

  VERIFIERS = [_InternalTemplateVerifier]

  def testAdditionalFormat(self):
    t = _TemplateDef(
        '{num|%.5f}', more_formatters=_PythonFormat)
    self.verify.Expansion(t, {'num': 1.0/3}, '0.33333')

  def testFormatterRaisesException(self):

    # For now, integers can't be formatted directly as html.  Just omit the
    # formatter.
    t = template2.Template('There are {num|html} ways to do it')
    try:
      t.expand({'num': 5})
    except template2.EvaluationError, e:
      self.assert_(e.args[0].startswith('Formatting value 5'), e.args[0])
      self.assertEqual(e.original_exception.__class__, AttributeError)
    else:
      self.fail('Expected EvaluationError')

  def testMultipleFormatters(self):
    # TODO: This could have a version in the external test too, just not with
    # 'url-params', which is not the same across platforms because of dictionary
    # iteration order

    # Single formatter
    t = _TemplateDef(
        'http://example.com?{params:url-params}',
        format_char=':')
    self.verify.Expansion(
        t,
        {'params': {'foo': 1, 'bar': 'String with spaces', 'baz': '!@#$%^&*('}},
        'http://example.com?baz=%21%40%23%24%25%5E%26%2A%28&foo=1&bar=String+with+spaces')

    # Multiple
    t = _TemplateDef(
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

    t = _TemplateDef('{@}', more_formatters=_More)
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

    t = template2.Template("""
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
    self.assertEqual(type(program), jsontemplate._Section)

  def testSimpleUnicodeSubstitution(self):
    t = jsontemplate.Template(u'Hello {name}')

    self.verify.Equal(t.expand({u'name': u'World'}), u'Hello World')

    # TODO: Need a lot more comprehensive *external* unicode tests, as well as
    # ones for the internal API.  Need to test mixing of unicode() and str()
    # instances (or declare it undefined).


class DocumentationTest(testy.Test):
  """Test cases added for the sake of documentation."""

  # TODO: The default labels for this test should be 'documentation'

  @testy.labels('documentation')
  def testSearchResultsExample(self):
    # TODO: Come up with a better search results example
    return

  @testy.labels('documentation', 'live-js', 'blog-format')
  def testTableExample(self):
    t = _TemplateDef("""\
{# This is a comment and will be removed from the output.}

{.section songs}
  <h2>Songs in '{playlist-name}'</h2>

  <table width="100%">
  {.repeated section @}
    <tr>
      <td><a href="{url-base|htmltag}{url|htmltag}">Play</a>
      <td><i>{title}</i></td>
      <td>{artist}</td>
    </tr>
  {.end}
  </table>
{.or}
  <p><em>(No page content matches)</em></p>
{.end}
""")

    d = {
      "playlist-name": "Epic Playlist",
      "url-base": "http://example.com/music/", 
      "songs": [
        { "title": "Sounds Like Thunder",
          "artist": "Grayceon",
          "url": "1.mp3"
        },
        { "title": "Their Hooves Carve Craters in the Earth",
          "artist": "Thou",
          "url": "2.mp3"
        }
      ]
    }

    expected = """\

  <h2>Songs in 'Epic Playlist'</h2>

  <table width="100%">
      <tr>
      <td><a href="http://example.com/music/1.mp3">Play</a>
      <td><i>Sounds Like Thunder</i></td>
      <td>Grayceon</td>
    </tr>
      <tr>
      <td><a href="http://example.com/music/2.mp3">Play</a>
      <td><i>Their Hooves Carve Craters in the Earth</i></td>
      <td>Thou</td>
    </tr>
    </table>
"""

    self.verify.Expansion(t, d, expected)


def main(argv):
  this_dir = os.path.dirname(__file__)

  # e.g. this works on my Ubuntu system
  default_v8_shell = os.path.join(
      this_dir, 'javascript', 'v8shell', 'linux-i686', 'shell')
  default_java = os.path.join(
      os.getenv('JAVA_HOME', ''), 'bin', 'java')

  run_params = testy.TEST_RUN_PARAMS + [
      params.OptionalString(
          'v8-shell', default=default_v8_shell,
          help='Location of the v8 shell to run JavaScript tests'),
      params.OptionalString(
          'java-interpreter', default=default_java,
          help='Location of the Java interpreter to run Java tests'),

      # Until we have better test filtering:
      params.OptionalBoolean('python', help='Run Python tests'),
      params.OptionalBoolean('java', help='Run Java tests'),
      params.OptionalBoolean('javascript', help='Run JavaScript tests'),

      params.OptionalString(
          'browser-test-out-dir', shortcut='b',
          help='Write browser tests to this directory'),

      params.OptionalString(
          'doc-output-dir', shortcut='d',
          help='Write generated docs to this directory'),

      params.OptionalBoolean('all-tests', help='Run all tests'),
      ]

  options = cmdapp.ParseArgv(argv, run_params)

  v = _InternalTemplateVerifier()

  python_impl = os.path.join(this_dir, 'python', 'expand.py')
  py_verifier = python_verifier.ExternalVerifier(python_impl)

  js_impl = os.path.join(this_dir, 'javascript', 'json-template.js')
  helpers = os.path.join(this_dir, 'pan', 'javascript', 'test_helpers.js')
  js_verifier = javascript_verifier.V8ShellVerifier(
      options.v8_shell, js_impl, helpers)

  java_impl = os.path.join(this_dir, 'java', 'jsontemplate.jar')
  java_test_classes = os.path.join(this_dir, 'java', 'jsontemplate_test.jar')
  jv_verifier = java_verifier.JavaVerifier(
      options.java_interpreter, java_impl, java_test_classes)


  filt = testy.MakeTestClassFilter(label='multilanguage')
  multi_tests = testy.GetTestClasses(__import__(__name__), filt)

  internal_tests = [
      # Things we can't test externally
      TokenizeTest(testy.StandardVerifier()),
      FromStringTest(testy.StandardVerifier()),
      InternalTemplateTest(v),
      ]

  # Also run the internal version of all the multilanguage tests
  internal_tests.extend(m(v) for m in multi_tests)

  # External versions
  if options.all_tests:
    tests = internal_tests
    tests.extend(m(py_verifier) for m in multi_tests)
    tests.extend(m(js_verifier) for m in multi_tests)
    tests.extend(m(jv_verifier) for m in multi_tests)

  elif options.python:
    tests = [m(py_verifier) for m in multi_tests]

  elif options.javascript:
    tests = [m(js_verifier) for m in multi_tests]

  elif options.java:
    tests = [m(jv_verifier) for m in multi_tests]

  elif options.doc_output_dir:
    # Generates the HTML fragments.

    docgen = doc_generator.DocGenerator(options.doc_output_dir)

    # Run the internal tests before generating docs.
    tests = []
    tests.extend(m(v) for m in multi_tests)
    tests.extend(m(docgen) for m in multi_tests)

    tests.extend([
        DocumentationTest(v), DocumentationTest(docgen),
        ])

  elif options.browser_test_out_dir:
    testgen = browser_tests.TestGenerator(options.browser_test_out_dir)

    # Run the internal tests before generating browser tests.
    tests = []
    tests.extend(m(v) for m in multi_tests)
    tests.extend(m(testgen) for m in multi_tests)

  else:
    tests = internal_tests

  testy.RunTests(tests, options)


if __name__ == '__main__':
  main(sys.argv[1:])
