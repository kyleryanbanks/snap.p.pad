"""
This is a combo converter tool.  It is intended to take a more user-friendly
combo format and convert it into the hex-string the snap code actually uses.

This will contain options to output the hex-strings to a file or transmit the
combos manually to the SNAP engine.

The combos will exist in lists and contain 3 pieces: direction, button, and frame.

Direction will accept numpad notation and text format (U, D, DB, UF, etc.)
Text inputs will be given with the assumption the combo will be executed from the 
P1 side of the screen. (DB = DL = 1, UF = UR = 9, etc.)

Buttons will accept LMHSAB as input and can have multiple buttons, the tool will
automatically calculate the hex-code for all buttons pressed.  When a button is
pressed, it is pulled low.

Frame will be a value from 1-255.  If you need a wait longer than 255 frames, you
will need to create a 2nd empty frame after to wait additional frames.

I will be using dictionaries to house most of the input definitions.

I will also be implementing shortcuts for common commands (QCF, DP, etc.) The format
will be: Shortcut, button to be pressed with last direction, frames to wait after button
In these situations, the system will assume you want 1 frame of wait for all inputs
and place the button press on the same frame as the last direction in the input.
"""

import sys
import getopt
import re

BUTTONS = {"L": 0xFE,
           "M": 0xFD,
           "H": 0xFB,
           "P": 0xF7,
           "S": 0xEF,
           "K": 0x7F,
           "A": 0xDF,
           "B": 0xBF,
           "l": 0xFE,
           "m": 0xFD,
           "h": 0xFB,
           "p": 0xF7,
           "s": 0xEF,
           "k": 0x7F,
           "a": 0xDF,
           "b": 0xBF,
           "1": 0xDF,
           "2": 0xBF,
           "x": 0xFF,
           "X": 0xFF,
           }

DIRECTIONS = {"4": "\x7F",
              "1":  "\x3F",
              "2": "\xBF",
              "3":  "\x9F",
              "6": "\xDF",
              "9":  "\xCF",
              "8": "\xEF",
              "7":  "\x6F",
              "B": "\x7F",
              "DB": "\x3F",
              "D": "\xBF",
              "DF": "\x9F",
              "F": "\xDF",
              "UF": "\xCF",
              "U": "\xEF",
              "UB": "\x6F",
              "b": "\x7F",
              "db": "\x3F",
              "d": "\xBF",
              "df": "\x9F",
              "f": "\xDF",
              "uf": "\xCF",
              "u": "\xEF",
              "ub": "\x6F",
              "x": "\xFF",
              "X": "\xFF",
              }

SHORTCUTS = {"QCF": "\xDF\xFF\x01\x9F\xFF\x01\xBF",
             "QCB": "\xDF\xFF\x01\xCF\xFF\x01\xEF",
             "HCF": "\xEF\xFF\x01\xCF\xFF\x01\xDF\xFF\x01\x9F\xFF\x01\xBF",
             "HCB": "\xBF\xFF\x01\x9E\xFF\x01\xDE\xFF\x01\xCF\xFF\x01\xEF",
             "DPF": "\xBF\xFF\x01\xDF\xFF\x01\x9F",
             "DPB": "\xBF\xFF\x01\xDF\xFF\x01\xCF",
             "MBF": "\x7F\xFF\x01\x3F\xFF\x01\xBF",
             "MBB": "\x7F\xFF\x01\x6F\xFF\x01\xEF",
             "qcf": "\xDF\xFF\x01\x9F\xFF\x01\xBF",
             "qcb": "\xDF\xFF\x01\xCF\xFF\x01\xEF",
             "hcf": "\xEF\xFF\x01\xCF\xFF\x01\xDF\xFF\x01\x9F\xFF\x01\xBF",
             "hcb": "\xBF\xFF\x01\x9E\xFF\x01\xDE\xFF\x01\xCF\xFF\x01\xEF",
             "dpf": "\xBF\xFF\x01\xDF\xFF\x01\x9F",
             "dpb": "\xBF\xFF\x01\xDF\xFF\x01\xCF",
             "mbf": "\xEF\xFF\x01\xCF\xFF\x01\xDF",
             "mbb": "\xEF\xFF\x01\x6F\xFF\x01\x7F",
             "sj": "\xBF\xFF\x03\xEF",
             "SJ": "\xBF\xFF\x03\xEF",
             "sjuf": "\xBF\xFF\x03\xCF",
             "SJUF": "\xBF\xFF\x03\xCF",
             "sjub": "\xBF\xFF\x03\x6F",
             "SJUB": "\xBF\xFF\x03\x6F"
             }

hex_combo_list = []
combo_list_1 = []
combo_list_2 = []
comment_list = []

combo_file = ''
output_file = ''


def main(argv):
    global combo_file, output_file
    try:
        opts, args = getopt.getopt(argv, "hc:o:", ["cfile=", "ofile="])
    except getopt.GetoptError:
        print 'Python Combo_Converter.py -c <combo_file> -o <output_file>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print 'Python Combo_Converter.py -c <combo_file> -o <output_file>'
            sys.exit()
        elif opt in ("-c", "--cfile"):
            combo_file = arg
        elif opt in ("-o", "--ofile"):
            output_file = arg

    export_combo_lib(combo_file, output_file)

def import_library(fn):
    command_search = re.compile(r"/(\w+)\.(\w+)\.(\w+)/")

    if fn == "":
        fn = 'combo.txt'

    comment = None
    p1_combo = []
    p2_combo = []
    with open(fn, 'r') as f:
        for line in f:
            if line.startswith("#"):
                if comment:
                    yield comment, p1_combo, p2_combo
                comment = line.strip()
                p1_combo = []
                p2_combo = []
            elif line.startswith("1"):
                p1_combo = command_search.findall(line)
            elif line.startswith("2"):
                p2_combo = command_search.findall(line)
            else:
                p1_combo = command_search.findall(line)
    if comment is not None:
        yield comment, p1_combo, p2_combo

def generate_hex(combo_list):
    triplet_search = re.compile("(.)(.)(.)")

    hex_combo = ""
    for move, button, delay in combo_list:
        if move in SHORTCUTS:
            hex_combo += SHORTCUTS[move]
        else:
            hex_combo += DIRECTIONS[move]

        empty_button = 0xFF
        for char_button in button:
            empty_button &= BUTTONS[char_button]
        hex_combo += chr(empty_button)

        if delay == '0':
            input_count = (len(hex_combo) + 1) / 3
            hex_combo = '\xFF\xFF' + chr(input_count) + hex_combo + chr(1)
        else:
            hex_combo += chr(int(delay))

    for move, button, delay in triplet_search.findall(hex_combo):
            for i in xrange(ord(delay)):
                yield move + button #+ chr(1)

def generate_byte_strings(p1_combo, p2_combo):
    p1_gen = generate_hex(p1_combo)
    p2_gen = generate_hex(p2_combo)
    current = prev = None
    count = 1
    p1_running = p2_running = True
    while p1_running or p2_running:
        p1_pair = "\xFF\xFF"
        if p1_running:
            try:
                p1_pair = p1_gen.next()
            except StopIteration:
                p1_running = False

        p2_pair = "\xFF\xFF"
        if p2_running:
            try:
                p2_pair = p2_gen.next()
            except StopIteration:
                p2_running = False

        current = p1_pair + p2_pair
        if current == prev:
            count += 1
        elif prev:
            yield prev + chr(count)
            count = 1

        prev = current

    yield "\xFF\xFF\xFF\xFF\x00"

def compile_final_hex(fn):
    for comment, p1_combo, p2_combo in import_library(fn):
        yield comment, "".join(generate_byte_strings(p1_combo, p2_combo))

def export_combo_lib(input_filename, output_file):
    if output_file == '':
        output_file = 'combo_output.txt'
    with open(output_file, 'a+') as f:
        f.write('\nCode for SNAPpPad Core\n\n')
        for count, (comment, string) in enumerate(compile_final_hex(input_filename)):
            # f.write("%s\nMIXUP_%d = ['%s']\n" % (comment, count, "".join(r"\x%02x" % ord(i) for i in string)))
            f.write("%s\nMIXUP_%d = [%s]\n" % (comment, count, ",".join("%d" % ord(i) for i in string)))

def output_hex(filename):
    return "".join(r"\x%02x" % i for i in compile_final_hex(filename))

if __name__ == "__main__":
    main(sys.argv[1:])

