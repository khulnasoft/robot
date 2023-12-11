#!/bin/bash -e
docker run --rm -it -v "$(pwd)":/aikit_robot khulnasoft/robot:latest python3 -m pytest aikit_robot_tests/
