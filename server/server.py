#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Loopback HTTP control for the native GTK calculator, or a standalone core.
No external Python modules are required. ROMs are opened read-only.
"""
import argparse
import base64
import ctypes
import json
import os
from pathlib import Path
import socket
import struct
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import zlib


class NativeCalculator:
    def __init__(self, path):
        self.path = os.fspath(path)

    def command(self, command):
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as conn:
            conn.settimeout(3)
            conn.connect(self.path)
            conn.sendall((command + '\n').encode('ascii'))
            with conn.makefile('rb') as stream:
                reply = stream.readline(65536)
        result = json.loads(reply)
        if 'error' in result:
            raise ValueError(result['error'])
        return result

    def state(self):
        return dict(self.command('state'), backend='native GTK')

    def key(self, code, pressed):
        self.command(f'key {code} {int(pressed)}')

    def reset(self):
        self.command('reset')

    def send(self, path):
        return self.command("send " + base64.b64encode(os.fsencode(path)).decode("ascii"))

    def close(self):
        pass


class StandaloneCalculator:
    def __init__(self, library, rom):
        self.lock = threading.RLock()
        self.stop = threading.Event()
        self.lib = ctypes.CDLL(os.fspath(library))
        pointer = ctypes.c_void_p
        signatures = {
            'open': ([ctypes.c_char_p], pointer),
            'close': ([pointer], None), 'model': ([pointer], ctypes.c_char_p),
            'width': ([pointer], ctypes.c_int), 'height': ([pointer], ctypes.c_int),
            'keyname': ([pointer, ctypes.c_int], ctypes.c_char_p),
            'key': ([pointer, ctypes.c_int, ctypes.c_int], ctypes.c_int),
            'step': ([pointer, ctypes.c_int], ctypes.c_uint),
            'reset': ([pointer], None), 'pc': ([pointer], ctypes.c_int),
            'lcd_active': ([pointer], ctypes.c_int),
            'screen': ([pointer, ctypes.c_void_p, ctypes.c_int], ctypes.c_int),
        }
        for name, (args, result) in signatures.items():
            fn = getattr(self.lib, 'tilem_bridge_' + name)
            fn.argtypes, fn.restype = args, result
            setattr(self, name + '_fn', fn)
        self.calc = self.open_fn(os.fsencode(rom))
        if not self.calc:
            raise ValueError('Unable to open the ROM or determine its calculator model')
        self.width, self.height = self.width_fn(self.calc), self.height_fn(self.calc)
        self.keys = [dict(code=code, name=name.decode('ascii')) for code in range(1, 65)
                     if (name := self.keyname_fn(self.calc, code))]
        self.thread = threading.Thread(target=self.run, name='tilem-core', daemon=True)
        self.thread.start()

    def run(self):
        deadline = time.monotonic()
        while not self.stop.is_set():
            with self.lock:
                self.step_fn(self.calc, 20000)
            deadline += .02
            self.stop.wait(max(0, deadline - time.monotonic()))
            if time.monotonic() - deadline > .1:
                deadline = time.monotonic()

    def state(self):
        with self.lock:
            pixels = (ctypes.c_ubyte * (self.width * self.height))()
            if self.screen_fn(self.calc, pixels, len(pixels)):
                raise RuntimeError('Unable to read LCD')
            return dict(model=self.model_fn(self.calc).decode('ascii'), width=self.width,
                        height=self.height, pc=self.pc_fn(self.calc),
                        lcd_active=bool(self.lcd_active_fn(self.calc)), keys=self.keys,
                        pixels=base64.b64encode(bytes(pixels)).decode('ascii'), backend='standalone core')

    def key(self, code, pressed):
        with self.lock:
            if self.key_fn(self.calc, code, int(pressed)):
                raise ValueError('Invalid key')

    def reset(self):
        with self.lock:
            self.reset_fn(self.calc)

    def close(self):
        self.stop.set()
        self.thread.join()
        self.close_fn(self.calc)


def screen_png(state):
    width, height = state['width'], state['height']
    pixels = base64.b64decode(state['pixels'])
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    rows = b''.join(b'\0' + bytes(0 if p else 255 for p in pixels[y*width:(y+1)*width]) for y in range(height))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 0, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(5)

    def log_message(self, fmt, *args):
        if self.server.verbose:
            super().log_message(fmt, *args)

    def allowed(self):
        port = self.server.server_address[1]
        valid = {f'127.0.0.1:{port}', f'localhost:{port}'}
        host, origin = self.headers.get('Host', ''), self.headers.get('Origin')
        return host in valid and (not origin or origin in {'http://' + h for h in valid})

    def reply(self, code, data, content_type='application/json'):
        if isinstance(data, (dict, list)):
            data = json.dumps(data, separators=(',', ':')).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if not self.allowed():
            return self.reply(403, {'error': 'Loopback requests only'})
        try:
            if self.path == '/':
                return self.reply(200, Path(__file__).with_name('index.html').read_bytes(), 'text/html; charset=utf-8')
            if self.path == '/api/programs':
                folder = self.server.program_dir
                files = sorted(p.name for p in folder.glob('*') if p.is_file() and p.suffix.lower() == '.85p') if folder else []
                return self.reply(200, {'files': files})
            if self.path == '/api/state':
                return self.reply(200, self.server.calculator.state())
            if self.path == '/screen.png':
                return self.reply(200, screen_png(self.server.calculator.state()), 'image/png')
            return self.reply(404, {'error': 'Not found'})
        except (OSError, ValueError, RuntimeError) as error:
            self.reply(503, {'error': str(error)})

    def do_POST(self):
        if not self.allowed():
            return self.reply(403, {'error': 'Loopback requests only'})
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            return self.reply(415, {'error': 'Expected application/json'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 4096:
                raise ValueError('Request size must be 1..4096 bytes')
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError('Expected JSON object')
            with self.server.actions:
                if self.path == '/api/key':
                    keys = {key['name']: key['code'] for key in self.server.calculator.state()['keys']}
                    name, action = body.get('key'), body.get('action', 'tap')
                    if not isinstance(name, str) or name not in keys or action not in ('tap', 'down', 'up'):
                        raise ValueError('Invalid key or action')
                    hold = body.get('hold_ms', 120)
                    if isinstance(hold, bool) or not isinstance(hold, int) or not 20 <= hold <= 1000:
                        raise ValueError('hold_ms must be 20..1000')
                    code = keys[name]
                    if action == 'tap':
                        self.server.calculator.key(code, True)
                        try:
                            time.sleep(hold / 1000)
                        finally:
                            self.server.calculator.key(code, False)
                        time.sleep(.08)
                    else:
                        self.server.calculator.key(code, action == 'down')
                elif self.path == '/api/send':
                    folder, name = self.server.program_dir, body.get('file')
                    if not folder or not isinstance(self.server.calculator, NativeCalculator):
                        raise ValueError('Program sending requires a native GUI and --program-dir')
                    if not isinstance(name, str) or Path(name).name != name or Path(name).suffix.lower() != '.85p':
                        raise ValueError('Expected a .85p basename from the configured program directory')
                    path = (folder / name).resolve()
                    if path.parent != folder or not path.is_file():
                        raise ValueError('Program not found in the configured directory')
                    result = self.server.calculator.send(path)
                    return self.reply(202, result)
                elif self.path == '/api/release':
                    for key in self.server.calculator.state()['keys']:
                        self.server.calculator.key(key['code'], False)
                elif self.path == '/api/reset':
                    self.server.calculator.reset()
                else:
                    return self.reply(404, {'error': 'Not found'})
            self.reply(200, {'ok': True})
        except (OSError, ValueError, RuntimeError) as error:
            self.reply(400, {'error': str(error)})


def default_library():
    root = Path(__file__).resolve().parents[1]
    prefix = Path(os.environ.get('TILEM_INSTALL_PREFIX', root))
    for folder in [root / 'build', root / 'build-core', prefix / 'lib', prefix / 'lib64']:
        for name in ['libtilembridge.dylib', 'libtilembridge.so']:
            if (folder / name).is_file():
                return folder / name
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    backend = parser.add_mutually_exclusive_group(required=True)
    backend.add_argument('--socket', type=Path, help='Control socket enabled by tilem2 --control-socket PATH')
    backend.add_argument('--rom', type=Path, help='Start a separate standalone calculator using this ROM')
    parser.add_argument('--library', type=Path, default=default_library())
    parser.add_argument('--port', type=int, default=8865)
    parser.add_argument('--program-dir', type=Path, help='Allow sending .85p files from this directory to the native GUI')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('port must be 1..65535')
    if args.rom and not args.library:
        parser.error('build the C library first, or supply --library')
    calculator = None
    httpd = None
    try:
        calculator = NativeCalculator(args.socket) if args.socket else StandaloneCalculator(args.library, args.rom)
        state = calculator.state()
        httpd = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
        httpd.daemon_threads = False
        httpd.program_dir = args.program_dir.resolve() if args.program_dir else None
        httpd.calculator, httpd.actions, httpd.verbose = calculator, threading.RLock(), args.verbose
        print(f"{state['model']} ({state['backend']}) at http://127.0.0.1:{args.port}", flush=True)
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if httpd:
            httpd.server_close()
        if calculator:
            calculator.close()


if __name__ == '__main__':
    main()
