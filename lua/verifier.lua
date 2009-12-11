-- Command line program called by verifier.py

json = require "Json"

o = json.Decode('{"a": 3}');
print(o)
print(o.a)
