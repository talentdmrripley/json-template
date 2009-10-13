#!/usr/bin/python -S
"""reusing_the_inside.py

Example of reusing a "panel" or subcomponent across multiple pages.
"""

import cgi
import os
import sys

try:
  import jsontemplate
except ImportError:
  # For development
  sys.path.insert(0, '..')
  import jsontemplate


# This builds on reusing_the_outside.py.  Read that first if you haven't.
#
# Now let's add a *list* of user profiles to page one ...

PAGE_ONE_DATA = {
    'title': "List of profiles",
    'profiles': [
        { 'name': 'Itchy',
          'pic_url': 'http://www.anvari.org/db/cols/'
                     'The_Simpsons_Characters_Picture_Gallery/Itchy.gif',
          },
        { 'name': 'Scratchy',
          'pic_url': 'http://www.tvacres.com/images/scratchy2.jpg',
          },
        ],
    'ONE_THIRD': 1.0 / 3,  # to show how to format a floating point number.
    }

# ... and a *single* profile to page two.

PAGE_TWO_DATA = {
    'title': 'Profile page for Ralph',
    'profile': {
        'name': 'Ralph Wiggum',
        'pic_url': 'http://www.anvari.org/db/cols/'
                   'The_Simpsons_Characters_Picture_Gallery/Ralph_Wiggum.gif',
        },
    }


# Define a template for the user profile.  This is the thing we're going to
# reuse across multiple pages.
#
# (This is also an example of the FromString construction method, which allows
# compilation options in the template string itself).

USER_PROFILE_TEMPLATE = jsontemplate.FromString("""\
default-formatter: html

<center> <!-- Good old center tag -->
  <img src="{pic_url}" /><br>
  <b>
  <a href="http://google.com/search?q={name|url-param-value}">
  {name}
  </a>
  </b>
</center>
""")


# Now we define a wrapper for templates that can render user profiles.
#
# To do this, we must specify a *function* MoreFormatters that maps formatter
# names (strings in the template) to other functions (which take *JSON node*
# values and return strings to be output in the template).


def MoreFormatters(formatter_name):

  # TIP: Name formatters to be read with "as" in the middle.  They should be
  # nouns that describe what is returned:
  #
  # "itchy profile node as a user profile"
  # "name as html"
  # "query as html-attr-value"
  #
  # We want to write things as {itchy_profile|user-profile}, so:

  if formatter_name == 'user-profile':
    # We are returning a function (or more specifically a 'bound method' in
    # Python)
    #
    # Note that this function will only work on valid profiles, which are
    # dictionaries.
    return USER_PROFILE_TEMPLATE.expand

  elif formatter_name.startswith('%'):
    # This is also a function.  It allows use printf style formatting in
    # templates, e.g. '{percent|%.3f}'
    #
    # Note that this function will only work on atoms.
    return lambda x: formatter_name % x

  else:
    # We don't recognize the formatter_name, so return None.  The built-in set
    # of default formatters will now be consulted.
    return None


# Wrapper for templates that can use the |user-profile formatter

def TemplateThatCanRenderProfiles(template_str):
  return jsontemplate.Template(
      template_str, more_formatters=MoreFormatters, default_formatter='html')


# On page one, we show a table where each cell is a user profile.  Things to
# note:
#
# 1. If profiles is [], then the <table></table> tags aren't shown at all, which
# is what you want.
#
# 2. The @ symbol means the *cursor*.  
#    a. '.section profiles' puts the cursor in the "profiles" node.
#    b. '.repeated section @' means repeat over the current node, which is
#    "profiles".
#    c. Now we are in a repeated section, and the cursor traverses over the
#    individual items in the JSON array.
#
# 3. We are formatting the cursor values in the repeated section (which are
# dictionaries in this case) as a user profile.

PAGE_ONE_TEMPLATE = TemplateThatCanRenderProfiles("""\
<b>{title}</b>

{.section profiles}
  <table border=1 width="100%"><tr>
  {.repeated section @}
    <td>{@|user-profile}</td>
  {.end}
  </tr></table>
{.end}


<!-- You don't need to read this part yet -->

<p>
OK that worked well.  We have multiple profiles on the page, without mentioning
the details of how format profiles in the template for this page.  That logic is
<b>encapsulated</b> in its own template and can be <b>reused</b> across multiple
pages.  </p>

<p>Oh yeah, and to demonstrate that we also enabled <code>printf</code>-style
formatting in <code>MoreFormatters</code>, here we format the variable
<code>ONE_THIRD</code> to two significant places, using the syntax
<code>{.meta-left}ONE_THIRD|%.2f{.meta-right}</code>:
</p>
<p>
<b>{ONE_THIRD|%.2f}</b>.
</p>

<p>
Easy.
</p>
""")

# Now on page two, we just show the profile itself, along with the *literal
# HTML* of the profile, "for debugging purposes".  This demonstrates *chaining*
# of formatters.
#
# Can be read: "the profile formatted as a user profile, as escaped HTML"

PAGE_TWO_TEMPLATE = TemplateThatCanRenderProfiles("""\
{profile|user-profile}

<p>Here is the HTML for the profile above:</p>

<pre>{profile|user-profile|html}</pre>
""")


# The same HTML template from reusing_the_outside.py.

HTML_TEMPLATE = jsontemplate.Template("""
<html>
  <head>
    <title>{title}</title>
  </head>
  <body>{body|raw}</body>
</html>
""", default_formatter='html')


# Same site as last time.
#
# Now go back to the 'Design Minimalism' blog post (linked from
# http://code.google.com/p/json-template/).

def Site(path_info):
  """Returns an HTML page."""

  if path_info == '/one':
    body = PAGE_ONE_TEMPLATE.expand(PAGE_ONE_DATA)
    title = PAGE_ONE_DATA['title']
  elif path_info == '/two':
    body = PAGE_TWO_TEMPLATE.expand(PAGE_TWO_DATA)
    title = PAGE_TWO_DATA['title']
  else:
    # Note: Request it with trailing slash: cgi-bin/reusing_the_inside.py/
    body = """
    <p><a href="one">List of Profiles</a> <a href="two">Single Profile</a></p>
    <p>(<b>View Source</b> to see that both are using the same HTML for the
    profile)</p>
    """
    title = 'Index'

  return HTML_TEMPLATE.expand({'body': body, 'title': title})


def main():
  """Returns an exit code."""

  print 'Content-Type: text/html'
  print
  print Site(os.getenv('PATH_INFO'))


if __name__ == '__main__':
  main()
