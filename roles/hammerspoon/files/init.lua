-- https://www.tutorialspoint.com/lua/
-- Documentation: http://www.hammerspoon.org/
-- Code: https://github.com/Hammerspoon/hammerspoon
-- Examples:
-- https://github.com/derekwyatt/dotfiles/blob/master/hammerspoon-init.lua
-- https://github.com/fikovnik/ShiftIt/wiki/The-Hammerspoon-Alternative
-- https://github.com/scottwhudson/Lunette

-- Configuration
local debug = false
local benchmark_enabled = false

-- Reposition all stubborn apps that don't save their last window positions
-- macOS 'Preview' windows are not being moved for some reason
-- List of apps to reposition on window creation
local stubbornApps = {
    -- keep-sorted start
    "Authy Desktop",
    "FaceTime",
    "Logseq",
    "Preview",
    "ScanSnap Home",
    "SimpleFloatingClock",
    -- "Telegram", -- Commenting out because it moves the right-click menus too
    -- keep-sorted end
}

-- Delay in seconds before repositioning stubborn apps (gives time for app to fully load)
local stubbornAppDelay = 0.5

-- Per-app delays for stubborn apps that need more time (overrides stubbornAppDelay)
local stubbornAppDelays = {
    ["Logseq"] = 1.0, -- Logseq might need more time to fully load
    ["Preview"] = 0.3, -- Preview is usually quick
}

-- List of apps to auto-hide on focus change (matching by appName only)
local autoHideApps = {
    -- keep-sorted start
    "Brave Browser Beta",
    "Code",
    "Logseq",
    "Telegram",
    "WhatsApp",
    -- keep-sorted end
}

-- Performance benchmarking utilities (defined early so they can be used throughout)
local benchmark_timers = {}

function benchmark_start(name)
    if benchmark_enabled then
        benchmark_timers[name] = hs.timer.secondsSinceEpoch()
    end
end

function benchmark_end(name)
    if benchmark_enabled and benchmark_timers[name] then
        local duration = hs.timer.secondsSinceEpoch() - benchmark_timers[name]
        print(string.format("⏱️  %s took %.3f seconds", name, duration))
        benchmark_timers[name] = nil
    end
end

function benchmark(name, func)
    if benchmark_enabled then
        local start = hs.timer.secondsSinceEpoch()
        func()
        local duration = hs.timer.secondsSinceEpoch() - start
        print(string.format("⏱️  %s took %.3f seconds", name, duration))
    else
        func()
    end
end

hs.window.animationDuration = 0
hs.console.clearConsole()

-- Start timing the entire config load
benchmark_start("total_config_load")

-- hs.wifi not showing current network in Sonoma 14.2.1
-- Workaround: https://github.com/Hammerspoon/hammerspoon/issues/3537#issuecomment-1743870568
-- See also https://github.com/Hammerspoon/hammerspoon/issues/3591#issuecomment-1988453778
print(hs.location.get())

print('Debugging? ' .. tostring(debug))

function debug_print(message)
    if debug then
        print(message)
    end
end

-- Because this stupid language doesn't have a proper ternary operator
-- https://stackoverflow.com/questions/5525817/inline-conditions-in-lua-a-b-yes-no
function ternary(condition, true_value, false_value)
    if condition then
        return true_value
    else
        return false_value
    end
end

benchmark_start("wifi_checks")

-- Only do expensive WiFi scanning when debugging
if debug then
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
end

-- Just get current network (fast)
local currentNetwork = hs.wifi.currentNetwork()
if currentNetwork then
    debug_print('WiFi network: ' .. currentNetwork)
else
    debug_print('WiFi network: Not connected')
end

local at_the_office = currentNetwork and string.match(currentNetwork, 'wolt') ~= nil
benchmark_end("wifi_checks")
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
        { { "alt", "cmd" }, "U" },
    },
    topRight = {
        { { "alt", "cmd" }, "I" },
    },
    bottomLeft = {
        { { "alt", "cmd" }, "J" },
    },
    bottomRight = {
        { { "alt", "cmd" }, "K" },
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
local wide_screens = { '34w%-20', '34w%-30' }
for index, screen_id in ipairs(wide_screens) do
    wide_screen = hs.screen.find(screen_id)
    if wide_screen ~= nil then
        break
    end
end

local horizontal_screen = nil
local horizontal_screens = { 'DELL', }
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
hs.layout.right40 = hs.geometry.rect(0.60, 0, 0.40, 1)
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
    local config = { app_name, window_title, screen, layout, nil, nil }
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

for _, jetbrains_ide in ipairs({ 'GoLand', 'PyCharm', 'RustRover', 'IntelliJ IDEA Ultimate' }) do
    config_app(jetbrains_ide, '', nil, { { wide_screen, true, hs.layout.right50 }, { horizontal_screen, true, hs.layout.right70 } })
    config_app(jetbrains_ide, 'Augment -', nil, { { laptop_screen, true, hs.layout.left50 } })
    config_app(jetbrains_ide, 'Run -', nil, { { laptop_screen, true, hs.layout.right50_top } })
end

-- The sort order of the entries is important; in case of issues, remove from the sorted block
-- keep-sorted start case=no
-- Use window_title = '' so the entry with no title appears first.
config_app('', hs.window.find('YouTube'), nil, { { laptop_screen, true, hs.layout.maximized } })
config_app('Activity Monitor', '', nil, { { wide_screen, true, hs.layout.right30 }, { horizontal_screen, true, hs.layout.right50 } })
config_app('Bitwarden', '', false, { { wide_screen, true, hs.layout.right30 }, { horizontal_screen, true, hs.layout.right30 } })
config_app('Brave Browser Beta', '', hide_when_working, { { wide_screen, true, hs.layout.right50 }, { horizontal_screen, true, hs.layout.right70 } })
config_app('Brave Browser', '', nil, { { wide_screen, true, hs.layout.right50 }, { horizontal_screen, true, hs.layout.right70 } })
config_app('Code', '', nil, { { wide_screen, true, hs.layout.right50 }, { horizontal_screen, true, hs.layout.right70 } })
config_app('DeepL', '', hide_when_working, { { wide_screen, true, hs.layout.right50_top }, { horizontal_screen, true, hs.layout.right50_top } })
config_app('FaceTime', nil, nil, { { laptop_screen, true, hs.layout.maximized } })
config_app('Finder', '', nil, { { wide_screen, true, hs.layout.right50_top }, { horizontal_screen, true, hs.layout.right50_top } })
config_app('Finder', 'consume-into-paperless', nil, { { wide_screen, true, hs.layout.right50_bottom }, { horizontal_screen, true, hs.layout.right50_bottom } })
config_app('Finder', 'import', nil, { { wide_screen, true, hs.layout.right50_bottom }, { horizontal_screen, true, hs.layout.right50_bottom } })
config_app('Finder', 'inbox', nil, { { wide_screen, true, hs.layout.right50_bottom }, { horizontal_screen, true, hs.layout.right50_bottom } })
config_app('Finicky', '', debug, { { laptop_screen, true, hs.layout.bottom50 } })
config_app('Gnucash', '', nil, { { wide_screen, not at_the_office, hs.layout.left50 }, { horizontal_screen, not at_the_office, hs.layout.left50 } })
config_app('Google Chrome', '', hide_when_working, { { wide_screen, true, hs.layout.right50 }, { horizontal_screen, true, hs.layout.right70 } })
config_app('Hammerspoon', 'Hammerspoon Console', debug, { { laptop_screen, true, hs.layout.bottom50 } })
config_app('iTerm2', '', nil, { { wide_screen, true, hs.layout.left50 }, { horizontal_screen, true, hs.layout.left70 } })
config_app('Logseq', '', hide_when_working, { { wide_screen, not at_the_office, hs.layout.left50 }, { horizontal_screen, not at_the_office, hs.layout.left70 } })
config_app('Mail', '', false, { { laptop_screen, true, hs.layout.bottom50 } })
config_app('OrbStack', '', false, { { laptop_screen, true, hs.layout.bottom50 } })
config_app('Preview', '', nil, { { wide_screen, not at_the_office, hs.layout.left50 }, { horizontal_screen, not at_the_office, hs.layout.left50 }, { laptop_screen, true, hs.layout.maximized } })
config_app('RustRover', '', nil, { { wide_screen, true, hs.layout.right50 }, { horizontal_screen, true, hs.layout.right70 } })
config_app('ScanSnap Home', hs.window.find('- Scan'), nil, { { laptop_screen, true, hs.layout.right70 } })
config_app('ScanSnap Home', nil, nil, { { laptop_screen, true, hs.geometry.rect(0.42, 0.23, 0.5, 0.5) } })
config_app('Signal', nil, hide_when_working, { { wide_screen, not at_the_office, hs.layout.left50 }, { horizontal_screen, not at_the_office, hs.layout.left70 } })
config_app('SimpleFloatingClock', nil, nil, { { laptop_screen, true, hs.layout.right40 } })
config_app('Slack', '', nil, { { wide_screen, true, hs.layout.left50 }, { horizontal_screen, true, hs.layout.left70 } })
config_app('Telegram', '', hide_when_working, { { wide_screen, not at_the_office, hs.layout.left50 }, { horizontal_screen, not at_the_office, hs.layout.left50 } })
config_app('Terminal', '', nil, { { wide_screen, true, hs.layout.left50 }, { horizontal_screen, true, hs.layout.left70 } })
config_app('VLC', '', hide_when_working, { { wide_screen, not at_the_office, hs.layout.maximized }, { horizontal_screen, not at_the_office, hs.layout.maximized } })
config_app('WhatsApp', '', hide_when_working, { { wide_screen, not at_the_office, hs.layout.left50 }, { horizontal_screen, not at_the_office, hs.layout.left70 } })
config_app('YouTube Music', nil, hide_when_working, { { laptop_screen, true, hs.layout.right70 } })
config_app('zoom.us', 'zoom floating video window', nil, { { laptop_screen, true, hs.layout.left50 } })
config_app('zoom.us', 'Zoom Meeting', nil, { { laptop_screen, true, hs.layout.maximized } })
config_app('zoom.us', 'zoom share statusbar window', nil, { { laptop_screen, true, hs.layout.right50 } })
config_app('zoom.us', 'zoom share toolbar window', nil, { { laptop_screen, true, hs.layout.right70 } })
config_app('zoom.us', 'Zoom', nil, { { laptop_screen, true, hs.layout.maximized }, { wide_screen, true, hs.layout.right50 }, { horizontal_screen, true, hs.layout.right70 } })
-- keep-sorted end

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
    benchmark_start("apply_window_layout")

    if not hs.window or not hs.window.allWindows then
        hs.alert.show("hs.window or hs.window.allWindows is missing!")
        return
    end

    -- Filter out applications that don't exist to prevent nil errors
    -- Optimization: Build a set of running apps first to avoid repeated lookups
    benchmark_start("filter_layout")
    local running_apps = {}
    for _, app in ipairs(hs.application.runningApplications()) do
        running_apps[app:name()] = app
    end

    local filtered_layout = {}
    for _, config in ipairs(window_layout) do
        local app_name = config[1]
        local window_title = config[2]

        if app_name and app_name ~= "" then
            -- Normal app case: check if app exists in our running apps set
            local app = running_apps[app_name]
            if app then
                debug_print("Including app in layout: " .. app_name)
                table.insert(filtered_layout, config)
            else
                debug_print("App not running: " .. app_name)
            end
        elseif app_name == "" and window_title then
            -- Special case: empty app name with specific window (like YouTube)
            if type(window_title) == "userdata" and window_title.isValid and window_title:isValid() then
                debug_print("Including window in layout: " .. tostring(window_title))
                table.insert(filtered_layout, config)
            else
                debug_print("Window not found or invalid, skipping: " .. tostring(window_title))
            end
        else
            -- Skip invalid configurations
            debug_print("Skipping invalid config: app_name=" .. tostring(app_name) .. ", window_title=" .. tostring(window_title))
        end
    end

    benchmark_end("filter_layout")

    -- Debug: print the filtered layout before applying
    debug_print("Filtered layout contains " .. #filtered_layout .. " entries:")
    for i, config in ipairs(filtered_layout) do
        debug_print("  [" .. i .. "] app_name=" .. tostring(config[1]) .. ", window_title=" .. tostring(config[2]) .. ", screen=" .. tostring(config[3]))
    end

    -- Final safety check: verify all apps in filtered layout actually exist and have allWindows method
    -- Optimization: Reuse the running_apps set from above
    benchmark_start("safety_check")
    local safe_layout = {}
    for _, config in ipairs(filtered_layout) do
        local app_name = config[1]
        if app_name and app_name ~= "" then
            local app = running_apps[app_name]
            if app and app.allWindows then
                table.insert(safe_layout, config)
                debug_print("Final check passed for: " .. app_name)
            else
                debug_print("Final check failed for: " .. app_name)
            end
        else
            -- Keep non-app entries (like window-specific configs)
            table.insert(safe_layout, config)
            debug_print("Keeping non-app config: " .. tostring(config[1]))
        end
    end

    benchmark_end("safety_check")

    debug_print("Safe layout contains " .. #safe_layout .. " entries")

    -- http://www.hammerspoon.org/docs/hs.layout.html
    -- Use pcall to prevent crashes from layout issues
    benchmark_start("layout_apply")
    local success, error_msg = pcall(function()
        hs.layout.apply(safe_layout, compare_window_title)
    end)
    benchmark_end("layout_apply")

    if not success then
        print("Layout application failed: " .. tostring(error_msg))
        print("Skipping layout application to prevent crash")
    else
        debug_print("Layout applied successfully")
    end

    benchmark_end("apply_window_layout")
end

benchmark("initial_layout_apply", function()
    apply_window_layout()
end)

-- Apply window layout when a monitor is connected/disconnected
-- Newsflash: it doesn't work. ;)
-- http://www.hammerspoon.org/docs/hs.screen.watcher.html
hs.screen.watcher.new(apply_window_layout)

-- Utility: simple string match against a list
local function isInList(value, list)
    for _, v in ipairs(list) do
        if v == value then
            return true
        end
    end
    return false
end

-- Utility: manually trigger repositioning for a specific app (useful for testing)
local function repositionApp(appName)
    if not appName then
        print("Usage: repositionApp('AppName')")
        return
    end

    local app = hs.application.find(appName)
    if not app then
        print("App not found: " .. appName)
        return
    end

    print("Manually repositioning app: " .. appName)
    apply_window_layout()
end

-- Utility: safely hide an app with retry logic
local function safeHideApp(appName, maxRetries)
    maxRetries = maxRetries or 3

    local app = hs.application.find(appName)

    if not app then
        debug_print("App not found: " .. appName)
        return false
    end

    -- Don't try to hide if app is already hidden
    if app:isHidden() then
        debug_print("App already hidden: " .. appName)
        return true
    end

    -- Don't hide if app has no windows (might be a background process)
    local windows = app:allWindows()
    if not windows or #windows == 0 then
        debug_print("App has no windows, skipping hide: " .. appName)
        return true
    end

    local function attemptHide(retryCount)
        local success = app:hide()
        debug_print("Hiding app: " .. appName .. " -> " .. tostring(success) .. " (attempt " .. retryCount .. ")")

        if success then
            return true
        elseif retryCount < maxRetries then
            -- Retry after a short delay
            hs.timer.doAfter(0.1, function()
                attemptHide(retryCount + 1)
            end)
        else
            debug_print("Failed to hide app after " .. maxRetries .. " attempts: " .. appName)
            return false
        end
    end

    return attemptHide(1)
end

-- Function to handle auto-hiding apps when focus changes
local function handleAutoHide(focusedAppName)
    benchmark_start("handleAutoHide")

    if not focusedAppName or not at_the_office then
        benchmark_end("handleAutoHide")
        return
    end

    debug_print("App focused: " .. focusedAppName)

    -- Add a small delay to ensure focus change is complete
    hs.timer.doAfter(0.05, function()
        benchmark_start("auto_hide_loop")
        -- Hide all apps in autoHideApps list except the one just focused
        for _, appToHide in ipairs(autoHideApps) do
            if appToHide ~= focusedAppName then
                safeHideApp(appToHide)
            end
        end
        benchmark_end("auto_hide_loop")
    end)

    benchmark_end("handleAutoHide")
end

-- Unified window event handler (for stubborn app repositioning)
local function unifiedWindowHandler(window, appName, event)
    benchmark_start("unifiedWindowHandler")

    if not window then
        benchmark_end("unifiedWindowHandler")
        return
    end

    if event == "windowCreated" then
        if isInList(appName, stubbornApps) then
            -- Use per-app delay if configured, otherwise use default delay
            local delay = stubbornAppDelays[appName] or stubbornAppDelay
            debug_print("Repositioning stubborn app window: " .. appName .. " (with " .. delay .. "s delay)")
            -- Add delay to give the app time to fully load and show up
            hs.timer.doAfter(delay, function()
                debug_print("Applying layout for stubborn app: " .. appName)
                apply_window_layout()
            end)
        end

    elseif event == "windowFocused" then
        if at_the_office then
            -- Also trigger auto-hide from window focus for redundancy
            handleAutoHide(appName)
        end
    end

    benchmark_end("unifiedWindowHandler")
end

-- Create a shared filter for window behaviors (repositioning stubborn apps)
local sharedFilter = hs.window.filter.new()
sharedFilter:subscribe({
    hs.window.filter.windowCreated,
    hs.window.filter.windowFocused
}, unifiedWindowHandler)

-- Create an application watcher for reliable app focus detection
local appWatcher = hs.application.watcher.new(function(appName, eventType, appObject)
    if eventType == hs.application.watcher.activated then
        handleAutoHide(appName)
    end
end)
appWatcher:start()

benchmark_end("total_config_load")
print("========================================")
print("🎯 Hammerspoon config loaded successfully!")
print("========================================")

hs.alert.show("Hammerspoon: window filter and app watcher running")
