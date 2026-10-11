/* SPDX-License-Identifier: GPL-3.0-or-later
 * Opt-in local automation socket for the very same calculator shown by GTK.
 * Commands: state, key CODE PRESSED, reset. One newline-terminated request
 * per connection, one newline-terminated JSON response. Main GTK thread only.
 */
#ifdef HAVE_CONFIG_H
#include <config.h>
#endif
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <sys/stat.h>
#include <unistd.h>
#include <gtk/gtk.h>
#include <glib/gstdio.h>
#include <gio/gio.h>
#include <ticalcs.h>
#include <tilem.h>
#include "gui.h"
#include "control.h"
#include "emucore.h"
static GSocketService *service;
static char *socket_path;
static gboolean transfer_busy;
static char *transfer_error;
static const char *transfer_status = "idle";
static void json_string(GString *out, const char *value) {
    const unsigned char *p = (const unsigned char *)value;
    g_string_append_c(out, '"');
    for (; *p; ++p) {
        if (*p == '"' || *p == '\\') g_string_append_c(out, '\\');
        if (*p < 32) g_string_append_printf(out, "\\u%04x", *p);
        else g_string_append_c(out, *p);
    }
    g_string_append_c(out, '"');
}
static void transfer_finished(TilemCalcEmulator *emu, gpointer data, gboolean cancelled) {
    struct TilemSendFileInfo *sf = data;
    (void)emu;
    g_free(transfer_error);
    transfer_error = g_strdup(cancelled ? "Transfer cancelled" : sf->error_message);
    transfer_status = transfer_error ? "error" : "done";
    transfer_busy = FALSE;
    if (!transfer_error) tilem_calc_emulator_autosave(emu);
    g_free(sf->filename); g_free(sf->display_name); g_free(sf->error_message);
    g_slice_free(struct TilemSendFileInfo, sf);
}
static char *snapshot(TilemCalcEmulator *emu) {
    TilemCalc *calc;
    TilemLCDBuffer *frame;
    GString *json = g_string_new(NULL);
    unsigned char *pixels;
    char *encoded;
    int width, height, x, y, first = 1;
    tilem_calc_emulator_lock(emu);
    calc = emu->calc;
    width = calc->hw.lcdwidth; height = calc->hw.lcdheight;
    pixels = g_malloc0((gsize)width * height);
    if (calc->lcd.active && !(calc->z80.halted && !calc->poweronhalt)) {
        frame = tilem_lcd_buffer_new(); tilem_lcd_get_frame1(calc, frame);
        for (y = 0; y < height; ++y)
            memcpy(pixels + y * width, frame->data + y * frame->rowstride, (size_t)width);
        tilem_lcd_buffer_free(frame);
    }
    encoded = g_base64_encode(pixels, (gsize)width * height);
    g_string_append_printf(json, "{\"model\":\"%s\",\"width\":%d,\"height\":%d,\"pc\":%u,\"lcd_active\":%s,\"pixels\":\"%s\",\"keys\":[",
       calc->hw.name, width, height, calc->z80.r.pc.d, calc->lcd.active ? "true" : "false", encoded);
    for (x = 0; x < 64; ++x) {
        if (calc->hw.keynames[x]) {
            g_string_append_printf(json, "%s{\"code\":%d,\"name\":\"%s\"}", first ? "" : ",", x + 1, calc->hw.keynames[x]);
            first = 0;
        }
    }
    g_string_append_printf(json, "],\"transfer\":{\"status\":\"%s\",\"error\":", transfer_status);
    if (transfer_error) json_string(json, transfer_error);
    else g_string_append(json, "null");
    g_string_append(json, "}}\n");
    tilem_calc_emulator_unlock(emu);
    g_free(pixels); g_free(encoded);
    return g_string_free(json, FALSE);
}
static gboolean incoming(GSocketService *listener, GSocketConnection *connection,
                          GObject *source, gpointer data) {
    TilemCalcEmulator *emu = data;
    GInputStream *in = g_io_stream_get_input_stream(G_IO_STREAM(connection));
    GOutputStream *out = g_io_stream_get_output_stream(G_IO_STREAM(connection));
    char command[8192], *reply = NULL;
    int code, pressed, consumed = 0;
    gsize n = 0;
    (void)listener; (void)source;
    g_socket_set_timeout(g_socket_connection_get_socket(connection), 1);
    while (n + 1 < sizeof(command)) {
        if (g_input_stream_read(in, command + n, 1, NULL, NULL) != 1) break;
        if (command[n++] == '\n') break;
    }
    command[n] = 0;
    if (!strcmp(command, "state\n")) reply = snapshot(emu);
    else if (!strcmp(command, "shutdown\n") && !transfer_busy) {
        gtk_widget_destroy(emu->ewin->window);
        reply = g_strdup("{\"ok\":true}\n");
    }
    else if (!strcmp(command, "reset\n") && !transfer_busy) {
        tilem_calc_emulator_reset(emu); reply = g_strdup("{\"ok\":true}\n");
    }
    else if (sscanf(command, "key %d %d%n", &code, &pressed, &consumed) == 2
             && !strcmp(command + consumed, "\n") && (pressed == 0 || pressed == 1)) {
        gboolean valid;
        tilem_calc_emulator_lock(emu);
        valid = code >= 1 && code <= 64 && emu->calc->hw.keynames[code - 1];
        tilem_calc_emulator_unlock(emu);
        if (valid) {
            if (pressed) tilem_calc_emulator_press_key(emu, code);
            else tilem_calc_emulator_release_key(emu, code);
            reply = g_strdup("{\"ok\":true}\n");
        }
    }
    else if (g_str_has_prefix(command, "send ") && !transfer_busy && n > 6 && command[n-1] == '\n') {
        gsize length;
        guchar *path;
        command[n-1] = 0;
        path = g_base64_decode(command + 5, &length);
        if (length > 0 && length < 4096 && !memchr(path, 0, length)) {
            char *filename = g_strndup((char *)path, length);
            if (g_path_is_absolute(filename) && g_file_test(filename, G_FILE_TEST_IS_REGULAR)
                    && tifiles_file_is_regular(filename)) {
                struct TilemSendFileInfo *sf = g_slice_new0(struct TilemSendFileInfo);
                sf->filename = filename;
                sf->display_name = g_filename_display_basename(filename);
                sf->slot = -1; sf->first = TRUE; sf->last = TRUE;
                transfer_busy = TRUE; transfer_status = "sending";
                g_free(transfer_error); transfer_error = NULL;
                tilem_calc_emulator_begin(emu, send_file_main, transfer_finished, sf);
                reply = g_strdup("{\"ok\":true,\"queued\":true}\n");
            } else g_free(filename);
        }
        g_free(path);
    }
    if (!reply) reply = g_strdup("{\"error\":\"invalid command\"}\n");
    g_output_stream_write_all(out, reply, strlen(reply), NULL, NULL, NULL);
    g_free(reply);
    g_io_stream_close(G_IO_STREAM(connection), NULL, NULL);
    return TRUE;
}
gboolean tilem_control_start(TilemCalcEmulator *emu, const char *path, GError **error) {
    GSocketAddress *address;
    struct stat before, after;
    g_return_val_if_fail(service == NULL, FALSE);
    address = g_unix_socket_address_new(path);
    if (g_lstat(path, &before) == 0) {
        GSocket *probe;
        GError *probe_error = NULL;
        gboolean connected;
        if (!S_ISSOCK(before.st_mode) || before.st_uid != getuid()) {
            g_set_error(error, G_IO_ERROR, G_IO_ERROR_EXISTS,
                        "Control path exists and is not an owned socket: %s", path);
            g_object_unref(address); return FALSE;
        }
        probe = g_socket_new(G_SOCKET_FAMILY_UNIX, G_SOCKET_TYPE_STREAM,
                             G_SOCKET_PROTOCOL_DEFAULT, error);
        if (!probe) { g_object_unref(address); return FALSE; }
        g_socket_set_timeout(probe, 1);
        connected = g_socket_connect(probe, address, NULL, &probe_error);
        g_object_unref(probe);
        if (connected || !g_error_matches(probe_error, G_IO_ERROR, G_IO_ERROR_CONNECTION_REFUSED)) {
            g_set_error(error, G_IO_ERROR, G_IO_ERROR_ADDRESS_IN_USE,
                        "Control socket is already active or unavailable: %s", path);
            g_clear_error(&probe_error); g_object_unref(address); return FALSE;
        }
        g_clear_error(&probe_error);
        /* Remove only the same stale socket that was just probed. */
        if (g_lstat(path, &after) || before.st_dev != after.st_dev
                || before.st_ino != after.st_ino || g_unlink(path)) {
            g_set_error(error, G_IO_ERROR, G_IO_ERROR_FAILED,
                        "Cannot remove stale control socket: %s", path);
            g_object_unref(address); return FALSE;
        }
    } else if (errno != ENOENT) {
        g_set_error(error, G_IO_ERROR, G_IO_ERROR_FAILED,
                    "Cannot inspect control socket: %s", path);
        g_object_unref(address); return FALSE;
    }
    service = g_socket_service_new();
    if (!g_socket_listener_add_address(G_SOCKET_LISTENER(service), address,
            G_SOCKET_TYPE_STREAM, G_SOCKET_PROTOCOL_DEFAULT, NULL, NULL, error)) {
        g_object_unref(address); g_object_unref(service); service = NULL; return FALSE;
    }
    g_object_unref(address);
    if (g_chmod(path, 0600)) {
        g_set_error(error, G_IO_ERROR, G_IO_ERROR_FAILED, "Cannot restrict control socket permissions");
        g_socket_listener_close(G_SOCKET_LISTENER(service));
        g_object_unref(service); service = NULL; g_unlink(path); return FALSE;
    }
    socket_path = g_strdup(path);
    g_signal_connect(service, "incoming", G_CALLBACK(incoming), emu);
    g_socket_service_start(service);
    return TRUE;
}
void tilem_control_stop(void) {
    if (!service) return;
    g_socket_service_stop(service);
    g_socket_listener_close(G_SOCKET_LISTENER(service));
    g_object_unref(service); service = NULL;
    g_unlink(socket_path); g_free(socket_path); socket_path = NULL;
}
