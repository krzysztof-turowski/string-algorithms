cmake_minimum_required(VERSION 3.4)
project(cbenchar)
add_subdirectory(../../lib/pybind11 ./build)
pybind11_add_module(cbenchar src/cbenchar.cpp)
