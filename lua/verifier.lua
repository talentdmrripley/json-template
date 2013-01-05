-- Command line program called by verifier.py

json = require "Json"
jsontemplate = require "json-template"

template_str = arg[1]
data_json = arg[2]
options_json = arg[3]

data = json.Decode(data_json)
options = json.Decode(options_json)

local t = jsontemplate.Template(template_str, options)
print(t.expand(data))
