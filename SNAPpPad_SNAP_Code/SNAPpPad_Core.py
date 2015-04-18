"""
This is an attempt at SNAPifying a PS360+ PCB board to allow the SNAP engine to interface with
either a PS3, Xbox360, or PC.

It is intended for use as a fighting game training/practice tool and, as such, would need to
be accurate to 1/60th of a second (1/60th sec = 16.67ms = 16670 microseconds).  On any given
frame, the SNAP engine will need to be able to press/release/hold one of the 15 input
buttons and wait for a set number of frames (between 0~255.)

To accomodate for this speed, we will be mapping all timing-specific buttons to contiguous
ports and Poke() all values in at once (rather than processing through the buttons one by one)
and utilizing hardware timers on the microprocessor to have timing be as stable and reliable
as possible..

Basic format for combo data will be as follows:
combo = "| 1byte_Port_F Buttons | 1_byte_PORT_E Buttons | 1_byte_frame_delay |
         | 2nd Port F Buttons | 2nd Port E | 2nd frame_delay |
         (3rd...),...,(Nth...)
         | Empty Port F | Empty Port E | Empty Delay"

example_combo = '\xfe\xff\x01\xde\xff\x01\xdf\x7f\x01\xff\xff\x00'
"""

from synapse.platforms import *

# Button Definitions
KICK4 = GPIO_14
KICK3 = GPIO_11
KICK2 = GPIO_12
KICK1 = GPIO_13

PUNCH4 = GPIO_15
PUNCH3 = GPIO_16
PUNCH2 = GPIO_17
PUNCH1 = GPIO_18

START = GPIO_2
SELECT = GPIO_1
HOME = GPIO_0

RIGHT = GPIO_6
LEFT = GPIO_5
UP = GPIO_4
DOWN = GPIO_3


# Global Inits
current_reset_position = 0
running_mixups = False
range_testing = False
mixup_timer = -1

INPUT = 0
OUTPUT = 1
board_mode = OUTPUT

range_test_combo = None
range_input_count = None

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
PORT_F_INPUT = 0x2F
PORT_E = 0x2E
PORT_E_INPUT = 0x2C
PORT_B = 0x25
PORT_A = 0x22

#           7   6   5   4   3   2   1  0
# Port F = 1P, 2P, 3P, 4P, __, 1K, 2K, 3K
# Port F =  L,  M,  H, 4P, __,  S, A1, A2 (Marvel Mappings)
# Port E = __, __, Ri, Le, __, 4K, Up, Do
# Port B = Ho, Se, St, __, __, __, __, __

# Reset Codes (Port E|Port B|Delay) Had to modify these temporarily due to a HW issue. -Kyle
#RESET_MID = "\x9F\xFF\x05\xFF\xFF\x26\xFF\xFF\x00"
#RESET_CORNER = "\x9F\xDF\x05\xFF\xFF\x26\xFF\xFF\x00"
# Reset Codes (Port B|Port E|Delay)
RESET_MID = "\xFF\x3F\x05\xFF\xFF\x26\xFF\xFF\x00"
RESET_CORNER = "\xDF\x3F\x05\xFF\xFF\x26\xFF\xFF\x00"

RESET_POSITION_LIST = (RESET_MID, RESET_CORNER)

# Mixup Combos (Port E|Port F|Frame)
MIXUP_0 = '\xff\xff\x06\xfd\xff\x03\xfe\xff\x0b\xfd\xff\x01\xdd\xff\x01\xdf\xff\x01\xde\x9f\x01\xff\x7f\x01\xff\xff\x00'
MIXUP_1 = '\xff\xff\x06\xfd\xff\x03\xfe\xff\x0b\xfd\xff\x01\xdd\xff\x01\xdf\xff\x01\xfe\x9f\x01\xff\x7f\x01\xff\xff\x00'
MIXUP_2 = '\xff\xff\x06\xfd\xff\x03\xfe\xff\x0b\xfd\xff\x01\xdd\xff\x01\xdf\xff\x01\xee\x9f\x01\xff\x7f\x01\xff\xff\x00'
MIXUP_3 = '\xff\xff\x06\xfd\xff\x03\xfe\xff\x0b\xfd\xff\x01\xdd\xff\x01\xdf\xff\x01\xee\x9f\x01\xff\x7f\x01\xff\xff\x00'
MIXUP_4 = '\xff\xff\x06\xfd\xff\x03\xfe\xff\x0b\xfd\xff\x01\xdd\xff\x01\xdf\xff\x01\xed\x9f\x01\xff\x7f\x01\xff\xff\x00'
MIXUP_5 = '\xff\xff\x06\xfd\xff\x03\xfe\xff\x0b\xfd\xff\x01\xdd\xff\x01\xdf\xff\x01\xfd\x9f\x01\xff\x7f\x01\xff\xff\x00'
MIXUP_6 = '\xff\xff\x06\xfd\xff\x03\xfe\xff\x0b\xfd\xff\x01\xdd\xff\x01\xdf\xff\x01\xdd\x9f\x01\xff\x7f\x01\xff\xff\x00'
MIXUP_7 = '\xff\xff\x06\xfd\xff\x03\xfe\xff\x0b\xfd\xff\x01\xdd\xff\x01\xdf\xff\x01\xdf\x9f\x01\xff\x7f\x01\xff\xff\x00'

BUTTON_LIST = (PUNCH1, PUNCH2, PUNCH3, PUNCH4, KICK1, KICK2, KICK3,
    KICK4, START, SELECT, HOME, RIGHT, LEFT, UP, DOWN)

#---------------------------
#      Mode Functions      #
#---------------------------

@setHook(HOOK_STARTUP)
def playback_mode():
    global board_mode
    board_mode = OUTPUT
    #Setting all sensor lines to High Outputs
    x=0
    while x < len(BUTTON_LIST):
        setPinDir(BUTTON_LIST[x], True)
        writePin(BUTTON_LIST[x], True)
        x = x + 1

    _init_frame_timer()

def passthrough_mode():
    global board_mode
    board_mode = INPUT
    x=0
    while x < len(BUTTON_LIST):
        setPinDir(BUTTON_LIST[x], False)
        x = x + 1
        
def record_combo():
    global MIXUP_0
    
    if board_mode == INPUT:
        MIXUP_0 = ""
        waiting_for_user_input = True
        recording_combo = True
        Port_F = 0xFF
        Port_E = 0xFF
        input_count = 0
        frame_delay = 0
        
        while waiting_for_user_input:
            Peek_F = peek(PORT_F_INPUT)
            Peek_E = peek(PORT_E_INPUT)
            if Peek_F != Port_F or Peek_E != Port_E:
                MIXUP_0 = MIXUP_0 + chr(Peek_E) + chr(Peek_F)
                Port_F = Peek_F
                Port_E = Peek_E
                _reset_timer()

                waiting_for_user_input = False
                input_count = input_count + 1
                
        while recording_combo:
            if peek(OCF1A) & 2:
                poke(OCF1A, 14)
                frame_delay = frame_delay + 1
                Peek_E = peek(PORT_E_INPUT)
                Peek_F = peek(PORT_F_INPUT)
                if Peek_F != Port_F or Peek_E != Port_E:
                    MIXUP_0 = MIXUP_0 + chr(frame_delay) + chr(Peek_E) + chr(Peek_F)
                    Port_F = Peek_F
                    Port_E = Peek_E
                    input_count = input_count + 1
                    frame_delay = 0
                    if input_count >= 41:
                        MIXUP_0 = MIXUP_0 + "\x01\xFF\xFF\x00"
                        recording_combo = False
                elif frame_delay >= 255:
                    MIXUP_0 = MIXUP_0 + "\x01\xFF\xFF\x00"
                    recording_combo = False
                    
        playback_mode()


#---------------------------------------
#  READ / WRITE / XMIT / RCV Functions *
#---------------------------------------

def _speek(combo, index):
    return ord(combo[index])
    
def send_combo_to_portal(combo_num):
    combo = _chooseComboFromList(combo_num)
    if len(combo) > 60:
        combo1 = combo[:60]
        combo2 = combo[60:]
        rpc('\x00\x00\x0F', 'combo', combo1)
        rpc('\x00\x00\x0F', 'combo', combo2)
    else:
        rpc('\x00\x00\x0F', 'combo', combo)

def _spoke(combo_position, index, val):
    global MIXUP_0, MIXUP_1, MIXUP_2, MIXUP_3, MIXUP_4, MIXUP_5, MIXUP_6, MIXUP_7, RANGE_COMBO
    if combo_position == 0:
        MIXUP_0 = MIXUP_0[:index] + chr(val) + MIXUP_0[index + 1:]
    if combo_position == 1:
        MIXUP_1 = MIXUP_1[:index] + chr(val) + MIXUP_1[index + 1:]
    if combo_position == 2:
        MIXUP_2 = MIXUP_2[:index] + chr(val) + MIXUP_2[index + 1:]
    if combo_position == 3:
        MIXUP_3 = MIXUP_3[:index] + chr(val) + MIXUP_3[index + 1:]
    if combo_position == 4:
        MIXUP_4 = MIXUP_4[:index] + chr(val) + MIXUP_4[index + 1:]
    if combo_position == 5:
        MIXUP_5 = MIXUP_5[:index] + chr(val) + MIXUP_5[index + 1:]
    if combo_position == 6:
        MIXUP_6 = MIXUP_6[:index] + chr(val) + MIXUP_6[index + 1:]
    if combo_position == 7:
        MIXUP_7 = MIXUP_7[:index] + chr(val) + MIXUP_7[index + 1:]

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
        combo_string = MIXUP_4
    elif combo == 5:
        combo_string = MIXUP_5
    elif combo == 6:
        combo_string = MIXUP_6
    elif combo == 7:
        combo_string = MIXUP_7
    return combo_string

#---------------------------
# Hardware Timer Functions #
#---------------------------

def _init_frame_timer():
    """Initialize the hardware timer, and reset count"""
    poke(TCCR1A, 192)  # Set OCF1A flag on match
    poke(TCCR1B, 10)  # Run counter-mode with prescaler at divide-by 8 and CTC set
    poke(OCR1AH, 0x7E)
    poke(OCR1AL, 0xFB) # Set OCR1A compare value = 0x7908 / 30728 cycles / 1 Frame - Overhead

def _reset_timer():
    # Note: Must write HI byte before LO byte
    poke(TCNT1H, 0)
    poke(TCNT1L, 0)
    poke(OCF1A, 14)  # Set OCF1A flag to 0

#---------------------------
#      Mixup Functions     #
#---------------------------

def start_mixups():
    global running_mixups
    running_mixups = True
    reset_training_mode()

def stop_mixups():
    global running_mixups
    running_mixups = False

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
            calculating_mixup = False
        else:
            mixup_choice = mixup_choice + 1
    return chosen_mixup

#---------------------------
#  Range Finder Functions  #
#---------------------------

def start_range_testing(combo_num):
    global range_testing, range_test_combo
    range_test_combo = combo_num
    reset_training_mode()
    range_testing = True
    run_combo(range_test_combo)

def stop_range_testing():
    global range_testing
    range_testing = False

def _set_range_input_count(val):
    global range_input_count
    range_input_count = val

def _update_range_test_frame():
    print 'Inside update range'
    print 'range_input_count: ', range_input_count
    print 'range_test_combo: ', range_test_combo
    frame_location = (range_input_count * 3) + 2
    print 'frame_location: ', frame_location
    range_test_string = _chooseComboFromList(range_test_combo)
    send_combo_to_portal(range_test_combo)
    current_frame_delay = _speek(range_test_string, frame_location)
    print 'current_frame_delay: ', current_frame_delay
    _spoke(range_test_combo, frame_location, current_frame_delay+1)
    send_combo_to_portal(range_test_combo)

#---------------------------
#  Basic Combo Functions   #
#---------------------------

@setHook(HOOK_100MS)
def _loop_timer():
    global reset_timer
    if reset_timer > 0:
        reset_timer = reset_timer - 1
    elif reset_timer == 0:
        reset_timer = reset_timer - 1
        reset_training_mode()

def reset_training_mode():
    global selected_mixup
    index = 0
    s_index = index * 3
    resetting = True
    combo = RESET_POSITION_LIST[current_reset_position]
    call(DISABLE_INTERRUPT)
    while resetting:
        poke(PORT_E, _speek(combo, s_index))
        poke(PORT_B, _speek(combo, s_index+1))
        frame_delay = _speek(combo, s_index+2)
        if frame_delay == 0:
            resetting = False
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
        chosen_mixup = _chooseMixup()
        run_combo(chosen_mixup)
    if range_testing:
        _update_range_test_frame()
        print 'updated the range combo.'
        run_combo(range_test_combo)

def run_combo(combo_num):
    global reset_timer
    running_combo = True
    combo = _chooseComboFromList(combo_num)
    
    #Don't try and run an empty combo
    if combo == '':
        running_combo = False
    
    #Check for range test flag, set input_number and tell combo to ignore first input.
    if combo[0:2] == '\xff\xff':
        _set_range_input_count(_speek(combo, 2))
        index = 1
    else:
        index = 0

    s_index = index * 3
    first_frame = True
    call(DISABLE_INTERRUPT)
    _reset_timer()
    while running_combo:
        #Push inputs to the real ports and set frame delay.
        poke(PORT_E, _speek(combo, s_index))
        poke(PORT_F, _speek(combo, s_index+1))
        frame_delay = _speek(combo, s_index+2)
        if frame_delay == 0:
            running_combo = False
        else:
            while frame_delay:
                if peek(OCF1A) & 2:
                    #DON'T MODIFY THIS PORTION. THIS IS SPECIFICALLY CODED TO CREATE CONSISTENT TIMING!!!!
                    if first_frame:
                        first_frame = False
                        _reset_timer()
                    else:
                        poke(PORT_A, _speek(combo, s_index+2))
                        _reset_timer()
                    frame_delay = frame_delay - 1
            index = index + 1
            s_index = index * 3
    call(ENABLE_INTERRUPT)

    if running_mixups or range_testing:
        reset_timer = 1