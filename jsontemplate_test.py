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
import sys

if __name__ == '__main__':
  # for jsontemplate package
  sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

from pan.core import cmdapp
from pan.core import params
from pan.core import json
from pan.core import util
from pan.test import testy

import jsontemplate  # module under *direct* test

# External verifiers:
from doc import doc_generator
from javascript import verifier as javascript_verifier
from javascript import browser_tests
from java import verifier as java_verifier
from php import verifier as php_verifier
from lua import verifier as lua_verifier
# import *must* be relative to python package to work
import verifier as python_verifier


# This is for making multiline strings look nicer.  Strips leading indentation.
B = util.BlockStr


class TrivialTests(testy.Test):
  """For getting the skeleton of code in place!"""

  LABELS = ['multilanguage']

  def testTrivial(self):
    t = testy.ClassDef('Hello')
    self.verify.Expansion(t, {}, 'Hello')


class SimpleTests(testy.Test):
  """Basic syntax."""

  LABELS = ['multilanguage']

  def testConfigurationErrors(self):
    self.verify.CompilationError(
        jsontemplate.ConfigurationError, '', format_char='!')
    self.verify.CompilationError(
        jsontemplate.ConfigurationError, '', meta='m')

    # Should I assert that meta is not something crazy?  Max length of 4 and
    # containing {}, [], <> or () is liberal.

  def testComment(self):
    t = testy.ClassDef('Hello {# Comment} There')
    self.verify.Expansion(t, {}, 'Hello  There')

  def testSpace(self):
    t = testy.ClassDef('{.space}{.space}')
    self.verify.Expansion(t, {}, '  ')

  def testWhitespace(self):
    t = testy.ClassDef('{.tab}{.tab}')
    self.verify.Expansion(t, {}, '\t\t')

    t = testy.ClassDef('Line{.newline}')
    self.verify.Expansion(t, {}, 'Line\n')

  def testOnlyDeclaration(self):
    t = testy.ClassDef('{# Comment}')
    self.verify.Expansion(t, {}, '')


class SubstitutionsTest(testy.Test):
  """Language-independent tests for JSON Template."""

  LABELS = ['multilanguage']

  # TODO: This isn't sed
  VERIFIERS = [
      python_verifier.InternalTemplateVerifier,
      python_verifier.ExternalVerifier]

  def testSimpleData(self):
    t = testy.ClassDef('Hello {name}, how are you')
    self.verify.Expansion(t, {'name': 'Andy'}, 'Hello Andy, how are you')

    self.verify.EvaluationError(jsontemplate.UndefinedVariable, t, {})

  def testExpandingInteger(self):
    t = testy.ClassDef('There are {num} ways to do it')
    self.verify.Expansion(t, {'num': 5}, 'There are 5 ways to do it')

  # TODO: Implement in Java
  @testy.no_verify('java')
  def testExpandingNull(self):
    t = testy.ClassDef('There are {num|str} ways to do it')
    self.verify.Expansion(t, {'num': None}, 'There are null ways to do it')

  def testVariableFormat(self):
    t = testy.ClassDef('Where is your {name|html}')
    self.verify.Expansion(t, {'name': '<head>'}, 'Where is your &lt;head&gt;')

  def testDefaultFormatter(self):
    t = testy.ClassDef('{name} {val|raw}', default_formatter='html')
    self.verify.Expansion(t, {'name': '<head>', 'val': '<>'}, '&lt;head&gt; <>')

  def testUndefinedVariable(self):
    t = testy.ClassDef('Where is your {name|html}')
    self.verify.EvaluationError(jsontemplate.UndefinedVariable, t, {})

  # TODO: Implement in Java
  @testy.no_verify('java')
  def testUndefinedVariableUsesUndefinedStr(self):
    t = testy.ClassDef('Where is your {name|html}', undefined_str='')
    self.verify.Expansion(t, {}, 'Where is your ')

    t = testy.ClassDef('Where is your {name|html}', undefined_str='???')
    self.verify.Expansion(t, {}, 'Where is your ???')

  def testChangingFormattingCharacter(self):
    t = testy.ClassDef('Where is your {name:html}', format_char=':')
    self.verify.Expansion(t, {'name': '<head>'}, 'Where is your &lt;head&gt;')

  def testBadFormatters(self):
    self.verify.CompilationError(
        jsontemplate.BadFormatter, 'Where is your {name|BAD}')

    self.verify.CompilationError(
        jsontemplate.BadFormatter, 'Where is your {name|really|bad}')

  def testMissingFormatter(self):
    self.verify.CompilationError(
        jsontemplate.MissingFormatter, 'What is your {name}',
        default_formatter=None)

  def testEscapeMetacharacter1(self):
    t = testy.ClassDef('[.meta-left]Hello[.meta-right]', meta='[]')
    self.verify.Expansion(t, {}, '[Hello]')

    t = testy.ClassDef('<%.meta-left%>Hello<%.meta-right%>', meta='<%%>')
    self.verify.Expansion(t, {}, '<%Hello%>')

    t = testy.ClassDef('(-.meta-left-)Hello(-.meta-right-)', meta='(--)')
    self.verify.Expansion(t, {}, '(-Hello-)')

    t = testy.ClassDef('^|.meta-left|^Hello^|.meta-right|^', meta='^||^')
    self.verify.Expansion(t, {}, '^|Hello|^')

    t = testy.ClassDef('$(.meta-left)$Hello$(.meta-right)$', meta='$()$')
    self.verify.Expansion(t, {}, '$(Hello)$')

  def testMeta(self):
    t = testy.ClassDef('Hello {{# Comment}} There', meta='{{}}')
    self.verify.Expansion(t, {}, 'Hello  There')

  def testSubstituteCursor(self):
    t = testy.ClassDef('{.section is-new}New since {@} ! {.end}')
    self.verify.Expansion(t, {}, '')
    self.verify.Expansion(t, {'is-new': 123}, 'New since 123 ! ')


class SectionsTest(testy.PyUnitCompatibleTest):
  """Test sections adn repeated sections."""

  LABELS = ['multilanguage']

  def testSimpleSection(self):
    # Has some newlines too
    t = testy.ClassDef(
        B("""
        {.section is-new}
          Hello there
          New since {date}!
          {date}
        {.end}
        """))

    self.verify.Expansion(t, {}, '')

    d = {'is-new': {'date': 'Monday'}}

    self.verify.Expansion(t, d,
        B("""
          Hello there
          New since Monday!
          Monday
        """))

  def testRepeatedSection(self):
    t = testy.ClassDef(
        B("""
        [header]
        ---------
        [.repeated section people]
          [name] [age]
        [.end]
        """), meta='[]')

    d = {
        'header': 'People',
        'people': [
            {'name': 'Andy', 'age': '20'},
            {'name': 'Bob', 'age': '25'},
            ],
        }

    self.verify.Expansion(t, d, B("""
        People
        ---------
          Andy 20
          Bob 25
        """))

    # Now test a missing section
    self.verify.Expansion(t, {'header': 'Header'}, B("""
        Header
        ---------
        """))

    # people=None is the same
    self.verify.Expansion(t, {'header': 'Header', 'people': None}, B("""
        Header
        ---------
        """))

  def testRepeatedSectionWithDot(self):
    t = testy.ClassDef(
        B("""
        [header]
        ---------
        [.repeated section people]
          [greeting] [@]
        [.end]
        """), meta='[]')

    d = {
        'greeting': 'Hello',
        'header': 'People',
        'people': [
            'Andy',
            'Bob',
            ],
        }

    self.verify.Expansion(t, d, B("""
        People
        ---------
          Hello Andy
          Hello Bob
        """))

  def testNestedRepeatedSections(self):
    t = testy.ClassDef(
        B("""
        [header]
        ---------
        [.repeated section people]
          [name]: [.repeated section attributes][@] [.end]
        [.end]
        """), meta='[]')

    d = {
        'header': 'People',
        'people': [
            {'name': 'Andy', 'attributes': ['jerk', 'cool']},
            {'name': 'Bob', 'attributes': ['nice', 'mean', 'fun']},
            ],
        }

    self.verify.Expansion(t, d, B("""
        People
        ---------
          Andy: jerk cool 
          Bob: nice mean fun 
        """), ignore_all_whitespace=True)

  @testy.no_verify('php', 'java')
  def testNestedAnonymousRepeatedSections(self):
    t = testy.ClassDef(
        B("""
        {.repeated section cells}
          {.repeated section @}{@} {.end}
        {.end}
        """))

    d = {
        'cells': [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
            ],
        }

    self.verify.Expansion(t, d, B("""
          1 2 3 
          4 5 6 
          7 8 9 
        """), ignore_all_whitespace=True)

  @testy.no_verify('php', 'java')
  def testNestedAnonymousRepeatedSectionsWithIndex(self):
    t = testy.ClassDef(
        B("""
        {.repeated section cells}
          {@index} : {.repeated section @}{@index}{@}-{.end}
        {.end}
        """))

    d = {
        'cells': [
            ['a', 'b', 'c'],
            ['d', 'e', 'f'],
            ],
        }

    self.verify.Expansion(t, d, B("""
          1 : 1a-2b-3c-
          2 : 1d-2e-3f-
        """), ignore_all_whitespace=True)

  def testRepeatedSectionAtRoot(self):
    # This tests expansion of a JSON *list* -- no dictionary in sight

    t = testy.ClassDef('[.repeated section @][@] [.end]', meta='[]')
    self.verify.Expansion(t, ['Andy', 'Bob'], 'Andy Bob ')

  @testy.no_verify('php', 'java', 'javascript')
  def testRepeatedSectionPreformatters(self):
    # Test formatting a list *before" expanding it into a template

    t = testy.ClassDef(B("""
        {.repeated section dirs|reverse}{@} {.end}
        """))
    self.verify.Expansion(t, {'dirs': ['1', '2', '3']}, '3 2 1 \n')

  @testy.no_verify('php', 'java', 'javascript')
  def testSectionPreformatters(self):
    # Synonym for the above.  Apply the pre-formatter in a section instead of
    # the list.
    t = testy.ClassDef(B("""
        {.section dirs|reverse}
        {.repeated section @}{@} {.end}
        {.end}
        """))
    self.verify.Expansion(t, {'dirs': ['1', '2', '3']}, '3 2 1 \n')

  def testAlternatesWith(self):
    t = testy.ClassDef(
        B("""
        [header]
        ---------
        [.repeated section people]
          Name: [name] Age: [age]
        [.alternates with]
          *****
        [.end]
        """), meta='[]')

    d = {
        'header': 'People',
        'people': [
            {'name': 'Andy', 'age': '20'},
            {'name': 'Bob', 'age': '25'},
            {'name': 'Carol', 'age': '30'},
            ],
        }

    self.verify.Expansion(t, d, B("""
        People
        ---------
          Name: Andy Age: 20
          *****
          Name: Bob Age: 25
          *****
          Name: Carol Age: 30
        """))

  @testy.no_verify('java', 'php')
  def testAlternatesWithInvalid(self):
    self.verify.CompilationError(jsontemplate.TemplateSyntaxError,
        B("""
        [header]
        ---------
        [.section people]
          Name: [name] Age: [age]
        [.alternates with]
          *****
        [.end]
        """), meta='[]')

  def testSection(self):

    t = testy.ClassDef(
        B("""
        [header]
        ---------
        [.section people]
        There are [summary] here:
          [.repeated section entries]
            [name] [age]
          [.end]
          [footer]
        [.end]
        """), meta='[]')

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

    # Relies on smart-indent behavior; ignore whitespace for some
    # implementations
    self.verify.Expansion(t, d, B("""
        People
        ---------
        There are 2 dudes here:
            Andy 20
            Bob 25
          Footer
        """), ignore_all_whitespace=True)

    self.verify.Expansion(t, {'header': 'People'}, B("""
        People
        ---------
        """))

    # Now test with people=None.  This is the same as omitting the key.
    self.verify.Expansion(t, {'header': 'People', 'people': None}, B("""
        People
        ---------
        """))

  def testExpansionInInnerScope(self):
    t = testy.ClassDef(
        B("""
        [url]
        [.section person]
          [name] [age] [url]
        [.end]
        """), meta='[]')

    d = {
        'url': 'http://example.com',
        'person': {
            'name': 'Andy',
            'age': 30,
            }
        }

    self.verify.Expansion(t, d, B("""
        http://example.com
          Andy 30 http://example.com
        """))

    d = {
        'person': {
            'name': 'Andy',
            'age': 30,
            }
        }
    self.verify.EvaluationError(jsontemplate.UndefinedVariable, t, d)

  def testTooManyEndBlocks(self):
    self.verify.CompilationError(jsontemplate.TemplateSyntaxError, B("""
        {.section people}
        {.end}
        {.end}
        """))

  def testTooFewEndBlocks(self):
    self.verify.CompilationError(jsontemplate.TemplateSyntaxError, B("""
        {.section people}
          {.section cars}
          {.end}
        """))

  def testSectionAndRepeatedSection(self):
    """A repeated section within a section."""
    t = testy.ClassDef(
        B("""
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
        """), meta='[]')

    d = {
        'header': 'People',
        'people': [
            {'name': 'Andy', 'age': '20'},
            {'name': 'Bob', 'age': '25'},
            ],
        }

    expected = B("""
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
        """)

    self.verify.Expansion(t, d, expected, ignore_whitespace=True)

    self.verify.Expansion(t, {'header': 'People'}, B("""
        People
        ---------
        """))

  def testBadContext(self):
    # Note: A list isn't really a valid top level context, but this case should
    # be some kind of error.
    t = testy.ClassDef("{foo}")
    self.verify.EvaluationError(jsontemplate.UndefinedVariable, t, [])

  def testSectionOr(self):
    t = testy.ClassDef(
        B("""
        Hello there.
        {.section person}
          {name} {age} {url}
        {.or}
          No person.
        {.end}
        {url}
        """))

    d = {
        'url': 'http://example.com',
        'person': {
            'name': 'Andy',
            'age': 30,
            }
        }

    expected = B("""
        Hello there.
          Andy 30 http://example.com
        http://example.com
        """)
    self.verify.Expansion(t, d, expected)

    d = { 'url': 'http://example.com' }

    expected = B("""
        Hello there.
          No person.
        http://example.com
        """)
    self.verify.Expansion(t, d, expected)

  @testy.no_verify('java', 'php')
  def testSectionOrWithBadPredicate(self):
    self.verify.CompilationError(jsontemplate.TemplateSyntaxError,
        B("""
        [header]
        ---------
        [.section people]
          Name: [name] Age: [age]
        [.or singular]
          *****
        [.end]
        """), meta='[]')

  @testy.labels('documentation')
  def testRepeatedSectionOr(self):
    t = testy.ClassDef(
        B("""
        {header}
        ---------
        {.repeated section people}
          {name} {age}
        {.or}
          No people.
        {.end}
        """))

    with_people = {
        'header': 'People',
        'people': [
            {'name': 'Andy', 'age': '20'},
            {'name': 'Bob', 'age': '25'},
            ],
        }

    self.verify.Expansion(t, with_people, B("""
        People
        ---------
          Andy 20
          Bob 25
        """))

    # Empty list
    without_people = {
        'header': 'People',
        'people': [],
        }

    self.verify.Expansion(t, without_people, B("""
        People
        ---------
          No people.
        """))

    # Null
    d = {
        'header': 'People',
        'people': None,
        }

    self.verify.Expansion(t, d, B("""
        People
        ---------
          No people.
        """))

    # Now there are 3 clauses
    t = testy.ClassDef(
        B("""
        {header}
        ---------
        {.repeated section people}
          {name} {age}
        {.alternates with}
          --
        {.or}
          No people.
        {.end}
        """))

    self.verify.Expansion(t, with_people, B("""
        People
        ---------
          Andy 20
          --
          Bob 25
        """))

    # Empty list
    d = {
        'header': 'People',
        'people': [],
        }

    self.verify.Expansion(t, without_people, B("""
        People
        ---------
          No people.
        """))

  def testEmptyListWithSection(self):
    # From the wiki

    t = testy.ClassDef(
        B("""
        {.section title-results}
          Results.
          {.repeated section @}
            {num}. {line}
          {.end}
        {.end}
        """))
    d = {
        'title-results': [
            {'num': 1, 'line': 'one'},
            {'num': 2, 'line': 'two'},
            ]
        }

    self.verify.Expansion(t, d, B("""
          Results.
            1. one
            2. two
        """), ignore_all_whitespace=True)

    d = { 'title-results': [] }

    self.verify.Expansion(t, d, '')


class DottedLookupTest(testy.Test):
  """Test substitutions like {foo.bar.baz}."""

  LABELS = ['multilanguage']

  @testy.no_verify('java')
  def testDottedLookup(self):
    t = testy.ClassDef('{foo.bar}')

    self.verify.Expansion(
        t,
        {'foo': {'bar': 'Hello'}},
        'Hello')

  @testy.no_verify('java')
  def testDottedLookupErrors(self):

    # TODO: Also test everything with setting undefined_str

    t = testy.ClassDef('{foo.bar}')

    # The second lookup doesn't look up the stack to find 'bar'
    self.verify.EvaluationError(
        jsontemplate.UndefinedVariable,
        t,
        {'foo': {}, 'bar': 100})

    # Can't look up bar in 100
    self.verify.EvaluationError(
        jsontemplate.UndefinedVariable,
        t,
        {'foo': 100})

    # Can't look up bar in a list
    self.verify.EvaluationError(
        jsontemplate.UndefinedVariable,
        t,
        {'foo': []})

    self.verify.EvaluationError(
        jsontemplate.UndefinedVariable,
        t,
        {'foo': {}})

    self.verify.EvaluationError(
        jsontemplate.UndefinedVariable,
        t,
        {})

  @testy.no_verify('java')
  def testDottedLookupErrorsWithUndefinedStr(self):

    t = testy.ClassDef('{foo.bar}', undefined_str='UNDEFINED')

    # The second lookup doesn't look up the stack to find 'bar'
    self.verify.Expansion(
        t,
        {'foo': {}, 'bar': 100},
        'UNDEFINED')

  @testy.no_verify('java')
  def testThreeLookups(self):
    t = testy.ClassDef('{foo.bar.baz}')

    self.verify.Expansion(
        t,
        {'foo': {'bar': {'baz': 'Hello'}}},
        'Hello')

    self.verify.EvaluationError(
        jsontemplate.UndefinedVariable,
        t,
        {'foo': 100})

  @testy.no_verify('java')
  def testScopedLookup(self):
    t = testy.ClassDef(
        B("""
        {.section foo}
          {bar.baz}
        {.end}
        """))

    self.verify.Expansion(
        t,
        {'foo': {'bar': {'baz': 'Hello'}}},
        '  Hello\n')

    # We should find 'bar' even if it's not under foo
    self.verify.Expansion(
        t,
        { 'foo': {'unused': 1},
          'bar': {'baz': 'Hello'},
        },
        '  Hello\n')

    self.verify.EvaluationError(
        jsontemplate.UndefinedVariable,
        t,
        {'foo': 100})


class SpecialVariableTest(testy.Test):
  """Tests the special @index variable."""

  LABELS = ['multilanguage']

  @testy.no_verify('java')
  def testIndex(self):
    t = testy.ClassDef(
        B("""
        {.repeated section @}
          {@index} {name}
        {.end}
        """))

    data = [
      {'name': 'Spam'},
      {'name': 'Eggs'},
      ]

    expected = B("""
      1 Spam
      2 Eggs
    """)
    self.verify.Expansion(t, data, expected)

  @testy.no_verify('java')
  def testTwoIndices(self):
    t = testy.ClassDef(
        B("""
        {.repeated section albums}
          {@index} {name}
          {.repeated section songs}
            {@index} {@}
          {.end}
        {.end}
        """))

    data = {
      'albums': [
        { 'name': 'Diary of a Madman',
          'songs': ['Over the Mountain', 'S.A.T.O']},
        { 'name': 'Bark at the Moon',
          'songs': ['Waiting for Darkness']},
        ]
      }

    expected = B("""
      1 Diary of a Madman
        1 Over the Mountain
        2 S.A.T.O
      2 Bark at the Moon
        1 Waiting for Darkness
    """)
    # Whitespace still differs between Python/JS
    self.verify.Expansion(t, data, expected, ignore_all_whitespace=True)

  @testy.no_verify('java')
  def testUndefinedIndex(self):
    t = testy.ClassDef(
        B("""
        {.section foo}
          {@index} {name}
        {.end}
        """))
    data = {'foo': 'bar'}
    self.verify.EvaluationError(jsontemplate.UndefinedVariable, t, data)


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

  @testy.only_verify('python', 'javascript')
  def testPlainUrlFormatter(self):
    t = testy.ClassDef('{url|plain-url}')
    self.verify.Expansion(
        t, {'url': 'http://foo/bar?foo=1&bar=2'},
        '<a href="http://foo/bar?foo=1&amp;bar=2">'
           'http://foo/bar?foo=1&amp;bar=2'
        '</a>')

  # TODO: Do this in 2 other languages
  @testy.no_verify('php', 'java')
  def testAbsUrlFormatter(self):
    """AbsUrl is mainly an example of 'context formatters'.

    The point of this is that the AbsUrl has access to the top-level 'base-url'
    value.  Without this, base-url would have to be repeated in every single
    item in 'users'.
    """

    t = testy.ClassDef(
        B("""
        {.repeated section users}
          {url|AbsUrl}
        {.end}
        """))

    data = {
        'base-url': 'http://example.com',
        'users': [
            {'url': 'dan'},
            {'url': 'ed'},
            ],
        }

    expected = B("""
      http://example.com/dan
      http://example.com/ed
    """)
    self.verify.Expansion(t, data, expected)

  # TODO: Do this in 2 other languages
  @testy.no_verify('php', 'java')
  def testPluralizeFormatter(self):
    """
    'pluralize' is an example of formatters which take arguments (and a
    variable number of them).  Based on Django's pluralize.
    """
    # 0 arguments
    t = testy.ClassDef('You have {num} message{num|pluralize}.')
    self.verify.Expansion(t, {'num': 1}, 'You have 1 message.')
    self.verify.Expansion(t, {'num': 3}, 'You have 3 messages.')

    # 1 argument
    t = testy.ClassDef('They suffered {num} loss{num|pluralize es}.')
    self.verify.Expansion(t, {'num': 1}, 'They suffered 1 loss.')
    self.verify.Expansion(t, {'num': 3}, 'They suffered 3 losses.')

    # 2 arguments
    t = testy.ClassDef(
        'There {num|pluralize is are} {num} song{num|pluralize}.')
    self.verify.Expansion(t, {'num': 1}, 'There is 1 song.')
    self.verify.Expansion(t, {'num': 3}, 'There are 3 songs.')

  # TODO: Do this in 2 other languages
  @testy.no_verify('php', 'java')
  def testPluralizeWithCustomDelimiters(self):

    # Arguments with spaces in them
    t = testy.ClassDef(
        '{num-people|pluralize/It depends/They depend} on {num-things} '
        'thing{num-things|pluralize}.')
    self.verify.Expansion(
        t, {'num-people': 1, 'num-things': 1},
        'It depends on 1 thing.')
    self.verify.Expansion(
        t, {'num-people': 1, 'num-things': 3},
        'It depends on 3 things.')
    self.verify.Expansion(
        t, {'num-people': 3, 'num-things': 1},
        'They depend on 1 thing.')
    self.verify.Expansion(
        t, {'num-people': 3, 'num-things': 3},
        'They depend on 3 things.')

  # TODO: Do this in 3 other languages
  @testy.no_verify('php', 'java')
  def testCycleFormatter(self):

    t = testy.ClassDef(
        B("""
        {.repeated section @}
          {@index|cycle red blue} {name}
        {.end}
        """))

    data = [
      {'name': 'Andy'},
      {'name': 'Bob'},
      {'name': 'Carol'},
      {'name': 'Dirk'},
      ]

    self.verify.Expansion(t, data,
        B("""
          red Andy
          blue Bob
          red Carol
          blue Dirk
        """))

    t = testy.ClassDef(
        B("""
        {.repeated section @}
          {@index|cycle/x x/y y/z z} {name}
        {.end}
        """))

    self.verify.Expansion(t, data,
        B("""
          x x Andy
          y y Bob
          z z Carol
          x x Dirk
        """))


class AllFormattersTest(testy.Test):
  """Test that each implementation implements the standard formatters."""

  LABELS = ['multilanguage']

  @testy.only_verify('python')
  def testPrintfFormatter(self):
    t = testy.ClassDef('<b>{num|printf %.3f}</b>')
    self.verify.ExpansionWithAllFormatters(
        t, {'num': 1.0/3}, '<b>0.333</b>')


class WhitespaceModesTest(testy.Test):
  """Tests the whitespace= option."""

  LABELS = ['multilanguage']

  @testy.no_verify('javascript', 'php', 'java')
  def testSmart(self):
    # The default mode
    t = testy.ClassDef('  Hello {name}  ')
    self.verify.Expansion(t, {'name': 'World'}, '  Hello World  ')

    t = testy.ClassDef(
        B("""
          {.section name}
            Hello {name}
          {.end}
        """))
    # Just 4 leading spaces and a trailing newline
    self.verify.Expansion(t, {'name': 'World'}, '    Hello World\n')

  @testy.no_verify('javascript', 'php', 'java')
  def testStripLine(self):
    t = testy.ClassDef(
        B("""
          {.section name}
            Hello {name}
          {.end}
        """), whitespace='strip-line')
    # Just 4 leading spaces and a trailing newline
    self.verify.Expansion(t, {'name': 'World'}, 'Hello World')


class PredicatesTest(testy.Test):
  """Tests the predicates feature."""

  LABELS = ['multilanguage']
  # TODO: Add class-level NO_VERIFY = [] to testy

  # TODO: Fix JS whitesspace in this test
  @testy.no_verify('java', 'php')
  def testValuePredicate(self):
    # OLD STYLE -- DISCOURAGED -- SEE BELOW
    t = testy.ClassDef(
    B("""
    {.repeated section num}
      {.plural?}
        There are {@} people here.
      {.or singular?}
        There is one person here.
      {.or}
        There is nobody here.
      {.end}
    {.end}
    """))

    data = {'num': [0, 1, 2, 3]}

    expected = B("""
        There is nobody here.
        There is one person here.
        There are 2 people here.
        There are 3 people here.
    """)
    self.verify.Expansion(t, data, expected, ignore_all_whitespace=True)

    # This is the same template in the NEW IDIOM
    t = testy.ClassDef(
    B("""
    {.repeated section num}
      {.if plural}
        There are {@} people here.
      {.or singular}
        There is one person here.
      {.or}
        There is nobody here.
      {.end}
    {.end}
    """))
    self.verify.Expansion(t, data, expected, ignore_all_whitespace=True)

  @testy.no_verify('java', 'php')
  def testValuePredicateWithRecord(self):
    t = testy.ClassDef(
    B("""
    {.repeated section groups}
      {.section num}
        {.if plural}
          {@} people in {name}.
        {.or singular}
          One person in {name}.
        {.end}
      {.or}
        {# IMPORTANT: This must be the .or clause, because 0 is a false value }
        {#            May be better to use Plural and Singular variants.      }
          Nobody in {name}.
      {.end}
    {.end}
    """))

    data = {
        'groups': [
            {'name': 'Beginner', 'num': 3},
            {'name': 'Intermediate', 'num': 1},
            {'name': 'Advanced', 'num': 0},
            ]
        }

    expected = B("""
          3 people in Beginner.
          One person in Intermediate.
          Nobody in Advanced.
    """)
    self.verify.Expansion(t, data, expected, ignore_all_whitespace=True)

  @testy.no_verify('java', 'php')
  def testContextPredicate(self):

    # OLD -- DISCOURAGED
    # The Debug? predicate looks up the stack for a "debug" attribute
    old_t = testy.ClassDef(
    B("""
    {.repeated section posts}
      Title: {title}
      Body: {body}
      {.Debug?}
        Rendered in 3 seconds
      {.end}
    {.end}
    """))

    data = {
        'posts': [
            {'title': 'Spam', 'body': 'This is spam'},
            {'title': 'Eggs', 'body': 'These are eggs'},
            ]
        }

    expected = B("""
      Title: Spam
      Body: This is spam
      Title: Eggs
      Body: These are eggs
    """)
    self.verify.Expansion(old_t, data, expected, ignore_all_whitespace=True)

    data = {
        'debug': True,
        'posts': [
            {'title': 'Spam', 'body': 'This is spam'},
            {'title': 'Eggs', 'body': 'These are eggs'},
            ]
        }

    expected = B("""
      Title: Spam
      Body: This is spam
        Rendered in 3 seconds
      Title: Eggs
      Body: These are eggs
        Rendered in 3 seconds
    """)
    self.verify.Expansion(old_t, data, expected, ignore_all_whitespace=True)

    # Test it at the top level too
    t = testy.ClassDef("{.Debug?}Rendered in 3 seconds{.end}")
    self.verify.Expansion(t, {'debug': True}, 'Rendered in 3 seconds')
    self.verify.Expansion(t, {'debug': False}, '')

  def testTestPredicateShorthand(self):
    # Test the NEW STYLE
    t = testy.ClassDef("{.debug?}Rendered in 3 seconds{.end}")
    self.verify.Expansion(t, {'debug': True}, 'Rendered in 3 seconds')
    self.verify.Expansion(t, {'debug': False}, '')

  @testy.no_verify('java', 'php')
  def testTestPredicate(self):
    # Test the predicate that tests for attributes
    t = testy.ClassDef("{.if test debug}Rendered in 3 seconds{.end}")
    self.verify.Expansion(t, {'debug': True}, 'Rendered in 3 seconds')
    self.verify.Expansion(t, {'debug': False}, '')

    # Make a nested test
    t = testy.ClassDef("{.if test meta.debug}Rendered in 3 seconds{.end}")
    self.verify.Expansion(t, {'meta': {'debug': True}}, 'Rendered in 3 seconds')
    self.verify.Expansion(t, {'meta': {'debug': False}}, '')

    # No argument
    t = testy.ClassDef("{.if test}Rendered in 3 seconds{.end}")
    self.verify.EvaluationError(jsontemplate.EvaluationError, t, {})

  @testy.no_verify('java', 'php')
  def testTestPredicateChained(self):
    # If you have more than one attribute to test, just use the "longhand"
    # format.
    t = testy.ClassDef(B("""
        {.if test debug}
          DEBUG
        {.or test release}
          RELEASE
        {.or}
          NONE
        {.end}
        """))
    self.verify.Expansion(t, {'debug': True}, '  DEBUG\n')
    self.verify.Expansion(t, {'release': True}, '  RELEASE\n')
    self.verify.Expansion(t, {}, '  NONE\n')


class DocumentationTest(testy.Test):
  """Test cases added for the sake of documentation."""

  # TODO: The default labels for this test should be 'documentation'
  LABELS = ['multilanguage']

  @testy.labels('documentation')
  def testSearchResultsExample(self):
    # TODO: Come up with a better search results example
    return

  @testy.labels('documentation', 'live-js', 'blog-format')
  def testTableExample(self):
    t = testy.ClassDef("""\
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

    self.verify.Expansion(t, d, expected, ignore_all_whitespace=True)


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
          'java-launcher', default=default_java,
          help='Location of the Java launcher to run Java tests'),
      params.OptionalString(
          'php-launcher', default='php',
          help='Location of the PHP launcher to run PHP tests'),
      params.OptionalString(
          'lua-launcher', default='lua.bat',  # I have a batch file that points
          help='Location of the standlone Lua interpreter'),

      # Until we have better test filtering:
      params.OptionalBoolean('python', help='Run Python tests'),
      params.OptionalBoolean('java', help='Run Java tests'),
      params.OptionalBoolean('php', help='Run PHP tests'),
      params.OptionalBoolean('javascript', help='Run JavaScript tests'),
      params.OptionalBoolean('lua', help='Run Lua tests'),

      params.OptionalString(
          'browser-test-out-dir', shortcut='b',
          help='Write browser tests to this directory'),

      params.OptionalString(
          'doc-output-dir', shortcut='d',
          help='Write generated docs to this directory'),

      params.OptionalBoolean('all-tests', help='Run all tests'),
      ]

  options = cmdapp.ParseArgv(argv, run_params)

  int_py_verifier = python_verifier.InternalTemplateVerifier()

  python_impl = os.path.join(this_dir, 'python', 'expand.py')
  py_verifier = python_verifier.ExternalVerifier(python_impl)

  js_impl = os.path.join(this_dir, 'javascript', 'json-template.js')
  # This assumes that you have the pan repository checked out
  helpers = os.path.join(
      this_dir, '..', '..', 'svn', 'pan', 'trunk', 'pan', 'javascript',
      'test_helpers.js')

  if sys.platform == 'win32':
    js_verifier = javascript_verifier.CScriptVerifier(js_impl, helpers)
  else:
    js_verifier = javascript_verifier.V8ShellVerifier(
        options.v8_shell, js_impl, helpers)

  java_impl = os.path.join(this_dir, 'java', 'jsontemplate.jar')
  java_test_classes = os.path.join(this_dir, 'java', 'jsontemplate_test.jar')
  jv_verifier = java_verifier.JavaVerifier(
      options.java_launcher, java_impl, java_test_classes)

  php_impl = os.path.join(this_dir, 'php', 'jsontemplate_cmd.php')
  ph_verifier = php_verifier.PhpVerifier(options.php_launcher, php_impl)

  lua_dir = os.path.join(this_dir, 'lua')
  lu_verifier = lua_verifier.LuaVerifier(options.lua_launcher, lua_dir)

  filt = testy.MakeTestClassFilter(
      label='multilanguage', regex=options.test_regex)
  multi_tests = testy.GetTestClasses(__import__(__name__), filt)

  internal_tests = [m(int_py_verifier) for m in multi_tests]

  # External versions
  if options.all_tests:
    tests = internal_tests
    tests.extend(m(py_verifier) for m in multi_tests)
    tests.extend(m(js_verifier) for m in multi_tests)
    tests.extend(m(jv_verifier) for m in multi_tests)
    tests.extend(m(ph_verifier) for m in multi_tests)
    tests.extend(m(lu_verifier) for m in multi_tests)

  elif options.python:
    tests = [m(py_verifier) for m in multi_tests]

  elif options.javascript:
    tests = [m(js_verifier) for m in multi_tests]

  elif options.java:
    tests = [m(jv_verifier) for m in multi_tests]

  elif options.php:
    tests = [m(ph_verifier) for m in multi_tests]

  elif options.lua:
    tests = [m(lu_verifier) for m in multi_tests]

  elif options.doc_output_dir:
    # Generates the HTML fragments.

    docgen = doc_generator.DocGenerator(options.doc_output_dir)

    # Run the internal tests before generating docs.
    tests = []
    tests.extend(m(int_py_verifier) for m in multi_tests)
    tests.extend(m(docgen) for m in multi_tests)

    tests.extend([
        DocumentationTest(int_py_verifier), DocumentationTest(docgen),
        ])

  elif options.browser_test_out_dir:
    testgen = browser_tests.TestGenerator()

    # Run the internal tests before generating browser tests.
    tests = []
    tests.extend(m(int_py_verifier) for m in multi_tests)
    tests.extend(m(testgen) for m in multi_tests)

  else:
    tests = internal_tests

  testy.RunTests(tests, options)

  # Write HTML *after* running all tests
  if options.browser_test_out_dir:
    testgen.WriteHtml(options.browser_test_out_dir)


if __name__ == '__main__':
  main(sys.argv[1:])
