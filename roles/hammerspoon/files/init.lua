-- Documentation: http://www.hammerspoon.org/
-- Examples:
-- https://github.com/derekwyatt/dotfiles/blob/master/hammerspoon-init.lua
-- https://github.com/fikovnik/ShiftIt/wiki/The-Hammerspoon-Alternative
-- https://github.com/scottwhudson/Lunette

hs.window.animationDuration = 0

-- http://www.hammerspoon.org/docs/hs.application.html#find
-- To find an application, run this on the console:
-- hs.application.find('brave')

-- http://www.hammerspoon.org/docs/hs.layout.html
local verticalScreen = "DELL P2414H"
local horizontalScreen = "HP E241i"
local laptopScreen = "Color LCD"
local windowLayout = {
    -- Left
    {"iTerm2", nil, verticalScreen, hs.layout.maximized, nil, nil},
    {"Zulip", nil, verticalScreen, hs.layout.maximized, nil, nil},

    -- Center
    {"Code", nil, horizontalScreen, hs.layout.maximized, nil, nil},
    {"Brave Browser", nil, horizontalScreen, hs.layout.maximized, nil, nil},
    {"Slack", nil, horizontalScreen, hs.layout.maximized, nil, nil},
    {"Vivaldi", nil, horizontalScreen, hs.layout.maximized, nil, nil},
    {"Skype", nil, horizontalScreen, hs.layout.maximized, nil, nil},
    {"PyCharm", nil, horizontalScreen, hs.layout.maximized, nil, nil},
    {"App Store", nil, horizontalScreen, hs.layout.maximized, nil, nil},
    {"TogglDesktop", nil, horizontalScreen, hs.layout.right30, nil, nil},
    {"PhpStorm", nil, horizontalScreen, hs.layout.maximized, nil, nil},

    -- Right
    {nil, hs.window.find('YouTube'), laptopScreen, hs.layout.maximized, nil, nil},
    {"Spotify", nil, laptopScreen, hs.layout.maximized, nil, nil},
    {"Telegram", nil, laptopScreen, hs.layout.maximized, nil, nil},
    {"WhatsApp", nil, laptopScreen, hs.layout.maximized, nil, nil},
    {"Signal", nil, laptopScreen, hs.layout.maximized, nil, nil},
    {"Hammerspoon", "Hammerspoon Console", laptopScreen, hs.layout.maximized, nil, nil},
}
hs.layout.apply(windowLayout)
