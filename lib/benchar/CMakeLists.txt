cmake_minimum_required(VERSION 3.20)

project(cbenchar)

include(FetchContent)

set(FETCHCONTENT_QUIET FALSE)

#<pybind11>
FetchContent_Declare(
    pybind11
    GIT_REPOSITORY "https://github.com/pybind/pybind11.git"
    GIT_TAG stable
    GIT_PROGRESS TRUE
    SOURCE_DIR "${CMAKE_SOURCE_DIR}/../../lib/pybind11"
  )
FetchContent_MakeAvailable(pybind11)
#</pybind11>

pybind11_add_module(cbenchar cbenchar.cpp)
