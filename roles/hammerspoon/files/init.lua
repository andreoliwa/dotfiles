-- https://www.tutorialspoint.com/lua/
-- Documentation: http://www.hammerspoon.org/
-- Code: https://github.com/Hammerspoon/hammerspoon
-- Examples:
-- https://github.com/derekwyatt/dotfiles/blob/master/hammerspoon-init.lua
-- https://github.com/fikovnik/ShiftIt/wiki/The-Hammerspoon-Alternative
-- https://github.com/scottwhudson/Lunette

hs.window.animationDuration = 0
hs.console.clearConsole()

-- hs.wifi not showing current network in Sonoma 14.2.1
-- Workaround: https://github.com/Hammerspoon/hammerspoon/issues/3537#issuecomment-1743870568
-- See also https://github.com/Hammerspoon/hammerspoon/issues/3591#issuecomment-1988453778
print(hs.location.get())

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

local networks = hs.wifi.availableNetworks()
debug_print('WiFi available:')
for i, network in ipairs(networks) do
    debug_print(i, network)
end
local interfaces = hs.wifi.interfaces()
debug_print('WiFi interfaces:')
for i, interface in ipairs(interfaces) do
    debug_print(i, interface)
end
local currentNetwork = hs.wifi.currentNetwork()
if currentNetwork then
    debug_print('WiFi network: ' .. currentNetwork)
else
    debug_print('WiFi network: Not connected')
end

local at_the_office = string.match(hs.wifi.currentNetwork(), 'wolt') ~= nil
debug_print('At the office: ' .. tostring(at_the_office))
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
customBindings = {
    topLeft = {
        {{"alt", "cmd"}, "U"},
    },
    topRight = {
        {{"alt", "cmd"}, "I"},
    },
    bottomLeft = {
        {{"alt", "cmd"}, "J"},
    },
    bottomRight = {
        {{"alt", "cmd"}, "K"},
    },
}
spoon.Lunette:bindHotkeys(customBindings)

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

-- Can be UUIDs or names; copy/paste from HammerSpoon console
-- Partial name matching works, don't need to use the full name of the monitor
-- Wide screen name is 'LEN T34w-20'; the dash has to be escaped with %
local wide_screen = nil
local wide_screens = {'34w%-20','34w%-30'}
for index, screen_id in ipairs(wide_screens) do
    wide_screen = hs.screen.find(screen_id)
    if wide_screen ~= nil then
        break
    end
end

local horizontal_screen = nil
local horizontal_screens = {'DELL',}
for index, screen_id in ipairs(horizontal_screens) do
    horizontal_screen = hs.screen.find(screen_id)
    if horizontal_screen ~= nil then
        break
    end
end

local vertical_screen = nil
local vertical_screens = {}
for index, screen_id in ipairs(vertical_screens) do
    vertical_screen = hs.screen.find(screen_id)
    if vertical_screen ~= nil then
        break
    end
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

function display_app(app_name, is_visible)
    if app_name ~= nil and is_visible ~= nil then
        -- The return can be hs.application or hs.window (or maybe more things)
        -- http://www.hammerspoon.org/docs/hs.application.html#find
        app_or_window = hs.application.find(app_name)

        if app_or_window ~= nil then
            -- Uncomment this to find and activate the application window (layout only works on visible/activated windows)
            -- app_or_window:activate()
            if is_visible then
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

function add_to_window_layout(app_name, window_title, screen, layout)
    local config = {app_name, window_title, screen, layout, nil, nil}
    table.insert(window_layout, config)
end

function config_screen(screen, apps)
    for index, tuple in pairs(apps) do
        local app_name, window_title, layout, is_visible = table.unpack(tuple)
        add_to_window_layout(app_name, window_title, screen, layout)
        display_app(app_name, is_visible)
    end
end

function config_app(app_name, window_title, is_visible, screen_condition_layout_list)
    if window_title == "" then
        window_title = nil
    end

    display_app(app_name, is_visible)

    local found = false
    for index, sl_tuple in pairs(screen_condition_layout_list) do
        local screen, condition, layout = table.unpack(sl_tuple)
        if screen ~= nil and condition then
            add_to_window_layout(app_name, window_title, screen, layout)
            found = true
            break
        end
    end

    -- If a layout could not be set due to the conditions above,
    -- fallback to maximise the window on the laptop screen
    if not found then
        add_to_window_layout(app_name, window_title, laptop_screen, hs.layout.maximized)
    end
end

-- The sort order of the entries is important; in case of issues, remove from the sorted block
-- keep-sorted start case=no
-- Use window_title = '' so the entry with no title appears first.
config_app('', hs.window.find('YouTube'), nil, {{laptop_screen, true, hs.layout.maximized}})
config_app('Activity Monitor', '', nil, {{wide_screen, true, hs.layout.right30}, {horizontal_screen, true, hs.layout.right50}})
config_app('App Store', '', nil, {{wide_screen, true, hs.layout.right50}, {horizontal_screen, true, hs.layout.right50}})
config_app('Authy Desktop', '', true, {{wide_screen, true, hs.layout.center_left}, {horizontal_screen, true, hs.layout.center_left}})
config_app('Bitwarden', '', false, {{wide_screen, true, hs.layout.right30}, {horizontal_screen, true, hs.layout.right30}})
config_app('Brave Browser Beta', '', nil, {{wide_screen, true, hs.layout.left50}, {horizontal_screen, true, hs.layout.left70}})
config_app('Brave Browser', '', nil, {{wide_screen, true, hs.layout.left50}, {horizontal_screen, true, hs.layout.left70}})
config_app('Code', '', nil, {{wide_screen, true, hs.layout.right50}, {horizontal_screen, true, hs.layout.right70}})
config_app('DeepL', '', hide_when_working, {{wide_screen, true, hs.layout.right50_top}, {horizontal_screen, true, hs.layout.right50_top}})
config_app('Docker Desktop', nil, nil, {{laptop_screen, true, hs.layout.top50}})
config_app('Finder', '', nil, {{wide_screen, true, hs.layout.right50_top}, {horizontal_screen, true, hs.layout.right50_top}})
config_app('Finder', 'consume-into-paperless', nil, {{wide_screen, true, hs.layout.right50_bottom}, {horizontal_screen, true, hs.layout.right50_bottom}})
config_app('Finder', 'import', nil, {{wide_screen, true, hs.layout.right50_bottom}, {horizontal_screen, true, hs.layout.right50_bottom}})
config_app('Finder', 'inbox', nil, {{wide_screen, true, hs.layout.right50_bottom}, {horizontal_screen, true, hs.layout.right50_bottom}})
config_app('Gnucash', '', nil, {{wide_screen, not at_the_office, hs.layout.left50}, {horizontal_screen, not at_the_office, hs.layout.left50}})
config_app('Hammerspoon', 'Hammerspoon Console', debug, {{laptop_screen, true, hs.layout.bottom50}})
config_app('iTerm2', '', nil, {{wide_screen, true, hs.layout.left50}, {horizontal_screen, true, hs.layout.left70}})
config_app('Logseq', '', hide_when_working, {{wide_screen, not at_the_office, hs.layout.left50}, {horizontal_screen, not at_the_office, hs.layout.left70}})
config_app('Notes', '', nil, {{wide_screen, true, hs.layout.right50}, {horizontal_screen, true, hs.layout.right50}})
config_app('Preview', '', nil, {{wide_screen, not at_the_office, hs.layout.left50}, {horizontal_screen, not at_the_office, hs.layout.left50}})
config_app('PyCharm', '', nil, {{wide_screen, true, hs.layout.right50}, {horizontal_screen, true, hs.layout.right70}})
config_app('RustRover-EAP', '', nil, {{wide_screen, true, hs.layout.right50}, {horizontal_screen, true, hs.layout.right70}})
config_app('ScanSnap Home', hs.window.find('- Scan'), nil, {{laptop_screen, true, hs.layout.right70}})
config_app('ScanSnap Home', nil, nil, {{laptop_screen, true, hs.geometry.rect(0.42, 0.23, 0.5, 0.5)}})
config_app('Signal', nil, hide_when_working, {{wide_screen, not at_the_office, hs.layout.left50}, {horizontal_screen, not at_the_office, hs.layout.left70}})
config_app('Skype', nil, nil, {{laptop_screen, true, hs.layout.maximized}})
config_app('Slack', '', nil, {{wide_screen, true, hs.layout.left50}, {horizontal_screen, true, hs.layout.left70}})
config_app('Speedtest', nil, nil, {{laptop_screen, true, hs.layout.left50}})
config_app('Spotify', nil, hide_when_working, {{laptop_screen, true, hs.layout.maximized}})
config_app('TeamViewer', nil, nil, {{laptop_screen, true, hs.layout.maximized}})
config_app('Telegram', '', hide_when_working, {{wide_screen, not at_the_office, hs.layout.left50}, {horizontal_screen, not at_the_office, hs.layout.left50}})
config_app('Terminal', '', nil, {{wide_screen, true, hs.layout.left50}, {horizontal_screen, true, hs.layout.left70}})
config_app('Todoist', nil, hide_when_working, {{laptop_screen, true, hs.layout.right70}})
config_app('Toggl Track', nil, hide_when_working, {{wide_screen, not at_the_office, hs.layout.left30}, {laptop_screen, true, hs.layout.left50}})
config_app('VLC', '', hide_when_working, {{wide_screen, not at_the_office, hs.layout.maximized}, {horizontal_screen, not at_the_office, hs.layout.maximized}})
config_app('WhatsApp', '', hide_when_working, {{wide_screen, not at_the_office, hs.layout.left50}, {horizontal_screen, not at_the_office, hs.layout.left70}})
config_app('zoom.us', 'zoom floating video window', nil, {{laptop_screen, true, hs.layout.left50}})
config_app('zoom.us', 'Zoom Meeting', nil, {{laptop_screen, true, hs.layout.maximized}})
config_app('zoom.us', 'zoom share statusbar window', nil, {{laptop_screen, true, hs.layout.right50}})
config_app('zoom.us', 'zoom share toolbar window', nil, {{laptop_screen, true, hs.layout.right70}})
config_app('zoom.us', 'Zoom', nil, {{wide_screen, true, hs.layout.right50}, {horizontal_screen, true, hs.layout.right70}})
-- keep-sorted end

-- TODO: I don't use a vertical screen anymore for some time; convert these other layouts on demand
if false and wide_screen == nil then
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
    if actual_window_title == nil or expected_window_title == nil then
        return false
    end

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
-- 'Preview' windows are not being moved for some reason
wf_stubborn_apps = hs.window.filter.new{'Authy Desktop', 'Logseq', 'ScanSnap Home'}
wf_stubborn_apps:subscribe(hs.window.filter.windowCreated, reposition_stubborn_windows)
