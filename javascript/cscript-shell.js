WScript.Echo("hello");

var lines = [];
while (!WScript.Stdin.AtEndOfStream) {
  var line = WScript.StdIn.ReadLine();
  lines.push(line + '\n');
}


//var code = lines.join("");
var code = "WScript.Echo('code');"

//WScript.Echo(code);
WScript.Stdout.WriteLine(eval(code));
