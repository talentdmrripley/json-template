// Read code from stdin

var lines = [];
while (!WScript.Stdin.AtEndOfStream) {
  var line = WScript.StdIn.ReadLine();
  lines.push(line + '\n');
}

var code = lines.join("");

//var code = "WScript.Echo('code');"

//WScript.Echo(code);

// Execute the code
WScript.Stdout.WriteLine(eval(code));
