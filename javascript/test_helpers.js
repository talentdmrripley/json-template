function log(msg) {
  // Multiline message break scraping
  msg = msg.replace(/\n/g, 'NEWLINE');
  print('V8LOG:', msg);
}

function repr(d) {
  var result = [];
  for (var k in d) {
    result.push('k: ' + k + ' v: ' + d[k] + '  ');
  }
  return result.join('');
}

function showArray(a) {
  var result = [];
  result.push('[');
  for (var i=0; i<a.length; i++) {
    result.push(a[i]);
    result.push(', ');
  }
  result.push(']');
  return result.join('');
}

