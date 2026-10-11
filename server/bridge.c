/* SPDX-License-Identifier: LGPL-2.1-or-later
 * Small C ABI for automation. Caller must serialize access to each instance.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <tilem.h>
#ifdef _WIN32
#define API __declspec(dllexport)
#else
#define API __attribute__((visibility("default")))
#endif
API TilemCalc *tilem_bridge_open(const char *path) {
    FILE *rom = fopen(path, "rb");
    TilemCalc *calc;
    char model;
    if (!rom) return NULL;
    model = tilem_guess_rom_type(rom);
    calc = tilem_calc_new(model);
    if (calc && tilem_calc_load_state(calc, rom, NULL)) {
        tilem_calc_free(calc); calc = NULL;
    }
    fclose(rom);
    return calc;
}
API void tilem_bridge_close(TilemCalc *calc) { if (calc) tilem_calc_free(calc); }
API const char *tilem_bridge_model(TilemCalc *calc) { return calc->hw.name; }
API int tilem_bridge_width(TilemCalc *calc) { return calc->hw.lcdwidth; }
API int tilem_bridge_height(TilemCalc *calc) { return calc->hw.lcdheight; }
API const char *tilem_bridge_keyname(TilemCalc *calc, int code) {
    return code >= 1 && code <= 64 ? calc->hw.keynames[code - 1] : NULL;
}
API int tilem_bridge_key(TilemCalc *calc, int code, int pressed) {
    if (!tilem_bridge_keyname(calc, code)) return -1;
    if (pressed) tilem_keypad_press_key(calc, code);
    else tilem_keypad_release_key(calc, code);
    return 0;
}
API unsigned int tilem_bridge_step(TilemCalc *calc, int microseconds) {
    if (microseconds < 0 || microseconds > 1000000) return (unsigned int)-1;
    return tilem_z80_run_time(calc, microseconds, NULL);
}
API void tilem_bridge_reset(TilemCalc *calc) { tilem_calc_reset(calc); }
API int tilem_bridge_pc(TilemCalc *calc) { return calc->z80.r.pc.d; }
API int tilem_bridge_lcd_active(TilemCalc *calc) { return calc->lcd.active; }
API int tilem_bridge_screen(TilemCalc *calc, unsigned char *out, int size) {
    TilemLCDBuffer *frame;
    int y, width = calc->hw.lcdwidth, height = calc->hw.lcdheight;
    if (size < width * height) return -1;
    memset(out, 0, (size_t)(width * height));
    if (!calc->lcd.active || (calc->z80.halted && !calc->poweronhalt)) return 0;
    frame = tilem_lcd_buffer_new();
    tilem_lcd_get_frame1(calc, frame);
    for (y = 0; y < height; ++y)
        memcpy(out + y * width, frame->data + y * frame->rowstride, (size_t)width);
    tilem_lcd_buffer_free(frame);
    return 0;
}
