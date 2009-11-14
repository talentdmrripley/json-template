// Standalone tests for the JavaScript version

jsUnity.log = print;  // From cscript-shell

var module = function() {

// Data for multiple tests
var foo = function(value) { return 'foo'; };

var FunctionsApiTest  = {
  suiteName: 'FunctionsApiTest',

  testMoreFormattersAsFunction: function () {

    formatters = function(user_str) {
      if (user_str == 'lower') {
        return function (s) { return s.toLowerCase(); };
      } else if (user_str == 'upper') {
        return function (s) { return s.toUpperCase(); };
      } else {
        return null;
      }
    };

    var t = jsontemplate.Template(
        'Hello {name|lower} {name|upper}',
        {more_formatters: formatters});

    var actual = t.expand({'name': 'World'});
    jsUnity.assertions.assertEqual(actual, 'Hello world WORLD');
  },

  testMoreFormattersAsObject: function () {
    // TODO: Make this work
    formatters = {
        'lower': function (s) { return s.toLowerCase(); },
        'upper': function (s) { return s.toUpperCase(); }
        };

    var t = jsontemplate.Template(
        'Hello {name|lower} {name|upper}',
        {more_formatters: formatters});

    var actual = t.expand({'name': 'World'});
    jsUnity.assertions.assertEqual(actual, 'Hello world WORLD');
  },

  testMoreFormattersAsClass: function () {
    var MyFormatters = function() {
      return {
        lookup: function(user_str) {
          var func;
          if (user_str == 'lower') {
            func = function (s) { return s.toLowerCase(); };
          } else if (user_str == 'upper') {
            func = function (s) { return s.toUpperCase(); };
          } else {
            func = null;
          }
          return [func, null];
        }
      };
    };
    var formatters = MyFormatters();

    var t = jsontemplate.Template(
        'Hello {name|lower} {name|upper}', {more_formatters: formatters});

    var actual = t.expand({'name': 'World'});
    jsUnity.assertions.assertEqual(actual, 'Hello world WORLD');
  },

  testSimpleRegistryLookup: function () {
    var s = new jsontemplate.SimpleRegistry({'foo': foo});
    var actual = s.lookup('foo');
    jsUnity.assertions.assertEqual(actual[0], foo);
  },

  testCallableRegistryLookup: function () {
    var s = new jsontemplate.CallableRegistry(
        function(user_str) { return foo; });
    var actual = s.lookup('anything');
    jsUnity.assertions.assertEqual(actual[0], foo);
  },

  testChainedRegistryLookup: function () {
    var bar = function(value) {return 'bar';};
    var simple = new jsontemplate.SimpleRegistry({'foo': foo});
    var callable = new jsontemplate.CallableRegistry(
        function(user_str) { return bar; });

    var chained = new jsontemplate.ChainedRegistry([simple, callable]);
    var actual = chained.lookup('foo');
    jsUnity.assertions.assertEqual(actual[0], foo);

    actual = chained.lookup('anything');
    jsUnity.assertions.assertEqual(actual[0], bar);
  }

};

var FromStringTest = {
  suiteName: 'FromString',

  testGoodTemplate: function () {
    var t = jsontemplate.fromString(
        'meta: [] \n' +
        'format-char: : \n' +
        'default-formatter: html \n' +
        'undefined-str: UNDEF \n' +
        '\n' +
        'foo [foo:html] [foo] [junk]\n');
    jsUnity.assertions.assertEqual(
        t.expand({'foo': '<a>'}), 'foo &lt;a&gt; &lt;a&gt; UNDEF\n');
  },

  testOptionsArgument: function () {
    var t = jsontemplate.fromString(
        'meta: [] \n' +
        '\n' +
        'foo [var|html] [var|foo]\n',
        {more_formatters: {'foo': foo}});  // Custom formatters
    jsUnity.assertions.assertEqual(
        t.expand({'var': '<a>'}), 'foo &lt;a&gt; foo\n');
  },

  testOptionsWithEmptyTemplate: function () {
    var t = jsontemplate.fromString('meta: []\n');
    jsUnity.assertions.assertEqual(
        t.expand({'foo': '<a>'}), '');
  }
};

var SectionsTest = {
  suiteName: 'SectionsTest',

  testSection: function () {
    var s = jsontemplate._Section({section_name: "foo"});
    jsUnity.assertions.assertEqual(s.section_name, "foo");
  }
};

var results = jsUnity.run(FunctionsApiTest, FromStringTest, SectionsTest);

}();
