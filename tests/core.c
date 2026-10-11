/* SPDX-License-Identifier: GPL-3.0-or-later */
#include <stdio.h>
#include <string.h>
#include <tilem.h>
#include <scancodes.h>
#define CHECK(c) do { if (!(c)) { fprintf(stderr, "Failed at line %d: %s\n", __LINE__, #c); return 1; } } while (0)
int main(void) {
    const TilemHardware **models;
    int count, i;
    TilemCalc *calc, *copy;
    /* LD A,42; LD (8000),A; INC A; LD (8001),A; HALT. No proprietary ROM. */
    const unsigned char program[] = {0x3e,0x2a,0x32,0x00,0x80,0x3c,0x32,0x01,0x80,0x76};
    tilem_get_supported_hardware(&models, &count); CHECK(count == 12);
    for (i = 0; i < count; ++i) {
        calc = tilem_calc_new(models[i]->model_id); CHECK(calc);
        copy = tilem_calc_copy(calc); CHECK(copy); CHECK(copy->mem != calc->mem);
        CHECK(copy->hw.model_id == calc->hw.model_id);
        tilem_calc_reset(copy); tilem_calc_free(copy); tilem_calc_free(calc);
    }
    calc = tilem_calc_new(TILEM_CALC_TI85); CHECK(calc);
    memset(calc->mem, 0, calc->hw.romsize); memcpy(calc->mem, program, sizeof(program));
    tilem_z80_run(calc, 200, NULL);
    CHECK(calc->hw.z80_rdmem(calc, 0x8000) == 42);
    CHECK(calc->hw.z80_rdmem(calc, 0x8001) == 43);
    tilem_keypad_set_group(calc, 0xfd); /* keypad row containing Enter */
    tilem_keypad_press_key(calc, TILEM_KEY_ENTER); CHECK(!(tilem_keypad_read_keys(calc) & 1));
    tilem_keypad_release_key(calc, TILEM_KEY_ENTER); CHECK(tilem_keypad_read_keys(calc) == 0xff);
    tilem_calc_free(calc);
    puts("12 models allocated/copied/reset; Z80 execution and keypad passed"); return 0;
}
