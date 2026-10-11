/* SPDX-License-Identifier: GPL-3.0-or-later */
#ifndef TILEM_CONTROL_H
#define TILEM_CONTROL_H
#include <gio/gio.h>
gboolean tilem_control_start(TilemCalcEmulator *emu, const char *path, GError **error);
void tilem_control_stop(void);
#endif
