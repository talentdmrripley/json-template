-- Command line program called by verifier.py

json = require "Json"
jsontemplate = require "json-template"

o = json.Decode('{"a": 3}')
print(o)
print(o.a)

o = jsontemplate.Template('{foo}')
print(o)
