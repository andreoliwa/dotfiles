-- https://www.tutorialspoint.com/lua/

-- Documentation: http://www.hammerspoon.org/
-- Code: https://github.com/Hammerspoon/hammerspoon
-- Examples:
-- https://github.com/derekwyatt/dotfiles/blob/master/hammerspoon-init.lua
-- https://github.com/fikovnik/ShiftIt/wiki/The-Hammerspoon-Alternative
-- https://github.com/scottwhudson/Lunette

hs.window.animationDuration = 0
hs.console.clearConsole()

local debug = false
print('Debugging? ' .. tostring(debug))

function debug_print(message)
    if debug then
       print(message)
    end
end

-- Because this stupid language doesn't have a proper ternary operator
-- https://stackoverflow.com/questions/5525817/inline-conditions-in-lua-a-b-yes-no
function ternary(condition, true_value, false_value)
    if condition then return true_value else return false_value end
end

local working = hs.application.find('slack') ~= nil
-- Hide app when working, keep its current visibility state when not working
local hide_when_working = ternary(working, false, nil)

-- http://www.hammerspoon.org/docs/hs.network.configuration.html#open
if debug then
    computer_name = hs.network.configuration.open():computerName()
    debug_print('Computer name: ' .. computer_name)
    work = string.match(computer_name, 'mac16')
    if work then
        debug_print('This is the work laptop')
    end
end

-- Reload config with function key
-- http://www.hammerspoon.org/docs/hs.hotkey.html#bind
hs.hotkey.bind(nil, 'f15', 'Config reloaded', hs.reload, nil, nil)

if debug then
    -- http://www.hammerspoon.org/docs/hs.screen.html#allScreens
    for index, screen in pairs(hs.screen.allScreens()) do
        debug_print('Screen #' .. index .. ': UUID: ' .. screen:getUUID() .. ' ' .. tostring(screen))
    end

    -- After v0.9.79, hs.configdir now contains the target of the symbolic link (~/.hammerspoon/init.lua)
    debug_print('hs.configdir = ' .. hs.configdir)
end

-- Change the relative path to load spoons
-- https://github.com/Hammerspoon/hammerspoon/blob/master/SPOONS.md#loading-a-spoon
package.path = package.path .. ";" .. hs.configdir .. "/../../../../.hammerspoon/Spoons/?.spoon/init.lua"
debug_print('package.path = ' .. package.path)

-- https://github.com/scottwhudson/Lunette
hs.loadSpoon("Lunette")
spoon.Lunette:bindHotkeys()

-- http://www.hammerspoon.org/docs/hs.application.html#find
-- To find an application, run this on the console:
-- hs.application.find('brave')

-- http://www.hammerspoon.org/docs/hs.application.html#runningApplications
hs.application.enableSpotlightForNameSearches(true)
if debug then
    for i, app in pairs(hs.application.runningApplications()) do
        debug_print('App #' .. i .. ': ' .. tostring(app))

        for j, window in pairs(app:allWindows()) do
            debug_print('    Window #' .. j .. ': ' .. tostring(window) .. ' - Geometry: ' .. tostring(window:frame()))
        end
    end
end

-- The two external monitors have the same name (HP E241i), so I have to use the UUID instead
-- If the external monitors are off, fallback to other screens
-- http://www.hammerspoon.org/docs/hs.screen.html#find
local laptop_screen = 'Built-in Retina Display'

-- Wide screen name is "LEN T34w-20"; I had to remove the "-20" for string.match() to find the screen
local wide_curved_screen = hs.screen.find('LEN T34w')

local horizontal_screen = nil
local vertical_screen = nil

-- Can be UUIDs or names; copy/paste from HammerSpoon console
local horizontal_screens = {'LEN T34w-20'}
local vertical_screens = {}

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
-- x, y, width, height, all ranging from 0 to 1
hs.layout.top30 = hs.geometry.rect(0, 0, 1, 0.30)
hs.layout.top50 = hs.geometry.rect(0, 0, 1, 0.5)
hs.layout.top70 = hs.geometry.rect(0, 0, 1, 0.7)
hs.layout.bottom50 = hs.geometry.rect(0, 0.5, 1, 0.5)
hs.layout.middle_left40 = hs.geometry.rect(0.10, 0, 0.40, 1)
hs.layout.center_left = hs.geometry.rect(0.25, 0, 0.25, 1)
hs.layout.center_right = hs.geometry.rect(0.5, 0, 0.25, 1)
hs.layout.right50_top = hs.geometry.rect(0.5, 0, 0.5, 0.5)
hs.layout.right50_bottom = hs.geometry.rect(0.5, 0.5, 0.5, 0.5)

local window_layout = {}

function config_screen(screen, apps)
    for index, tuple in pairs(apps) do
        local app_name = tuple[1]
        local config = {app_name, tuple[2], screen, tuple[3], nil, nil}
        local show_app = tuple[4]
        table.insert(window_layout, config)

        if show_app ~= nil and app_name ~= nil then
            -- The return can be hs.application or hs.window (or maybe more things)
            -- http://www.hammerspoon.org/docs/hs.application.html#find
            app_or_window = hs.application.find(app_name)

            if app_or_window ~= nil then
                -- Uncomment this to find and activate the application window (layout only works on visible/activated windows)
                -- app_or_window:activate()
                if show_app then
                    -- http://www.hammerspoon.org/docs/hs.application.html#unhide
                    app_or_window:unhide()
                else
                    -- http://www.hammerspoon.org/docs/hs.application.html#hide
                    -- A window doesn't have the hide() method and raises:
                    -- method 'hide' is not callable (a nil value)
                    if app_or_window.hide ~= nil then
                        app_or_window:hide()
                    end
                end
            end
        end
    end
end

if wide_curved_screen ~= nil then
    config_screen(wide_curved_screen, {
        -- Left
        {"iTerm2", nil, hs.layout.left50, nil},
        {"Preview", nil, hs.layout.left50, nil},

        {"Finder", nil, hs.layout.right50_top, nil},
        {"Finder", "consume", hs.layout.right50_bottom, nil},
        {"Finder", "inbox", hs.layout.right50_bottom, nil},
        {"Finder", "import", hs.layout.right50_bottom, nil},

        {"Brave Browser", nil, hs.layout.left50, nil},
        {"Brave Browser Beta", nil, hs.layout.left50, nil},
        {"Slack", nil, hs.layout.left50, nil},
        {"Telegram", nil, hs.layout.left50, hide_when_working},
        {"WhatsApp", nil, hs.layout.left50, hide_when_working},
        {"Signal", nil, hs.layout.left50, hide_when_working},
        {"Bitwarden", nil, hs.layout.left30, false},
        {"Gnucash", nil, hs.layout.left50, nil},
        {"Logseq", nil, hs.layout.middle_left40, hide_when_working},
        {"Authy Desktop", nil, hs.layout.center_left, true},

        -- Right
        {"PyCharm", nil, hs.layout.right50, nil},
        {"Code", nil, hs.layout.right50, nil},
        {"App Store", nil, hs.layout.right50, nil},
        {"Notes", nil, hs.layout.right50, nil},
        {"zoom.us", 'Zoom', hs.layout.right50, nil},
        {"Activity Monitor", nil, hs.layout.right30, nil},
        {"DeepL", nil, hs.layout.right50_top, hide_when_working},

        -- Full
        {"VLC", nil, hs.layout.maximized, hide_when_working},
    })
    config_screen(laptop_screen, {
        {"Skype", nil, hs.layout.maximized, nil},
        {nil, hs.window.find('YouTube'), hs.layout.maximized, nil},
        {"Toggl Track", nil, hs.layout.right50, hide_when_working},
        {"Spotify", nil, hs.layout.left70, hide_when_working},
        {"TeamViewer", nil, hs.layout.maximized, nil},
        {"zoom.us", 'Zoom Meeting', hs.layout.maximized, nil},
        {"zoom.us", "zoom floating video window", hs.layout.left50, nil},
        {"zoom.us", "zoom share statusbar window", hs.layout.right50, nil},
        {"zoom.us", "zoom share toolbar window", hs.layout.right70, nil},

        {"Hammerspoon", "Hammerspoon Console", hs.layout.bottom50, debug},
        {"Speedtest", nil, hs.layout.left50, nil},
        {"Todoist", nil, hs.layout.right70, hide_when_working},
        {"Docker Desktop", nil, hs.layout.top50, nil},
        {"ScanSnap Home", nil, hs.geometry.rect(0.42, 0.23, 0.5, 0.5), nil},
        {nil, hs.window.find('- Scan'), hs.layout.right70, nil},
    })
else
    config_screen(horizontal_screen, {
        {"Finder", nil, hs.layout.top50, nil},
        {"Code", nil, hs.layout.maximized, nil},
        {"Brave Browser", nil, hs.layout.maximized, nil},
        {"Slack", nil, hs.layout.maximized, nil},
        {"Brave Browser Beta", "Brave Beta – WAA", hs.layout.maximized, nil},
        {"PyCharm", nil, hs.layout.maximized, nil},
        {"VLC", nil, hs.layout.maximized, false},
        {"zoom.us", "Zoom", hs.layout.maximized, nil},
        {"dupeGuru", "dupeGuru Results", hs.layout.maximized, nil},
        {"Brave Browser", "Todoist", hs.layout.maximized, nil},
    })
    config_screen(vertical_screen, {
        {"iTerm2", nil, hs.layout.maximized, nil},
        {"Telegram", nil, hs.layout.bottom50, false},
        {"WhatsApp", nil, hs.layout.top50, false},
        {"DeepL", nil, hs.layout.top50, false},
        {"Signal", nil, hs.layout.top30, false},
        {"Preview", nil, hs.layout.maximized, nil},
        {"dupeGuru", "dupeGuru", hs.layout.top50, nil},
        {"Brave Browser Beta", "Brave Beta – Regina", hs.layout.top50, nil},
        {"Brave Browser Beta", "Brave Beta – Torrent", hs.layout.bottom50, nil},

        -- Work profiles
        -- TODO feat: find a better way to configure apps/windows here in this script, because the order
        --   of these layout tables is important; they are applied in the order they appear
        {"Brave Browser", "JIRA", hs.layout.top70, nil},
        {"Brave Browser", "Google Sheets", hs.layout.top70, nil},
        {"Brave Browser", "Figma", hs.layout.top70, nil},
        {"Brave Browser", "Brave – Finance", hs.layout.top50, nil},
        {"Brave Browser", "Brave – DD", hs.layout.bottom50, nil},
        {"Brave Browser", "DevTools", hs.layout.top50, nil},

        {"Todoist", nil, hs.layout.bottom50, nil},
        {"Bitwarden", nil, hs.layout.bottom50, nil},

        {"PyCharm", "Debug -", hs.layout.top50, nil},
        {"PyCharm", "Run -", hs.layout.bottom50, nil},
    })
    config_screen(laptop_screen, {
        {"Spotify", nil, hs.layout.maximized, false},
        {"Hammerspoon", "Hammerspoon Console", hs.layout.bottom50, debug},
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
        debug_print('  Found this: ' .. expected_window_title .. ' in this existing window title: ' .. actual_window_title)
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

function monitor_app_events(app_name, event_type, app_object)
    if app_name == 'Preview' then
        debug_print(app_name)
        debug_print(event_type)
        debug_print(app_object)
        --if event_type == hs.application.watcher.activated then
       --    debug_print(app_name .. ' opened')
       --end
       --if event_type == hs.application.watcher.deactivated then
       --    debug_print(app_name .. ' closed')
       --end
    end
end

-- https://nikhilism.com/post/2021/useful-hammerspoon-tips/
-- https://www.hammerspoon.org/docs/hs.application.watcher.html
debug_print('Starting app watcher')
local my_watch = hs.application.watcher.new(monitor_app_events)
my_watch:start()

function reposition_stubborn_windows(window, app_name, event)
    debug_print(window)
    debug_print(app_name)
    debug_print(event)
    apply_window_layout()
end

-- Reposition all stubborn apps that don't save their last window positions
-- https://www.hammerspoon.org/docs/hs.window.filter.html#subscribe
wf_stubborn_apps = hs.window.filter.new{'Authy Desktop', 'Preview', 'Logseq', 'ScanSnap Home'}
wf_stubborn_apps:subscribe(hs.window.filter.windowCreated, reposition_stubborn_windows)
