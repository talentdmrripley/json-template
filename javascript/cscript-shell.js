// define this because v8 has it
function print(msg) {
  WScript.Stdout.WriteLine(msg);
}


var lines = [];
var files = [];  // list of JS files to run


if (WScript.Arguments.length > 0) {  // program name not included
  var fs = WScript.CreateObject("Scripting.FileSystemObject");
  for (var i=0; i < WScript.Arguments.length; i++) {
    var name = WScript.Arguments(i);  // this isn't a JS array, apparently
    var f = fs.OpenTextFile(name, 1);  // 1 means reading
    while (!f.AtEndOfStream) {
      var line = f.ReadLine();
      lines.push(line + '\n');
    }
  }
} else {
  // Read code from stdin if there are no arguments
  while (!WScript.Stdin.AtEndOfStream) {
    var line = WScript.StdIn.ReadLine();
    lines.push(line + '\n');
  }
}

var code = lines.join("");

//WScript.Echo(code);

// Execute the code
WScript.Stdout.WriteLine(eval(code));
