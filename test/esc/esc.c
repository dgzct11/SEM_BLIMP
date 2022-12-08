#include "pico/stdlib.h"
#include "hardware/pwm.h"

#define LEFT 9
#define RIGHT 1
#define MAX 2000
#define MIN 1000

void setMillis(int servoPin, float millis) {
    pwm_set_gpio_level(servoPin, (millis/20000.f)*38062.f);
}

void setESC(int servoPin, float startMillis) {
    gpio_set_function(servoPin, GPIO_FUNC_PWM);
    uint slice_num = pwm_gpio_to_slice_num(servoPin);

    pwm_config config = pwm_get_default_config();
    pwm_config_set_clkdiv(&config, 64.f);
    pwm_config_set_wrap(&config, 39062.f);

    pwm_init(slice_num, &config, true);

    setMillis(servoPin, startMillis);
}

int main() {
    setESC(LEFT, MAX);
    setESC(RIGHT, MAX);
    sleep_ms(2000);

    setMillis(LEFT, 0);
    setMillis(RIGHT, 0);
    sleep_ms(2000);

    setMillis(LEFT, MIN);
    setMillis(RIGHT, MIN);
    sleep_ms(2000);

    setMillis(RIGHT, MAX);
    setMillis(RIGHT, MIN);
}
