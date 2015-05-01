"""
This is an attempt to interface the SNAPpPad core with wxPython GUI.

As such, this has been pared down in relation to the v1 core.  All of the
brains have been pushed off to the GUI side and the SNAPpPad will only be
resonsible for holding the reset combos, receieving combos to be run
from the gui, recording inputs, and passing recorded combos/sending combos
back for debug/verification purposes.
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
INPUT = 0
OUTPUT = 1
board_mode = OUTPUT

GUI = "\xbe\xef\xda"

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

BUTTON_LIST = (PUNCH1, PUNCH2, PUNCH3, PUNCH4, KICK1, KICK2, KICK3,
    KICK4, START, SELECT, HOME, RIGHT, LEFT, UP, DOWN)

#---------------------------
#      Mode Functions      #
#---------------------------

@setHook(HOOK_STARTUP)
def playback_mode():
    global board_mode, combo_buf
    combo_blank_1 = "\x00" * 63
    combo_blank_2 = "\x00" * 63
    combo_buf = combo_blank_1 + combo_blank_2
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
    global combo_buf
    
    if board_mode == INPUT:
        combo_buf = ""
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
                combo_buf = combo_buf + chr(Peek_E) + chr(Peek_F)
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
                    combo_buf = combo_buf + chr(frame_delay) + chr(Peek_E) + chr(Peek_F)
                    Port_F = Peek_F
                    Port_E = Peek_E
                    input_count = input_count + 1
                    frame_delay = 0
                    if input_count >= 41:
                        combo_buf = combo_buf + "\x01\xFF\xFF\x00"
                        recording_combo = False
                elif frame_delay >= 255:
                    combo_buf = combo_buf + "\x01\xFF\xFF\x00"
                    recording_combo = False
                    
        playback_mode()


#---------------------------------------
#  READ / WRITE / XMIT / RCV Functions *
#---------------------------------------

def _speek(combo, index):
    return ord(combo[index])

def _spoke(index, val):
    global combo_buf
    combo_buf = combo_buf[:index] + chr(val) + combo_buf[index + 1:]

def comboFromGUI(combo, index):
    global combo_buf
    if index == 0:
        clearComboBuf()
        print "combo: ", combo
        byte = 0
        while byte < len(combo):
            _spoke(byte, _speek(combo, byte))
            byte = byte + 1
        rpc(GUI, "sendNext")
        print "Combo_buf: ", combo_buf
    else:
        byte = 0
        while byte < len(combo):
            _spoke(byte+64, _speek(combo, byte))
            byte = byte + 1
        print "Combo_buf: ", combo_buf
        
def clearComboBuf():
    byte = 0
    while byte < len(combo_buf):
        _spoke(byte, 0)
        byte = byte + 1
    

def _update_Range_Frame(rangeFrame, val):
    global combo_buf
    index = rangeFrame * 3
    _spoke(index, val)

def comboToGUI():
    print "combo_buf: ", combo_buf
    if len(combo_buf) > 60:
        combo1 = combo_buf[:60]
        combo2 = combo_buf[60:]
        rpc(GUI, 'comboToGUI', combo1, 1)
        rpc(GUI, 'comboToGUI', combo2, 0)
    else:
        rpc(GUI, 'comboToGUI', combo_buf, 0)

def confirm_com():
    rpc(GUI, "SNAPpPadConfirm")

#---------------------------
# Hardware Timer Functions #
#---------------------------

def _init_frame_timer():
    """Initialize the hardware timer, and reset count"""
    poke(TCCR1A, 192)  # Set OCF1A flag on match
    poke(TCCR1B, 10)  # Run counter-mode with prescaler at divide-by 8 and CTC set
    poke(OCR1AH, 0x98)
    poke(OCR1AL, 0x17) # Set OCR1A compare value = 0x7908 / 30728 cycles / 1 Frame - Overhead

def _reset_timer():
    # Note: Must write HI byte before LO byte
    poke(TCNT1H, 0)
    poke(TCNT1L, 0)
    poke(OCF1A, 14)  # Set OCF1A flag to 0

#---------------------------
#  Basic Combo Functions   #
#---------------------------

# Reset Codes (Port E|Port B|Delay)
RESET_BACK = "\x9F\xEF\x05\xFF\xFF\x26\xFF\xFF\x00"
RESET_MID = "\x9F\xFF\x05\xFF\xFF\x26\xFF\xFF\x00"
RESET_CORNER = "\x9F\xDF\x05\xFF\xFF\x26\xFF\xFF\x00"

RESET_POSITION_LIST = (RESET_BACK, RESET_MID, RESET_CORNER)

def reset_training_mode(position):
    index = 0
    s_index = index * 3
    resetting = True
    call(DISABLE_INTERRUPT)
    combo = RESET_POSITION_LIST[position]
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
    return True

def run_combo():
    running_combo = True
    index = 0
    s_index = index * 3
    first_frame = True
    call(DISABLE_INTERRUPT)
    _reset_timer()
    while running_combo:
        #Push inputs to the real ports and set frame delay.
        poke(PORT_E, _speek(combo_buf, s_index))
        poke(PORT_F, _speek(combo_buf, s_index+1))
        frame_delay = _speek(combo_buf, s_index+2)
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
                        poke(PORT_A, _speek(combo_buf, s_index+2))
                        _reset_timer()
                    frame_delay = frame_delay - 1
            index = index + 1
            s_index = index * 3
    call(ENABLE_INTERRUPT)
    return True

def run_combo_debug_pokeless():
    print 'Attempting to run combo: ', combo_buf
    index = 0
    s_index = index * 3
    running = True
    while running:
        print 'poking E: ', _speek(combo_buf, s_index)
        print 'poking F: ', _speek(combo_buf, s_index+1)
        print 'Frame Delay: ', _speek(combo_buf, s_index+2)
        frame_delay = _speek(combo_buf, s_index+2)
        if frame_delay == 0:
            running = False
        index = index + 1
        s_index = index * 3
    

def run_combo_debug():
    print 'Attempting to run combo: ', combo_buf
    running_combo = True
    index = 0
    s_index = index * 3
    first_frame = True
    _reset_timer()
    while running_combo:
        #Push inputs to the real ports and set frame delay.
        print 'poking E: ', _speek(combo_buf, s_index)
        poke(PORT_E, _speek(combo_buf, s_index))
        print 'poking F: ', _speek(combo_buf, s_index+1)
        poke(PORT_F, _speek(combo_buf, s_index+1))
        print 'Frame Delay: ', _speek(combo_buf, s_index+2)
        frame_delay = _speek(combo_buf, s_index+2)
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
                        poke(PORT_A, _speek(combo_buf, s_index+2))
                        _reset_timer()
                    frame_delay = frame_delay - 1
                    print "Frame Delay", frame_delay
            index = index + 1
            s_index = index * 3
    return True