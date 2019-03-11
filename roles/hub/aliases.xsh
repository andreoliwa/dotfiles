# Add git aliases for hub
hub_alias = $(hub alias -s bash)
source-bash @(hub_alias)

aliases["hi"] = 'hub pull-request -i'
