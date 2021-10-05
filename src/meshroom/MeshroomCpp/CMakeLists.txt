cmake_minimum_required(VERSION 3.13)

project(rd VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 14 CACHE STRING "C++ version selection")  # or 11, 14, 17, 20
set(CMAKE_CXX_STANDARD_REQUIRED ON)  # optional, ensure standard is supported
set(CMAKE_CXX_EXTENSIONS OFF)  # optional, keep compiler extensionsn off
set(CMAKE_INSTALL_PREFIX CMAKE_SOURCE_DIR)

#add_library(renderDepth STATIC renderDepth.cpp)
#set_target_properties(renderDepth PROPERTIES POSITION_INDEPENDENT_CODE ON)

set(pybind11_DIR "~/anaconda3/envs/patch2pix/share/cmake/pybind11")
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)
pybind11_add_module(MeshroomCpp MeshroomCpp.cpp)
#target_link_libraries(pymodule PRIVATE renderDepth)


install(TARGETS MeshroomCpp
        DESTINATION ${CMAKE_SOURCE_DIR}/..
)