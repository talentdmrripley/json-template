// log_element: An element you can 'append' to
// tests: An object which holds methods starting with 'test'

var testy = function(tests, log_element) {
  return {
    verifyEqual: function (left, right) {

    },

    runTests: function () {
      document.write('hello there');
      this.log(tests.length);
    },

    log: function (msg) {
      log_element.append(msg + '<br>\n');
    }

  };
}
