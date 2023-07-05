cmake_minimum_required(VERSION 3.4)
project(cbenchar)
add_subdirectory(pybind11)
pybind11_add_module(cbenchar src/cbenchar.cpp)