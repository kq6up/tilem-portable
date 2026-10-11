/* SPDX-License-Identifier: GPL-3.0-or-later */
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <tilem.h>
#include <scancodes.h>
int main(int argc, char **argv) {
    FILE *rom, *out;
    TilemCalc *calc;
    TilemLCDBuffer *frame;
    char model, *end;
    long duration = 1000;
    int i, x, y;
    if (argc == 2 && !strcmp(argv[1], "--help")) {
        puts("Usage: tilem-headless ROM [duration-ms [screen.pbm]]\nRuns a real ROM without GTK; writes no ROM or calculator save file.");
        return 0;
    }
    if (argc < 2 || argc > 4) { fputs("Use tilem-headless --help\n", stderr); return 2; }
    if (argc >= 3) {
        errno = 0; duration = strtol(argv[2], &end, 10);
        if (errno || !*argv[2] || *end || duration < 1 || duration > 60000) {
            fputs("Duration must be 1..60000 ms\n", stderr); return 2;
        }
    }
    rom = fopen(argv[1], "rb");
    if (!rom) { perror(argv[1]); return 1; }
    model = tilem_guess_rom_type(rom);
    calc = tilem_calc_new(model);
    if (!calc || tilem_calc_load_state(calc, rom, NULL)) {
        fputs("Unsupported or invalid ROM\n", stderr); fclose(rom);
        if (calc) tilem_calc_free(calc); return 1;
    }
    fclose(rom);
    tilem_z80_run_time(calc, 1000000, NULL);
    tilem_keypad_press_key(calc, TILEM_KEY_ON);
    tilem_z80_run_time(calc, 500000, NULL);
    tilem_keypad_release_key(calc, TILEM_KEY_ON);
    for (i = 0; i < duration; ++i) tilem_z80_run_time(calc, 1000, NULL);
    printf("%s: %ld ms, PC=0x%04x, LCD=%s (%dx%d)\n", calc->hw.name,
           duration, calc->z80.r.pc.d, calc->lcd.active ? "on" : "off",
           calc->hw.lcdwidth, calc->hw.lcdheight);
    if (argc == 4) {
        out = fopen(argv[3], "wb");
        if (!out) { perror(argv[3]); tilem_calc_free(calc); return 1; }
        frame = tilem_lcd_buffer_new(); tilem_lcd_get_frame1(calc, frame);
        fprintf(out, "P1\n%d %d\n", calc->hw.lcdwidth, calc->hw.lcdheight);
        for (y = 0; y < calc->hw.lcdheight; ++y) {
            for (x = 0; x < calc->hw.lcdwidth; ++x)
                fprintf(out, "%d ", calc->lcd.active ? frame->data[y * frame->rowstride + x] != 0 : 0);
            fputc('\n', out);
        }
        tilem_lcd_buffer_free(frame);
        if (fclose(out)) { perror(argv[3]); tilem_calc_free(calc); return 1; }
    }
    tilem_calc_free(calc); return 0;
}
