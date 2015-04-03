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
combo = ((1byte_Port_F Buttons, 1_byte_PORT_E Buttons, 1_byte_frame_delay),
         (2nd Port F Buttons, 2nd Port E, 2nd frame_delay),
         (3rd...),...,(Nth...)
         (Empty Port F, Empty Port E, Empty Delay))
"""

from synapse.platforms import *

# Button Definitions
PUNCH1 = GPIO_18
PUNCH2 = GPIO_17
PUNCH3 = GPIO_16
PUNCH4 = GPIO_15
KICK1 = GPIO_13
KICK2 = GPIO_12
KICK3 = GPIO_11
KICK4 = GPIO_14
START = GPIO_0
SELECT = GPIO_1
HOME = GPIO_2
RIGHT = GPIO_6
LEFT = GPIO_5
UP = GPIO_3
DOWN = GPIO_4
PULSE = GPIO_10

# Global Inits
current_reset_position = 1
running_mixups = False
mixup_timer = -1

#Raw Opcodes
DISABLE_INTERRUPT = "\xF8\x94\x08\x95"
ENABLE_INTERRUPT = "\x78\x94\x08\x95"

#Hardware timer API for AVR, using Timer 1
TCCR1A = 0x80  # Control register A
TCCR1B = 0x81  # Control register B
TCNT1H = 0x85  # Counter High byte
TCNT1L = 0x84  # Counter Low byte
OCR1AH = 0x89  # Compare High Byte
OCR1AL = 0x88  # Compare Low Byte
OCF1A = 0x36 # Bit 2 is the OCRA1 Flag

# ATmeg128RFA1 Address Mapping
PORT_F = 0x31
PORT_E = 0x2E
PORT_B = 0x25

#           7   6   5   4   3   2   1  0
# Port F = 1P, 2P, 3P, 4P, __, 1K, 2K, 3K
# Port F =  L,  M,  H, 4P, __,  S, A1, A2 (Marvel Mappings)
# Port E = __, __, Ri, Le, __, 4K, Do, Up
# Port B = St, Se, Ho, __, __, __, __, __

# Reset Codes (Port B|Port E|Delay)
RESET_MID = "\x3F\xFF\x05\xFF\xFF\x26\xFF\xFF\x00"
RESET_CORNER = "\x3F\xDF\x05\xFF\xFF\x26\xFF\xFF\x00"

RESET_POSITION_LIST = (RESET_MID, RESET_CORNER)

# Mixup Combos (Port F|Port E|Frame)
MIXUP_0 = "\xFF\xDD\x0C\x9F\xDE\x03\xFF\xFF\x06\x7F\xFE\x01\xFF\xFF\x07\x7F\xFE\x01\xFF\xFF\x40\xFF\xFF\x00"
MIXUP_1 = "\xFF\xDD\x0C\x9F\xDE\x03\x7F\xFF\x08\xFF\xFE\x03\xFF\xFD\x0C\x9F\xFE\x03\x7F\xFF\x01\xFF\xFF\x0C\x7F\xFE\x01\xFF\xFF\x40\xFF\xFF\x00"
MIXUP_2 = "\xFF\xDD\x0C\x9F\xDE\x03\x7F\xFF\x08\xFF\xFF\x03\x7F\xFE\x01\xFF\xFF\x07\x7F\xFE\x01\xFF\xFF\x40\xFF\xFF\x00"
MIXUP_3 = "\xFF\xDD\x0E\x9F\xDE\x03\x7F\xFF\x01\xFF\xFF\x04\x7F\xFE\x01\xFF\xFF\x14\xDF\xDF\x01\xFF\xFF\x40\xFF\xFF\x00"
MIXUP_4 = "\xFF\xDD\x0E\x9F\xDE\x14\xFF\xFF\x01\xDF\xDF\x01\xFF\xFF\x40\xFF\xFF\x00"
MIXUP_5 = "\x9F\xFF\x09\x7F\xFE\x08\xFF\xFF\x01\x7F\xFE\x08\xFF\xFF\x14\xDF\xDF\x01\xFF\xFF\x40\xFF\xFF\x00"
MIXUP_6 = "\x9F\xFF\x06\x7F\xFE\x09\xFF\xFF\x12\xDF\xDF\x01\xFF\xFF\x40\xFF\xFF\x00"
MIXUP_7 = "\x9F\xFF\x06\x7F\xFE\x09\xFF\xFF\x12\xFF\xDD\x0E\x9F\xDE\x03\x7F\xFF\x01\xFF\xFF\x40\xFF\xFF\x00"

BUTTON_LIST = (PUNCH1, PUNCH2, PUNCH3, PUNCH4, KICK1, KICK2, KICK3,
    KICK4, START, SELECT, HOME, RIGHT, LEFT, UP, DOWN)

@setHook(HOOK_STARTUP)
def _init():
    #Setting all sensor lines to High Outputs
    x=0
    while x < len(BUTTON_LIST):
        setPinDir(BUTTON_LIST[x], True)
        writePin(BUTTON_LIST[x], True)
        x = x + 1
    _init_frame_timer()

@setHook(HOOK_100MS)
def _mixup_delay():
    global mixup_timer
    if mixup_timer > 0:
        mixup_timer = mixup_timer - 1
    elif mixup_timer == 0:
        mixup_timer = mixup_timer - 1
        reset_training_mode()
        
def _update_frame_delay(combo_position, frame_to_update, new_frame_delay):
    global MIXUP_0, MIXUP_1, MIXUP_2, MIXUP_3, MIXUP_4, MIXUP_5, MIXUP_6, MIXUP_7
    if combo_position == 0:
        MIXUP_0 = MIXUP_0[frame_to_update*12+8:] + new_frame_delay + MIXUP_0[frame_to_update+1*12]
    if combo_position == 1:
        MIXUP_1 = MIXUP_1[frame_to_update*12+8:] + new_frame_delay + MIXUP_1[frame_to_update+1*12]
    if combo_position == 2:
        MIXUP_2 = MIXUP_2[frame_to_update*12+8:] + new_frame_delay + MIXUP_2[frame_to_update+1*12]
    if combo_position == 3:
        MIXUP_3 = MIXUP_3[frame_to_update*12+8:] + new_frame_delay + MIXUP_3[frame_to_update+1*12]
    if combo_position == 4:
        MIXUP_4 = MIXUP_4[frame_to_update*12+8:] + new_frame_delay + MIXUP_4[frame_to_update+1*12]
    if combo_position == 5:
        MIXUP_5 = MIXUP_5[frame_to_update*12+8:] + new_frame_delay + MIXUP_5[frame_to_update+1*12]
    if combo_position == 6:
        MIXUP_6 = MIXUP_6[frame_to_update*12+8:] + new_frame_delay + MIXUP_6[frame_to_update+1*12]
    if combo_position == 7:
        MIXUP_7 = MIXUP_7[frame_to_update*12+8:] + new_frame_delay + MIXUP_7[frame_to_update+1*12]

def _recieve_combo(combo_position, combo_string, append=False):
    global MIXUP_0, MIXUP_1, MIXUP_2, MIXUP_3, MIXUP_4, MIXUP_5, MIXUP_6, MIXUP_7
    if combo_position == 0:
        if append:
            MIXUP_0 = MIXUP_0 + combo_string
        else:
            MIXUP_0 = combo_string
    elif combo_position == 1:
        if append:
            MIXUP_1 = MIXUP_1 + combo_string
        else:
            MIXUP_1 = combo_string
    elif combo_position == 2:
        if append:
            MIXUP_2 = MIXUP_2 + combo_string
        else:
            MIXUP_2 = combo_string
    elif combo_position == 3:
        if append:
            MIXUP_3 = MIXUP_3 + combo_string
        else:
            MIXUP_3 = combo_string
    elif combo_position == 4:
        if append:
            MIXUP_4 = MIXUP_4 + combo_string
        else:
            MIXUP_4 = combo_string
    elif combo_position == 5:
        if append:
            MIXUP_5 = MIXUP_5 + combo_string
        else:
            MIXUP_5 = combo_string
    elif combo_position == 6:
        if append:
            MIXUP_6 = MIXUP_6 + combo_string
        else:
            MIXUP_6 = combo_string
    elif combo_position == 7:
        if append:
            MIXUP_7 = MIXUP_7 + combo_string
        else:
            MIXUP_7 = combo_string


def _init_frame_timer():
    """Initialize the hardware timer, and reset count"""
    poke(TCCR1A, 192)  # Set OCF1A flag on match
    poke(TCCR1B, 10)  # Run counter-mode with prescaler at divide-by 8 and CTC set
    poke(OCR1AH, 0x82)
    poke(OCR1AL, 0x3C) # Set OCR1A compare value = 0x823C / 33340 cycles / 16.67mS / 1 Frame

def _reset_timer():
    # Note: Must write HI byte before LO byte
    poke(TCNT1H, 0)
    poke(TCNT1L, 0)
    poke(OCF1A, 14)  # Set OCF1A flag to 0

def _poll_timer_flag():
    # Note: Must read LO byte before HI byte
    if peek(OCF1A) & 2:
        poke(OCF1A, 14)
        return True
    else:
        return False

def _speek(combo, index):
    return ord(combo[index])

def _spoke(index, val):
    global array_buf1
    array_buf1 = array_buf1[:index] + chr(val) + array_buf1[index + 1:]

def _chooseMixup():
    calculating_mixup = True
    random_number = random()
    mixup_choice = 0
    num_mixups = 8
    random_max = 4096
    random_segment = random_max / num_mixups
    while mixup_choice < num_mixups and calculating_mixup:
        if random_segment * mixup_choice <= random_number < random_segment * (mixup_choice + 1):
            chosen_mixup = mixup_choice
            print chosen_mixup
            calculating_mixup = False
        else:
            mixup_choice = mixup_choice + 1
    return chosen_mixup
            
def _chooseComboFromList(combo):
    if combo == 0:
            combo_string = MIXUP_0
    elif combo == 1:
            combo_string = MIXUP_1
    elif combo == 2:
            combo_string = MIXUP_2
    elif combo == 3:
            combo_string = MIXUP_3
    elif combo == 4:
            combo_string = MIXUP_0
    elif combo == 5:
            combo_string = MIXUP_1
    elif combo == 6:
            combo_string = MIXUP_2
    elif combo == 7:
            combo_string = MIXUP_3
    return combo_string

def start_mixups():
    global running_mixups
    running_mixups = True
    reset_training_mode()

def stop_mixups():
    global running_mixups
    running_mixups = False

def reset_training_mode():
    global selected_mixup
    index = 0
    s_index = index * 3
    resetting = True
    combo = RESET_POSITION_LIST[current_reset_position]
    call(DISABLE_INTERRUPT)
    while resetting:
        poke(PORT_B, _speek(combo, s_index))
        poke(PORT_E, _speek(combo, s_index+1))
        frame_delay = _speek(combo, s_index+2)
        if frame_delay == 0:
            resetting = False
        else:
            while frame_delay:
                pulsePin(PULSE, -32767, True)
                pulsePin(PULSE, -pulse_window, True)
                frame_delay = frame_delay - 1
            index = index + 1
            s_index = index * 3
    call(ENABLE_INTERRUPT)
    if running_mixups:
        chosen_mixup = _chooseMixup()
        run_combo_with_HW_timer(chosen_mixup)

def run_combo_with_HW_timer(combo_num):
    global mixup_timer
    index = 0
    s_index = index * 3
    running_combo = True
    combo = _chooseComboFromList(combo_num)
    call(DISABLE_INTERRUPT)
    while running_combo:
        poke(PORT_F, _speek(combo, s_index))
        poke(PORT_E, _speek(combo, s_index+1))
        frame_delay = _speek(combo, s_index+2)
        if frame_delay == 0:
            running_combo = False
        else:
            _reset_timer()
            while frame_delay:
                if peek(OCF1A) & 2:
                    poke(OCF1A, 14)
                    frame_delay = frame_delay - 1
            index = index + 1
            s_index = index * 3
    call(ENABLE_INTERRUPT)
    if running_mixups:
        mixup_timer = 1

