/* SPDX-License-Identifier: GPL-3.0-or-later
 * Read optional, local development .app defaults before GTK initialization.
 */
#include <stdio.h>
#include <string.h>
#include <glib.h>
#include "macos.h"
#ifdef __APPLE__
#include <mach-o/dyld.h>
#include <limits.h>
#include <stdlib.h>
#endif
void tilem_macos_bundle_defaults(char **rom, char **control) {
#ifdef __APPLE__
    char path[PATH_MAX], real[PATH_MAX], *slash, *value, line[PATH_MAX + 64];
    uint32_t size = sizeof(path);
    FILE *file;
    if (_NSGetExecutablePath(path, &size) || !realpath(path, real)) return;
    slash = strrchr(real, '/'); if (!slash) return; *slash = 0;
    if (g_snprintf(path, sizeof(path), "%s/../Resources/runtime.env", real) >= sizeof(path)) return;
    file = fopen(path, "r"); if (!file) return;
    while (fgets(line, sizeof(line), file)) {
        line[strcspn(line, "\r\n")] = 0;
        value = strchr(line, '='); if (!value) continue; *value++ = 0;
        if (!strcmp(line, "ROM")) { if (g_file_test(value, G_FILE_TEST_IS_REGULAR)) *rom = g_strdup(value); }
        else if (!strcmp(line, "CONTROL_SOCKET")) { if (!g_file_test(value, G_FILE_TEST_EXISTS)) *control = g_strdup(value); }
        else if (!strcmp(line, "XDG_CONFIG_HOME") || !strcmp(line, "GDK_PIXBUF_MODULE_FILE"))
            g_setenv(line, value, FALSE);
    }
    fclose(file);
#else
    (void)rom; (void)control;
#endif
}
