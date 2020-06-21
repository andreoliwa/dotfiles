#!/usr/bin/env bash
# Autocomplete tags for todoist-cli
# TODO: this is only a test, a WIP

__todoist_completion() {
    local cur prev opts query
    COMPREPLY=()
    opts=
    cur=$2
    prev=$3

    # echo -e "\nCOMP_WORDS = $COMP_CWORD\n"
    case "${prev}" in
        todoist)
            opts="list l show completed-list c-l cl add a modify m close c delete d labels projects karma sync s quick q \
                help h --header --color --csv --debug --namespace --indent --project-namespace --help -h --version -v"
            ;;
        add|a)
            opts="--priority -p --label-ids -L --project-id -P --project-name -N --date -d --reminder -r"
            ;;
        --priority)
            opts="1 2 3 4"
            ;;
        --label-ids)
            query=
            test -n "$cur" && query="-q $cur"
            # --height=10 --no-clear
            COMPREPLY=( $(todoist labels | fzf --select-1 --exit-0 --multi ${query} | cut -f 1 -d ' ' | paste -d, -s -) )
            ;;
    esac
    test -n "$opts" && COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
}

complete -F __todoist_completion todoist
