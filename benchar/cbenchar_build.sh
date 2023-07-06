#!/bin/bash

cd "$(dirname "${BASH_SOURCE[0]}")"
cmake -B./build
cd ./build && make
