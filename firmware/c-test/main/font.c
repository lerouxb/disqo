#include "font.h"

#include <stdio.h>
#include <string.h>
#include "gc9a01.h"

typedef struct _rgb_t {
    float r;
    float g;
    float b;
} rgb_t;

rgb_t parse565(uint16_t color) {
    rgb_t rgb = {
        .r = ((color >> 11) & 31) / 31,
        .g = ((color >> 5) & 63) / 63,
        .b = (color & 31) / 31
    };

    return rgb;
}
uint16_t format565(rgb_t rgb) {
    uint16_t r = rgb.r * 31;
    uint16_t g = rgb.g * 63;
    uint16_t b = rgb.b * 31;
    return r << 11 | g << 5 | b;
}

static void GC9A01_Char(font_t *font, char c, uint16_t x, uint16_t y, uint16_t *palette) {
    uint16_t width = font->width;
    uint16_t height = font->height;
    uint16_t bpp = font->bpp;
    uint8_t *bitmap = font->bitmap;
    uint32_t bitsPerChar = width * height * bpp;

    // figure out the character, byte, bit index
    uint8_t charIndex = c - 32;
    uint32_t bytesPerChar = bitsPerChar / 8;
    uint32_t byteIndex = bytesPerChar * charIndex;

    // loop through the pixels and print based on the palettte
    uint16_t xp = x;
    uint16_t yp = y;
    for (int i = 0; i < bytesPerChar; i++) {
        uint8_t byte = bitmap[byteIndex + i];
        uint8_t firstNibble = (byte >> 4) & 15;
        uint8_t secondNibble = byte & 15;
        GC9A01_DrawPixel(xp, yp, palette[firstNibble]);
        xp++;
        if (xp == x + width) {
            xp = x;
            yp++;
        }
        GC9A01_DrawPixel(xp, yp, palette[secondNibble]);
        xp++;
        if (xp == x + width) {
            xp = x;
            yp++;
        }
    }
}


void GC9A01_Text(font_t *font, char *s, uint16_t x, uint16_t y, uint16_t fg, uint16_t bg) {
    uint16_t width = font->width;
    uint16_t height = font->height;
    uint16_t bpp = font->bpp;

    assert(bpp == 4);
    assert(font->map[0] == ' ' && strlen(font->map) == 96);
    uint32_t bitsPerChar = width * height * bpp;
    assert(bitsPerChar % 8 == 0);

    // figure out the bit depth and palette
    uint16_t palette[16];
    for (int i = 0; i < 16; i++ ) {
        float alpha = (float)i / 15;
        // out = alpha * new + (1 - alpha) * old
        rgb_t new = parse565(fg);
        rgb_t old = parse565(bg);
        rgb_t rgb = {
            .r = alpha * new.r + (1 - alpha) * old.r,
            .g = alpha * new.g + (1 - alpha) * old.g,
            .b = alpha * new.b + (1 - alpha) * old.b
        };
        //printf("%d, r=%.2f g=%.2f b=%.2f\n", i, rgb.r, rgb.g, rgb.g);
        palette[15-i] = format565(rgb); // the bitmap palette levels are inverted
        //printf("%d, %d\n", i, palette[i]);
    }

    uint16_t length = strlen(s);
    for (int i=0; i<length; i++) {
        GC9A01_Char(font, s[i], x+i*width, y, palette);
    }
}