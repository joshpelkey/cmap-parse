##
#
# gui.py
# An attempt to parse concept maps, exported from cmap tools...take one
#
# Copyright 2015 Josh Pelkey
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing permissions and limitations under the
# License.
#
##

import os
import wx
import cmap_parse

cmap_files = []
results = ''

class Example(wx.Frame):

    def __init__(self, parent, title):    
        super(Example, self).__init__(parent, title=title, 
            size=(750, 350))

        self.InitUI()
        self.Centre()
        self.Show()     

    def InitUI(self):
      
        panel = wx.Panel(self)
        
        sizer = wx.GridBagSizer(5, 5)

        text1 = wx.StaticText(panel, label="cmap-parse: parsing cmaps and stuff")
        sizer.Add(text1, pos=(0, 0), flag=wx.TOP|wx.LEFT|wx.BOTTOM, 
            border=10)

        #icon = wx.StaticBitmap(panel, bitmap=wx.Bitmap('info.png'))
        #sizer.Add(icon, pos=(0, 4), flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT, 
        #    border=5)

        line = wx.StaticLine(panel)
        sizer.Add(line, pos=(1, 0), span=(1, 5), 
            flag=wx.EXPAND|wx.BOTTOM, border=10)

        # Name the root node
        text2 = wx.StaticText(panel, label="Root Concept")
        sizer.Add(text2, pos=(2, 0), flag=wx.LEFT, border=10)

        self.tc1 = wx.TextCtrl(panel)
        sizer.Add(self.tc1, pos=(2, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND)
        self.tc1.ChangeValue("Sustainability")


        # Import the results choice
        text3 = wx.StaticText(panel, label="Select concept maps...")
        sizer.Add(text3, pos=(3, 0), flag=wx.LEFT|wx.TOP, border=10)

        self.tc2 = wx.TextCtrl(panel, style=wx.TE_READONLY)
        sizer.Add(self.tc2, pos=(3, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND, 
            border=5)

        button1 = wx.Button(panel, label="Browse...")
        sizer.Add(button1, pos=(3, 4), flag=wx.TOP|wx.RIGHT, border=5)
        self.Bind(wx.EVT_BUTTON, self.OnOpen, button1)


        # Export the results choice
        text4 = wx.StaticText(panel, label="Save results as...")
        sizer.Add(text4, pos=(4, 0), flag=wx.TOP|wx.LEFT, border=10)

        self.tc3 = wx.TextCtrl(panel, style=wx.TE_READONLY)
        sizer.Add(self.tc3, pos=(4, 1), span=(1, 3), 
            flag=wx.TOP|wx.EXPAND, border=5)

        button2 = wx.Button(panel, label="Browse...")
        sizer.Add(button2, pos=(4, 4), flag=wx.TOP|wx.RIGHT, border=5)
        self.Bind(wx.EVT_BUTTON, self.OnOpen2, button2)

        # Optional Attributes which do nothing
        sb = wx.StaticBox(panel, label="Optional Attributes")

        boxsizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
        boxsizer.Add(wx.CheckBox(panel, label=" Use The Force"), 
            flag=wx.LEFT|wx.TOP, border=5)
        boxsizer.Add(wx.CheckBox(panel, label=" Cast Hogwarts Spell"),
            flag=wx.LEFT, border=5)
        boxsizer.Add(wx.CheckBox(panel, label=" Enter the Matrix"), 
            flag=wx.LEFT|wx.BOTTOM, border=5)
        sizer.Add(boxsizer, pos=(5, 0), span=(1, 5), 
            flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

        # Halp!
        button3 = wx.Button(panel, label='Help')
        sizer.Add(button3, pos=(7, 0), flag=wx.LEFT, border=10)
        self.Bind(wx.EVT_BUTTON, self.OnHelp, button3)

        # Run the codes
        button4 = wx.Button(panel, label="Run")
        sizer.Add(button4, pos=(7, 3))
        self.Bind(wx.EVT_BUTTON, self.OnRun, button4)
        

        # Get me out of here
        button5 = wx.Button(panel, label="Exit")
        sizer.Add(button5, pos=(7, 4), span=(1, 1),  
            flag=wx.BOTTOM|wx.RIGHT, border=5)
        self.Bind(wx.EVT_BUTTON, self.OnExit, button5)

        sizer.AddGrowableCol(2)
        
        panel.SetSizer(sizer)


    # Open up all your files
    def OnOpen(self, evt):

        # Create the dialog. In this case the current directory is forced as the starting
        # directory for the dialog, and no default file name is forced. This can easilly
        # be changed in your program. This is an 'open' dialog, and allows multitple
        # file selections as well.
        #
        # Finally, if the directory is changed in the process of getting files, this
        # dialog is set up to change the current working directory to the path chosen.
        dlg = wx.FileDialog(
            self, message="Select concept maps",
            defaultDir=os.getcwd(), 
            defaultFile="",
            wildcard="Text files (*.txt)|*.txt",
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )

        
        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # set us up the file to pass in
            global cmap_files
            cmap_files = dlg.GetPaths()
            filenames = dlg.GetFilenames()

        if len(filenames) > 1:
            self.tc2.ChangeValue(filenames[0] + ' + ' + str(len(cmap_files)-1) + ' more files')
        else:
            self.tc2.ChangeValue(filenames[0])

        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()

    # Save it out
    def OnOpen2(self, evt):

        # Create the dialog. In this case the current directory is forced as the starting
        # directory for the dialog, and no default file name is forced. This can easilly
        # be changed in your program. This is an 'save' dialog.
        #
        # Finally, if the directory is changed in the process of getting files, this
        # dialog is set up to change the current working directory to the path chosen.
        dlg = wx.FileDialog(
            self, message="Save results as",
            defaultDir=os.getcwd(), 
            defaultFile="CmapResults.txt",
            style=wx.SAVE | wx.OVERWRITE_PROMPT
            )

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            global results
            results = dlg.GetPath()

        self.tc3.ChangeValue(results)

        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()


    # Run the program...finally
    def OnRun (self,e):
        if self.tc2.IsEmpty():
            dlg = wx.MessageDialog( self, "Please select your cmap files.", "Missing info", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()

        elif self.tc3.IsEmpty():
            dlg = wx.MessageDialog( self, "Please choose where to save results.", "Missing info", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            
        else:
            root_concept = self.tc1.GetValue ()
            cmap_parse.CmapParse (cmap_files, results, root_concept)
            dlg = wx.MessageDialog( self, "Your results are ready!", "Complete!", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()


    # Help text
    def OnHelp(self,e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, "cmap-parse.py\n\
An attempt to parse concept maps, exported from cmap tools...take one\n\
------------------------------------------------------------------------------------------\n\n\
Step 1: Set your root node name. This is the 'top' of your concept map. We will start at this node for many calculations.\n\n\
Step 2: Choose your cmap files. These must be txt files, exported 'Propositions as text...' from Cmap Tools.\n\n\
Step 3: Choose your export path and filename. Results will be exported as plain-text.\n\n\
Step 4: Click Run and go view your results!\n\n\
------------------------------------------------------------------------------------------\n\
Copyright 2015 Josh Pelkey\n\n\
Licensed under the Apache License, Version 2.0 (the \"License\"); you may not\n\
use this file except in compliance with the License. You may obtain a copy of\n\
the License at\n\n\
http://www.apache.org/licenses/LICENSE-2.0\n\n\
Unless required by applicable law or agreed to in writing, software distributed\n\
under the License is distributed on an \"AS IS\" BASIS, WITHOUT WARRANTIES OR\n\
CONDITIONS OF ANY KIND, either express or implied. See the License for the specific\n\
language governing permissions and limitations under the License."
                                ,
                              "cmap-parse help", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

    # Quit the program
    def OnExit(self,e):
	    self.Close(True)
	    


if __name__ == '__main__':
  
    app = wx.App()
    Example(None, title="cmap-parse")
    app.MainLoop()
