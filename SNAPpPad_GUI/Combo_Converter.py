"""
This is a combo converter tool.  It is intended to take a more user-friendly
combo format and convert it into the hex-string the snap code actually uses.

This will contain options to output the hex-strings to a file or transmit the
combos manually to the SNAP engine.

The combos will exist in lists and contain 3 pieces: direction, button, and frame.

Direction will acception numpad notation and text format (U, D, DB, UF, etc.)
Text inputs will be given with the assumption the combo will be executed from the
P1 side of the screen. (DB = DL = 1, RF = RR = 9, etc.)

Buttons will accept LMHSAB as input and can have multiple buttons, the tool will
automatically calculate the hex-code for all buttons pressed.  When a button is
pressed, it is pulled low.

Frame will be a value from 1-255.  If you need a wait longer than 255 frames, you
will need to create a 2nd empty frame after to wait additional frames.

I will be using dictionaries to house most of the input definitions.

I will also be implementing shortcuts for common commands (QCF, DP, etc.) The format
will be: Shorcut, button to be pressed with last direction, frames to wait after button
In these situations, the system will assume you want 1 frame of wait for all inputs
and place the button press on the same frame as the last direction in the input.
"""

import sys, getopt

DIRECTIONS ={"4" : "\xEF",
             "1" : "\xEE",
             "2" : "\xFE",
             "3" : "\xDE",
             "6" : "\xDF",
             "9" : "\xDD",
             "8" : "\xFD",
             "7" : "\xED",
             "B" : "\xEF",
             "DB" : "\xEE",
             "D" : "\xFE",
             "DF" : "\xDE",
             "F" : "\xDF",
             "UF" : "\xDD",
             "U" : "\xFD",
             "UB" : "\xED",
             "b" : "\xEF",
             "db" : "\xEE",
             "d" : "\xFE",
             "df" : "\xDE",
             "f" : "\xDF",
             "uf" : "\xDD",
             "u" : "\xFD",
             "ub" : "\xED",
             "x" : "\xFF",
             "X" : "\xFF",
             }

BUTTONS = {"L" : "\x7F",
           "M" : "\xBF",
           "H" : "\xDF",
           "4P" : "\xEF",
           "S" : "\xFB",
           "A1" : "\xFD",
           "A2" : "\xFE",
           "4K" : "\xFB",
           "A" : "\xFD",
           "B" : "\xFE",
           "1" : "\xFD",
           "2" : "\xFE",
           "l" : "\x7F",
           "m" : "\xBF",
           "h" : "\xDF",
           "4p" : "\xEF",
           "s" : "\xFB",
           "a1" : "\xFD",
           "a2" : "\xFE",
           "4k" : "\xFB",
           "a" : "\xFD",
           "b" : "\xFE",
           "1" : "\xFD",
           "2" : "\xFE",
           "x" : "\xFF",
           "X" : "\xFF",
           }

SHORTCUTS = {"QCF": "\xFE\xFF\x01\xDE\xFF\x01\xDF",
             "QCB": "\xFE\xFF\x01\xEE\xFF\x01\xEF",
             "HCF": "\xEF\xFF\x01\xEE\xFF\x01\xFE\xFF\x01\xDE\xFF\x01\xDF",
             "HCB": "\xDF\xFF\x01\xDE\xFF\x01\xFE\xFF\x01\xEE\xFF\x01\xEF",
             "DPF": "\xDF\xFF\x01\xFE\xFF\x01\xDE",
             "DPB": "\xEF\xFF\x01\xFE\xFF\x01\xEE",
             "MBF": "\xFD\xFF\x01\xDD\xFF\x01\xDF",
             "MBB": "\xFD\xFF\x01\xED\xFF\x01\xEF",
             "qcf": "\xFE\xFF\x01\xDE\xFF\x01\xDF",
             "qcb": "\xFE\xFF\x01\xEE\xFF\x01\xEF",
             "hcf": "\xEF\xFF\x01\xEE\xFF\x01\xFE\xFF\x01\xDE\xFF\x01\xDF",
             "hcb": "\xDF\xFF\x01\xDE\xFF\x01\xFE\xFF\x01\xEE\xFF\x01\xEF",
             "dpf": "\xDF\xFF\x01\xFE\xFF\x01\xDE",
             "dpb": "\xEF\xFF\x01\xFE\xFF\x01\xEE",
             "mbf": "\xFD\xFF\x01\xDD\xFF\x01\xDF",
             "mbb": "\xFD\xFF\x01\xED\xFF\x01\xEF",
             "sj": "\xFE\xFF\x03\xFD",
             "SJ": "\xFE\xFF\x03\xFD",
             "sjuf": "\xFE\xFF\x03\xDD",
             "SJUF": "\xFE\xFF\x03\xDD",
             "sjub": "\xFE\xFF\x03\xED",
             "SJUB": "\xFE\xFF\x03\xED"
             }

def breakdown_combo(combo_to_convert):
    combo = []
    frame = []
    command = ''
    for char in combo_to_convert:
        if char == ".":
            #print 'append command to frame and reset'
            frame.append(command)
            command = ''
        elif char == '/':
            #print 'check if starting/ending a frame, append and reinit as needed'
            if command:
              frame.append(int(command))
              combo.append(frame)
            command = ''
            frame = []
        elif char == ' ':
            pass
        else:
            #print 'adding char to command'
            command = command + char
    return combo

def build_hex_combo(combo):
      #init new combo string
      hex_combo = ""
      for frame in combo:
          #Shorcut handling check
          if frame[0] in SHORTCUTS:
              hex_combo = hex_combo + SHORTCUTS[frame[0]]
          else:
              hex_combo = hex_combo + DIRECTIONS[frame[0]]
          #Multiple buttons check
          if len(frame[1]) > 1:
              hex_buttons = '\xFF'
              for button in frame[1]:
                  hex_buttons = ord(hex_buttons) & ord(BUTTONS[button])
                  hex_buttons = chr(hex_buttons)
              hex_combo = hex_combo + str(hex_buttons)
          else:
              hex_combo = hex_combo + BUTTONS[(frame[1])]
          #Add Frame Value
          #If frame count is 0, add range counter tag to front of combo.
          if frame[2] == 0:
            input_count = (len(hex_combo)+1)/3
            hex_combo = '\xFF\xFF' + chr(input_count) + hex_combo + chr(1)
          else:
            hex_combo = hex_combo + chr(frame[2])
      hex_combo = hex_combo + '\xFF\xFF\x00'
      #hex_combo_list.append("".join([r"\x%02x" % ord(i) for i in hex_combo]))
      return hex_combo

