cmake_minimum_required(VERSION 3.4...3.18)
project(MeshroomCpp)

find_package(pybind11)
pybind11_add_module(MeshroomCpp MeshroomCpp.cpp)

install(TARGETS MeshroomCpp
        DESTINATION ${CMAKE_SOURCE_DIR}/..
)