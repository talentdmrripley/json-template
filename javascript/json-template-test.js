// Standalone tests for the JavaScript version

jsUnity.log = print;  // From cscript-shell

var module = function() {

// Data for multiple tests
var foo = function(value) { return 'foo'; };

var FunctionsApiTest  = {
  suiteName: "FunctionsApiTest",

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

  testSimpleRegistryLookup: function () {
    var s = new jsontemplate.SimpleRegistry({'foo': foo});
    var actual = s.Lookup('foo');
    jsUnity.assertions.assertEqual(actual[0], foo);
  },

  testCallableRegistryLookup: function () {
    var s = new jsontemplate.CallableRegistry(
        function(user_str) { return foo; });
    var actual = s.Lookup('anything');
    jsUnity.assertions.assertEqual(actual[0], foo);
  },

  testChainedRegistryLookup: function () {
    var bar = function(value) {return 'bar';};
    var simple = new jsontemplate.SimpleRegistry({'foo': foo});
    var callable = new jsontemplate.CallableRegistry(
        function(user_str) { return bar; });

    var chained = new jsontemplate.ChainedRegistry([simple, callable]);
    var actual = chained.Lookup('foo');
    jsUnity.assertions.assertEqual(actual[0], foo);

    actual = chained.Lookup('anything');
    jsUnity.assertions.assertEqual(actual[0], bar);
  }

};

jsUnity.run(FunctionsApiTest);

}();
