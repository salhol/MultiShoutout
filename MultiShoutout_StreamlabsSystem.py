# -*- coding: utf-8 -*-
## ---------------------------------------
##  Import Libraries
## ---------------------------------------
import os
import codecs
import json
import sys
import ctypes
import clr

# CLR References
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

## ---------------------------------------
##  [Required] Script Information
## ---------------------------------------
ScriptName = "MultiShoutout"
Website = "https://github.com/salhol/MultiShoutout"
Description = "Give a shoutout to multiple people at once!"
Creator = "Sally Holm"
Version = "1.0.0.1"

## ---------------------------------------
##  [Required] Settings Class
## ---------------------------------------
class MySettings(object):
    """
    This class can use a json object to read and save existing settings set through the UI. If no object exist, it will create a new json file with default values.
    """
    def __init__(self, SettingsFile=None):
        """
        Tries to load setting if they are already set from settings file. If file is missing, the values set in the else block will be used. 
        """
        try:
            if SettingsFile and os.path.isfile(SettingsFile):
                with codecs.open(SettingsFile, encoding="utf-8-sig", mode="r") as f:
                    self.__dict__ = json.load(f, encoding="utf-8")
            else:
                ## Default values for settings. These must match set in the UI settings file.
                self.Enabled = True
                self.OnlyLive = False
                self.Command = "!so"
                self.Permission = "Moderator"
                self.PermissionInfo = ""
                self.Cost = 0
                self.Cooldown = 0
                self.Service = "Twitch"
                self.Usage = "Stream Chat"
                self.TextMessage = "/me go give these guys a follow <3 "
                self.Emotes = "bleedPurple bleedPurple bleedPurple"
                self.Seperator = True
                self.SeperatorStyle = "ThinSep1"
                self.EndSeperator = True
                #self.Extended = False
                #self.Thick = False
                self.EndMessage = "Send them some love! <3"
                self.Tags = True
        except:
            Parent.Log(ScriptName, "Failed to initiate settings")
        
    def Reload(self, jsondata):
        self.__dict__ = json.loads(jsondata, encoding="utf-8")
        return
    
    def Save(self, settingsfile):
        """
        Tries to save settings changed into json dict format.
        """
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f, encoding="utf-8")
            with codecs.open(settingsfile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8')))
        except:
            Parent.Log(ScriptName, "Failed to save settings to file.")
        return

## ---------------------------------------
##  Define Global Variables
## ---------------------------------------
global SettingsFile
SettingsFile = ""
global ScriptSettings
ScriptSettings = MySettings()

## ---------------------------------------
##  [Required] Initialize Data (Only called on load)
## ---------------------------------------
def Init():
    """
    Try to load in settings for script.
    """
    try:
        global ScriptSettings
        SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
        ScriptSettings = MySettings(SettingsFile)
        return

    except:
        Parent.Log(ScriptName, "Failed to initiate script on load.")

## ---------------------------------------
##  [Optional] Script Specific Functions
## ---------------------------------------
def SendChat(data, soText):
    """
    Send message to stream as either message or whisper. 
    """
    try:
        if data.IsFromTwitch():
            if not data.IsWhisper():
                Parent.SendStreamMessage(soText)
            else:
                Parent.SendStreamWhisper(data.User, soText)
    except:
        Parent.Log(ScriptName, "Failed to send message to chat.")
    

def ShoutOut(data):
    """
    Try to generate a long string with the information needed for the shoutout, including seperators. 
    After generating a sting, calls function to send message to chat.
    """
    try:
        # These are the different seperators. Each should be the same length as the default Twitch chat width in a browser on PC. This is not true in phone. 
        ThinSep1 = "────────────────────────────────"
        ThinSep2 = "════════════ ⋆★⋆ ════════════════"
        ThinSep3 = "───────────※ ·❆· ※─────────────"
        ThickSep1 = "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░"
        ThickSep2 = "▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌"
        ThickSep3 = "█▒▒▒▒▒▒▒▒▒▒█   ◈   █▒▒▒▒▒▒▒▒▒▒▒█"
        
        MySeperator = ScriptSettings.SeperatorStyle
        MySeperator = MySeperator.replace("ThinSep1", ThinSep1)
        MySeperator = MySeperator.replace("ThinSep2", ThinSep2)
        MySeperator = MySeperator.replace("ThinSep3", ThinSep3)
        MySeperator = MySeperator.replace("ThickSep1", ThickSep1)
        MySeperator = MySeperator.replace("ThickSep2", ThickSep2)
        MySeperator = MySeperator.replace("ThickSep3", ThickSep3)
        
        if ScriptSettings.Seperator:
            MyStart = ScriptSettings.TextMessage + MySeperator
        else:
            MyStart = ScriptSettings.TextMessage
        if ScriptSettings.EndSeperator:
            MyEnd = MySeperator + ScriptSettings.EndMessage
        else:
            MyEnd = ScriptSettings.EndMessage
        if ScriptSettings.Tags:
            Tag = "@"
        else:
            Tag = ""
    
        soText = MyStart
        Emotes = " " + ScriptSettings.Emotes + " "

        for i in range(1, data.GetParamCount()):
            namn = data.GetParam(i).lower()
            namn = namn.replace("@", "")
            namn = namn.replace(",", "")
            soText += Emotes + Tag + Parent.GetDisplayName(namn) + " over at: https://twitch.tv/" + namn + " "
            if data.GetParamCount() == 2:
                break
        soText += MyEnd
        return soText
        
    except:
        Parent.Log(ScriptName, "Falied to run ShoutOut function")

## ---------------------------------------
##  [Required] Execute Data / Process messages
## ---------------------------------------
def Execute(data):
    """
    Try to process messages and send response to chat.
    """
    if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.Command:
        if not Parent.HasPermission(data.User, ScriptSettings.Permission, ScriptSettings.PermissionInfo):
            return
        SendChat(data, ShoutOut(data))
    return

## ---------------------------------------
##  [Required] Tick method (Gets called during every iteration even when there is no incoming data)
## ---------------------------------------
def Tick():
    return

## ---------------------------------------
##  [Optional] Parse method (Allows you to create your own custom $parameters) 
## ---------------------------------------
def Parse(parseString, userid, username, targetid, targetname, message):
    
    if "$myparameter" in parseString:
        return parseString.replace("$myparameter","I am a cat!")
    
    return parseString

## ---------------------------------------
##  [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
## ---------------------------------------
def Unload():
    return

## ---------------------------------------
##  [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
## ---------------------------------------
def ScriptToggled(state):
    return

## ---------------------------------------
##  [Optional] Settings Functions
## ---------------------------------------
def ReloadSettings(jsonData):
    """
    Reloads and saves the settings when clicking the Save Settings button through the Chabot UI.
    """
    # Execute json reloading here
    ScriptSettings.__dict__ = json.loads(jsonData)
    ScriptSettings.Save(SettingsFile)
    return

def SetDefault():
    """
    Give the option in the UI to restore settings to default.
    """
    Messagebox = ctypes.windll.user32.MessageBoxA
    MB_OK = 0x0
    MB_YESNO = 0x04
    MB_YESNOCXL = 0x03
    ICON_EXLAIM = 0x30
    ICON_INFO = 0x40
    ICON_STOP = 0x10

    DefaultReturn = Messagebox(0, "Restore to default settings?", "Default Settings", MB_YESNO | ICON_EXLAIM)
    if DefaultReturn == 6: 
        ScriptSettings = MySettings()
        ScriptSettings.Save(SettingsFile)
        OkMessage = Messagebox(0, "Settings restored.", "Success", MB_OK | ICON_INFO)
    else:
        AbortMessage = Messagebox(0, "Aborted, settings not restored.", "Cancelled", MB_OK | ICON_STOP)
