cmake_minimum_required(VERSION 3.12)

include(pico_sdk_import.cmake)

project(servo C CXX)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

set(PICO_EXAMPLES_PATH ${PROJECT_SOURCE_DIR})

pico_sdk_init()

add_executable(servo servo.c)

target_link_libraries(servo PRIVATE pico_stdlib hardware_pwm)

pico_add_extra_outputs(servo)

