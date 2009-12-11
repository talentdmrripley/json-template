-- json-template.lua

module("json-template")

function Template(template_str)
  self = {}

  return {
    expand = function(data)
      return template_str
    end
  }
end
