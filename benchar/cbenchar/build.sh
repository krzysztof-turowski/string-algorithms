#!/bin/bash

cd "$(dirname "${BASH_SOURCE[0]}")"
rm ./build/*.so
git submodule update --init
cmake -B./build
(cd ./build && make)