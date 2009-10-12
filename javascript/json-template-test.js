// Standalone tests for the JavaScript version

jsUnity.log = print;  // From cscript-shell

var results = jsUnity.run({

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
    print("---------------------------");

    var MyFormatters = function() {};
    MyFormatters.prototype = new jsontemplate.FunctionRegistry();
    print("f! " + typeof(MyFormatters));

    MyFormatters.prototype.Lookup = function(user_str) {
      var func;
      if (user_str == 'lower') {
        func = function (s) { return s.toLowerCase(); };
      } else if (user_str == 'upper') {
        func = function (s) { return s.toUpperCase(); };
      } else {
        func = null;
      }
      return [func, null];
    };

    formatters = new MyFormatters();

    var t = jsontemplate.Template(
        'Hello {name|lower} {name|upper}',
        {more_formatters: formatters});

    var actual = t.expand({'name': 'World'});
    jsUnity.assertions.assertEqual(actual, 'Hello world WORLD');
  },

  testChainedRegistry: function () {
    print("TODO");
  },

  testSimpleRegistry: function () {
    var foo = function(value) {return 'foo'};
    var s = new jsontemplate.SimpleRegistry({'foo': foo});
    actual = s.Lookup('foo');
    jsUnity.assertions.assertEqual(actual[0], foo);
  }

});
