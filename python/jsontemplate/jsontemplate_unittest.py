#!/usr/bin/python -S
"""
jsontemplate_unittest.py
"""

__author__ = 'Andy Chu'


import os
import sys
try:
  import json
except ImportError:
  import simplejson as json

if __name__ == '__main__':
  # for jsontemplate and pan, respectively
  sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
  sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import taste
from taste import util

# We need access to the internals here
from jsontemplate import _jsontemplate as jsontemplate
import verifier as python_verifier

B = util.BlockStr


class TokenizeTest(taste.Test):

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

  def testTokenRegexIgnoresCode(self):
    # Special case:
    s = jsontemplate.expand('{foo}', {'foo': 'bar'})
    self.verify.Equal('bar', s)

    s = jsontemplate.expand('{.repeated section foo}{@}{.end}',
                            {'foo': ['a', 'b', 'c']})
    self.verify.Equal('abc', s)

    # This didn't used to work because the variable would be " foo" and it would
    # be undefined.  Now we just let it pass through as literal text.
    s = jsontemplate.expand('{ foo}', {'foo': 'bar'})
    self.verify.Equal('{ foo}', s)

    s = jsontemplate.expand('function() { return {@}; }', 1)
    self.verify.Equal('function() { return 1; }', s)

    s = jsontemplate.expand('function() { return {@};', 1)
    self.verify.Equal('function() { return 1;', s)

    # If you have an {.end} you'll get a different error because it'll be
    # unmatched
    s = jsontemplate.expand('{ .repeated section foo}',
                            {'foo': ['a', 'b', 'c']})
    self.verify.Equal('{ .repeated section foo}', s)  # ignored

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


class FromStringTest(taste.Test):

  def testEmpty(self):
    s = """\
Format-Char: |
Meta: <>
"""
    t = jsontemplate.FromString(s, _constructor=taste.ClassDef)
    self.verify.Equal(t.args[0], '')
    self.verify.Equal(t.kwargs['meta'], '<>')
    self.verify.Equal(t.kwargs['format_char'], '|')

    # Empty template
    t = jsontemplate.FromString('', _constructor=taste.ClassDef)
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
    t = jsontemplate.FromString(f, _constructor=taste.ClassDef)
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
    # strings.  (This is why we use StringIO instead of cStringIO).
    t = jsontemplate.FromString(u'\u00FF')
    self.verify.Equal(t.expand({}), u'\u00FF')

    t = jsontemplate.FromString(u'\uFF00')
    self.verify.Equal(t.expand({}), u'\uFF00')


class ScopedContextTest(taste.Test):

  def testScopedContext(self):
    data = {'foo': [1,2,3]}
    s = jsontemplate._ScopedContext(data, '')
    self.verify.Equal(s.Lookup('@'), data)
    self.verify.Equal(s.Lookup('foo'), data['foo'])
    self.verify.Equal(s.Lookup('@'), data)

    print s.PushSection('foo', [])
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


class InternalTemplateTest(taste.Test):
  """Tests that can only be run internally."""

  VERIFIERS = [python_verifier.InternalTemplateVerifier]

  def testNumberWithDefaultHtmlFormatter(self):

    # For now, integers can't be formatted directly as html.  Just omit the
    # formatter.
    t = jsontemplate.FromString(
        B("""
        default-formatter: html
        
        There are {num} ways to do it
        """))
    self.verify.Equal('There are 5 ways to do it\n', t.expand({'num': 5L}))

  def testMultipleFormatters(self):
    # TODO: This could have a version in the external test too, just not with
    # 'url-params', which is not the same across platforms because of dictionary
    # iteration order

    # Single formatter
    t = taste.ClassDef(
        'http://example.com?{params:url-params}',
        format_char=':')
    self.verify.Expansion(
        t,
        {'params': {'foo': 1, 'bar': 'String with spaces', 'baz': '!@#$%^&*('}},
        'http://example.com?baz=%21%40%23%24%25%5E%26%2A%28&foo=1&bar=String+with+spaces')

    # Multiple
    t = taste.ClassDef(
        'http://example.com?{params | url-params | html}',
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

    t = taste.ClassDef('{@}', more_formatters=_More)
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

  def testExecute(self):
    """Test the .execute() method."""

    t = jsontemplate.Template('Hello {name}')
    tokens = []
    t.execute({'name': 'World'}, tokens.append)
    self.verify.In('Hello ', tokens)

    tokens = []
    # Legacy alias for execute()
    t.render({'name': 'World'}, tokens.append)
    self.verify.In('Hello ', tokens)

  def testTemplateTrace(self):
    trace = jsontemplate.Trace()
    t = jsontemplate.Template('Hello {name}')
    t.expand({'name': 'World'}, trace=trace)
    self.verify.Equal(trace.exec_depth, 1)

  def testSimpleUnicodeSubstitution(self):
    t = jsontemplate.Template(u'Hello {name}')

    self.verify.Equal(t.expand({u'name': u'World'}), u'Hello World')

  def testUnicodeTemplateMixed(self):
    # Unicode template
    t = jsontemplate.Template(u'Hello {name}')

    # Encoded utf-8 data is OK
    self.verify.Equal(t.expand({u'name': '\xc2\xb5'}), u'Hello \xb5')

    # Latin-1 data is not OK
    self.verify.Raises(UnicodeDecodeError, t.expand, {u'name': '\xb5'})

    # Byte string \0 turns into code point 0
    self.verify.Equal(t.expand({u'name': '\0'}), u'Hello \u0000')

  def testByteTemplateMixed(self):

    # (Latin-1) Byte string template
    t = jsontemplate.Template('Hello \xb5 {name}')

    # Byte string OK
    self.verify.Equal(t.expand({u'name': '\xb5'}), 'Hello \xb5 \xb5')

    self.verify.Raises(UnicodeDecodeError, t.expand, {u'name': u'\u00b5'})

    # Byte string template without any special chars
    t = jsontemplate.Template('Hello {name}')
    # Unicode data is OK
    self.verify.Equal(t.expand({u'name': u'\u00b5'}), u'Hello \u00B5')

  def testRepeatedSectionFormatter(self):
    def _Columns(x):
      n = len(x)
      i = 0
      columns = []
      while True:
        columns.append(x[i:i+3])
        i += 3
        if i >= len(x):
          break
      return columns

    t = jsontemplate.Template(B("""
        {.repeated section dirs | columns}
          {.repeated section @}{@} {.end}
        {.end}
        """), more_formatters={'columns': _Columns})

    d = {'dirs': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']}
    self.verify.LongStringsEqual(B("""
          a b c 
          d e f 
          g h i 
          j 
        """),
        t.expand(d))

  def testExpandWithStyle(self):
    # TODO: REMOVE with execute_with_style_LEGACY
    data = {
        'title': 'Greetings!',
        'body': {'names': ['andy', 'bob']},
        }
    body_template = jsontemplate.Template(B("""
        {.repeated section names}
          Hello {@}
        {.end}
        """))
    style = jsontemplate.Template(B("""
        {title}
        {.section body}{@|raw}{.end}
        """))
    result = jsontemplate.expand_with_style(body_template, style, data)
    self.verify.LongStringsEqual(B("""
        Greetings!
          Hello andy
          Hello bob
        
        """), result)
    self.verify.Raises(
        jsontemplate.EvaluationError,
        jsontemplate.expand_with_style, body_template, style, data, 'foo')

    # New style with old API
    body_template = jsontemplate.Template(B("""
        {.define TITLE}
        Definition of '{word}'
        {.end}

        {.define BODY}
          <h3>{.template TITLE}</h3>
          {definition}
        {.end}
        """))

    style = jsontemplate.Template(B("""
        <title>{.template TITLE}</title>
        <body>
        {.template BODY}
        </body>
        """))
    data = {
        'word': 'hello',
        'definition': 'greeting',
        }
    s = jsontemplate.expand_with_style(body_template, style, data)
    self.verify.LongStringsEqual(B("""
        <title>Definition of 'hello'
        </title>
        <body>
          <h3>Definition of 'hello'
        </h3>
          greeting
        </body>
        """), s)


class FunctionsApiTest(taste.Test):
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

    def MyFormatters(user_str):
      if user_str == 'lower':
        return lambda v: v.lower()
      elif user_str == 'upper':
        return lambda v: v.upper()
      else:
        return None

    t = jsontemplate.Template(
        'Hello {name|lower} {name|upper}', more_formatters=MyFormatters)

    self.verify.Equal(t.expand({'name': 'World'}), 'Hello world WORLD')

  def testMoreFormattersAsClass(self):

    class MyFormatters(jsontemplate.FunctionRegistry):
      def Lookup(self, user_str):
        """Returns func, args, type."""
        if user_str == 'lower':
          func = lambda v, context, args: v.lower()
        elif user_str == 'upper':
          func = lambda v, context, args: v.upper()
        else:
          func = None
        return func, None

    t = jsontemplate.Template(
        'Hello {name|lower} {name|upper}', more_formatters=MyFormatters())

    self.verify.Equal(t.expand({'name': 'World'}), 'Hello world WORLD')


class TemplateGroupTest(taste.Test):

  def testMakeTemplateGroup(self):
    child_template = jsontemplate.Template('- {@}')

    top = jsontemplate.Template(
        B("""
        Directory listing for {root}

        {.repeated section children}
          {@|template child}
        {.end}
        """))

    data = {
      'root': '/home',
      'children': [
        'bin',
        'work',
        ],
      }

    self.verify.Raises(jsontemplate.EvaluationError, top.expand, data)

    jsontemplate.MakeTemplateGroup({'child': child_template, 'top': top})

    self.verify.LongStringsEqual(
        top.expand(data),
        B("""
        Directory listing for /home
          - bin
          - work
        """))

  def testMutualRecursion(self):

    class NodePredicates(jsontemplate.FunctionRegistry):
      def Lookup(self, user_str):
        """The node type is also a predicate."""
        func = lambda v, context, args: (v['type'] == user_str)
        return func, None  # No arguments

    expr = jsontemplate.Template(
        B("""
        {.if PLUS}
        {a} + {b}
        {.or MINUS}
        {a} - {b}
        {.or MULT}
        {a} * {b}
        {.or DIV}
        {a} / {b}
        {.or FUNC}
        {@|template func}
        {.end}
        """), more_predicates=NodePredicates())

    func = jsontemplate.Template(
        B("""
        function ({.repeated section params}{@} {.end}) {
          {.repeated section exprs}
          {@|template expr}
          {.end}
        }
        """))

    jsontemplate.MakeTemplateGroup({'func': func, 'expr': expr})

    self.verify.LongStringsEqual(
        expr.expand({'type': 'PLUS', 'a': 1, 'b': 2}),
        '1 + 2\n')

    self.verify.LongStringsEqual(
        expr.expand({'type': 'FUNC', 'params': ['x'],
                     'exprs': [{'type': 'PLUS', 'a': 3, 'b': 4}]}),
        B("""
        function (x ) {
          3 + 4

        }
        """), ignore_all_whitespace=True)

  def testSelfRecursion(self):
    data = {
      'name': '/home',
      'files': ['a.txt', 'b.txt'],
      'dirs': [
        {'name': 'andy', 'files': ['1.txt', '2.txt']},
        ],
      }

    t = jsontemplate.Template(
        B("""
        {name}
        {.repeated section dirs}
          {@|template SELF}
        {.end}
        {.repeated section files}
          {@}
        {.end}
        """))

    # TODO: A nicer job with whitespace
    self.verify.LongStringsEqual(
        t.expand(data),
        B("""
        /home
        andy
        1.txt
        2.txt
        a.txt
        b.txt
        """), ignore_all_whitespace=True)

    # Now CHAIN a regular formatter with a template-formatter
    t = jsontemplate.Template(
        B("""
        {name}
        {.repeated section dirs}
          {@|template SELF|upper}
        {.end}
        {.repeated section files}
          {@}
        {.end}
        """))

    # TODO: A nicer job with whitespace
    self.verify.LongStringsEqual(
        t.expand(data),
        B("""
        /home
        ANDY
        1.TXT
        2.TXT
        a.txt
        b.txt
        """), ignore_all_whitespace=True)

  def testStyles(self):
    data = {
        'word': 'hello',
        'definition': 'greeting',
        }
    # TITLE is reused
    body_template = jsontemplate.Template(B("""
        {.define TITLE}
        Definition of '{word}'
        {.end}

        {.define BODY}
          <h3>{.template TITLE}</h3>
          {definition}
        {.end}
        """))
    style = jsontemplate.Template(B("""
        <title>{.template TITLE}</title>
        <body>
        {.template BODY}
        </body>
        """))
    s = body_template.expand(data, style=style)
    self.verify.LongStringsEqual(B("""
        <title>Definition of 'hello'
        </title>
        <body>
          <h3>Definition of 'hello'
        </h3>
          greeting
        </body>
        """), s)

    # Now do it with "strip-line"
    body_template = jsontemplate.Template(B("""
        {.OPTION strip-line}
          {.define TITLE}
            Definition of '{word}'
          {.end}
        {.END}

        {.define BODY}
          <h3>{.template TITLE}</h3>
          {definition}
        {.end}
        """))

    style = jsontemplate.Template(B("""
        <title>{.template TITLE}</title>
        <body>
        {.template BODY}
        </body>
        """))
    s = body_template.expand(data, style=style)
    self.verify.LongStringsEqual(B("""
        <title>Definition of 'hello'</title>
        <body>
          <h3>Definition of 'hello'</h3>
          greeting
        </body>
        """), s)

  def testMultipleTemplateGroups(self):
    style = jsontemplate.Template('')
    body = jsontemplate.Template('')
    jsontemplate.MakeTemplateGroup({'style': style, 'body': body})
    # Can't do it twice
    self.verify.Raises(
        jsontemplate.UsageError,
        jsontemplate.MakeTemplateGroup,
        {'style': style, 'body': body})

  def testConflictingGroups(self):
    t = jsontemplate.Template(B("""
        {.define TITLE}
        Definition of '{word}'
        {.end}

        {.define BODY}
          <h3>{.template TITLE}</h3>
          {definition}
        {.end}
        """))
    # TODO: Re-enable when Poly is updated
    #self.verify.Raises(
    #    jsontemplate.UsageError,
    #    jsontemplate.MakeTemplateGroup,
    #    {'body': t})


if __name__ == '__main__':
  taste.RunThisModule()
