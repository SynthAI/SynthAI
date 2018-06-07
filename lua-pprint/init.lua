--[[ Pretty Printing for Torch and Lua, main module.

Code adapted from inspect.lua, here (https://github.com/kikito/inspect.lua).
 * changed some formatting, removed numbering of elements
 * added support for tensors
 * changed various function names
]]

require 'torch'

-- Wraps quoted strings in apostraphes
local function smart_quote(str)
  if string.match( string.gsub(str, "[^'\"]", ""), '^"+$' ) then
    return "'" .. str .. "'"
  end
  return string.format("%q", str)
end


local control_chars_translation = {
    ["\a"] = "\\a",  ["\b"] = "\\b", ["\f"] = "\\f",  ["\n"] = "\\n",
    ["\r"] = "\\r",  ["\t"] = "\\t", ["\v"] = "\\v",  ["\\"] = "\\\\"
}


local function unescape_char(c)
  return control_chars_translation[c]
end


local function unescape(str)
  local result, _ = string.gsub( str, "(%c)", unescape_char )
  return result
end


local function is_identifier(str)
  return string.match( str, "^[_%a][_%a%d]*$" )
end


local function is_array_key(k, length)
  return type(k)=='number' and 1 <= k and k <= length
end


local function is_dictionary_key(k, length)
  return not is_array_key(k, length)
end


local sort_orders_by_type = {
    ['number'] = 1, ['boolean']  = 2, ['string'] = 3, ['table'] = 4,
    ['tensor'] = 5, ['function'] = 6, ['userdata'] = 7, ['thread'] = 8
}


local function sort_keys(a,b)
  local ta, tb = type(a), type(b)
  if ta ~= tb then return sort_orders_by_type[ta] < sort_orders_by_type[tb] end
  if ta == 'string' or ta == 'number' then return a < b end
  return false
end


local function get_dictionary_keys(t)
  local length = #t
  local keys = {}
  for k, _ in pairs(t) do
    if is_dictionary_key(k, length) then table.insert(keys, k) end
  end
  table.sort(keys, sort_keys)
  return keys
end


local function get_to_string_result_safely(t, mt)
  local __tostring = type(mt) == 'table' and mt.__tostring
  local string, status
  if type(__tostring) == 'function' then
    status, string = pcall(__tostring, t)
    string = status and string or 'error: ' .. tostring(string)
  end
  return string
end


local Printer = {}

function Printer:init(depth, inline)
  local pprintor = {
      buffer = {},
      depth = depth or 0,
      inline = inline or false,
      level = 0,
      counters = {
          ['function'] = 0,
          ['userdata'] = 0,
          ['thread'] = 0,
          ['table'] = 0
      },
      pools = {
          ['function'] = setmetatable({}, {__mode = "kv"}),
          ['userdata'] = setmetatable({}, {__mode = "kv"}),
          ['thread'] = setmetatable({}, {__mode = "kv"}),
          ['table'] = setmetatable({}, {__mode = "kv"})
      }
  }

  setmetatable(pprintor, {
      __index = Printer,
      __tostring = function(instance) return table.concat(instance.buffer) end
  } )
  return pprintor
end


function Printer:new(v, depth, inline)
   local p = self:init(depth, inline)
   return p:put_value(v)
end


function Printer:puts(...)
  local args = {...}
  for i = 1, #args do
    table.insert(self.buffer, tostring(args[i]))
  end
  return self
end


function Printer:tabify()
  if self.inline then
    self:puts(" ")
  else
    self:puts("\n", string.rep("  ", self.level))
  end
  return self
end


function Printer:up()
  self.level = self.level - 1
end


function Printer:down()
  self.level = self.level + 1
end


function Printer:put_comma(comma)
  if comma then self:puts(',') end
  return true
end


function Printer:put_table(t)
  if self:already_seen(t) then
    self:puts('<table>')
  elseif self.level >= self.depth then
    self:puts('{...}')
  else
    self:down()

    local length = #t
    local mt = getmetatable(t)
    self:puts('{')

    local string = get_to_string_result_safely(t, mt)
    if type(string) == 'string' and #string > 0 then
      self:puts(' -- ', unescape(string))
      if length >= 1 then self:tabify() end -- tabify the array values
    end

    local comma = false
    for i = 1, length do
      comma = self:put_comma(comma)
      self:puts(' '):put_value(t[i])
    end

    local dict_keys = get_dictionary_keys(t)

    for _, k in ipairs(dict_keys) do
      comma = self:put_comma(comma)
      self:tabify():put_key(k):puts(' = '):put_value(t[k])
    end

    if mt then
      comma = self:put_comma(comma)
      self:tabify():puts('<metatable> = '):put_value(mt)
    end
    self:up()

    if #dict_keys > 0 or mt then -- dictionary table. Justify closing }
      self:tabify()
    elseif length > 0 then -- array tables have one extra space before closing }
      self:puts(' ')
    end
    self:puts('}')
  end
  return self
end


function Printer:put_tensor(t)
  local size = t:nElement()
  if size <= 20 then
    self:puts(tostring(t))
  else
    self:puts('[' .. torch.typename(t) .. ' of dimension ')
    self:put_tensor_dims(t)
    self:puts(']')
  end
end

function Printer:put_storage(t)
  local size = t:size()
  if size <= 20 then
    self:puts(tostring(t))
  else
    self:puts('[' .. torch.typename(t) .. ' of size ')
    self:puts(size)
    self:puts(']')
  end
end

function Printer:put_tensor_dims(t)
  local n_dims = t:dim()
  local dim_sizes = t:size()
  if n_dims == 0 then
    self:puts('[0-dimensional tensor]')
  else
    for i = 1, n_dims-1 do
      self:puts(dim_sizes[i]):puts('x')
    end
    self:puts(dim_sizes[n_dims])
  end
end


function Printer:already_seen(v)
  local tv = type(v)
  return self.pools[tv][v] ~= nil
end


function Printer:get_or_create_counter(v)
  local tv = type(v)
  local current = self.pools[tv][v]
  if not current then
    current = self.counters[tv] + 1
    self.counters[tv] = current
    self.pools[tv][v] = current
  end
  return current
end


function Printer:put_value(v)
  local tv = type(v)

  if tv == 'string' then
    self:puts(smart_quote(unescape(v)))
  elseif tv == 'number' or tv == 'boolean' or tv == 'nil' then
    if v == math.huge then
      self:puts('math.huge')
    elseif v == -math.huge then
      self:puts('-math.huge')
    else
      self:puts(tostring(v))
    end
  elseif tv == 'table' then
    self:put_table(v)
  elseif torch.isTensor(v) then
    self:put_tensor(v)
  elseif torch.isStorage(v) then
    self:put_storage(v)
  else
    self:puts('<',tv,'>')
  end
  return self
end


function Printer:put_key(k)
  if type(k) == "string" and is_identifier(k) then
    return self:puts(k)
  end
  return self:puts( "[" ):put_value(k):puts("]")
end


local function print_tensor_dimensions(t)
  local p = Printer.init()
  p:put_tensor_dims(t)
  return tostring(p)
end


local function print_tensor_info(t)
  local p = Printer.init()
  
  -- if we find a table, recursively call info on its elements
  if type(t) == 'table' then
    local newline = ' '
    if #t > 1 then newline = '\n' end
    p:puts('{' .. newline)
    for i = 1, #t do
      p:puts(print_tensor_info(t[i]))
      p:puts(newline)
    end
    p:puts('}')
  else
    if t == nil then p:puts("[nil]") end
    p:puts('['):put_tensor_dims(t)
    if t.min then p:puts(', min: '):put_value(t:min()) end
    if t.mean then p:puts(', mean: '):put_value(t:mean()) end
    if t.max then p:puts(', max: '):put_value(t:max()) end
    if t.type then p:puts(', type: '):put_value(t:type()) end
    p:puts(']')
  end
  return tostring(p)
end


local function pretty_string(t, depth, inline)
  depth = depth or 4
  inline = inline or false
  return tostring(Printer:new(t, depth, inline))
end

-- Returns an inline string.
local function string(t, depth)
  return pretty_string(t, depth, true)
end

local function pprint_pprint(self, data, depth)
  print(pretty_string(data, depth))
end

pprint = {
    pretty_string = pretty_string, -- multi-line string
    string = string, -- inline string
    dims = print_tensor_dimensions,
    info = print_tensor_info,
    __call = pprint_pprint,
    printer = function(depth)
        depth = depth or 4
        local function pretty_string(...)
            local str_table = {}
            for i = 1, select('#', ...) do
              local obj = select(i, ...)
              table.insert(str_table, tostring(Printer:new(obj, depth)))
            end
            return table.concat(str_table, ' ')
        end
        return pretty_string
    end
}


setmetatable(pprint, pprint)


return pprint
