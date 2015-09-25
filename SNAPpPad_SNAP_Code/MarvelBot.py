"""
This is an attempt to interface the SNAPpPad core with wxPython GUI.

As such, this has been pared down in relation to the v1 core.  All of the
brains have been pushed off to the GUI side and the SNAPpPad will only be
responsible for holding the reset combos, receiving combos to be run
from the gui, recording inputs, and passing recorded combos/sending combos
back for debug/verification purposes.

This version is utilizing an SN173 to control 2 controllers at the same
time and uses SNAP Collect to utilize as much buffer space as possible
as well as byte-lists released in SNAP Core 2.6 to get away from having
to use the horrible string buffer workaround used in the earlier versions.

This version will not be compatible with earlier versions, as the SN172
utilized the IO ports much more cleanly than the SN171.

P1
Port E: Directions + St/Se/Home
Port F: Buttons

P2
Port B: Directions + St/Se/Home
Port D: Buttons
"""

from synapse.SM220 import *

# Button Definitions
# Player 1
P1_K1 = GPIO_B2
P1_K2 = GPIO_C3
P1_K3 = GPIO_B3
P1_K4 = GPIO_C5

P1_P1 = GPIO_C1
P1_P2 = GPIO_C2
P1_P3 = GPIO_B1
P1_P4 = GPIO_C4

P1_ST = GPIO_A4
P1_SE = GPIO_B4
P1_HO = GPIO_A5

P1_R = GPIO_B7
P1_L = GPIO_A7
P1_U = GPIO_A6
P1_D = GPIO_B6

P2_K1 = GPIO_E2
P2_K2 = GPIO_E3
P2_K3 = GPIO_D1
P2_K4 = GPIO_D3

P2_P1 = GPIO_F1
P2_P2 = GPIO_F2
P2_P3 = GPIO_E1
P2_P4 = GPIO_D2

P2_ST = GPIO_F4
P2_SE = GPIO_F3
P2_HO = GPIO_G4

P2_R = GPIO_G2
P2_L = GPIO_H2
P2_U = GPIO_G3
P2_D = GPIO_H3

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
PORT_D = 0x2B
PORT_D_INPUT = 0x29
PORT_B = 0x25
PORT_B_INPUT = 0x23


#           7   6   5   4   3   2   1  0
# Port B = 4K ,4P , B , A , S , H , M , L
# Port D =  F , B , D , U , _ ,HO ,SE ,ST
# Port E = 4k ,4p , b , a , s , h , m , l
# Port F =  f , b , d , u , _ ,ho ,se ,st


BUTTON_LIST = (P1_K1, P1_K2, P1_K3, P1_K4, P1_P1, P1_P2, P1_P3, P1_P4, P1_ST, P1_SE, P1_HO, P1_R, P1_L, P1_U, P1_D,
                P2_K1, P2_K2, P2_K3, P2_K4, P2_P1, P2_P2, P2_P3, P2_P4, P2_ST, P2_SE, P2_HO, P2_R, P2_L, P2_U, P2_D)

MIXUP_0 = ['\x7f\xfe\x7f\xfe\x01\x3f\xfd\x3f\xfd\x01\xbf\xfb\xbf\xfb\x01\x9f\xef\x9f\xef\x01\xdf\xdf\xdf\xdf\x01\xcf\x9f\xcf\x9f\x01\xbf\xfe\xbf\xfe\x01\x6f\xfd\x6f\xfd\x01\x7f\xfb\x7f\xfb\x01\xff\xff\xff\xff\x00']


#---------------------------
#      Mode Functions      #
#---------------------------

@setHook(HOOK_STARTUP)
def _init():
    saveNvParam(11, 0x011F)
    playback_mode()
    _init_frame_timer()

def playback_mode():
    global board_mode
    #Setting all sensor lines to High Outputs
    board_mode = OUTPUT
    for x in BUTTON_LIST:
        setPinDir(x, True)
        writePin(x, True)

def passthrough_mode():
    global board_mode
    board_mode = INPUT
    for x in BUTTON_LIST:
        setPinDir(x, False)

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
        comboFromSNAPpPad()
        playback_mode()

#---------------------------------------
#  READ / WRITE / XMIT / RCV Functions *
#---------------------------------------

def comboToSNAPpPad(combo, index):
    global combo_buf
    if index == 0:
        clearComboBuf()
        byte = 0
        while byte < len(combo):
            _spoke(byte, _speek(combo, byte))
            byte = byte + 1
    else:
        byte = 0
        while byte < len(combo):
            _spoke(byte+64, _speek(combo, byte))
            byte = byte + 1
    return 0

def comboFromSNAPpPad():
    print "combo_buf: ", combo_buf
    if len(combo_buf) > 60:
        combo1 = combo_buf[:60]
        combo2 = combo_buf[60:]
        rpc(GUI, 'comboFromSNAPpPad', combo1, 1)
        rpc(GUI, 'comboFromSNAPpPad', combo2, 0)
    else:
        rpc(GUI, 'comboFromSNAPpPad', combo_buf, 0)

def confirm_com():
    return True

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

def PressButton(Port, Command):
    if Port == "B":
        poke(PORT_B, Command)
    if Port == "F":
        poke(PORT_F, Command)
    if Port == "E":
        poke(PORT_E, Command)

# Reset Codes (Port E|Port B|Delay)
RESET_BACK = "\xEF\x3F\x05\xFF\xFF\x00"
RESET_MID = "\xFF\x3F\x05\xFF\xFF\x00"
RESET_FRONT = "\xDF\x3F\x05\xFF\xFF\x00"

RESET_POSITION_LIST = (RESET_BACK, RESET_MID, RESET_FRONT)

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
    return 2

def run_combo():
    running_combo = True
    combo = MIXUP_0
    index = 0
    command = 0
    first_frame = True
    call(DISABLE_INTERRUPT)
    _reset_timer()
    while running_combo:
        #Push inputs to the real commands and set frame delay.
        poke(PORT_F, (combo, command))
        poke(PORT_D, (combo, command+1))
        poke(PORT_E, (combo, command+2))
        poke(PORT_B, (combo, command+3))
        frame_delay = (combo, command+4)
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
                        poke(PORT_A, _speek(combo_buf, command+4))
                        _reset_timer()
                    frame_delay = frame_delay - 1
            index = index + 1
            command = index * 3
    call(ENABLE_INTERRUPT)
    return 1

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