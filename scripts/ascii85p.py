#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Convert a supported subset of ASCII85P BASIC source into tokenized .85p.
Format reference: https://debrouxl.github.io/tilp-linkguide/ti85/tokens.html
Unsupported syntax is rejected rather than silently changed. No source is run.
"""
import argparse
from pathlib import Path
import re
import struct

TOKENS = {'Degree': 0x57, 'Radian': 0x56, 'ClLCD': 0xec,
          'Disp': 0xe9, 'Prompt': 0xe7, 'Pause': 0xe2, 'Stop': 0xe3,
          'If': 0xd8, 'Then': 0xd9, 'Else': 0xda, 'End': 0xde,
          'Return': 0xdf, 'While': 0xdb, 'Repeat': 0xdc, 'For': 0xdd,
          'abs': 0xa2, 'iPart': 0xa3, 'fPart': 0xa4, 'int': 0xa5,
          'sin': 0xaa, 'cos': 0xac, 'tan': 0xae, 'ln': 0xa6, 'log': 0xa8,
          'round': 0x12, 'min': 0x14, 'max': 0x13}
ESCAPES = {'->': 0x0b, '>=': 0x54, '<=': 0x53, 'sin^-1': 0xab,
           'cos^-1': 0xad, 'tan^-1': 0xaf, '(-)': 0xa1}
OPERATORS = {'(': 0x10, ')': 0x11, ',': 0x2f, '=': 0x3f,
             '<': 0x51, '>': 0x52, '+': 0x60, '-': 0x61,
             '*': 0x70, '/': 0x71, '^': 0xf0, ':': 0x6e}
LEX = re.compile(r'\s+|\\[^\\\n]+\\|"[^"\n]*"|(?:\d+(?:\.\d*)?|\.\d+)|[A-Za-z][A-Za-z0-9]*|[(),=<>+*/^:\-]')

def tokenize_line(line):
    label = re.fullmatch(r'(Lbl|Goto)\s+([A-Za-z][A-Za-z0-9]{0,7})\s*', line)
    if label:
        # TI-85 Goto reserves two bytes for its runtime destination cache.
        # Initialize the cache to zero; the ROM resolves the label when run.
        prefix = b'\xe0' if label[1] == 'Lbl' else b'\xe1\0\0'
        return prefix + label[2].encode('ascii') + b'\0'
    output = bytearray()
    position = 0
    while position < len(line):
        match = LEX.match(line, position)
        if not match:
            raise ValueError(f'Unsupported syntax at column {position + 1}: {line[position:]}')
        value = match[0]
        position = match.end()
        if value.isspace():
            continue
        if value.startswith('\\'):
            escape = value[1:-1]
            if escape not in ESCAPES:
                raise ValueError(f'Unsupported escape {value}')
            output.append(ESCAPES[escape])
        elif value.startswith('"'):
            output.extend(b'\x2d' + value[1:-1].encode('ascii') + b'\0')
        elif value[0].isdigit() or value[0] == '.':
            output.extend(b'\x44' + value.encode('ascii') + b'\0')
        elif value in TOKENS:
            output.append(TOKENS[value])
        elif value in OPERATORS:
            output.append(OPERATORS[value])
        elif re.fullmatch(r'[A-Z][A-Z0-9]{0,7}', value):
            output.append(0x32 + len(value))
            output.extend(value.encode('ascii'))
        else:
            raise ValueError(f'Unsupported command or variable {value!r}')
    return bytes(output)

def convert(path):
    lines = path.read_text(encoding='ascii').splitlines()
    if not lines or lines[0] != '\\START\\' or lines[-1] != '\\STOP\\':
        raise ValueError('Expected one ASCII85P program between \\START\\ and \\STOP\\')
    header, body = {}, []
    for line in lines[1:-1]:
        if not body and line.startswith('\\') and '=' in line:
            key, value = line[1:].split('=', 1)
            if key not in ('COMMENT', 'NAME', 'FILE') or key in header:
                raise ValueError(f'Unsupported or duplicate header {key}')
            header[key] = value
        else:
            body.append(line)
    name = header.get('NAME', '')
    if not re.fullmatch(r'[A-Z][A-Z0-9]{0,7}', name):
        raise ValueError('Program NAME must be 1..8 uppercase letters/digits, starting with a letter')
    program = bytearray()
    for number, line in enumerate(body, 1):
        try:
            program.extend(tokenize_line(line))
            program.append(0x6f)
        except ValueError as error:
            raise ValueError(f'{path}: BASIC line {number}: {error}') from error
    if len(program) > 30000:
        raise ValueError('Program too large for this converter')
    u16 = lambda value: struct.pack('<H', value)
    data = u16(len(program)) + program
    entry = (u16(6 + len(name)) + u16(len(data)) + bytes([0x12, len(name)])
             + name.encode('ascii') + u16(len(data)) + data)
    comment = header.get('COMMENT', 'TilEm Portable ASCII85P conversion').encode('ascii')[:42].ljust(42, b'\0')
    result = b'**TI85**\x1a\x0c\x00' + comment + u16(len(entry)) + entry + u16(sum(entry) & 0xffff)
    return name, result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sources', type=Path, nargs='+')
    parser.add_argument('--output-dir', type=Path, default=Path('.'))
    args = parser.parse_args()
    converted = [convert(path) for path in args.sources]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, data in converted:
        output = args.output_dir / (name + '.85p')
        output.write_bytes(data)
        print(f'{output}: {len(data)} bytes')

if __name__ == '__main__':
    main()
