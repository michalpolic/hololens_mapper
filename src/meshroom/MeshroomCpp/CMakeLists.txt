cmake_minimum_required(VERSION 3.4...3.18)
project(MeshroomCpp)

find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED PATHS ${pybind11_DIR} NO_DEFAULT_PATH)
pybind11_add_module(MeshroomCpp MeshroomCpp.cpp)

install(TARGETS MeshroomCpp
        DESTINATION ${CMAKE_SOURCE_DIR}/..
)
