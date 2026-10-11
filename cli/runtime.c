/* SPDX-License-Identifier: LGPL-2.1-or-later
 * Portable allocation and logging callbacks for the TilEm emulator core.
 */
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <tilem.h>
static void *checked(void *p, size_t size) {
    if (size && !p) { fputs("TilEm: out of memory\n", stderr); abort(); }
    return p;
}
void tilem_free(void *p) { free(p); }
void *tilem_malloc(size_t s) { return checked(malloc(s), s); }
void *tilem_realloc(void *p, size_t s) { return checked(realloc(p, s), s); }
void *tilem_try_malloc(size_t s) { return malloc(s); }
void *tilem_malloc0(size_t s) { return checked(calloc(1, s), s); }
void *tilem_try_malloc0(size_t s) { return calloc(1, s); }
void *tilem_malloc_atomic(size_t s) { return tilem_malloc(s); }
void *tilem_try_malloc_atomic(size_t s) { return malloc(s); }
#define LOGGER(function, label) \
void function(TilemCalc *calc, const char *message, ...) { \
    va_list args; va_start(args, message); \
    fprintf(stderr, "%s%s: ", calc ? calc->hw.name : "TilEm", label); \
    vfprintf(stderr, message, args); fputc('\n', stderr); va_end(args); \
}
LOGGER(tilem_message, "")
LOGGER(tilem_warning, " warning")
LOGGER(tilem_internal, " internal error")
