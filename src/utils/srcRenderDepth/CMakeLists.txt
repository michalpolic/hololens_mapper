cmake_minimum_required(VERSION 3.4...3.18)
project(renderDepth)

find_package(pybind11)
pybind11_add_module(renderDepth renderDepth.cpp)

install(TARGETS renderDepth
        DESTINATION ${CMAKE_SOURCE_DIR}/..
)