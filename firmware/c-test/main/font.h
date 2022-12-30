#ifndef INC_FONT_H
#define INC_FONT_H

#include <stdint.h>

typedef struct _font_t {
    char *name;
    uint8_t width;
    uint8_t height;
    uint8_t bpp;
    char *map;
    uint8_t *bitmap;
} font_t;


void GC9A01_Text(font_t * font, char *c, uint16_t x, uint16_t y, uint16_t fg, uint16_t bg);


#endif