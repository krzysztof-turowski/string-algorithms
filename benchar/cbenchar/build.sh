#!/bin/bash

cd "$(dirname "${BASH_SOURCE[0]}")"
git submodule update --init
cmake -B./build
(cd ./build && make)
