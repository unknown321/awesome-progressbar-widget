-- local pairs = pairs
-- local print = print
local unpack = unpack
-- local type = type
-- local tostring = tostring

local helpers = require("blingbling.helpers")
local setmetatable = setmetatable
local lgi = require("lgi")
local cairo = lgi.cairo
local Pango = lgi.Pango
local PangoCairo = lgi.PangoCairo
local oocairo = require("oocairo")



-- local cairo = require("oocairo")
local capi = { image = image, widget = widget, timer = timer}
local timer = timer
local layout = require("awful.widget.layout")
local io = io
local naughty = require('naughty')
local loadstring = loadstring or load

module("blingbling.new_widget")

local p_bar = {}

function update()
   -- local handle = io.popen('/home/unknown/.config/awesome/music.py -p')
   -- local text = handle:read("*a")
   local width = 300
   local height = 20
   local image_path = '/home/unknown/.config/awesome/music_image.png'
   local mpdinfofile = io.open('/home/unknown/.config/awesome/mpdinfo','r')
   local time = mpdinfofile:read('*line')
   if time ~= 'No connection' then
      TEXT = mpdinfofile:read('*line')
      time = helpers.split(time,':')
      progress = time[1]/time[2]
   else
      TEXT = 'No MPD connection'
      progress = 0
   end


      p_bar_surface = cairo.ImageSurface.create("argb32",width, height)
      cr = cairo.Context.create(p_bar_surface)

      local background = {63/255,63/255,63/255} -- get color from awesome theme
      cr:set_source_rgb(unpack(background))
      cr:rectangle(0, 0, width, height)
      cr:fill()

      local line_color = {0,255,0}
      r,g,b = unpack(line_color)
      cr:set_source_rgb(unpack(line_color))
      cr:rectangle(0, height-3, width*progress, height)
      gradient = cairo.Pattern.create_linear(0, height-20, 0, height)
      gradient:add_color_stop_rgba(0.8, r,g,b, 0)
      gradient:add_color_stop_rgba(1,  r,g,b, 1)
      cr:set_source(gradient)
      cr:fill()

      --move  and set scale
      cr:translate(0,2)
      cr:scale(1,1)

      local text_color = {255/255, 255/255, 255/255}
      cr:set_source_rgb(unpack(text_color))

      -- Create a Pango.Layout, set the text, font and attributes.
      
      local FONT = 'Sans 9'
      local layout = PangoCairo.create_layout(cr)
      layout.text = TEXT
      layout.font_description = Pango.FontDescription.from_string(FONT)
      cr:show_layout(layout)
      cr:fill()
      

      -- because awesome 3.4 cannot work with pointers from pangocairo library
      -- it is easier to dump image to png and reread it using oocairo
      p_bar_surface:flush()
      p_bar_surface:write_to_png(image_path)
      s = oocairo.image_surface_create_from_png(image_path)
      p_bar.widget.image = capi.image.argb32(width, height, s:get_data())
end

function start_timer(p_bar)
    p_bar.timer = capi.timer({timeout=2})
    p_bar.timer:add_signal('timeout',update)
    p_bar.timer:start()
end


-- {{{ CPU widget type
function new(format, args)
    local args = args or {}
    args.type = "imagebox"
    p_bar.widget = capi.widget(args)
    p_bar.widget.resize = false
    p_bar.layout = layout.horizontal.leftright
    p_bar.font_size = 20
    p_bar.update = update
    update(p_bar, format)
    start_timer(p_bar)
    return p_bar.widget
end
-- }}}

setmetatable(_M, { __call = function(_, ...) return new(...) end })
