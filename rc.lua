local function show_notif()
            path = run_script()
            naughty.config.presets.normal.icon_size = 180

            naughty.notify({
                text = table.concat(path[4],'\n'),
                title = path[3],
                position = "top_right",
                timeout = 5,
                icon=path[1],
                screen = 1,
                ontop = false
            })

            naughty.config.presets.normal.icon_size = 50
        end


local function okok(text)
end

mybar = blingbling.new_widget.new()
mybar:buttons(awful.util.table.join(
        awful.button({ }, 1,  show_notif, nil ),
        awful.button({ }, 3,  show_notif, nil )
))
vicious.register(mybar, okok, "$1", 3)

