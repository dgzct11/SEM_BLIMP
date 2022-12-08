#include "pico/stdlib.h"

int main() {
    gpio_init("LED");
    gpio_set_dir("LED", GPIO_OUT);

    while (true) {
        gpio_put("LED", 1);
        sleep_ms(1000);
        gpio_put("LED", 0);
        sleep_ms(1000);
    }
}
