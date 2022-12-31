#include <stdio.h>
#include <string.h>
#include <math.h>
#include "esp_attr.h" // help intellisense with freertos/task.h
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_sleep.h"
#include "driver/gpio.h"
#include "sdkconfig.h"
#include "pwm_audio.h"

#include "gc9a01.h"
#include "font.h"

extern font_t font_roboto_mono_regular_11x24;
font_t * smallFont = &font_roboto_mono_regular_11x24;

extern font_t font_roboto_mono_regular_14x32;
font_t * bigFont = &font_roboto_mono_regular_14x32;

#define STACK_SIZE 2048

#define POWER_DISABLE 27
#define B1 37
#define B2 39
#define B3 39
#define USB_CONNECTED 7
#define BATTERY_CHARGING 4
#define BATTERY_ADC 34
#define PIEZO 5



// 'SCL': 22,
// 'SDA': 21,

void deepsleep() {
    esp_sleep_enable_ext0_wakeup(B3, 0);
    while (gpio_get_level(B3) == 0) {
        // wait for it to go high before going to sleep so it doesn't wake up immediately
        vTaskDelay(1 / portTICK_PERIOD_MS);
    }
    esp_deep_sleep_start();
}

uint16_t rgb565(float r, float g, float b) {
    uint16_t _r = r * 31;
    uint16_t _g = g * 63;
    uint16_t _b = b * 31;
    return _r << 11 | _g << 5 | _b;
}

void LCD(void * arg) {
    //uint16_t Color;
    GC9A01_Init();
    GC9A01_SetBL(64);

    for(int i=0; i<60; ++i) {
        //Color = rand();
        //GC9A01_FillRect(0, 0, 239, 239, 0);
        char * smallText = "2022/12/30";
        uint8_t smallLength = strlen(smallText);
        GC9A01_Text(smallFont, smallText, 120-((float)smallLength/2*smallFont->width), 120-smallFont->height-0.5*bigFont->height, rgb565(1, 1, 1), 0);
        char * bigText = "01:02:45";
        uint8_t bigLength = strlen(bigText);
        GC9A01_Text(bigFont, bigText, 120-((float)bigLength/2*bigFont->width), 120-bigFont->height/2, rgb565(1, 0, 1), 0);

        GC9A01_Update();
        vTaskDelay(1000/portTICK_PERIOD_MS);
    }

    deepsleep();
}

void setup_io(void) {
    // outputs
    gpio_config_t io_conf = {};
    io_conf.intr_type = GPIO_INTR_DISABLE;
    io_conf.mode = GPIO_MODE_OUTPUT;
    io_conf.pin_bit_mask = ((1ULL<<POWER_DISABLE));
    io_conf.pull_down_en = 0;
    io_conf.pull_up_en = 0;
    gpio_config(&io_conf);

    gpio_set_level(POWER_DISABLE, 0);

    // inputs with pull-ups
    io_conf.intr_type = GPIO_INTR_DISABLE;
    io_conf.mode = GPIO_MODE_INPUT;
    io_conf.pin_bit_mask = ((1ULL<<USB_CONNECTED) | (1ULL<<BATTERY_CHARGING));
    io_conf.pull_down_en = 0;
    io_conf.pull_up_en = 1;
    gpio_config(&io_conf);

    // inputs without pull-ups
    io_conf.intr_type = GPIO_INTR_DISABLE;
    io_conf.mode = GPIO_MODE_INPUT;
    io_conf.pin_bit_mask = ((1ULL<<B1) | (1ULL<<B2) | (1ULL<<B3));
    io_conf.pull_down_en = 0;
    io_conf.pull_up_en = 0;
    gpio_config(&io_conf);
}


void app_main(void) {
    esp_err_t ret;

    setup_io();

    TaskHandle_t LCDHandle;
    xTaskCreate(LCD, "Test LCD", STACK_SIZE, NULL, tskIDLE_PRIORITY, &LCDHandle);
    configASSERT(LCDHandle);

    /*
    pwm_audio_config_t pac;
    pac.duty_resolution    = LEDC_TIMER_8_BIT;
    pac.gpio_num_left      = PIEZO;
    pac.ledc_channel_left  = LEDC_CHANNEL_1;
    pac.gpio_num_right     = -1;
    pac.ledc_channel_right = LEDC_CHANNEL_2;
    pac.ledc_timer_sel     = LEDC_TIMER_1;
    pac.tg_num             = TIMER_GROUP_1;
    pac.timer_num          = TIMER_1;
    pac.ringbuf_len        = 1024 * 8;
    ret = pwm_audio_init(&pac);
    assert(ret==ESP_OK);

    ret = pwm_audio_set_param(44100, 8, 1);
    assert(ret==ESP_OK);

    ret = pwm_audio_start();
    assert(ret==ESP_OK);

    const size_t buffer_size = 4096;
    uint8_t *buffer = malloc(buffer_size);
    //for (int i=0; i<buffer_size; i++) {
    //    buffer[i] = 0;
    //}

    // how much to write before we continue
    const size_t batch_size = 1024;

    size_t cnt;
    size_t write_pos = 0;
    size_t read_pos = 0;
    size_t write_available = buffer_size;
    size_t total_written = 0;

    // B========
    // ===B=====
    // ========B

    // ====R===W
    // R===W====
    // ====R===W

    // ====W===R
    // W===R====
    // ====W===B

    // 5 seconds of audio
    const float PI_2 = 6.283185307179f;
    int phase = 0;
    int volume = 0;
    int diff = 3;
    while (total_written < 5*44100) {
        // fill the buffer
        while (write_available > 0) {
            //buffer[write_pos] = phase * (((float)volume)/127.0);
            buffer[write_pos] = (phase < 128) ? 128+volume : 127-volume;
            //buffer[write_pos] = (random() % 256) * (((float)volume)/127);
            //buffer[write_pos] = 127.8f * sinf(PI_2 * (float)phase / (float)256);// * (float)volume/(float)127 + 127-volume;

            ++write_pos;
            if (write_pos == buffer_size) {
                write_pos = 0;
            }

            ++phase;
            if (phase >= 256) { 
                phase -= 256;
                volume += diff;
                if (volume > 127 || volume < 0) {
                    diff *= -1;
                    volume += diff;    
                }
                //printf("%d\n", volume);
            }

            --write_available;
        }

        // either copy the part at the end or the part up to the write position
        // (ie. don't try and wrap around the end in one operation)
        size_t len = read_pos >= write_pos ? buffer_size - read_pos : write_pos - read_pos;
        if (len > batch_size) {
            len = batch_size;
        }
        ret = pwm_audio_write(buffer+read_pos, len, &cnt, 1000 / portTICK_PERIOD_MS);
        assert(ret==ESP_OK);
        //pwm_audio_write(buffer+read_pos, len, &cnt, 0); // don't wait

        total_written += cnt;
        read_pos += cnt;
        if (read_pos >= buffer_size) {
            read_pos -= buffer_size;
        }
        write_available += cnt;

        //printf("read_pos=%d, write_pos=%d, write_available=%d, len=%d, cnt=%d\n", read_pos, write_pos, write_available, len, cnt);


        // sleep a little bit
        vTaskDelay(10/portTICK_PERIOD_MS);
    }

    ret = pwm_audio_stop();
    assert(ret==ESP_OK);

    ret = pwm_audio_deinit();
    assert(ret==ESP_OK);

    //for (int i = 0; i < buffer_size; i++) {
    //    printf("%d, %d\n", i, buffer[i]);
    //}

    free(buffer);

    deepsleep();
    */
}