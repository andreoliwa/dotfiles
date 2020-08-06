-- https://www.tutorialspoint.com/lua/

-- Documentation: http://www.hammerspoon.org/
-- Examples:
-- https://github.com/derekwyatt/dotfiles/blob/master/hammerspoon-init.lua
-- https://github.com/fikovnik/ShiftIt/wiki/The-Hammerspoon-Alternative
-- https://github.com/scottwhudson/Lunette

hs.window.animationDuration = 0
hs.console.clearConsole()

-- http://www.hammerspoon.org/docs/hs.network.configuration.html#open
computer_name = hs.network.configuration.open():computerName()
print('Computer name: ' .. computer_name)
work = string.match(computer_name, 'mac13')
if work then
    print('This is the work laptop')
end

-- Reload config with function key
-- http://www.hammerspoon.org/docs/hs.hotkey.html#bind
hs.hotkey.bind(nil, 'f15', 'Config reloaded', hs.reload, nil, nil)

-- https://github.com/scottwhudson/Lunette
hs.loadSpoon("Lunette")
spoon.Lunette:bindHotkeys()

-- http://www.hammerspoon.org/docs/hs.application.html#find
-- To find an application, run this on the console:
-- hs.application.find('brave')

-- http://www.hammerspoon.org/docs/hs.application.html#runningApplications
hs.application.enableSpotlightForNameSearches(true)
for i, app in pairs(hs.application.runningApplications()) do
    print('App #' .. i .. ': ' .. tostring(app))

    for j, window in pairs(app:allWindows()) do
        print('    Window #' .. j .. ': ' .. tostring(window))
    end
end

-- http://www.hammerspoon.org/docs/hs.screen.html#allScreens
for index, screen in pairs(hs.screen.allScreens()) do
    print('Screen #' .. index .. ': UUID: ' .. screen:getUUID() .. ' ' .. tostring(screen))
end

-- The two external monitors have the same name (HP E241i), so I have to use the UUID instead
-- If the external monitors are off, fallback to other screens
local laptop_screen = 'Color LCD'
local wide_curved_screen = hs.screen.find('DELL U3415W')

local horizontal_screen = nil
local vertical_screen = nil
local horizontal_screens = {'E65B6F7D-7840-00EF-1990-CF2EF44F5BFC', '565E033B-3870-00DF-A63A-1F5160E08F52', 'E225737C-8F00-0D95-82AF-6FBF32B14368', 'DELL U2719DC'}
local vertical_screens = {'7B9820D5-4E5D-A176-973E-790B87B2F4FA', '4198EDAA-340A-0A10-CCA4-3216126A10C8', '5689A5C1-5CF9-118D-8400-DF34508D2985'}

for index, screen_id in ipairs(horizontal_screens) do
    horizontal_screen = hs.screen.find(screen_id)
    if horizontal_screen ~= nil then
        break
    end
end
if horizontal_screen == nil then
    horizontal_screen = laptop_screen
end

for index, screen_id in ipairs(vertical_screens) do
    vertical_screen = hs.screen.find(screen_id)
    if vertical_screen ~= nil then
        break
    end
end
if vertical_screen == nil then
    vertical_screen = horizontal_screen
end

-- http://www.hammerspoon.org/docs/hs.geometry.html#rect
layout_top50 = hs.geometry.rect(0, 0, 1, 0.5)
layout_bottom50 = hs.geometry.rect(0, 0.5, 1, 0.5)

local window_layout = {}

function config_screen(screen, apps)
    for index, tuple in pairs(apps) do
        local app_name = tuple[1]
        local config = {app_name, tuple[2], screen, tuple[3], nil, nil}
        table.insert(window_layout, config)

        -- Only visible windows will be repositioned
        -- Uncomment this to find and activate the application window (layout only works on visible/activated windows)
        -- if app_name ~= nil then
        --     app = hs.application.find(app_name)
        --     if app ~= nil then
        --         app:activate()
        --     end
        -- end
    end
end

if wide_curved_screen ~= nil then
    config_screen(wide_curved_screen, {
        {"iTerm2", nil, hs.layout.left50},
        {"Preview", nil, hs.layout.left50},
        {"Finder", nil, hs.layout.left50},
        {"Brave Browser", nil, hs.layout.left50},
        {"zoom.us", 'Zoom', hs.layout.left50},

        {"PyCharm", nil, hs.layout.right50},
        {"Code", nil, hs.layout.right50},
        {"App Store", nil, hs.layout.right50},
        {"Hammerspoon", "Hammerspoon Console", hs.layout.right50},
    })
    config_screen(laptop_screen, {
        {"Skype", nil, hs.layout.maximized},
        {"Telegram", nil, hs.layout.maximized},
        {"WhatsApp", nil, hs.layout.maximized},
        {"Signal", nil, hs.layout.maximized},
        {nil, hs.window.find('YouTube'), hs.layout.maximized},
        {"Slack", nil, hs.layout.maximized},
        {"Brave Browser Dev", nil, hs.layout.maximized},
        {"TogglDesktop", nil, hs.layout.right30},
        {"VLC", nil, hs.layout.maximized},
        {"Spotify", nil, hs.layout.maximized},
        {"TeamViewer", nil, hs.layout.maximized},
        {"zoom.us", 'Zoom Meeting', hs.layout.maximized},
    })
else
    config_screen(vertical_screen, {
        {"iTerm2", nil, hs.layout.maximized},
        {"Skype", nil, hs.layout.maximized},
        {"Telegram", nil, layout_bottom50},
        {"WhatsApp", nil, layout_top50},
        {"Signal", nil, layout_top50},
        {nil, hs.window.find('YouTube'), hs.layout.maximized},
        {"Preview", nil, hs.layout.maximized},
        {"dupeGuru", "dupeGuru", layout_top50},
    })
    config_screen(horizontal_screen, {
        {"Finder", nil, layout_top50},
        {"Code", nil, hs.layout.maximized},
        {"Brave Browser", nil, hs.layout.maximized},
        {"Slack", nil, hs.layout.maximized},
        {"Brave Browser Dev", nil, hs.layout.maximized},
        {"PyCharm", nil, hs.layout.maximized},
        {"App Store", nil, hs.layout.maximized},
        {"TogglDesktop", nil, hs.layout.right30},
        {"VLC", nil, hs.layout.maximized},
        {"zoom.us", "Zoom", hs.layout.maximized},
        {"dupeGuru", "dupeGuru Results", hs.layout.maximized},
    })
    config_screen(laptop_screen, {
        {"Spotify", nil, hs.layout.maximized},
        {"Hammerspoon", "Hammerspoon Console", layout_bottom50},
        {"TeamViewer", nil, hs.layout.maximized},
        {"zoom.us", 'Zoom Meeting', hs.layout.maximized},
    })
end

function apply_window_layout()
    -- http://www.hammerspoon.org/docs/hs.layout.html
    hs.layout.apply(window_layout)
end

apply_window_layout()

-- Apply window layout when a monitor is connected/disconnected
-- Newsflash: it doesn't work. ;)
-- http://www.hammerspoon.org/docs/hs.screen.watcher.html
hs.screen.watcher.new(apply_window_layout)
