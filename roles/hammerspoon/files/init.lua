-- https://www.tutorialspoint.com/lua/

-- Documentation: http://www.hammerspoon.org/
-- Examples:
-- https://github.com/derekwyatt/dotfiles/blob/master/hammerspoon-init.lua
-- https://github.com/fikovnik/ShiftIt/wiki/The-Hammerspoon-Alternative
-- https://github.com/scottwhudson/Lunette

hs.window.animationDuration = 0

-- Reload config with function key
-- http://www.hammerspoon.org/docs/hs.hotkey.html#bind
hs.hotkey.bind(nil, 'f15', 'Config reloaded', hs.reload, nil, nil)

-- http://www.hammerspoon.org/docs/hs.application.html#find
-- To find an application, run this on the console:
-- hs.application.find('brave')

-- http://www.hammerspoon.org/docs/hs.application.html#runningApplications
for index, app in pairs(hs.application.runningApplications()) do
    print('App #' .. index .. ': ' .. tostring(app))
end

-- http://www.hammerspoon.org/docs/hs.screen.html#allScreens
for index, screen in pairs(hs.screen.allScreens()) do
    print('Screen #' .. index .. ': UUID: ' .. screen:getUUID() .. ' ' .. tostring(screen))
end

-- The two external monitors have the same name (HP E241i), so I have to use the UUID instead
-- If the external monitors are off, fallback to other screens
local laptop_screen_right = 'Color LCD'
local horizontal_screen_center = hs.screen.find('565E033B-3870-00DF-A63A-1F5160E08F52') or laptop_screen_right
local vertical_screen_left = hs.screen.find('7B9820D5-4E5D-A176-973E-790B87B2F4FA') or horizontal_screen_center

-- http://www.hammerspoon.org/docs/hs.geometry.html#rect
layout_top50 = hs.geometry.rect(0, 0, 1, 0.5)
layout_bottom50 = hs.geometry.rect(0, 0.5, 1, 0.5)

local window_layout = {}

function config_screen(screen, apps)
    for index, tuple in pairs(apps) do
        local app_name = tuple[1]
        local config = {app_name, tuple[2], screen, tuple[3], nil, nil}
        table.insert(window_layout, config)

        -- Find and activate the application window (layout only works on visible/activated windows)
        if app_name ~= nil then
            app = hs.application.find(app_name)
            if app ~= nil then
                app:activate()
            end
        end
    end
end

config_screen(vertical_screen_left, {
    {"iTerm2", nil, hs.layout.maximized},
    {"Skype", nil, hs.layout.maximized},
    {"Telegram", nil, layout_top50},
    {"WhatsApp", nil, layout_bottom50},
    {"Signal", nil, hs.layout.maximized},
    {nil, hs.window.find('YouTube'), hs.layout.maximized},
    {"Preview", nil, hs.layout.maximized},
})

config_screen(horizontal_screen_center, {
    {"Finder", nil, layout_top50},
    {"Code", nil, hs.layout.maximized},
    {"Brave Browser", nil, hs.layout.maximized},
    {"Slack", nil, hs.layout.maximized},
    {"Brave Browser Dev", nil, hs.layout.maximized},
    {"PyCharm", nil, hs.layout.maximized},
    {"App Store", nil, hs.layout.maximized},
    {"TogglDesktop", nil, hs.layout.right30},
    {"VLC", nil, hs.layout.maximized},
})

config_screen(laptop_screen_right, {
    {"Spotify", nil, hs.layout.maximized},
    {"Hammerspoon", "Hammerspoon Console", layout_bottom50},
})

function apply_window_layout()
    -- http://www.hammerspoon.org/docs/hs.layout.html
    hs.layout.apply(window_layout)
end

apply_window_layout()

-- Apply window layout when a monitor is connected/disconnected
-- Newsflash: it doesn't work. ;)
-- http://www.hammerspoon.org/docs/hs.screen.watcher.html
hs.screen.watcher.new(apply_window_layout)
