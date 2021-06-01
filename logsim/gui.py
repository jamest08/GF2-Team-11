"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
from wx.core import BoxSizer
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT

import sys

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, pos, size, devices, monitors):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1, pos=pos, size=size,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

        self.devices = devices
        self.monitors = monitors


    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)


    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        # get list of signals for a single monitor

        device_number = 0

        for device_id, output_id in self.monitors.monitors_dictionary:
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            signal_list = self.monitors.monitors_dictionary[(device_id, output_id)]

            x = 10
            y = 85 + device_number*50

            self.render_text(monitor_name, x, y)
            margin = self.monitors.get_margin()
            # print(margin)

            GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
            GL.glBegin(GL.GL_LINE_STRIP)

            for i in range(len(signal_list)):
                x = (i * 20) + 40 + margin*10
                x_next = (i * 20) + 60 + margin*10
                if signal_list[i] == self.devices.LOW:
                    y = 75 + device_number*50
                elif signal_list[i] == self.devices.HIGH:
                    y = 100 + device_number*50
                
                GL.glVertex2f(x, y)
                GL.glVertex2f(x_next, y)
            GL.glEnd()

            device_number += 1

            # for i in range(10):
            #     x = (i * 20) + 10
            #     x_next = (i * 20) + 30
            #     if i % 2 == 0:
            #         y = 75
            #     else:
            #         y = 100
            #     GL.glVertex2f(x, y)
            #     GL.glVertex2f(x_next, y)
            # GL.glEnd()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_18

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(600, 500)) # size of entire window at beginning

        # Configure the file menu

        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.SetTitle("File")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)
        print(menuBar.GetMenu(0).GetTitle())
        menuBar.EnableTop(0,True)

        # set scrollable area for canvas

        self.scrollable = wx.ScrolledCanvas(self, wx.ID_ANY)
        self.scrollable.SetSizeHints(500, 500)  #!!!! what is this doing
        self.scrollable.ShowScrollbars(wx.SHOW_SB_ALWAYS,wx.SHOW_SB_DEFAULT)

        # Declare "run simulation items"

        self.spin_value = 0
        self.run_text = wx.StaticText(self, wx.ID_ANY, "Run Simulation")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "0")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.continue_button = wx.Button(self, wx.ID_ANY, "Continue")

        # Declare "manage switches items"

        self.switches_text = wx.StaticText(self, wx.ID_ANY, "Manage Switches")

        self.switches_id_list = devices.find_devices(devices.SWITCH)
        self.switches_list = []
        for id in self.switches_id_list:
            name = names.get_name_string(id)
            self.switches_list.append(name)

        self.switches = wx.Choice(self, wx.ID_ANY, choices = self.switches_list)
        self.switch_setting = wx.Choice(self, wx.ID_ANY, choices = ["0", "1"])
        self.switch_button = wx.Button(self, wx.ID_ANY, "Switch")

        # Declare "manage monitors items"

        self.monitors_text = wx.StaticText(self, wx.ID_ANY, "Manage Monitors")

        self.monitored_list = monitors.get_signal_names()[0]
        self.unmonitored_list = monitors.get_signal_names()[1]

        self.monitored = wx.Choice(self, wx.ID_ANY, choices = self.monitored_list)
        self.not_monitored = wx.Choice(self, wx.ID_ANY, choices = self.unmonitored_list)

        self.zap_monitor_button = wx.Button(self, wx.ID_ANY, "Zap")
        self.add_monitor_button = wx.Button(self, wx.ID_ANY, "Add")
        
        # declare bottom items

        self.quit_button = wx.Button(self, wx.ID_ANY, "Quit")
        self.help_button = wx.Button(self, wx.ID_ANY, "Help")

        self.dialogue_box = wx.TextCtrl(self, wx.ID_ANY, "", style = wx.TE_MULTILINE|wx.TE_READONLY)

        self.help_text = """HELP MENU: \n
        To run the simulation for N cycles, select N with the scroll menu and click 'Run'. \n
        To continue the simulation for N cycles, select N with the scroll menu and click 'Continue'. \n
        To toggle a switch, select the switch from the 'Manage Switches' drop-down menu and a state for the switch to be in. Then click 'Switch'. \n
        To remove a monitor point, choose one from the first 'Manage Monitors' drop-down menu and click 'Zap'. \n
        To add a monitor point, choose one from the second 'Manage Monitors' drop-down menu and click 'Add'. \n
        To quit the program, click quit. """

        # Bind events to widgets

        # self.text_box.Bind(wx.EVT_TEXT_ENTER, self.on_text_box)
        self.Bind(wx.EVT_MENU, self.on_menu)

        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.switch_button.Bind(wx.EVT_BUTTON, self.on_switch_button)
        self.add_monitor_button.Bind(wx.EVT_BUTTON, self.on_add_button)
        self.zap_monitor_button.Bind(wx.EVT_BUTTON, self.on_zap_button)
        self.quit_button.Bind(wx.EVT_BUTTON, self.on_quit_button)
        self.help_button.Bind(wx.EVT_BUTTON, self.on_help_button)

        '''need to add binds to new features'''

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.GridBagSizer(12, 4)
        main_sizer.Add(side_sizer, 1, wx.TOP|wx.LEFT, 5)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.scrollable, 1, wx.TOP, 5)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self.scrollable, wx.DefaultPosition,  
        wx.Size(1000, 1000), devices, monitors) # size of canvas
        self.canvas.SetSizeHints(500, 500)
        self.scrollable.SetScrollbars(20, 20, 50, 50)
        self.scrollable.Scroll(0, 50)

        # place "run simulation" items

        side_sizer.Add(self.run_text, pos = (0, 0), flag = wx.TOP|wx.EXPAND, border = 5)
        side_sizer.Add(self.spin, pos = (1, 0), span = (1, 1), flag = wx.TOP|wx.EXPAND, border = 5)
        side_sizer.Add(self.run_button, pos = (1, 1), span = (1, 1), flag = wx.TOP|wx.EXPAND, border = 5)
        side_sizer.Add(self.continue_button, pos = (1, 2), span = (1, 1), flag = wx.TOP|wx.EXPAND, border = 5)

        # place "manage switches" items

        side_sizer.Add(self.switches_text, pos = (2, 0), flag = wx.TOP|wx.EXPAND, border = 5)
        side_sizer.Add(self.switches, pos = (3, 0), span = (1, 1), flag = wx.TOP|wx.EXPAND, border = 5)
        side_sizer.Add(self.switch_setting, pos = (3, 1), span = (1, 1), flag = wx.TOP|wx.EXPAND, border = 5)
        side_sizer.Add(self.switch_button, pos = (3, 2), flag = wx.TOP|wx.EXPAND, border = 5)

        # place "manage monitors" items

        side_sizer.Add(self.monitors_text, pos = (4, 0), flag = wx.TOP|wx.EXPAND, border = 5)
        side_sizer.Add(self.monitored, pos = (5, 0), span = (1, 2), flag = wx.TOP|wx.EXPAND, border = 5)
        side_sizer.Add(self.zap_monitor_button, pos = (5, 2), flag = wx.TOP|wx.EXPAND, border = 5)
        side_sizer.Add(self.not_monitored, pos = (6, 0), span = (1, 2), flag = wx.TOP|wx.EXPAND, border = 5)
        side_sizer.Add(self.add_monitor_button, pos = (6, 2), flag = wx.TOP|wx.EXPAND, border = 5)

        # place bottom items

        side_sizer.Add(self.quit_button, pos = (8, 0), span = (1, 1), flag = wx.BOTTOM, border = 5)
        side_sizer.Add(self.help_button, pos = (8, 1), span = (1, 1), flag = wx.BOTTOM, border = 5)
        side_sizer.Add(self.dialogue_box, pos = (9, 0), span = (3, 4), flag = wx.EXPAND, border = 5)


        # side_sizer.Add(self.text_box, 1, wx.ALL, 5)
        # side_sizer.Add(self.help_text, 10, wx.TOP, 10)

        self.SetSizeHints(600, 500) # minimum size of entire window
        self.SetSizer(main_sizer)

        # variables from userint

        self.cycles_completed = 0  # number of simulation cycles completed

        self.character = ""  # current character
        self.line = ""  # current string entered by the user
        self.cursor = 0  # cursor position

        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.network = network

        self.start_view = 0


    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        print("menu button pressed")
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Mojisola Agboola\n2017",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)


    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        self.spin_value = spin_value
        text = "".join(["New spin control value: ", str(spin_value)])
        # self.canvas.render(text)
        self.dialogue_box.write("{} \n".format(text))


    def on_run_button(self, event):
        """Handle the event when the user clicks the run button.
        Run the simulation from scratch."""

        self.cycles_completed = 0
        cycles = self.spin_value

        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            text = "".join(["Running for ", str(cycles), " cycles"])
            print(text)
            self.devices.cold_startup()
            if self.run_network(cycles):
                self.cycles_completed += cycles
        
        self.canvas.render(text)
        self.dialogue_box.write("{} \n".format(text))


    def on_continue_button(self, event):
        """Handle the event when the user clicks the continue button.
        Continue a previously run simulation."""

        cycles = self.spin_value
        if cycles is not None:  # if the number of cycles provided is valid
            if self.cycles_completed == 0:
                text = "Error! Nothing to continue. Run first."
                print(text)
            elif self.run_network(cycles):
                self.cycles_completed += cycles
                text = " ".join(["Continuing for", str(cycles), "cycles.",
                                "Total:", str(self.cycles_completed)])
                print(text)
        
        self.canvas.render(text)
        self.dialogue_box.write("{} \n".format(text))


    def on_switch_button(self, event):
        """Handle the event when the user clicks the switch button.
        Set the specified switch to the specified signal level."""
        
        switch_index = self.switches.GetSelection()
        switch_id = self.switches_id_list[switch_index]

        if switch_id is not None:
            choice = int(self.switch_setting.GetSelection())
            switch_state = choice
            if switch_state is not None:
                if self.devices.set_switch(switch_id, switch_state):
                    text = "Successfully set switch."
                    print(text)
                else:
                    text = "Error! Invalid switch."
                    print(text)
        
        # self.canvas.render(text)
        self.dialogue_box.write("{} \n".format(text))


    def on_zap_button(self, event):
        """Handle the event when the user clicks the run button.
        Remove the specified monitor."""

        try: 
            monitor_name = self.monitored.GetString(self.monitored.GetSelection())
        except:
            text = "Error! Could not zap monitor."
            print(text)
            # self.canvas.render(text)
            self.dialogue_box.write("{} \n".format(text))
            return False

        device_name_list = []
        port_name_list = []
        is_device = True # keep track of when '.' is hit.
        for i in monitor_name:
            if i.isalnum() is True and is_device is True:
                device_name_list.append(i)
            elif i.isalnum() is True:
                port_name_list.append(i)
            else:
                is_device = 0
        
        device_name = ''.join(device_name_list)
        port_name = ''.join(port_name_list)

        device_id = self.names.query(device_name)
        if port_name == '':
            port_id = None
        else:
            port_id = self.names.query(port_name)

        monitor = [device_id, port_id]
        if monitor is not None:
            [device, port] = monitor
            if self.monitors.remove_monitor(device, port):
                text = "Successfully zapped monitor"
                print(text)
            else:
                text = "Error! Could not zap monitor."
                print(text)
    
        self.canvas.render(text)
        self.dialogue_box.write("{} \n".format(text))

        self.monitored.Clear()
        self.monitored_list = self.monitors.get_signal_names()[0]
        self.monitored.SetItems(self.monitored_list)

        self.not_monitored.Clear()
        self.unmonitored_list = self.monitors.get_signal_names()[1]
        self.not_monitored.SetItems(self.unmonitored_list)


    def on_add_button(self, event):
        """Handle the event when the user clicks the run button.
        Set the specified monitor."""

        try:
            monitor_name = self.not_monitored.GetString(self.not_monitored.GetSelection())
        except:
            text = "Error! Could not make monitor."
            print(text)
            # self.canvas.render(text)
            self.dialogue_box.write("{} \n".format(text))
            return False

        device_name_list = []
        port_name_list = []
        is_device = True # keep track of when '.' is hit.
        for i in monitor_name:
            if i.isalnum() is True and is_device is True:
                device_name_list.append(i)
            elif i.isalnum() is True:
                port_name_list.append(i)
            else:
                is_device = 0
        
        device_name = ''.join(device_name_list)
        port_name = ''.join(port_name_list)

        device_id = self.names.query(device_name)
        if port_name == '':
            port_id = None
        else:
            port_id = self.names.query(port_name)

        monitor = [device_id, port_id]
        
        if monitor is not None:
            [device, port] = monitor
            monitor_error = self.monitors.make_monitor(device, port,
                                                       self.cycles_completed)
            if monitor_error == self.monitors.NO_ERROR:
                text = "Successfully made monitor."
                print(text)
            else:
                text = "Error! Could not make monitor."
                print(text)
        
        self.canvas.render(text)
        self.dialogue_box.write("{} \n".format(text))

        self.monitored.Clear()
        self.monitored_list = self.monitors.get_signal_names()[0]
        self.monitored.SetItems(self.monitored_list)

        self.not_monitored.Clear()
        self.unmonitored_list = self.monitors.get_signal_names()[1]
        self.not_monitored.SetItems(self.unmonitored_list)


    def on_quit_button(self, event):
        """Handle the event when the user clicks the quit button."""
        print("quitting program")
        sys.exit()


    def on_help_button(self, event):
        """Handle the event when the user clicks the reset button."""
        text = "reset button pressed."

        self.canvas.render(text)

        self.dialogue_box.write(self.help_text)


    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                text = "Error! Network oscillating."
                print(text)
                # self.canvas.render(text)
                self.dialogue_box.write("{} \n".format(text))
                return False
        self.monitors.display_signals()
        return True