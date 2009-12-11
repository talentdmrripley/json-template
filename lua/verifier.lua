-- Command line program called by verifier.py

json = require "Json"
jsontemplate = require "json-template"


template_str = arg[1]
data_json = arg[2]
options_json = arg[3]
-- print (template_str)
-- print (data_json)
-- print (options_json)

-- data = json:Decode(data_json)
-- options = json:Decode(options_json)

local t = jsontemplate.Template(template_str)
print(t.expand(data_json))
