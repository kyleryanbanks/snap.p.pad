"""
This is an attempt at SNAPifying a PS360+ PCB board to allow the SNAP engine to interface with
either a PS3, Xbox360, or PC.

It is intended for use as a fighting game training/practice tool and, as such, would need to
be accurate to 1/60th of a second (1/60th sec = 16.67ms = 16670 microseconds).  On any given
frame, the SNAP engine will need to be able to press/release/hold one of the 15 input
buttons and wait for a set number of frames (between 0 to a currently unspecified value.)

To accomodate for this speed, we will be mapping all timing-specific buttons to contiguous
ports and Poke() all values in at once (rather than processing through the buttons one by one)
and utilizing either hook_1ms or if we find it necc. to have more control over
the timing, pulsePin() on an unused GPIO at negative increments (-1 = ~0.94 microseconds).

Eventually, we will be using S_Peek() and S_Poke() to store and pull combo data from the string
buffer, but for initial testing, combos will be stored in a tuple and pulled manually.

Basic format for combo data will be as follows:
combo = ((1byte_Port_F Buttons, 1_byte_Port_E Buttons, 1_byte_frame_delay),
         (2nd Port F Buttons, 2nd Port E, 2nd frame_delay),
         (3rd...),...,(Nth...)
         (Empty Port F, Empty Port E, Empty Delay))
"""
import random
# Global Inits
frame_microsecond = -16670
pulse_window = 11090
current_reset_position = 1

#Raw Opcodes
Disable_Interrupt = "\xF8\x94\x08\x95"
Enable_Interrupt = "\x78\x94\x08\x95"

# ATmeg128RFA1 Address Mapping
Port_F = 0x31
Port_E = 0x2E
Port_B = 0x25

#           0   0   0   0   0   0   0   0
# Port F = 1P, 2P, 3P, 4P, __, 1K, 2K, 3K
# Port F =  L,  M,  H, 4P, __,  S, A1, A2 (Marvel Mappings)
# Port E = __, __, D , Up, __, 4K, Le, Ri
# Port B = St, Se, Ho, __, __, __, __, __

# Reset Codes (Port F|Port E|Port B)
RESET_M = "\X00\X3F\X00"
RESET_R = "\X00\X3F\XFE"
RESET_L = "\X00\X3F\XFD"

RESET_M_A1 = "\XFD\X3F\X00"
RESET_R_A1 = "\XFD\X3F\XFE"
RESET_L_A1 = "\XFD\X3F\XFD"

RESET_M_A2 = "\XFE\X3F\X00"
RESET_R_A2 = "\XFE\X3F\XFE"
RESET_L_A2 = "\XFE\X3F\XFD"

RESET_POSITION_LIST = (RESET_M, RESET_R, RESET_L, RESET_M_A1, RESET_R_A1, RESET_L_A1, RESET_M_A2, RESET_R_A2, RESET_L_A2)

#Port_F_Shortcuts
P1x = 0x7F
P2x = 0xBF
P3x = 0xDF
P23x = 0x9F
P4x = 0xEF
K2x = 0xFB
K3x = 0xFD
K4x = 0xFE
#Port_E_Shortcuts
Lx = 0xEF
DLx = 0xEE
Dx = 0xFE
DRx = 0xDE
Rx = 0xDF
URx = 0xDD
Ux = 0xFD
ULx = 0xED
K1x = 0xFB
#Other_Shortcuts
Nox = 0xFF
Endx = (Nox, Nox, 0)

# Mixup Combos (Port F|Port E|Frame)
MIXUP_1 = "\x00\xDD\x0E\x9F\xDE\x03\x7F\x00\x01\x00\x00\x04\x00\xDD\x0E\x9F\xDE\x03\x7F\x00\x01\x00\x00\x01  \
           \x7F\xFE\x01\x00\x00\x00"
MIXUP_2 = "\x00\xDD\x0E\x9F\xDE\x03\x7F\x00\x01\x00\x00\x04\x7F\xFE\x01\x00\x00\x04\x7F\xFE\x01\x00\x00\x00"
MIXUP_3 = "\x00\xDD\x0E\x9F\xDE\x03\x7F\x00\x01\x00\x00\x04\x7F\xFE\x01\x00\x00\x04\xDF\xDF\x01\x00\x00\x00"
MIXUP_4 = "\x00\xDD\x0E\x9F\xDE\x0E\xDF\xDF\x01\x00\x00\x00"
MIXUP_5 = "\x9F\x00\x09\x7F\xFE\x08\x00\x00\x01\x7F\xFE\x08\x00\x00\x01\xDF\xDF\x01\x00\x00\x00"
MIXUP_6 = "\x9F\x00\x09\x7F\xFE\x08\x00\x00\x01\xDF\xDF\x01\x00\x00\x00"
MIXUP_7 = "\x9F\x00\x09\x7F\xFE\x08\x00\x00\x01\x00\xDD\x0E\x9F\xDE\x03\x7F\x00\x01\x00\x00\x00"
MIXUP_8 = "\x00\xDD\x0E\x9F\xDE\x0E\x00\x00\x00\x7F\xFE\x01\x00\x00\x00"

MIXUP_LIST = (MIXUP_1, MIXUP_2, MIXUP_3, MIXUP_4, MIXUP_5, MIXUP_6, MIXUP_7, MIXUP_8)

def _init():
    #Setting all sensor lines to High Outputs
    x=0
    while x < len(BUTTON_LIST):
        setPinDir(BUTTON_LIST[x], True)
        writePin(BUTTON_LIST[x], True)
        x = x + 1

def _wait_for_frame_delay(frames_to_wait):
    while frames_to_wait:
        pulsePin(Pulse, -32767, True)
        pulsePin(Pulse, -pulse_window, True)
        frames_to_wait = frames_to_wait - 1

def _speek(combo, index):
    return ord(combo[index])

def _spoke(index, val):
    global array_buf1
    array_buf1 = array_buf1[:index] + chr(val) + array_buf1[index + 1:]

def _chooseMixup():
    mixupNotSelected = True
    numMixups = 8
    randomMax = 4096
    randomSegment = randomMax / numMixups
    while mixupNotSelected:
        x = 0
        while x < numMixups:
            mixupCheck = random.randint(0, 4096)
            if randomSegment * x <= mixupCheck < randomSegment * x+1:
                chosenMixup = x
                mixupNotSelected = False
                break
            else:
                x = x + 1
    return chosenMixup

def run_single_mixup():
    chosenMixup = _chooseMixup()
    chosen_mixup = _chooseMixup()
    combo = MIXUP_LIST[chosen_mixup]
    run_combo_from_array(combo)
    reset_training_mode()

def start_block_training(total_mixups):
    mixups_remaining = total_mixups
    while mixups_remaining:
        chosen_mixup = _chooseMixup()
        combo = MIXUP_LIST[chosen_mixup]
        run_combo_from_array(combo)
        reset_training_mode()
        _wait_for_frame_delay(60*5)
        mixups_remaining = mixups_remaining - 1

def reset_training_mode():
    combo = RESET_POSITION_LIST[current_reset_position]
    index = 0
    s_index = index * 3
    combo_executing = True
    combo = MIXUP_LIST[combo]
    while combo_executing:
        poke(Port_B, _speek(combo, s_index))
        poke(Port_E, _speek(combo, s_index+1))
        frame_delay = _speek(combo, s_index+2)
        if frame_delay == 0:
            combo_executing = False
            if mixups_left:
                run_next_mixup()
        else:
            while frame_delay:
                pulsePin(PULSE, -32767, True)
                pulsePin(PULSE, -pulse_window, True)
                frame_delay = frame_delay - 1
            index = index + 1
            s_index = index * 3

def set_pulse_window(number):
    global pulse_window
    pulse_window = number

def run_combo_from_array(combo):
    global State, frame_delay, Address_Pointer
    index = 0
    s_index = index * 3
    combo_executing = True
    while combo_executing:
        print _speek(combo, s_index))
        print _speek(combo, s_index+1))
        frame_delay = _speek(combo, s_index+2)
        if frame_delay == 0:
            combo_executing = False
        else:
            _wait_for_frame_delay(frame_delay)
            index = index + 1
            s_index = index * 3


def run_combo_from_tuple(combo):
    global State, frame_delay, Address_Pointer
    Address_Pointer = 0
    combo_executing = True
    while combo_executing:
        poke(Port_F, combo[Address_Pointer][0])
        poke(Port_E, combo[Address_Pointer][1])
        frame_delay = combo[Address_Pointer][2]
        if frame_delay == 0:
            combo_executing = False
        else:
            _wait_for_frame_delay(frame_delay)
            Address_Pointer = Address_Pointer + 1

if __name__ == '__main__':
    start_block_training(1)