// Standalone tests for the JavaScript version

jsUnity.log = print;  // From cscript-shell

var results = jsUnity.run({
  // for fixing bug
  testNoOptions: function () {
    var t = jsontemplate.Template('Hello {name}');
    var actual = t.expand({'name': 'World'});
    jsUnity.assertions.assertEqual(actual, 'Hello World');
  }
})
