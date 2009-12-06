// Plugins for JSON Template docs

PLUGINS.onDocPush = function(docStack) {
  if (docStack.get('filename').slice(null, 1) === 'r') {
    print('FILENAME ' + docStack.get('filename'));
    print(docStack.debugString());
  }
  var prettyBase = docStack.get('prettify-base-url');
  var newEntry = {};
  if (docStack.get('pretty')) {
    newEntry['include-js'] = [prettyBase + 'prettify.js'];
    newEntry['include-css'] = [prettyBase + 'prettify.css'];
    newEntry['onload-js'] = 'prettyPrint()';
  }
  return newEntry;
}
