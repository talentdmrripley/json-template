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

"""Python implementation of json-template.

Exports:
  class Template 
  function expand

Exceptions:
  All exceptions have the base class Error.
"""

__author__ = 'Andy Chu'


import cStringIO
import pprint
import re
import sys

# For formatters
import cgi  # cgi.escape
import urllib  # for urllib.encode


class Error(Exception):
  pass


class CompilationError(Error):
  """Base class for errors that happen during the compilation stage."""


class EvaluationError(Error):
  """Base class for errors that happen when expanding the template.

  That is, this class of errors generally involve the data dictionary or the
  execution of the formatters.
  """
  def __init__(self, msg, original_exception=None):
    Error.__init__(self, msg)
    self.original_exception = original_exception


class BadFormatter(CompilationError):
  """
  Raised when a bad formatter is specified, e.g. [variable|BAD]
  """

class ConfigurationError(CompilationError):
  """Bad metacharacters."""


class TemplateSyntaxError(CompilationError):
  """Syntax error in the template text."""


class UndefinedVariable(EvaluationError):
  """
  Raised when evaluating a template that contains variable not defined by the
  data dictionary.
  """


def PythonFormat(format_str):
  """Use Python % format strings as template format specifiers."""
  # A little hack for now
  if format_str.startswith('%'):
    return lambda value: format_str % value
  else:
    return None


_SECTION_RE = re.compile(r'(repeated)?\s*(section)\s+(\S+)')

_token_re_cache = {}

def _MakeTokenRegex(meta_left, meta_right):
  key = meta_left, meta_right
  if key not in _token_re_cache:
    # Need () for re.split
    _token_re_cache[key] = re.compile(
        r'(' +
        re.escape(meta_left) +
        # For simplicity, we allow all characters except newlines inside
        # metacharacters ({} / [])
        r'.+?' +
        re.escape(meta_right) +
        # Some declarations also include the newline at the end -- that is, we
        # don't expand the newline in that case
        r'\n?)')
  return _token_re_cache[key]


class _ProgramBuilder(object):

  def __init__(self, more_formatters):
    """
    Args:
      more_formatters: A function which returns a function to apply to the
          value, given a format string.  It can return None, in which case the
          DEFAULT_FORMATTERS dictionary is consulted.
    """
    self.current_block = _StatementBlock()
    self.stack = [self.current_block]
    self.more_formatters = more_formatters

  def Append(self, statement):
    """
    Args:
      statement: Append a literal
    """
    self.current_block.Append(statement)

  def _GetFormatter(self, format_str):
    """The user's formatters are consulted first, then the default
    formatters."""
    formatter = (
        self.more_formatters(format_str) or DEFAULT_FORMATTERS.get(format_str))

    if formatter:
      return formatter
    else:
      raise BadFormatter('%r is not a valid formatter' % format_str)

  def AppendSubstitution(self, name, formatters):
    formatters = [self._GetFormatter(f) for f in formatters]
    self.current_block.Append((_DoSubstitute, (name, formatters)))

  def NewSection(self, repeated, section_name):
    """
    For sections or repeated sections.
    """
    new_block = _StatementBlock(section_name)
    if repeated:
      func = _DoRepeatedSection
    else:
      func = _DoSection

    self.current_block.Append((func, new_block))
    self.stack.append(new_block)
    self.current_block = new_block

  def NewClause(self, name):
    # TODO: Raise errors if the clause isn't appropriate for the current block
    # isn't a 'repeated section' (e.g. alternates with in a non-repeated
    # section)
    self.current_block.NewClause(name)

  def EndSection(self):
    self.stack.pop()
    self.current_block = self.stack[-1]

  def Root(self):
    # It's assumed that we call this at the end of the program
    return self.current_block


class _StatementBlock(object):

  def __init__(self, section_name=None):
    """
    Args:
      section_name: name given as an argument to the section
    """
    self.section_name = section_name

    # Pairs of func, args, or a literal string
    self.current_clause = []
    self.statements = {'default': self.current_clause}

  def __repr__(self):
    return '<Block %s>' % self.section_name

  def Statements(self, clause='default'):
    return self.statements.get(clause, [])

  def NewClause(self, clause_name):
    new_clause = []
    self.statements[clause_name] = new_clause
    self.current_clause = new_clause

  def Append(self, statement):
    """Append a statement to this block."""
    self.current_clause.append(statement)


class _ScopedContext(object):
  """Allows scoped lookup of variables.

  If the variable isn't in the current context, then we search up the stack.
  """

  def __init__(self, context):
    self.stack = [context]
    
  def PushSection(self, name):
    new_context = self.stack[-1].get(name)
    self.stack.append(new_context)
    return new_context

  def Pop(self):
    self.stack.pop()

  def CursorValue(self):
    return self.stack[-1]

  def __iter__(self):
    """Assumes that the top of the stack is a list."""

    # The top of the stack is always the current context.
    self.stack.append(None)
    for item in self.stack[-2]:
      self.stack[-1] = item
      yield item
    self.stack.pop()

  def Lookup(self, name):
    """
    Get the value associated with a name in the current context.  The current
    context could be an dictionary in a list, or a dictionary outside a list.
    """
    i = len(self.stack) - 1
    while 1:
      context = self.stack[i]

      if type(context) is not dict:  # Can't look up names in a list or atom
        i -= 1
      else:
        value = context.get(name)
        if value is None:  # A key of None or a missing key are treated the same
          i -= 1
        else:
          return value

      if i <= -1:  # Couldn't find it anywhere
        raise UndefinedVariable('%r is not defined' % name)


def _ToString(x):
  if type(x) in (str, unicode):
    return x
  else:
    return pprint.pformat(x)

# See http://google-ctemplate.googlecode.com/svn/trunk/doc/howto.html for more
# escape types.
#
# This is a *public* constant, so that callers can use it construct their own
# formatter lookup dictionaries, and pass them in to Template.
DEFAULT_FORMATTERS = {
    'html': cgi.escape,
    'htmltag': lambda x: cgi.escape(x, quote=True),
    'raw': lambda x: x,
    # Used for the length of a list.  Can be used for the size of a dictionary
    # too, though I haven't run into that use case.
    'size': lambda value: str(len(value)),
    'url-params': urllib.urlencode,  # param is a dictionary
    # The default formatter, when no other default is specifier.  For debugging,
    # this could be lambda x: json.dumps(x, indent=2), but here we want to be
    # compatible to Python 2.4.
    'str': _ToString,
    }


def ParseTemplate(
    template_str, builder, meta='{}', format_char='|', default_formatter='str'):
  """
  Args:
    template_str: The template string.  It should not have any compilation
        options in the header -- those are parsed by FromString/FromFile.
    builder: Something with the interface of _ProgramBuilder
    meta: metacharacters to use.
    default_formatter: The formatter to use if none is specified in the
        template.  The 'str' formatter is the default default -- it just tries
        to convert the context value to a string in some unspecified manner.

  This function is public so it can be used by other tools, e.g. a syntax
  checking tool run before submitting a template to source control.
  """

  # Split the metacharacters
  n = len(meta)
  if n % 2 == 1:
    raise ConfigurationError(
        '%r has an odd number of metacharacters' % meta)
  meta_left = meta[:n/2]
  meta_right = meta[n/2:]

  # : is meant to look like Python 3000 formatting {foo:.3f}.  According to
  # PEP 3101, that's also what .NET uses.
  # | is more readable, but, more importantly, reminiscent of pipes, which is
  # useful for multiple formatters, e.g. {name|js-string|html}
  if format_char not in (':', '|'):
    raise ConfigurationError(
        'Only format characters : and | are accepted (got %r)' % format_char)

  # Need () for re.split
  token_re = _MakeTokenRegex(meta_left, meta_right)
  tokens = token_re.split(template_str)

  # If we go to -1, then we got too many {end}.  If end at 1, then we're missing
  # an {end}.
  balance_counter = 0

  for i, token in enumerate(tokens):

    # By the definition of re.split, even tokens are literal strings, and odd
    # tokens are directives.
    if i % 2 == 0:
      # A literal string
      if token:
        builder.Append(token)

    else:
      had_newline = False
      if token.endswith('\n'):
        token = token[:-1]
        had_newline = True

      assert token.startswith(meta_left), token
      assert token.endswith(meta_right), token

      token = token[len(meta_left) : -len(meta_right)]

      # It's a comment
      if token.startswith('#'):
        continue  

      # It's a "keyword" directive
      if token.startswith('.'):
        token = token[1:]

        literal = {
            'meta-left': meta_left,
            'meta-right': meta_right,
            'space': ' ',
            }.get(token)

        if literal is not None:
          builder.Append(literal)
          continue

        match = _SECTION_RE.match(token)

        if match:
          repeated, _, section_name = match.groups()
          builder.NewSection(repeated, section_name)
          balance_counter += 1
          continue

        if token in ('or', 'alternates with'):
          builder.NewClause(token)
          continue

        if token == 'end':
          balance_counter -= 1
          if balance_counter < 0:
            # TODO: Show some context for errors
            raise TemplateSyntaxError(
                'Got too many %send%s statements.  You may have mistyped an '
                "earlier 'section' or 'repeated section' directive."
                % (meta_left, meta_right))
          builder.EndSection()
          continue

      # Now we know the directive is a substitution.
      parts = token.split(format_char)
      if len(parts) == 1:
        # If no formatter is specified, the default is the 'str' formatter,
        # which the user can define however they desire.
        name = token
        formatters = [default_formatter]
      else:
        name = parts[0]
        formatters = parts[1:]

      builder.AppendSubstitution(name, formatters)
      if had_newline:
        builder.Append('\n')

  if balance_counter != 0:
    raise TemplateSyntaxError('Got too few %send%s statements' %
        (meta_left, meta_right))

  return builder.Root()


def FromString(s, _constructor=None):
  f = cStringIO.StringIO(s)
  return FromFile(f, _constructor=_constructor)


def FromFile(f, _constructor=None):
  """Parse a template from a file, using a simple file format.
  
  This is useful when you want to include template options in a file, rather
  than in source code.

  The first lines of the file can specify template options, such as the
  metacharacters to use.  One blank line must separate the options from the
  template body.

  Args:
    f: A file handle to read from.  Caller is responsible for closing it.
  """
  _constructor = _constructor or Template

  options = {}

  # Parse lines until the first one that doesn't look like an option
  while 1:
    line = f.readline()
    match = Template._OPTION_RE.match(line)
    if match:
      name, value = match.group(1), match.group(2)
      if name in Template._OPTION_NAMES:
        options[name.replace('-', '_')] = value.strip()
      else:
        break
    else:
      break

  if options:
    if line.strip():
      raise CompilationError(
          'Must be one blank line between template options and body (got %r)'
          % line)
    body = f.read()
  else:
    # There were no options, so no blank line is necessary.
    body = line + f.read()

  return _constructor(body, **options)


class Template(object):
  """
  Don't go crazy with metacharacters.  {}, [], or <> (in order of preference)
  should cover nearly any circumstance, e.g. generating HTML, XML, JavaScript, C
  programs, text files, etc.

  How this works:
    Like many template systems, the template string is compiled into a program,
    and then it can be expanded any number of times.  For a web server, this
    makes it easy to compile the templates once at server startup, and have fast
    expansion for request handling.

  TODO: more docs.
  """

  def __init__(
      self, template_str, builder=None, more_formatters=lambda x: None,
      **compile_options):
    """
    See ParseTemplate for options.
    """
    builder = builder or _ProgramBuilder(more_formatters)
    self._program = ParseTemplate(template_str, builder, **compile_options)

  _OPTION_RE = re.compile(r'^([a-zA-Z\-]+)\s+(.*)')
  # TODO: whitespace mode, etc.
  _OPTION_NAMES = ['meta', 'format-char', 'default-formatter']

  #
  # Public API
  #

  def render(self, data_dict, callback):
    """Calls a callback with each expanded token."""
    _Execute(self._program.Statements(), _ScopedContext(data_dict), callback)

  def expand(self, data_dict, encoding='utf-8'):
    """Returns a string.

    By default we encode as utf-8.  If you want a raw unicode instance back,
    then that's easy to assemble with get with tokenstream()/render().
    """
    tokens = []
    self.render(data_dict, tokens.append)
    return ''.join(t.encode(encoding) for t in tokens)

  def tokenstream(self, data_dict):
    """Yields a list of tokens resulting from expansion.

    This may be useful for WSGI apps.

    NOTE: This is a generator, but JavaScript doesn't have generators.
    """
    tokens = []
    self.render(data_dict, tokens.append)
    for token in tokens:
      yield token



def _DoRepeatedSection(args, context, callback):
  """[repeated section foo]"""

  block = args

  if block.section_name == '@': 
    # If the name is @, we stay in the enclosing context, but assume it's a
    # list, and repeat this block many times.
    items = context.CursorValue()
    if type(items) is not list:
      raise EvaluationError('Expected a list; got %s' % type(items))
    pushed = False
  else:
    items = context.PushSection(block.section_name)
    pushed = True

  # TODO: what if items is a dictionary?

  if items:
    last_index = len(items) - 1
    statements = block.Statements()
    alt_statements = block.Statements('alternates with')
    # NOTE: Iteration mutates the context!
    for i, _ in enumerate(context):
      # Execute the statements in the block for every item in the list.  Execute
      # the alternate block on every iteration except the last.
      # Each item could be an atom (string, integer, etc.) or a dictionary.
      _Execute(statements, context, callback)
      if i != last_index:
        _Execute(alt_statements, context, callback)

  else:
    _Execute(block.Statements('or'), context, callback)

  if pushed:
    context.Pop()


def _DoSection(args, context, callback):
  """[section foo]"""

  block = args
  # If a section isn't present in the dictionary, or is None, then don't show it
  # at all.
  if context.PushSection(block.section_name):
    _Execute(block.Statements(), context, callback)
    context.Pop()
  else:  # Empty list, None, False, etc.
    context.Pop()
    _Execute(block.Statements('or'), context, callback)


def _DoSubstitute(args, context, callback):
  name, formatters = args

  # So we can have {.section is_new}new since {@}{.end}.  Hopefully this idiom
  # is OK.
  if name == '@':
    value = context.CursorValue()
  else:
    try:
      value = context.Lookup(name)
    except TypeError, e:
      raise EvaluationError(
          'Error evaluating %r in context %r: %r' % (name, context, e))

  for f in formatters:
    try:
      value = f(value)
    except KeyboardInterrupt:
      raise
    except Exception, e:
      raise EvaluationError(
          'Formatting value %r with formatter %s raised exception: %r' %
          (value, formatters, e), original_exception=e)

  # TODO: Require a string/unicode instance here?
  if value is None:
    raise EvaluationError('Evaluating %r gave None value' % name)
  callback(value)

  
def _Execute(statements, context, callback):
  """This is recursively called."""
  for statement in statements:
    if isinstance(statement, str):
      callback(statement)
    else:
      # In the case of a substitution, args is a pair (name, formatter).
      # In the case of a section, it's a _StatementBlock instance.
      func, args = statement
      func(args, context, callback)


def expand(template_str, dictionary, encoding='utf-8', **kwargs):
  """Expands a template string with a data dictionary.

  This is useful for cases where you don't care about saving the result of
  compilation (similar to re.match('.*', s) vs DOT_STAR.match(s))
  """
  t = Template(template_str, **kwargs)
  return t.expand(dictionary, encoding=encoding)
