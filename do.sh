#!/bin/bash
#
# Misc utilities

action=$1
shift

case $action in

  pygrep)
    find . -name \*.py | xargs grep "$@"
    ;;

  *)
    echo "Invalid action '$action'"
    exit 1
    ;;
esac
