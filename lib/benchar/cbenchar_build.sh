#!/bin/bash

cd ./lib/benchar
cmake -B./build
cd ./build && make
