-- https://www.tutorialspoint.com/lua/

-- Documentation: http://www.hammerspoon.org/
-- Code: https://github.com/Hammerspoon/hammerspoon
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

-- http://www.hammerspoon.org/docs/hs.screen.html#allScreens
for index, screen in pairs(hs.screen.allScreens()) do
    print('Screen #' .. index .. ': UUID: ' .. screen:getUUID() .. ' ' .. tostring(screen))
end

-- After v0.9.79, hs.configdir now contains the target of the symbolic link (~/.hammerspoon/init.lua)
print('hs.configdir = ' .. hs.configdir)

-- Change the relative path to load spoons
-- https://github.com/Hammerspoon/hammerspoon/blob/master/SPOONS.md#loading-a-spoon
package.path = package.path .. ";" .. hs.configdir .. "/../../../../.hammerspoon/Spoons/?.spoon/init.lua"
print('package.path = ' .. package.path)

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

-- The two external monitors have the same name (HP E241i), so I have to use the UUID instead
-- If the external monitors are off, fallback to other screens
local laptop_screen = 'Built-in Retina Display'
local wide_curved_screen = hs.screen.find('DELL U3415W')

local horizontal_screen = nil
local vertical_screen = nil
local horizontal_screens = {'E65B6F7D-7840-00EF-1990-CF2EF44F5BFC', '565E033B-3870-00DF-A63A-1F5160E08F52', 'E225737C-8F00-0D95-82AF-6FBF32B14368', 'DELL U2719DC', 'D359FA2C-C508-12BD-FBA7-B3C511A4E7F5'}
local vertical_screens = {'7B9820D5-4E5D-A176-973E-790B87B2F4FA', '4198EDAA-340A-0A10-CCA4-3216126A10C8', '5689A5C1-5CF9-118D-8400-DF34508D2985', 'E1421D32-3481-3E59-B4B0-8CCEFC9F1FA1'}

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

-- Default layouts: http://www.hammerspoon.org/docs/hs.layout.html
-- http://www.hammerspoon.org/docs/hs.geometry.html#rect
layout_top30 = hs.geometry.rect(0, 0, 1, 0.30)
layout_top50 = hs.geometry.rect(0, 0, 1, 0.5)
layout_top70 = hs.geometry.rect(0, 0, 1, 0.7)
layout_bottom50 = hs.geometry.rect(0, 0.5, 1, 0.5)

local window_layout = {}

function config_screen(screen, apps)
    for index, tuple in pairs(apps) do
        local app_name = tuple[1]
        local config = {app_name, tuple[2], screen, tuple[3], nil, nil}
        local show_app = tuple[4]
        table.insert(window_layout, config)

        if show_app ~= nil and app_name ~= nil then
            app = hs.application.find(app_name)
            if app ~= nil then
                -- Uncomment this to find and activate the application window (layout only works on visible/activated windows)
                -- app:activate()
                if show_app then
                    -- http://www.hammerspoon.org/docs/hs.application.html#unhide
                    app:unhide()
                else
                    -- http://www.hammerspoon.org/docs/hs.application.html#hide
                    app:hide()
                end
            end
        end
    end
end

if wide_curved_screen ~= nil then
    config_screen(wide_curved_screen, {
        {"iTerm2", nil, hs.layout.left50, nil},
        {"Preview", nil, hs.layout.left50, nil},
        {"Finder", nil, hs.layout.left50, nil},
        {"Brave Browser", nil, hs.layout.left50, nil},
        {"zoom.us", 'Zoom', hs.layout.left50, nil},

        {"PyCharm", nil, hs.layout.right50, nil},
        {"Code", nil, hs.layout.right50, nil},
        {"App Store", nil, hs.layout.right50, nil},
        {"Hammerspoon", "Hammerspoon Console", hs.layout.right50, nil},
        {"Activity Monitor", nil, hs.layout.right50, nil},
    })
    config_screen(laptop_screen, {
        {"Skype", nil, hs.layout.maximized, nil},
        {"Telegram", nil, hs.layout.maximized, false},
        {"WhatsApp", nil, hs.layout.maximized, false},
        {"DeepL", nil, hs.layout.maximized, false},
        {"Signal", nil, hs.layout.maximized, false},
        {nil, hs.window.find('YouTube'), hs.layout.maximized, nil},
        {"Slack", nil, hs.layout.maximized, nil},
        {"Brave Browser Dev", nil, hs.layout.maximized, nil},
        {"Toggl Track", nil, hs.layout.right30, false},
        {"VLC", nil, hs.layout.maximized, false},
        {"Spotify", nil, hs.layout.maximized, false},
        {"TeamViewer", nil, hs.layout.maximized, nil},
        {"zoom.us", 'Zoom Meeting', hs.layout.maximized, nil},
    })
else
    config_screen(horizontal_screen, {
        {"Finder", nil, layout_top50, nil},
        {"Code", nil, hs.layout.maximized, nil},
        {"Brave Browser", nil, hs.layout.maximized, nil},
        {"Slack", nil, hs.layout.maximized, nil},
        {"Brave Browser Dev", "Brave Dev – WAA", hs.layout.maximized, nil},
        {"PyCharm", nil, hs.layout.maximized, nil},
        {"VLC", nil, hs.layout.maximized, false},
        {"zoom.us", "Zoom", hs.layout.maximized, nil},
        {"dupeGuru", "dupeGuru Results", hs.layout.maximized, nil},
        {"Brave Browser", "Todoist", hs.layout.maximized, nil},
    })
    config_screen(vertical_screen, {
        {"iTerm2", nil, hs.layout.maximized, nil},
        {"Telegram", nil, layout_bottom50, false},
        {"WhatsApp", nil, layout_top50, false},
        {"DeepL", nil, layout_top50, false},
        {"Signal", nil, layout_top30, false},
        {"Preview", nil, hs.layout.maximized, nil},
        {"dupeGuru", "dupeGuru", layout_top50, nil},
        {"Brave Browser Dev", "Brave Dev – Regina", layout_top50, nil},
        {"Brave Browser Dev", "Brave Dev – Torrent", layout_bottom50, nil},

        -- Work profiles
        -- TODO: find a better way to configure apps/windows here in this script,
        --   because the order of these layout tables is important;
        --   they are applied in the order they appear
        {"Brave Browser", "JIRA", layout_top70, nil},
        {"Brave Browser", "Google Sheets", layout_top70, nil},
        {"Brave Browser", "Figma", layout_top70, nil},
        {"Brave Browser", "Brave – Finance", layout_top50, nil},
        {"Brave Browser", "Brave – DD", layout_bottom50, nil},
        {"Brave Browser", "DevTools", layout_top50, nil},

        {"Todoist", nil, layout_bottom50, nil},
        {"Bitwarden", nil, layout_bottom50, nil},

        {"PyCharm", "Debug -", layout_top50, nil},
        {"PyCharm", "Run -", layout_bottom50, nil},
    })
    config_screen(laptop_screen, {
        {"Spotify", nil, hs.layout.maximized, false},
        {"Hammerspoon", "Hammerspoon Console", layout_bottom50, false},
        {"TeamViewer", nil, hs.layout.maximized, nil},
        {"zoom.us", 'Zoom Meeting', hs.layout.maximized, nil},
        {"Skype", nil, hs.layout.maximized, nil},
        {"App Store", nil, hs.layout.maximized, nil},
        {"Toggl Track", nil, hs.layout.right70, false},
        {'AWS VPN Client', 'AWS VPN Client', hs.layout.right50, nil},
        {nil, hs.window.find('YouTube'), hs.layout.maximized, nil},
        {"Activity Monitor", nil, hs.layout.right50, nil},
    })
end

-- http://www.hammerspoon.org/docs/hs.layout.html#apply
function compare_window_title(actual_window_title, expected_window_title)
    local found = string.match(actual_window_title, expected_window_title)
    if found ~= nil then
        print('  Found this: ' .. expected_window_title .. ' in this existing window title: ' .. actual_window_title)
    end
    return found
end

function apply_window_layout()
    -- http://www.hammerspoon.org/docs/hs.layout.html
    hs.layout.apply(window_layout, compare_window_title)
end

apply_window_layout()

-- Apply window layout when a monitor is connected/disconnected
-- Newsflash: it doesn't work. ;)
-- http://www.hammerspoon.org/docs/hs.screen.watcher.html
hs.screen.watcher.new(apply_window_layout)
