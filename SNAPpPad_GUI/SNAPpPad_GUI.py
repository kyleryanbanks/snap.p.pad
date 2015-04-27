import sys
import os
import itertools
import re

import wx
import wx.lib.newevent
import SNAPpPad_wx

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
        self.log = logging.getLogger("SNAPpPad")

        self.mainFrame = SNAPpPad_wx.mainFrame.__init__(self,parent)

        handler = WxTextCtrlHandler(self.Console)
        self.log.addHandler(handler)
        FORMAT = "%(asctime)s %(levelname)s %(message)s"
        handler.setFormatter(logging.Formatter(FORMAT))
        self.log.setLevel(logging.DEBUG)

        self.libFiles = os.listdir("Library")
        self.comboDict = {}
        self.buildLibrary()

        self.suite = None
        self.activeSuiteDict = {}
        self.combo = None


    def buildLibrary(self):
        for suite in self.libFiles:
            self.comboDict[suite] = {}
            with open("Library/" + suite) as f:
                for commentLine, comboLine in itertools.izip_longest(f, f, fillvalue=''):
                    commentLine = commentLine.rstrip('\n')
                    comboLine = comboLine.rstrip('\n')
                    self.comboDict[suite][commentLine] = comboLine

        self.root = self.library.AddRoot('Library')
        for suite in self.comboDict:
            header = self.library.AppendItem(self.root, suite)
            for combo in self.comboDict[suite]:
                self.library.AppendItem(header, combo)

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

    def clickSuite(self, event):
        item = event.GetString()
        self.log.info("%s double clicked" % item)
        self.buildActiveCombo(self.activeSuiteDict[item])

### ActiveCombo Methods ###
    def buildActiveCombo(self, combo):
        self.clearCombo()
        self.log.info("Loading %s into active combo." % combo)
        parser = r'(?<=\/).*?(?=\/)'
        inputs = re.findall(parser,combo)
        inputs[:] = [x for x in inputs if x != ""]
        x = 0
        for i in inputs:
            self.activeCombo.SetCellValue(x,0, i)
            x += 1

### SuiteTools Methods ###
    def buildActiveSuite(self, suite):
        self.clearSuite()
        self.log.info("Populating active suite with '%s'" % suite)
        self.suite = suite
        for combo in self.comboDict[suite]:
            self.activeSuite.Append(combo)
            self.activeSuiteDict[combo] = self.comboDict[suite][combo]

    def buildSuite(self):
        pass

    def clearSuite(self, event=None):
        self.log.info("Clearing active suite.")
        self.activeSuite.Clear()
        self.activeSuiteDict.clear()


    def saveSuiteAs(self):
        pass

### ComboTools Methods ###

    def runCombo(self, event):
        pass

    def clearCombo(self, event=None):
        self.log.info("Clearing active combo.")
        self.activeCombo.DeleteCols()
        self.activeCombo.AppendCols()

    def addToSuite(self, event):
        addToSuiteDialog = SNAPpPad_wx.addToSuiteDialog(self.mainFrame)
        result = addToSuiteDialog.ShowModal()
        addToSuiteDialog.Destroy()
        if result == wx.ID_OK:
            comboName = addToSuiteDialog.textCtrl_ComboName.GetValue()
            self.activeSuite.Append(comboName)
            combo = self.convertActiveComboToString()
            self.activeSuiteDict[comboName] = combo
            self.log.info("Added %s to active suite as '%s'." % (combo, comboName))

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




###  Menu Handlers ###

    def toggleLibrary(self, event):
        self.log.info("Library Panel Toggled.")
        if self.library_Panel.IsShown():
            self.library_Panel.Hide()
        else:
            self.library_Panel.Show()
        self.GetTopLevelParent().Layout()

    def toggleConsole(self, event):
        self.log.info("Console Panel Toggled.")
        if self.history_Panel.IsShown():
            self.history_Panel.Hide()
        else:
            self.history_Panel.Show()
        self.GetTopLevelParent().Layout()



app = wx.App(False)
frame = SNAPpPad_GUI(None)
frame.Show(True)
app.MainLoop()