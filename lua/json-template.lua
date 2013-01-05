-- json-template.lua

module("json-template")

function Template(template_str, options)
  self = {}
  options = options or {}

  return {
    expand = function(data)
      return template_str
    end
  }
end
