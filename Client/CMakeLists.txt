cmake_minimum_required(VERSION 3.12)

include(pico_sdk_import.cmake)

project(blimp C CXX)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_executable(blimp blimp.c)

target_compile_definitions(blimp
    WIFI_SSID=""
    WIFI_PASSWORD=""
    )

target_link_libraries(blimp pico_stdlib hardware_pwm pico_cyw43_arch_lwip_poll)

pico_add_extra_outputs(blimp)

