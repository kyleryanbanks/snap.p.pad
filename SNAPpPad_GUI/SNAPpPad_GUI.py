import sys
import os
import itertools
import re
import random

from snapconnect import snap
import binascii

import wx
import wx.lib.newevent
import SNAPpPad_wx
import Combo_Converter

import logging

class WxTextCtrlHandler(logging.Handler):
    def __init__(self, ctrl):
        logging.Handler.__init__(self)
        self.ctrl = ctrl

    def emit(self, record):
        s = self.format(record) + '\n'
        wx.CallAfter(self.ctrl.WriteText, s)

class SNAPpPad_GUI(SNAPpPad_wx.mainFrame):
    #constructor
    def __init__(self,parent):
        self._log = logging.getLogger("SNAPpPad")

        self.mainFrame = SNAPpPad_wx.mainFrame.__init__(self,parent)

        handler = WxTextCtrlHandler(self.Console)
        self._log.addHandler(handler)
        FORMAT = "%(asctime)s %(levelname)s %(message)s"
        handler.setFormatter(logging.Formatter(FORMAT))
        self._log.setLevel(logging.DEBUG)

        self.libFiles = os.listdir("Library")
        self.comboDict = {}
        self.activeSuiteDict = {}
	self.mixupDict = {}
        self.buildLibrary()
	self.btnDict = {'Port_B' : {'bHo' : "\x7F",
	                          'bSe' : "\xBF",
	                          'bHo' : "\xDF"
	                          },
	                'Port_F' : {'bP1' : "\x7F",
	                          'bP2' : "\xBF",
	                          'bP3' : "\xDF",
	                          'bK1' : "\xFB",
	                          'bK2' : "\xFD",
	                          'bK3' : "\xFE"
	                          },
	                'Port_E' : {'bLeft' : "\xEF",
	                          'bDown' : "\xFE",
	                          'bRight' : "\xDF",
	                          'bUp' : "\xFD",
	                          'bRelease' : "\xFF"
	                          },
	                }

	self.buildMode = False
	self.runningMixups = False
	self.rangeTesting = False
	self.rangeMode = False
	self.rangeFrame = None
	self.radioAddr = None

        self.suite = None
        self.combo = None

	self.funcdir = {"SNAPpPadConfirm": self.SNAPpPadConfirm,
	                "SNAPpPadReturn": self.SNAPpPadReturn,
	                "sendNext" : self.sendNext,
	                }
	self.com = None

###   Init Functions   ###
    def buildLibrary(self):
        if self.comboDict:
            self._log.info("Rebuilding Library")
            self.comboDict.clear()
            self.library.DeleteAllItems()
        for suite in self.libFiles:
            self.comboDict[suite] = {}
            with open("Library/" + suite) as f:
                for commentLine, comboLine in itertools.izip_longest(f, f, fillvalue=''):
                    commentLine = commentLine.rstrip('\n')
                    comboLine = comboLine.rstrip('\n')
		    if commentLine not in self.comboDict[suite]:
			self.comboDict[suite][commentLine] = comboLine

        self.root = self.library.AddRoot('Library')
        for suite in self.comboDict:
            header = self.library.AppendItem(self.root, suite)
            for combo in self.comboDict[suite]:
                self.library.AppendItem(header, combo)

###  General Functions  ###
    def showMessage(self, msgTypeStr, string):
	dlg = wx.MessageDialog(None, string, msgTypeStr, wx.OK)
	dlg.ShowModal()
	dlg.Destroy()

###  SnapConnect Functions  ###
    def openSnapCom(self):
	    if self.com == None:
		try:
		    self.com = snap.Snap("SNAP_license.dat", funcs=self.funcdir)
		    if self.com:
			try:
			    self.com.open_serial(snap.SERIAL_TYPE_SNAPSTICK100, 0, dll_path='.')
			except:
			    try:
				self.com.open_serial(snap.SERIAL_TYPE_SNAPSTICK200, 0, dll_path='.')
			    except:
				errStr = "Could not locate any USB bridge.\
				          \nPlease check the USB ports & verify they are not in use by another program."
				self.showMessage("Error", errStr)

				self.com = None
			    else:
				CONN_TYPE = snap.SERIAL_TYPE_SNAPSTICK200
			else:
			    CONN_TYPE = snap.SERIAL_TYPE_SNAPSTICK100
		except:
		    errStr = "The system could not establish a Snap instance.\
			      \nPlease check that the license file is in the program directory."
		    self.showMessage("Error", errStr)
		    self.com = None

    def OnIdle(self, event):
	if self.com:
	    self.com.poll()
	event.RequestMore(True)

    def testConnection(self, e):
	if self.com == None:
	    self.openSnapCom()
	    self._log.info("Attempting to open connection to SNAP Bridge.")
	self.com.save_nv_param(11, 0x011F)
	self.FindingRadioActive = True
	radioMac = self.textCtrl_MAC.GetValue()
	    # Check if the value entered by the user is a valid hexadecimal
	if self.IsValidHex(radioMac):
	    if (len(radioMac) == 6):
		self.radioAddr = binascii.unhexlify(radioMac)
		if self.com:
		    self.com.rpc(self.radioAddr, "callback", "SNAPpPadConfirm", "confirm_com")
		else:
		    self._log.info("Unable to connect to SNAP Bridge.")
	    else:
		self.showMessage("Error", "An invalid MAC address was entered, please try again.")
	else:
	    self.showMessage("Error", "An invalid MAC address was entered, please try again.")

    def SNAPpPadConfirm(self, ret):
	self._log.info("Recieved SNAPpPad Confirmation RPC.")
	self.txt_Confirm.SetLabel("Connected")
	self.txt_Confirm.SetForegroundColour(wx.GREEN)

    def connectErrorMsg(self):
	msg = "Please connect to SNAPpPad before attempting communications."
	self.showMessage("Connect to SNAPpPad...", msg)

    def IsValidHex(self, val):
        try:
            # Verify it is a valid Hexadecimal Value
            hexIntVal = int(val, 16)
            return True
        except:
            # Invalid Hexadecimal Value provided
            return False

### Click Handlers ###
    def clickLibrary(self, event):
        item = event.GetItem()
        item_label = self.library.GetItemText(item)
        if self.library.ItemHasChildren(item):
            self.buildActiveSuite(item_label)
        else:
            suite = self.library.GetItemParent(item)
            suite_label = self.library.GetItemText(suite)
            self.buildActiveCombo(self.comboDict[suite_label][item_label])
	    if self.buildMode == True:
		self.activeSuite.Append(item_label)
		self.activeSuiteDict[item_label] = self.comboDict[suite_label][item_label]

    def clickSuite(self, event):
        item = event.GetString()
        self._log.info("%s double clicked" % item)
        self.buildActiveCombo(self.activeSuiteDict[item])

### RangeTools Methods ###
    def setTestFrame(self, e=None):
	if self.rangeMode == False:
	    self._log.info("Selecting range frame...")
	    self.btn_SetTestFrame.SetLabel("Select Frame...")
	    self.rangeMode = True
	    msg = "Select the frame in the active combo to be used for range testing."
	    self.showMessage("Set Test Frame", msg)
	else:
	    self._log.info("Range Test Frame: %s" % self.rangeFrame)
	    self.rangeMode = False
	    self.btn_SetTestFrame.SetLabel("Set Test Frame")

    def startRangeTest(self, e):
	if self.runningMixups == False:
	    self.mixupDict.clear()
	    selectedMixups = self.activeSuite.GetCheckedStrings()
	    if not self.radioAddr:
		self.connectErrorMsg()
	    elif not selectedMixups:
		msg = "Please select mixups to train against."
		self.showMessage("No Mixups Selected...", msg)
	    else:
		self._log.info("Starting mixup mode")
		self.btn_StartMixupTraining.SetLabel("Stop Mixup Training")
		self.runningMixups = True

	    for mixup in selectedMixups:
		self.mixupDict[mixup] = self.activeSuiteDict[mixup]
		self._log.info(self.mixupDict)
		mixup = self.mixupDict[random.choice(self.mixupDict.keys())]
		self.comboToSNAPpPad(mixup)
	else:
	    self._log.info("Deactivating mixup mode.")
	    self.runningMixups = False
	    self.btn_StartMixupTraining.SetLabel("Start Mixup Training")

    def rangeFrameCheck(self, e):
	row = e.GetRow()
	if self.rangeMode == True:
	    self._log.info("Highlighting and setting row %s for range testing" % row)
	    self.activeCombo.SetCellBackgroundColour(row, 0, wx.RED)
	    if self.rangeFrame:
		self.activeCombo.SetCellBackgroundColour(self.rangeFrame, 0, None)
	    self.rangeFrame = row
	    self.setTestFrame()
	    self.activeCombo.Refresh()
	e.Skip()

### ActiveCombo Methods ###
    def buildActiveCombo(self, combo):
	self._log.info("Converting combo for table display...")
	self.clearCombo()
        self._log.info("Loading %s into active combo." % combo)
        parser = r'(?<=\/).*?(?=\/)'
        inputs = re.findall(parser,combo)
        inputs[:] = [x for x in inputs if x != ""]
        x = 0
        for i in inputs:
            self.activeCombo.SetCellValue(x,0,i)
            x += 1

### Run Mixup Tools ###
    def startMixupTraining(self, e=None):
	if self.runningMixups == False:
	    self.mixupDict.clear()
	    self.selectedMixups = self.activeSuite.GetCheckedStrings()
	    if not self.radioAddr:
		self.connectErrorMsg()
	    elif not self.selectedMixups:
		msg = "Please select mixups to train against."
		self.showMessage("No Mixups Selected...", msg)
	    else:
		self._log.info("Starting mixup mode")
		self.btn_StartMixupTraining.SetLabel("Stop Mixup Training")
		self.runningMixups = True

		for mixup in self.selectedMixups:
		    self.mixupDict[mixup] = self.activeSuiteDict[mixup]
		mixup = self.mixupDict[random.choice(self.mixupDict.keys())]
		self.comboToSNAPpPad(mixup)
	else:
	    self._log.info("Deactivating mixup mode.")
	    self.runningMixups = False
	    self.btn_StartMixupTraining.SetLabel("Start Mixup Training")

    def runNextMixup(self, ret):
	if ret == 0: #SNAPpPad returned after recieving combo
	    wx.CallLater(100, self.runCombo)
	elif ret == 1: #SNAPpPad returned after running combo
	    wx.CallLater(1250, self.reset)
	elif ret == 2: #SNAPpPad returned after resetting
	    currentSelection = self.activeSuite.GetCheckedStrings()
	    print currentSelection
	    print self.selectedMixups
	    if not currentSelection:
		msg = "Please select mixups to train against."
		self.showMessage("No Mixups Selected...", msg)
		self.startMixupTraining()
	    elif self.selectedMixups != currentSelection:
		self.selectedMixups = currentSelection
		self.mixupDict.clear()
		for mixup in self.selectedMixups:
		    self.mixupDict[mixup] = self.activeSuiteDict[mixup]
		mixup = self.mixupDict[random.choice(self.mixupDict.keys())]
		self._log.info("Selecting next mixup.")
		self.comboToSNAPpPad(mixup)
	    else:
		mixup = self.mixupDict[random.choice(self.mixupDict.keys())]
		self._log.info("Selecting next mixup.")
		self.comboToSNAPpPad(mixup)

### SuiteTools Methods ###
    def buildActiveSuite(self, suite):
	if self.buildMode != True:
	    self.clearSuite()
        self._log.info("Populating active suite with '%s'" % suite)
        self.suite = suite
        for combo in self.comboDict[suite]:
            self.activeSuite.Append(combo)
            self.activeSuiteDict[combo] = self.comboDict[suite][combo]

    def buildSuite(self, e):
	if self.buildMode == False:
	    self._log.info("Activating suite building mode.")
	    self.btn_BuildSuite.SetLabel("Stop Build")
	    self.buildMode = True
	    msg = "In Build Mode, combos selected from the library will be added directly to the suite."
	    self.showMessage("Suite Building", msg)
	else:
	    self._log.info("Deactivating suite building mode.")
	    self.buildMode = False
	    self.btn_BuildSuite.SetLabel("Build Suite")

    def clearSuite(self, event=None):
        self._log.info("Clearing active suite.")
        self.activeSuite.Clear()
        self.activeSuiteDict.clear()

    def saveSuiteAs(self, e):
        if not self.activeSuiteDict:
            pass
        else:
            dlg = wx.FileDialog(self.mainFrame, "Save suite as...", 'Library', "", "*.txt", \
                            wx.SAVE|wx.OVERWRITE_PROMPT)
            result = dlg.ShowModal()
            inFile = dlg.GetPath()
            dlg.Destroy()

            if result == wx.ID_OK:
		self._log.info("Suite saved as %s." % inFile)
                self.saveActiveSuite(inFile)
                self.buildLibrary()
                return True
            elif result == wx.ID_CANCEL:
		self._log.info("Suite not saved.")
                return False

    def saveActiveSuite(self, inFile):
	self._log.info("Writing suite to file.")
        activeSuiteOrder = self.activeSuite.GetStrings()
        with open(inFile, 'w+') as f:
            for combo in activeSuiteOrder:
                f.write("%s\n" % combo)
                f.write("%s\n" % self.activeSuiteDict[str(combo)])


### ComboTools Methods ###
    def sendActiveCombo(self, event):
	if not self.radioAddr:
	    self.connectErrorMsg()
        elif self.activeCombo.GetCellValue(0, 0) == "":
	    msg = "Please input a combo to send."
	    self.showMessage("No active combo...", msg)
	activeCombo = self.convertActiveComboToString()
	self._log.info("Converting & sending active combo to SNAPpPad for run.")
	self.comboToSNAPpPad(activeCombo)

    def comboToSNAPpPad(self, combo):
	comboTuple = Combo_Converter.breakdown_combo(combo)
	self.combo = Combo_Converter.build_hex_combo(comboTuple)
	self._log.info("Sending combo: %s" % repr(self.combo))
	self._log.info("Combo Length: %s" % len(self.combo))
	if len(self.combo) > 123:
	    msg = "Combo contains %s inputs, We're currently limited to 123. Shorten the combo and try again." % len(self.combo)
	    self.showMessage("Combo too long...", msg)
	if len(self.combo) > 64:
	    self.more = True
	    self.com.rpc(self.radioAddr, "callback", "SNAPpPadReturn", "comboToSNAPpPad", self.combo[:64], 0)
	    self._log.info("Combo Part 1: %s" % self.combo[0:64])
	else:
	    self.more = False
	    self.com.rpc(self.radioAddr, "callback", "SNAPpPadReturn", "comboToSNAPpPad", self.combo, 0)

    def sendNext(self):
	self.more = False
	self.com.rpc(self.radioAddr, "callback", "SNAPpPadReturn", "comboToSNAPpPad", self.combo[64:], 1)
	self._log.info("Combo Part 2: %s:" % self.combo[64:])

    def SNAPpPadReturn(self, ret):
	self._log.info("SNAPpPad is ready for comm.")
	if self.runningMixups:
	    self.runNextMixup(ret)
	elif self.rangeTesting:
	    self.runNextRangeTest(ret)
	elif self.more:
	    self.sendNext()

    def runCombo(self,e=None):
	if not self.radioAddr:
	    self.connectErrorMsg()
	else:
	    self._log.info("Sending run command to SNAPpPad.")
	    self.com.rpc(self.radioAddr, "callback", "SNAPpPadReturn", "run_combo")

    def clearCombo(self, event=None):
        self._log.info("Clearing active combo.")
        self.activeCombo.DeleteCols()
        self.activeCombo.AppendCols()
	self.rangeFrame = None

    def addToSuite(self, event=None):
        if self.activeCombo.GetCellValue(0, 0) == "":
            event.Skip()
        else:
            addToSuiteDialog = SNAPpPad_wx.addToSuiteDialog(self.mainFrame)
            result = addToSuiteDialog.ShowModal()
            addToSuiteDialog.Destroy()
            if result == wx.ID_OK:
                comboName = addToSuiteDialog.textCtrl_ComboName.GetValue()
                self.activeSuite.Append(comboName)
                combo = self.convertActiveComboToString()
                self.activeSuiteDict[comboName] = combo
                self._log.info("Added %s to active suite as '%s'." % (combo, comboName))

    def convertActiveComboToString(self):
        ActiveCombo = []
        for row in range(self.activeCombo.GetNumberRows()):
            cell = self.activeCombo.GetCellValue(row, 0)
            if cell != "":
                ActiveCombo.append(str(cell))
        StringCombo = ""
        for inputs in ActiveCombo:
            StringCombo = StringCombo + "/%s/" % inputs
        return StringCombo

    def reset(self, e=None):
	if not self.radioAddr:
	    self.connectErrorMsg()
	else:
	    position = self.resetPosition_rBox.GetSelection()
	    self._log.info("Reset training mode to %s." % position)
	    self.com.rpc(self.radioAddr, "callback", "SNAPpPadReturn", 'reset_training_mode', position)


###  Menu Handlers ###

    def toggleLibrary(self, event):
        self._log.info("Library Panel Toggled.")
        if self.library_Panel.IsShown():
            self.library_Panel.Hide()
        else:
            self.library_Panel.Show()
        self.GetTopLevelParent().Layout()

    def toggleConsole(self, event):
        self._log.info("Console Panel Toggled.")
        if self.history_Panel.IsShown():
            self.history_Panel.Hide()
        else:
            self.history_Panel.Show()
        self.GetTopLevelParent().Layout()



app = wx.App(False)
frame = SNAPpPad_GUI(None)
frame.Show(True)
frame.openSnapCom()
app.MainLoop()