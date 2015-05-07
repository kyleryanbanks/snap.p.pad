# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun  5 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.grid

wx.ID_LIBRARY = 1000

###########################################################################
## Class mainFrame
###########################################################################

class mainFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"SNAPpPad", pos = wx.DefaultPosition, size = wx.Size( 828,550 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.Size( 828,550 ), wx.DefaultSize )
		self.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, False, "Open Sans" ) )
		self.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DLIGHT ) )
		
		self.menuBar = wx.MenuBar( 0 )
		self.menuBar.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )
		self.menuBar.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )
		
		self.file = wx.Menu()
		self.file_NewSuite = wx.MenuItem( self.file, wx.ID_ANY, u"New Suite", wx.EmptyString, wx.ITEM_NORMAL )
		self.file.AppendItem( self.file_NewSuite )
		
		self.file_OpenSuite = wx.MenuItem( self.file, wx.ID_ANY, u"Open Suite...", wx.EmptyString, wx.ITEM_NORMAL )
		self.file.AppendItem( self.file_OpenSuite )
		
		self.file.AppendSeparator()
		
		self.file_SaveSuite = wx.MenuItem( self.file, wx.ID_ANY, u"Save Suite", wx.EmptyString, wx.ITEM_NORMAL )
		self.file.AppendItem( self.file_SaveSuite )
		
		self.file_SaveSuiteAs = wx.MenuItem( self.file, wx.ID_ANY, u"Save Suite  As...", wx.EmptyString, wx.ITEM_NORMAL )
		self.file.AppendItem( self.file_SaveSuiteAs )
		
		self.file.AppendSeparator()
		
		self.m_file_exit = wx.MenuItem( self.file, wx.ID_EXIT, u"Exit", u"Close SNAPpPad", wx.ITEM_NORMAL )
		self.file.AppendItem( self.m_file_exit )
		
		self.menuBar.Append( self.file, u"File" ) 
		
		self.edit = wx.Menu()
		self.m_edit_cut = wx.MenuItem( self.edit, wx.ID_CUT, u"Cut", u"Cut Selected Text", wx.ITEM_NORMAL )
		self.edit.AppendItem( self.m_edit_cut )
		
		self.m_edit_copy = wx.MenuItem( self.edit, wx.ID_ANY, u"Copy", u"Copy selected text", wx.ITEM_NORMAL )
		self.edit.AppendItem( self.m_edit_copy )
		
		self.edit.AppendSeparator()
		
		self.m_edit_paste = wx.MenuItem( self.edit, wx.ID_PASTE, u"Paste", u"Paste text from clipboard", wx.ITEM_NORMAL )
		self.edit.AppendItem( self.m_edit_paste )
		
		self.menuBar.Append( self.edit, u"Edit" ) 
		
		self.view = wx.Menu()
		self.view_ShowConsole = wx.MenuItem( self.view, wx.ID_ANY, u"Show/Hide Console", wx.EmptyString, wx.ITEM_NORMAL )
		self.view.AppendItem( self.view_ShowConsole )
		
		self.view_ShowLibrary = wx.MenuItem( self.view, wx.ID_ANY, u"Show/Hide Library", wx.EmptyString, wx.ITEM_NORMAL )
		self.view.AppendItem( self.view_ShowLibrary )
		
		self.view_ShowManual = wx.MenuItem( self.view, wx.ID_ANY, u"Show Manual Ctrl", wx.EmptyString, wx.ITEM_NORMAL )
		self.view.AppendItem( self.view_ShowManual )
		
		self.menuBar.Append( self.view, u"View" ) 
		
		self.help = wx.Menu()
		self.help_About = wx.MenuItem( self.help, wx.ID_ANY, u"About", wx.EmptyString, wx.ITEM_NORMAL )
		self.help.AppendItem( self.help_About )
		
		self.menuBar.Append( self.help, u"Help" ) 
		
		self.SetMenuBar( self.menuBar )
		
		mainFrame_Sizer = wx.BoxSizer( wx.VERTICAL )
		
		workspace_Sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.library_Panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer14 = wx.BoxSizer( wx.VERTICAL )
		
		library_sbSizer = wx.StaticBoxSizer( wx.StaticBox( self.library_Panel, wx.ID_ANY, u"Library" ), wx.VERTICAL )
		
		self.library = wx.TreeCtrl( self.library_Panel, wx.ID_LIBRARY, wx.DefaultPosition, wx.Size( 200,-1 ), wx.TR_EDIT_LABELS|wx.TR_FULL_ROW_HIGHLIGHT|wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT|wx.TR_LINES_AT_ROOT|wx.TR_NO_LINES|wx.TR_TWIST_BUTTONS )
		self.library.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, False, "Open Sans" ) )
		
		library_sbSizer.Add( self.library, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 0 )
		
		
		bSizer14.Add( library_sbSizer, 1, wx.EXPAND, 5 )
		
		SNAPpPad_sbSizer = wx.StaticBoxSizer( wx.StaticBox( self.library_Panel, wx.ID_ANY, u"SNAPpPad Info" ), wx.VERTICAL )
		
		bSizer15 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText5 = wx.StaticText( self.library_Panel, wx.ID_ANY, u"MAC Address", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText5.Wrap( -1 )
		bSizer15.Add( self.m_staticText5, 0, wx.ALIGN_CENTER_VERTICAL|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		self.textCtrl_MAC = wx.TextCtrl( self.library_Panel, wx.ID_ANY, u"5f6f94", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textCtrl_MAC.SetMaxLength( 6 ) 
		bSizer15.Add( self.textCtrl_MAC, 1, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		
		SNAPpPad_sbSizer.Add( bSizer15, 1, wx.EXPAND, 5 )
		
		bSizer16 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.btn_TestConnection = wx.Button( self.library_Panel, wx.ID_ANY, u"Test Connection", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer16.Add( self.btn_TestConnection, 0, wx.ALL|wx.EXPAND, 0 )
		
		self.txt_Confirm = wx.StaticText( self.library_Panel, wx.ID_ANY, u"Not Connected", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.txt_Confirm.Wrap( -1 )
		self.txt_Confirm.SetForegroundColour( wx.Colour( 255, 0, 0 ) )
		
		bSizer16.Add( self.txt_Confirm, 1, wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT, 5 )
		
		
		SNAPpPad_sbSizer.Add( bSizer16, 1, wx.EXPAND, 5 )
		
		
		bSizer14.Add( SNAPpPad_sbSizer, 0, wx.EXPAND, 5 )
		
		
		self.library_Panel.SetSizer( bSizer14 )
		self.library_Panel.Layout()
		bSizer14.Fit( self.library_Panel )
		workspace_Sizer.Add( self.library_Panel, 1, wx.EXPAND |wx.ALL, 5 )
		
		central_Sizer = wx.BoxSizer( wx.VERTICAL )
		
		tools_Sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		rangeTools_sbSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Range Tools" ), wx.VERTICAL )
		
		setTestFrame_Sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.btn_SetTestFrame = wx.Button( self, wx.ID_ANY, u"Set Test Frame", wx.DefaultPosition, wx.DefaultSize, 0 )
		setTestFrame_Sizer.Add( self.btn_SetTestFrame, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT|wx.LEFT, 2 )
		
		
		rangeTools_sbSizer.Add( setTestFrame_Sizer, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )
		
		rangeFrames_gSizer = wx.GridSizer( 2, 3, 0, 0 )
		
		self.txt_Start = wx.StaticText( self, wx.ID_ANY, u"Start", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.txt_Start.Wrap( -1 )
		rangeFrames_gSizer.Add( self.txt_Start, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.txt_End = wx.StaticText( self, wx.ID_ANY, u"End", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.txt_End.Wrap( -1 )
		rangeFrames_gSizer.Add( self.txt_End, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.txt_Runs = wx.StaticText( self, wx.ID_ANY, u"Runs", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.txt_Runs.Wrap( -1 )
		rangeFrames_gSizer.Add( self.txt_Runs, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.textCtrl_Start = wx.TextCtrl( self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_TAB )
		self.textCtrl_Start.SetMaxLength( 3 ) 
		self.textCtrl_Start.SetMaxSize( wx.Size( 50,-1 ) )
		
		rangeFrames_gSizer.Add( self.textCtrl_Start, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.textCtrl_End = wx.TextCtrl( self, wx.ID_ANY, u"10", wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_TAB )
		self.textCtrl_End.SetMaxSize( wx.Size( 50,-1 ) )
		
		rangeFrames_gSizer.Add( self.textCtrl_End, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.textCtrl_Runs = wx.TextCtrl( self, wx.ID_ANY, u"5", wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_TAB )
		self.textCtrl_Runs.SetMaxSize( wx.Size( 50,-1 ) )
		
		rangeFrames_gSizer.Add( self.textCtrl_Runs, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		rangeTools_sbSizer.Add( rangeFrames_gSizer, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 2 )
		
		startRangeTest_Sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.btn_StartRangeTesting = wx.Button( self, wx.ID_ANY, u"Start Range Test", wx.DefaultPosition, wx.DefaultSize, 0 )
		startRangeTest_Sizer.Add( self.btn_StartRangeTesting, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_BOTTOM|wx.RIGHT|wx.LEFT, 2 )
		
		
		rangeTools_sbSizer.Add( startRangeTest_Sizer, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )
		
		
		tools_Sizer.Add( rangeTools_sbSizer, 1, wx.EXPAND, 5 )
		
		resetTools_sbSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Reset Tools" ), wx.VERTICAL )
		
		self.btn_Reset = wx.Button( self, wx.ID_ANY, u"Reset", wx.DefaultPosition, wx.DefaultSize, 0 )
		resetTools_sbSizer.Add( self.btn_Reset, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT|wx.LEFT|wx.EXPAND, 2 )
		
		resetPosition_rBoxChoices = [ u"Cornered", u"Midscreen", u"Corner" ]
		self.resetPosition_rBox = wx.RadioBox( self, wx.ID_ANY, u"Position", wx.DefaultPosition, wx.DefaultSize, resetPosition_rBoxChoices, 1, wx.RA_SPECIFY_COLS )
		self.resetPosition_rBox.SetSelection( 0 )
		resetTools_sbSizer.Add( self.resetPosition_rBox, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND|wx.RIGHT|wx.LEFT, 2 )
		
		
		tools_Sizer.Add( resetTools_sbSizer, 0, wx.ALIGN_CENTER_VERTICAL, 5 )
		
		comboTools_sbSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Combo Tools" ), wx.VERTICAL )
		
		bSizer17 = wx.BoxSizer( wx.VERTICAL )
		
		self.btn_SendCombo = wx.Button( self, wx.ID_ANY, u"Send Combo", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer17.Add( self.btn_SendCombo, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.RIGHT|wx.LEFT, 2 )
		
		
		comboTools_sbSizer.Add( bSizer17, 1, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 0 )
		
		bSizer34 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.btn_RunCombo = wx.Button( self, wx.ID_ANY, u"Run Combo", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer34.Add( self.btn_RunCombo, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT|wx.LEFT, 2 )
		
		
		comboTools_sbSizer.Add( bSizer34, 1, wx.EXPAND, 0 )
		
		bSizer35 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.btn_ClearComboInput = wx.Button( self, wx.ID_ANY, u"Clear Combo", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer35.Add( self.btn_ClearComboInput, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2 )
		
		
		comboTools_sbSizer.Add( bSizer35, 1, wx.EXPAND, 0 )
		
		bSizer36 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.btn_AddComboToSuite = wx.Button( self, wx.ID_ANY, u"Add To Suite", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer36.Add( self.btn_AddComboToSuite, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_BOTTOM|wx.RIGHT|wx.LEFT, 2 )
		
		
		comboTools_sbSizer.Add( bSizer36, 1, wx.EXPAND, 0 )
		
		
		tools_Sizer.Add( comboTools_sbSizer, 1, wx.EXPAND, 5 )
		
		
		central_Sizer.Add( tools_Sizer, 0, wx.EXPAND, 5 )
		
		suiteTools_sbSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Suite Tools" ), wx.VERTICAL )
		
		mixupsBtn_Sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.btn_BuildSuite = wx.Button( self, wx.ID_ANY, u"Build Suite", wx.DefaultPosition, wx.DefaultSize, 0 )
		mixupsBtn_Sizer.Add( self.btn_BuildSuite, 1, wx.RIGHT|wx.LEFT, 2 )
		
		self.btn_clearSuite = wx.Button( self, wx.ID_ANY, u"Clear Suite", wx.DefaultPosition, wx.DefaultSize, 0 )
		mixupsBtn_Sizer.Add( self.btn_clearSuite, 1, wx.RIGHT|wx.LEFT, 2 )
		
		self.btn_SaveSuiteAs = wx.Button( self, wx.ID_ANY, u"Save Suite As...", wx.DefaultPosition, wx.DefaultSize, 0 )
		mixupsBtn_Sizer.Add( self.btn_SaveSuiteAs, 1, wx.RIGHT|wx.LEFT, 2 )
		
		
		suiteTools_sbSizer.Add( mixupsBtn_Sizer, 0, wx.EXPAND, 5 )
		
		mixupWindow_Sizer = wx.BoxSizer( wx.VERTICAL )
		
		activeSuiteChoices = []
		self.activeSuite = wx.CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, activeSuiteChoices, 0 )
		self.activeSuite.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, False, "Open Sans" ) )
		
		mixupWindow_Sizer.Add( self.activeSuite, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND|wx.RIGHT|wx.LEFT, 2 )
		
		self.btn_StartMixupTraining = wx.Button( self, wx.ID_ANY, u"Start Mixup Training", wx.DefaultPosition, wx.DefaultSize, 0 )
		mixupWindow_Sizer.Add( self.btn_StartMixupTraining, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND|wx.RIGHT|wx.LEFT, 2 )
		
		
		suiteTools_sbSizer.Add( mixupWindow_Sizer, 1, wx.EXPAND, 5 )
		
		
		central_Sizer.Add( suiteTools_sbSizer, 1, wx.EXPAND, 5 )
		
		
		workspace_Sizer.Add( central_Sizer, 1, wx.EXPAND, 5 )
		
		activeCombo_sbSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Active Combo" ), wx.HORIZONTAL )
		
		self.activeCombo = wx.grid.Grid( self, wx.ID_ANY, wx.Point( -1,-1 ), wx.Size( -1,-1 ), 0 )
		
		# Grid
		self.activeCombo.CreateGrid( 123, 1 )
		self.activeCombo.EnableEditing( True )
		self.activeCombo.EnableGridLines( True )
		self.activeCombo.SetGridLineColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )
		self.activeCombo.EnableDragGridSize( False )
		self.activeCombo.SetMargins( 0, 0 )
		
		# Columns
		self.activeCombo.EnableDragColMove( False )
		self.activeCombo.EnableDragColSize( True )
		self.activeCombo.SetColLabelSize( 0 )
		self.activeCombo.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Rows
		self.activeCombo.AutoSizeRows()
		self.activeCombo.EnableDragRowSize( False )
		self.activeCombo.SetRowLabelSize( 0 )
		self.activeCombo.SetRowLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Label Appearance
		
		# Cell Defaults
		self.activeCombo.SetDefaultCellBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		self.activeCombo.SetDefaultCellFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, False, "Open Sans" ) )
		self.activeCombo.SetDefaultCellAlignment( wx.ALIGN_CENTRE, wx.ALIGN_TOP )
		activeCombo_sbSizer.Add( self.activeCombo, 1, wx.ALL|wx.EXPAND, 0 )
		
		
		workspace_Sizer.Add( activeCombo_sbSizer, 1, wx.EXPAND, 5 )
		
		
		mainFrame_Sizer.Add( workspace_Sizer, 1, wx.EXPAND, 5 )
		
		self.history_Panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TAB_TRAVERSAL )
		self.history_Panel.Hide()
		
		console_sbSizer = wx.StaticBoxSizer( wx.StaticBox( self.history_Panel, wx.ID_ANY, u"History" ), wx.VERTICAL )
		
		self.Console = wx.TextCtrl( self.history_Panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,150 ), wx.HSCROLL|wx.TE_MULTILINE|wx.TE_READONLY )
		console_sbSizer.Add( self.Console, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		
		self.history_Panel.SetSizer( console_sbSizer )
		self.history_Panel.Layout()
		console_sbSizer.Fit( self.history_Panel )
		mainFrame_Sizer.Add( self.history_Panel, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.SetSizer( mainFrame_Sizer )
		self.Layout()
		self.statusBar = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_IDLE, self.OnIdle )
		self.Bind( wx.EVT_MENU, self.OnExit, id = self.m_file_exit.GetId() )
		self.Bind( wx.EVT_MENU, self.toggleConsole, id = self.view_ShowConsole.GetId() )
		self.Bind( wx.EVT_MENU, self.toggleLibrary, id = self.view_ShowLibrary.GetId() )
		self.Bind( wx.EVT_MENU, self.showManualCtrl, id = self.view_ShowManual.GetId() )
		self.library.Bind( wx.EVT_TREE_ITEM_ACTIVATED, self.clickLibrary )
		self.btn_TestConnection.Bind( wx.EVT_BUTTON, self.testConnection )
		self.btn_SetTestFrame.Bind( wx.EVT_BUTTON, self.setTestFrame )
		self.btn_StartRangeTesting.Bind( wx.EVT_BUTTON, self.startRangeTest )
		self.btn_Reset.Bind( wx.EVT_BUTTON, self.reset )
		self.btn_SendCombo.Bind( wx.EVT_BUTTON, self.sendActiveCombo )
		self.btn_RunCombo.Bind( wx.EVT_BUTTON, self.runCombo )
		self.btn_ClearComboInput.Bind( wx.EVT_BUTTON, self.clearCombo )
		self.btn_AddComboToSuite.Bind( wx.EVT_BUTTON, self.addToSuite )
		self.btn_BuildSuite.Bind( wx.EVT_BUTTON, self.buildSuite )
		self.btn_clearSuite.Bind( wx.EVT_BUTTON, self.clearSuite )
		self.btn_SaveSuiteAs.Bind( wx.EVT_BUTTON, self.saveSuiteAs )
		self.activeSuite.Bind( wx.EVT_LISTBOX_DCLICK, self.clickSuite )
		self.btn_StartMixupTraining.Bind( wx.EVT_BUTTON, self.startMixupTraining )
		self.activeCombo.Bind( wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.rangeFrameCheck )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnIdle( self, event ):
		event.Skip()
	
	def OnExit( self, event ):
		event.Skip()
	
	def toggleConsole( self, event ):
		event.Skip()
	
	def toggleLibrary( self, event ):
		event.Skip()
	
	def showManualCtrl( self, event ):
		event.Skip()
	
	def clickLibrary( self, event ):
		event.Skip()
	
	def testConnection( self, event ):
		event.Skip()
	
	def setTestFrame( self, event ):
		event.Skip()
	
	def startRangeTest( self, event ):
		event.Skip()
	
	def reset( self, event ):
		event.Skip()
	
	def sendActiveCombo( self, event ):
		event.Skip()
	
	def runCombo( self, event ):
		event.Skip()
	
	def clearCombo( self, event ):
		event.Skip()
	
	def addToSuite( self, event ):
		event.Skip()
	
	def buildSuite( self, event ):
		event.Skip()
	
	def clearSuite( self, event ):
		event.Skip()
	
	def saveSuiteAs( self, event ):
		event.Skip()
	
	def clickSuite( self, event ):
		event.Skip()
	
	def startMixupTraining( self, event ):
		event.Skip()
	
	def rangeFrameCheck( self, event ):
		event.Skip()
	

###########################################################################
## Class addToSuiteDialog
###########################################################################

class addToSuiteDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Add To Suite", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer12 = wx.BoxSizer( wx.VERTICAL )
		
		self.txt_nameCombo = wx.StaticText( self, wx.ID_ANY, u"Enter combo name...", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.txt_nameCombo.Wrap( -1 )
		bSizer12.Add( self.txt_nameCombo, 0, wx.ALL, 5 )
		
		self.textCtrl_ComboName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer12.Add( self.textCtrl_ComboName, 0, wx.ALL|wx.EXPAND, 5 )
		
		bSizer14 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.btn_Cancel = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.btn_Cancel, 0, wx.ALL, 5 )
		
		self.btn_ok = wx.Button( self, wx.ID_OK, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.btn_ok, 0, wx.ALL, 5 )
		
		
		bSizer12.Add( bSizer14, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer12 )
		self.Layout()
		bSizer12.Fit( self )
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class Manual_Input
###########################################################################

class Manual_Input ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Manual Input", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer19 = wx.BoxSizer( wx.HORIZONTAL )
		
		gSizer4 = wx.GridSizer( 3, 3, 0, 0 )
		
		
		gSizer4.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.btn_Up = wx.Button( self, wx.ID_ANY, u"Up", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer4.Add( self.btn_Up, 0, wx.ALL, 0 )
		
		
		gSizer4.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.btn_Left = wx.Button( self, wx.ID_ANY, u"Left", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer4.Add( self.btn_Left, 0, wx.ALL, 0 )
		
		
		gSizer4.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.btn_Right = wx.Button( self, wx.ID_ANY, u"Right", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer4.Add( self.btn_Right, 0, wx.ALL, 0 )
		
		
		gSizer4.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.btn_Down = wx.Button( self, wx.ID_ANY, u"Down", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer4.Add( self.btn_Down, 0, wx.ALL, 0 )
		
		
		gSizer4.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		bSizer19.Add( gSizer4, 1, wx.EXPAND, 5 )
		
		gSizer5 = wx.GridSizer( 2, 3, 0, 0 )
		
		self.bnt_P1 = wx.Button( self, wx.ID_ANY, u"P1", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer5.Add( self.bnt_P1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0 )
		
		self.btn_P2 = wx.Button( self, wx.ID_ANY, u"P2", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer5.Add( self.btn_P2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0 )
		
		self.btn_P3 = wx.Button( self, wx.ID_ANY, u"P3", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer5.Add( self.btn_P3, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0 )
		
		self.btn_K1 = wx.Button( self, wx.ID_ANY, u"K1", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer5.Add( self.btn_K1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0 )
		
		self.btn_K2 = wx.Button( self, wx.ID_ANY, u"K2", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer5.Add( self.btn_K2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0 )
		
		self.btn_K3 = wx.Button( self, wx.ID_ANY, u"K3", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer5.Add( self.btn_K3, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0 )
		
		
		bSizer19.Add( gSizer5, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer19 )
		self.Layout()
		bSizer19.Fit( self )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.btn_Up.Bind( wx.EVT_BUTTON, self.up )
		self.btn_Up.Bind( wx.EVT_LEFT_DOWN, self.up )
		self.btn_Up.Bind( wx.EVT_LEFT_UP, self.release )
		self.btn_Left.Bind( wx.EVT_BUTTON, self.left )
		self.btn_Left.Bind( wx.EVT_LEFT_DOWN, self.left )
		self.btn_Right.Bind( wx.EVT_BUTTON, self.right )
		self.btn_Down.Bind( wx.EVT_BUTTON, self.down )
		self.bnt_P1.Bind( wx.EVT_BUTTON, self.p1 )
		self.btn_P2.Bind( wx.EVT_BUTTON, self.p2 )
		self.btn_P3.Bind( wx.EVT_BUTTON, self.p3 )
		self.btn_K1.Bind( wx.EVT_BUTTON, self.k1 )
		self.btn_K2.Bind( wx.EVT_BUTTON, self.k2 )
		self.btn_K3.Bind( wx.EVT_BUTTON, self.k3 )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def up( self, event ):
		event.Skip()
	
	
	def release( self, event ):
		event.Skip()
	
	def left( self, event ):
		event.Skip()
	
	
	def right( self, event ):
		event.Skip()
	
	def down( self, event ):
		event.Skip()
	
	def p1( self, event ):
		event.Skip()
	
	def p2( self, event ):
		event.Skip()
	
	def p3( self, event ):
		event.Skip()
	
	def k1( self, event ):
		event.Skip()
	
	def k2( self, event ):
		event.Skip()
	
	def k3( self, event ):
		event.Skip()
	

