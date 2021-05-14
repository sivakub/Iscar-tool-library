#Author-Boopathi Sivakumar
#Description-Iscar tooling

import adsk.core, adsk.fusion, adsk.cam, traceback
import json
import wget

location = r'C:/Users/sivakub/Desktop/Bug Bash/'
url =''
# global set of event handlers to keep them referenced for the duration of the command
handlers = []
app = adsk.core.Application.cast(None)
ui = adsk.core.UserInterface.cast(None)
num = 0
paleteWidth = 400
paleteHeight = 300

# Event handler for the commandExecuted event.
class ShowPaletteCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # wget.detect_filename('https://www.iscar.com/eCatalog/FilesDownload.aspx?FileType=P&cat=5668473&itemDesc=EC-E7%2002-04C06CF-M57')

            wget.download('https://www.iscar.com/eCatalog/FilesDownload.aspx?FileType=P&cat=5668473&itemDesc=EC-E7%2002-04C06CF-M57', location)
               
        except:
            ui.messageBox('Command executed failed: {}'.format(traceback.format_exc()))


# Event handler for the commandCreated event.
class ShowPaletteCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()              
    def notify(self, args):
        try:

            global downloadBool
            # Create and display the palette.
            palette = ui.palettes.itemById('IscarPalette')

            command = args.command
            inputs = command.commandInputs

            downloadBool = inputs.addBoolValueInput('downloadTool','Download tool',True,"",False)   
            downloadBool.isVisible = False  
            if not palette:
                palette = ui.palettes.add('IscarPalette', 'Isacar Tool Library', 'https://www.iscar.com/Products.aspx/CountryId/1/ProductId/3531', True, True, True,paleteWidth, paleteHeight)

                # Dock the palette to the right side of Fusion window.
                palette.dockingState = adsk.core.PaletteDockingStates.PaletteDockStateRight

                # Add handler to HTMLEvent of the palette.
                onHTMLEvent = MyHTMLEventHandler()
                palette.incomingFromHTML.add(onHTMLEvent)   
                handlers.append(onHTMLEvent)

                onNavigationEvent = NavigationEventHandler()
                palette.navigatingURL.add(onNavigationEvent)
                handlers.append(onNavigationEvent)  
                
                # Add handler to CloseEvent of the palette.
                onClosed = MyCloseEventHandler()
                palette.closed.add(onClosed)
                handlers.append(onClosed)   
             
            else:
                palette.isVisible = True   

            onExecute = ShowPaletteCommandExecuteHandler()
            command.execute.add(onExecute)
            handlers.append(onExecute)  

        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))     


# Event handler for the commandExecuted event.
class SendInfoCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # Send information to the palette. This will trigger an event in the javascript
            # within the html so that it can be handled.

            palette = ui.palettes.itemById('IscarPalette')
            if palette:
                global num
                num += 1
                palette.sendInfoToHTML('send', 'This is a message sent to the palette from Fusion. It has been sent {} times.'.format(num))                        
        except:
            ui.messageBox('Command executed failed: {}'.format(traceback.format_exc()))

class NavigationEventHandler(adsk.core.NavigationEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global url
            if "https://www.iscar.com/eCatalog/item.aspx" in args.navigationURL:
                downloadBool.isVisible = True
                url = args.navigationURL

        except:
            ui.messageBox('Command executed failed: {}'.format(traceback.format_exc()))

# Event handler for the commandCreated event.
class SendInfoCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()              
    def notify(self, args):
        try:
            command = args.command
            onExecute = SendInfoCommandExecuteHandler()
            command.execute.add(onExecute)
            handlers.append(onExecute)                                     
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))     


# Event handler for the palette close event.
class MyCloseEventHandler(adsk.core.UserInterfaceGeneralEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global paleteWidth, paleteHeight
            palette = ui.palettes.itemById('IscarPalette')
            if palette :
                paleteWidth = palette.width
                paleteHeight = paleteHeight
                # ui.messageBox(palette.htmlFileURL)
                # ui.messageBox(str(palette.navigatingURL))
                palette.deleteMe()
      
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the palette HTML event.                
class MyHTMLEventHandler(adsk.core.HTMLEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            htmlArgs = adsk.core.HTMLEventArgs.cast(args)            
            data = json.loads(htmlArgs.data)
            msg = "An event has been fired from the html to Fusion with the following data:\n"
            msg += '    Command: {}\n    arg1: {}\n    arg2: {}'.format(htmlArgs.action, data['arg1'], data['arg2'])
            ui.messageBox(msg)
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))           

                
def run(context):
    try:
        global ui, app
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        # Add a command that displays the panel.
        showPaletteCmdDef = ui.commandDefinitions.itemById('showPalette')
        if not showPaletteCmdDef:
            showPaletteCmdDef = ui.commandDefinitions.addButtonDefinition('showPalette', 'Show Custom Palette', 'Show the custom palette', '')

            # Connect to Command Created event.
            onCommandCreated = ShowPaletteCommandCreatedHandler()
            showPaletteCmdDef.commandCreated.add(onCommandCreated)
            handlers.append(onCommandCreated)
        
         
        # Add a command under ADD-INS panel which sends information from Fusion to the palette's HTML.
        # sendInfoCmdDef = ui.commandDefinitions.itemById('sendInfoToHTML')
        # if not sendInfoCmdDef:
        #     sendInfoCmdDef = ui.commandDefinitions.addButtonDefinition('sendInfoToHTML', 'Send Info to Palette', 'Send Info to Palette HTML', '')

        #     # Connect to Command Created event.
        #     onCommandCreated = SendInfoCommandCreatedHandler()
        #     sendInfoCmdDef.commandCreated.add(onCommandCreated)
        #     handlers.append(onCommandCreated)

        # Add the command to the toolbar.
        panel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        cntrl = panel.controls.itemById('showPalette')
        if not cntrl:
            panel.controls.addCommand(showPaletteCmdDef)

        # cntrl = panel.controls.itemById('sendInfoToHTML')
        # if not cntrl:
        #     panel.controls.addCommand(sendInfoCmdDef)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:        
        # Delete the palette created by this add-in.
        palette = ui.palettes.itemById('IscarPalette')
        if palette:
            palette.deleteMe()
            
        # Delete controls and associated command definitions created by this add-ins
        panel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        cmd = panel.controls.itemById('showPalette')
        if cmd:
            cmd.deleteMe()
        cmdDef = ui.commandDefinitions.itemById('showPalette')
        if cmdDef:
            cmdDef.deleteMe() 

        cmd = panel.controls.itemById('sendInfoToHTML')
        if cmd:
            cmd.deleteMe()
        cmdDef = ui.commandDefinitions.itemById('sendInfoToHTML')
        if cmdDef:
            cmdDef.deleteMe() 
            
        ui.messageBox('Stop addin')
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))