cmake_minimum_required(VERSION 3.12)

include(pico_sdk_import.cmake)

project(blink C CXX)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

set(PICO_EXAMPLES_PATH ${PROJECT_SOURCE_DIR})

pico_sdk_init()

add_executable(led_test led_test.c)

target_link_libraries(led_test pico_stdlib)

pico_add_extra_outputs(led_test)

