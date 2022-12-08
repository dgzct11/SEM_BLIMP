#include "pico/stdlib.h"
#include "hardware/pwm.h"

void setMillis(int servoPin, float millis) {
    pwm_set_gpio_level(servoPin, (millis/20000.f)*38062.f);
}

void setServo(int servoPin, float startMillis) {
    gpio_set_function(servoPin, GPIO_FUNC_PWM);
    uint slice_num = pwm_gpio_to_slice_num(servoPin);

    pwm_config config = pwm_get_default_config();
    pwm_config_set_clkdiv(&config, 64.f);
    pwm_config_set_wrap(&config, 39062.f);

    pwm_init(slice_num, &config, true);

    setMillis(servoPin, startMillis);
}

int main() {
    setServo(28, 1400);

    while (true) {
        setServo(28, 400);
        sleep_ms(1000);
        setServo(28, 1400);
        sleep_ms(1000);
        setServo(28, 2400);
        sleep_ms(1000);
    }
}
