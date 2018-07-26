#!/bin/bash

wait_deps () {
  ./wait-for-it.sh mysql:3306 -t 60
}

case $1 in
  "run")
    python app.py
    wait_deps
    ;;
  *)
    echo "usage: $0 [run]"
    exit 1
    ;;
esac
