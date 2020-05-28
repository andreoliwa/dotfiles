#!/usr/bin/env bash
if [[ $OSTYPE == darwin* ]]; then
    LATEST_JAVA_8="$(find /Library/Java/JavaVirtualMachines -type d -depth 1 | sort --version-sort --reverse | grep jdk1.8 | head -n 1)"
    if [ -z "$LATEST_JAVA_8" ]; then
        echo "Java 8 not found"
    else
        export PENTAHO_JAVA_HOME="${LATEST_JAVA_8}/Contents/Home"
    fi
fi
