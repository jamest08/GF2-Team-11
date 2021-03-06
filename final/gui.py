"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
import gettext

import wx.glcanvas as wxcanvas
import numpy as np
import math
import os

from OpenGL import GL, GLU, GLUT
from wx.core import BoxSizer, LANGUAGE_JAPANESE


import sys

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
import builtins


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
    reset_tranformation_variables(self): Resets variables to init state

    init_gl(self): Configures the OpenGL context.

    render(self): Handles all drawing operations.

    draw_cuboid(self, x_pos, z_pos, half_width, half_depth, height): Renders
                            a cuboid in 3D view at the specified coordinates.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.

    Private methods
    ---------------
    init_2D(self): Called from init_gl.
                   Configures OpenGL 2D context.

    init_3D(self): Called from init_gl.
                   Configures OpenGL 3D context.

    render_2D(self): Called from render.
                     Handles 2D view rendering.

    render_3D(self): Called from render.
                     Handles 3D view rendering.

    on_mouse_2D(self, event): Called from on_mouse.
                              Handles mouse events in 2D view.

    on_mouse_3D(self, event): Called from on_mouse.
                              Handles mouse events in 3D view.

    render_text_2D(self, text, x_pos, y_pos, text_small): Called from render.
                        Handles all text writing on the canvas for the 2D view.

    render_text_3D(self, text, x_pos, y_pos, text_small): Called from render.
                        Handles all text writing on the canvas for the 3D view.
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
        self.devices = devices
        self.monitors = monitors

        # Constants for OpenGL materials and lights
        self.mat_diffuse = [0.0, 0.0, 0.0, 1.0]
        self.mat_no_specular = [0.0, 0.0, 0.0, 0.0]
        self.mat_no_shininess = [0.0]
        self.mat_specular = [0.5, 0.5, 0.5, 1.0]
        self.mat_shininess = [50.0]
        self.top_right = [1.0, 1.0, 1.0, 0.0]
        self.straight_on = [0.0, 0.0, 1.0, 0.0]
        self.no_ambient = [0.0, 0.0, 0.0, 1.0]
        self.dim_diffuse = [0.5, 0.5, 0.5, 1.0]
        self.bright_diffuse = [1.0, 1.0, 1.0, 1.0]
        self.med_diffuse = [0.75, 0.75, 0.75, 1.0]
        self.full_specular = [0.5, 0.5, 0.5, 1.0]
        self.no_specular = [0.0, 0.0, 0.0, 1.0]

        self.reset_transformation_variables()

        # Offset between viewpoint and origin of the scene
        self.depth_offset = 1000

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

        # control whether in 2D or 3D view
        self.choose_3D = False

    def reset_transformation_variables(self):
        """Set all transformation variables back to initial values."""
        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise the scene rotation matrix
        self.scene_rotate = np.identity(4, 'f')

        # Initialise variables for zooming
        self.zoom = 1

    def init_gl(self):
        """Handle directing initialise command to the 2D or 3D handler."""
        if self.choose_3D is False:
            self.init_2D()
        else:
            self.init_3D()

    def init_2D(self):
        """Configure and initialise the OpenGL context for a 2D render."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, size.height, 0, -1, 1)
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def init_3D(self):
        """Configure and initialise the OpenGL context for a 3D render."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)

        GL.glViewport(0, 0, size.width, size.height)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(45, size.width / size.height, 10, 10000)

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()  # lights positioned relative to the viewer

        # set the parameters for 2 light sources in the 3D view.
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, self.no_ambient)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, self.med_diffuse)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_SPECULAR, self.no_specular)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, self.top_right)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_AMBIENT, self.no_ambient)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_DIFFUSE, self.dim_diffuse)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_SPECULAR, self.no_specular)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_POSITION, self.straight_on)

        # set the material properties of the rendered items
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SPECULAR, self.mat_specular)
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SHININESS, self.mat_shininess)
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE,
                        self.mat_diffuse)
        GL.glColorMaterial(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE)

        GL.glClearColor(0.0, 0.0, 0.0, 0.0)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glCullFace(GL.GL_BACK)
        GL.glEnable(GL.GL_COLOR_MATERIAL)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)
        GL.glEnable(GL.GL_LIGHT1)
        GL.glEnable(GL.GL_NORMALIZE)

        # Viewing transformation - set the viewpoint back from the scene
        GL.glTranslatef(0, 0, -self.depth_offset)

        # Modelling transformation - pan, zoom and rotate
        GL.glTranslatef(self.pan_x, self.pan_y, 0.0)
        GL.glMultMatrixf(self.scene_rotate)
        GL.glScalef(self.zoom, self.zoom, self.zoom)
        GL.glRotatef(45, 1, 1, 0)  # rotate view to more agreeable start point.

    def render(self):
        """Handle directing render command to the 2D or 3D handler."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        if self.choose_3D is False:
            self.render_2D()
        else:
            self.render_3D()

    def render_2D(self):
        """Handle all drawing operations for a 2D render."""
        # clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # get list of signals for a single monitor

        device_number = 0
        signal_list_length = 0

        for device_id, output_id in self.monitors.monitors_dictionary:
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            signal_list = self.monitors.monitors_dictionary[(device_id, output_id)]

            x = 10
            y = 85 + device_number*50

            self.render_text_2D(monitor_name, x, y, False)
            margin = self.monitors.get_margin()

            GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
            GL.glBegin(GL.GL_LINE_STRIP)

            # draw signal according to list of states

            signal_list_length = len(signal_list)

            for i in range(signal_list_length):
                x = (i * 20) + 40 + margin*10
                x_next = (i * 20) + 60 + margin*10
                if signal_list[i] == self.devices.LOW:
                    y = 100 + device_number*50
                elif signal_list[i] == self.devices.HIGH:
                    y = 75 + device_number*50
                elif signal_list[i] == self.devices.BLANK:
                    y = 0

                # keep waveforms for monitor points added after
                # first cycles blank until point of addition

                if y != 0:
                    GL.glVertex2f(x, y)
                    GL.glVertex2f(x_next, y)
            GL.glEnd()

            device_number += 1

        # draw x axis
        y = 85 + (device_number)*50
        for i in range(signal_list_length):
            x = (i * 20) + 40 + margin*10
            self.render_text_2D('|', x, y, True)
            if i % 5 == 0:
                self.render_text_2D(str(i), x-2, y+20, True)

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def render_3D(self):
        """Handle all drawing operations for a 3D render."""
        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # configure range in x to keep origin in the center of the signals

        num_devices = len(self.monitors.monitors_dictionary)
        start_index_devices = -(num_devices//2)
        if num_devices % 2 == 0:
            end_index_devices = -start_index_devices
        else:
            end_index_devices = -start_index_devices + 1
        device_range = range(start_index_devices, end_index_devices)

        # for each device, plot its name and waveform.

        device_number = 0
        margin = self.monitors.get_margin()

        for device_id, output_id in self.monitors.monitors_dictionary:
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            signal_list = self.monitors.monitors_dictionary[(device_id, output_id)]
            signal_list_length = len(signal_list)

            # configure range in z to keep origin in the center of the signals

            start_index_signal = -(signal_list_length//2)
            if signal_list_length % 2 == 0:
                end_index_signal = -start_index_signal
            else:
                end_index_signal = -start_index_signal + 1
            signal_range = range(start_index_signal, end_index_signal)

            # draw signal according to list of states

            x = device_range[device_number] * 20
            self.render_text_3D(monitor_name, x, 0, start_index_signal * 20 - 20 - margin*10)

            GL.glColor3f(0.7, 0.2, 1)  # signal trace is purple
            for i in range(signal_list_length):
                z = signal_range[i] * 20
                if signal_list[i] == self.devices.LOW:
                    self.draw_cuboid(x, z, 5, 10, 1)
                elif signal_list[i] == self.devices.HIGH:
                    self.draw_cuboid(x, z, 5, 10, 11)

            device_number += 1

        # draw axis for number of cycles.

        for i in range(signal_list_length):
            z = signal_range[i] * 20
            self.render_text_3D(str(i), (device_range[0]-1)*20, 0, z - 10)

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def draw_cuboid(self, x_pos, z_pos, half_width, half_depth, height):
        """Draw a cuboid.

        Draw a cuboid at the specified position, with the specified
        dimensions.
        """
        GL.glBegin(GL.GL_QUADS)
        GL.glNormal3f(0, -1, 0)
        GL.glVertex3f(x_pos - half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos + half_depth)
        GL.glNormal3f(0, 1, 0)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos + half_depth)
        GL.glNormal3f(-1, 0, 0)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos + half_depth)
        GL.glNormal3f(1, 0, 0)
        GL.glVertex3f(x_pos + half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos + half_depth)
        GL.glNormal3f(0, 0, -1)
        GL.glVertex3f(x_pos - half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos - half_depth)
        GL.glNormal3f(0, 0, 1)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos + half_depth)
        GL.glEnd()

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
        self.render()

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle directing mouse events to the 2D or 3D handler."""
        if self.choose_3D is False:
            self.on_mouse_2D(event)
        else:
            self.on_mouse_3D(event)

    def on_mouse_2D(self, event):
        """Handle mouse events for a 2D render."""
        text = ""
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = -event.GetY()

        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= -event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = -event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            if self.zoom < 0.65:
                self.zoom = 0.65  # stop user zooming out so signals don't overlap.
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
            self.render()
        else:
            self.Refresh()  # triggers the paint event

    def on_mouse_3D(self, event):
        """Handle mouse events for a 3D render."""
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()

        if event.Dragging():
            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glLoadIdentity()
            x = event.GetX() - self.last_mouse_x
            y = event.GetY() - self.last_mouse_y
            if event.LeftIsDown():
                GL.glRotatef(math.sqrt((x * x) + (y * y)), y, x, 0)
            if event.MiddleIsDown():
                GL.glRotatef((x + y), 0, 0, 1)
            if event.RightIsDown():
                self.pan_x += x
                self.pan_y -= y
            GL.glMultMatrixf(self.scene_rotate)
            GL.glGetFloatv(GL.GL_MODELVIEW_MATRIX, self.scene_rotate)
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False

        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False

        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False

        self.Refresh()  # triggers the paint event

    def render_text_2D(self, text, x_pos, y_pos, text_small):
        """Handle text drawing operations for a 2D render."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        if text_small is True:
            font = GLUT.GLUT_BITMAP_HELVETICA_12
        else:
            font = GLUT.GLUT_BITMAP_HELVETICA_18

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

    def render_text_3D(self, text, x_pos, y_pos, z_pos):
        """Handle text drawing operations for a 3D render."""
        GL.glColor3f(1, 1, 1)  # text in white
        GL.glDisable(GL.GL_LIGHTING)
        GL.glRasterPos3f(x_pos, y_pos, z_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_18

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos3f(x_pos, y_pos, z_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

        GL.glEnable(GL.GL_LIGHTING)


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
                                button. Runs the number of cycles chosen by the
                                current spin value.

    on_continue_button(self, event): Event handler for when the user clicks the
                                continue button. Continues the simulation for a
                                number of cycles chosen by the current spin value.

    on_switch_button(self, event): Event handler for when the user clicks the
                                switch button. Changes the state of the selected switch.

    on_zap_button(self, event): Event handler for when the user clicks the
                                zap button. Zaps the chosen monitor.

    on_add_button(self, event): Event handler for when the user clicks the
                                add button. Adds the chosen monitor.

    get_monitor_IDs(self, monitor_name): Takes an argument of the monitor
                    point name. Returns the IDs of the device and port associated
                    in a list of the form [device_id, port_id].

    on_text_box(self, event): Event handler for when the user enters text.

    write_to_dialogue(self, text): Prints text in the dialogue box with a line
                                   between each call.

    run_network(self, cycles): Runs the network for the specified number of
                               simulation cycles.

    Private methods
    ---------------
    configure_view(self): Initialises all widgets into appropriate places
                          on the GUI.

    reset_monitor_lists(self): Called from zap and add button event handlers.
                               Used to reset the lists for the drop-down menus.

    define_long_texts(self): Defines long text inputs for use in the GUI.

    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(600, 530))
        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.network = network
        self.define_long_texts()

        # define variables used similarly to userint class

        self.cycles_completed = 0  # number of simulation cycles completed
        self.character = ""  # current character
        self.line = ""  # current string entered by the user
        self.cursor = 0  # cursor position

        # Configure the menu bar
        fileMenu = wx.Menu()
        helpMenu = wx.Menu()
        menuBar = wx.MenuBar()

        fileMenu.SetTitle(_("File"))
        fileMenu.Append(wx.ID_ABOUT, _("&About"))
        fileMenu.Append(wx.ID_EXIT, _("&Exit"))

        helpMenu.SetTitle(_("Help"))
        helpMenu.Append(wx.ID_HELP, _("&Help"))
        helpMenu.Append(wx.ID_HELP_CONTEXT, "&EBNF")

        menuBar.Append(fileMenu, _("&File"))
        menuBar.Append(helpMenu, _("&Help"))
        self.SetMenuBar(menuBar)

        # set scrollable area for canvas

        self.scrollable = wx.ScrolledCanvas(self, wx.ID_ANY)
        self.scrollable.SetSizeHints(800, 1000)
        self.scrollable.ShowScrollbars(wx.SHOW_SB_ALWAYS, wx.SHOW_SB_DEFAULT)

        # Declare "run simulation items"

        self.spin_value = 0
        self.run_text = wx.StaticText(self, wx.ID_ANY, _('Run Simulation'))
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "0")
        self.run_button = wx.Button(self, wx.ID_ANY, _("Run"))
        self.continue_button = wx.Button(self, wx.ID_ANY, _("Continue"))

        # Declare "manage switches items"

        self.switches_text = wx.StaticText(self, wx.ID_ANY, _("Manage Switches"))

        self.switches_id_list = devices.find_devices(devices.SWITCH)
        self.switches_list = []
        for id in self.switches_id_list:
            name = names.get_name_string(id)
            self.switches_list.append(name)

        self.switches = wx.Choice(self, wx.ID_ANY, choices=self.switches_list)
        self.switch_setting = wx.Choice(self, wx.ID_ANY, choices=["0", "1"])
        self.switch_button = wx.Button(self, wx.ID_ANY, _("Switch"))

        # Declare "manage monitors items"

        self.monitors_text = wx.StaticText(self, wx.ID_ANY, _("Manage Monitors"))

        self.monitored_list = monitors.get_signal_names()[0]
        self.unmonitored_list = monitors.get_signal_names()[1]

        self.monitored = wx.Choice(self, wx.ID_ANY, choices=self.monitored_list)
        self.not_monitored = wx.Choice(self, wx.ID_ANY, choices=self.unmonitored_list)

        self.add_monitor_button = wx.Button(self, wx.ID_ANY, _("Add"))
        self.zap_monitor_button = wx.Button(self, wx.ID_ANY, _("Zap"))

        # declare bottom items

        self.toggle_view_button = wx.Button(self, wx.ID_ANY, _("Toggle 2D/3D"))
        self.dialogue_box = wx.TextCtrl(self, wx.ID_ANY, "",
                                        style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Bind events to widgets

        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.switch_button.Bind(wx.EVT_BUTTON, self.on_switch_button)
        self.add_monitor_button.Bind(wx.EVT_BUTTON, self.on_add_button)
        self.zap_monitor_button.Bind(wx.EVT_BUTTON, self.on_zap_button)
        self.toggle_view_button.Bind(wx.EVT_BUTTON, self.on_toggle_view_button)

        self.configure_view()

    def configure_view(self):
        """Set up sizers and place objects in them."""
        # Configure sizers for layout

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.GridBagSizer(14, 4)
        side_sizer.AddGrowableCol(0)
        side_sizer.AddGrowableRow(11)
        main_sizer.Add(side_sizer, 1, wx.TOP | wx.LEFT | wx.EXPAND, 5)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.scrollable, 1, wx.TOP, 5)

        # initialise canvas for drawing signals

        self.canvas = MyGLCanvas(self.scrollable, wx.DefaultPosition,
                                 wx.Size(1000, 1000), self.devices, self.monitors)
        self.canvas.SetSizeHints(500, 500)
        self.scrollable.SetScrollbars(20, 20, 50, 50)
        self.scrollable.Scroll(0, 0)

        # place "run simulation" items

        side_sizer.Add(self.run_text, pos=(0, 0), flag=wx.TOP | wx.EXPAND, border=5)
        side_sizer.Add(self.spin, pos=(1, 0), span=(1, 1), flag=wx.TOP | wx.EXPAND, border=5)
        side_sizer.Add(self.run_button, pos=(1, 1), span=(1, 1), flag=wx.TOP | wx.EXPAND, border=5)
        side_sizer.Add(self.continue_button, pos=(1, 2),
                       span=(1, 1), flag=wx.TOP | wx.EXPAND, border=5)

        # place "manage switches" items

        side_sizer.Add(self.switches_text, pos=(2, 0), flag=wx.TOP | wx.EXPAND, border=5)
        side_sizer.Add(self.switches, pos=(3, 0), span=(1, 1), flag=wx.TOP | wx.EXPAND, border=5)
        side_sizer.Add(self.switch_setting, pos=(3, 1),
                       span=(1, 1), flag=wx.TOP | wx.EXPAND, border=5)
        side_sizer.Add(self.switch_button, pos=(3, 2), flag=wx.TOP | wx.EXPAND, border=5)

        # place "manage monitors" items

        side_sizer.Add(self.monitors_text, pos=(4, 0), flag=wx.TOP | wx.EXPAND, border=5)
        side_sizer.Add(self.monitored, pos=(5, 0), span=(1, 2), flag=wx.TOP | wx.EXPAND, border=5)
        side_sizer.Add(self.zap_monitor_button, pos=(5, 2), flag=wx.TOP | wx.EXPAND, border=5)
        side_sizer.Add(self.not_monitored, pos=(6, 0),
                       span=(1, 2), flag=wx.TOP | wx.EXPAND, border=5)
        side_sizer.Add(self.add_monitor_button, pos=(6, 2), flag=wx.TOP | wx.EXPAND, border=5)

        # place bottom items

        side_sizer.Add(self.toggle_view_button, pos=(13, 0), span=(1, 1), flag=wx.BOTTOM, border=5)
        side_sizer.Add(self.dialogue_box, pos=(8, 0), span=(5, 4), flag=wx.EXPAND, border=5)

        self.SetSizeHints(600, 530)  # minimum size of entire window
        self.SetSizer(main_sizer)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        print("Menu button pressed\n")
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_HELP_CONTEXT:
            text = _("EBNF Button Pressed")
            print("EBNF Button Pressed\n")
            self.write_to_dialogue(text)
            ebnf_box = wx.GenericMessageDialog(None, self.EBNF_text,
                                               _("Rules for the user definition file."),
                                               wx.ICON_INFORMATION)
            ebnf_box.ShowModal()

        if Id == wx.ID_HELP:
            text = _("Help button pressed.")
            self.dialogue_box.write("{} \n \n".format(text))
            self.dialogue_box.write("{} \n \n".format(self.help_text))
        if Id == wx.ID_ABOUT:
            wx.MessageBox("""Logic Simulator
                          \nCreated by James Thompson, Anna Mills and Neelay Sant\n2021""",
                          _("About Logsim"), wx.ICON_INFORMATION | wx.OK)

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        self.spin_value = spin_value
        text = _("New spin control value: {} \n").format(str(spin_value))
        print("New spin control value: {} \n".format(str(spin_value)))
        self.write_to_dialogue(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button.

        Run the simulation from scratch.
        """
        self.cycles_completed = 0
        cycles = self.spin_value

        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            text = _("Running for {} cycles\n").format(str(cycles))
            print(("Running for {} cycles\n").format(str(cycles)))
            self.devices.cold_startup()
            if self.run_network(cycles):
                self.cycles_completed += cycles

        self.canvas.render()
        self.write_to_dialogue(text)

    def on_continue_button(self, event):
        """Handle the event when the user clicks the continue button.

        Continue a previously run simulation.
        """
        cycles = self.spin_value
        if cycles is not None:  # if the number of cycles provided is valid
            if self.cycles_completed == 0:
                text = _("Error! Nothing to continue. Run first.\n")
                print("Error! Nothing to continue. Run first.\n")
            elif self.run_network(cycles):
                self.cycles_completed += cycles
                text = _("Continuing for {} cycles. \nTotal: {} \n").format(
                    str(cycles), str(self.cycles_completed))
                print(("Continuing for {} cycles. \nTotal: {} \n").format(
                    str(cycles), str(self.cycles_completed)))

        self.canvas.render()
        self.write_to_dialogue(text)

    def on_switch_button(self, event):
        """Handle the event when the user clicks the switch button.

        Set the specified switch to the specified signal level.
        """
        switch_index = self.switches.GetSelection()
        switch_id = self.switches_id_list[switch_index]

        if switch_id is not None:
            choice = int(self.switch_setting.GetSelection())
            switch_state = choice
            if switch_state is not None:
                if self.devices.set_switch(switch_id, switch_state):
                    text = _("Successfully set switch.")
                    print("Successfully set switch.\n")
                else:
                    text = _("Error! Invalid switch.")
                    print("Error! Invalid switch.\n")

        self.write_to_dialogue(text)

    def on_zap_button(self, event):
        """Handle the event when the user clicks the run button.

        Remove the specified monitor.
        """
        try:
            monitor_name = self.monitored.GetString(self.monitored.GetSelection())
        except Exception:
            text = _("Error! Could not zap monitor.")
            print("Error! Could not zap monitor.\n")
            self.write_to_dialogue(text)
            return False
        monitor = self.get_monitor_IDs(monitor_name)

        # attempt to zap monitor once IDs have been found.

        if monitor is not None:
            [device, port] = monitor
            if self.monitors.remove_monitor(device, port):
                text = _("Successfully zapped monitor")
                print("Successfully zapped monitor\n")
            else:
                text = _("Error! Could not zap monitor.")
                print("Error! Could not zap monitor.\n")

        self.canvas.render()
        self.write_to_dialogue(text)
        self.reset_monitor_lists()

    def on_add_button(self, event):
        """Handle the event when the user clicks the run button.

        Set the specified monitor.
        """
        try:
            monitor_name = self.not_monitored.GetString(self.not_monitored.GetSelection())
        except Exception:
            text = _("Error! Could not make monitor.")
            print("Error! Could not make monitor.\n")
            self.write_to_dialogue(text)
            return False
        monitor = self.get_monitor_IDs(monitor_name)

        # attempt to make monitor once IDs have been found.

        if monitor is not None:
            [device, port] = monitor
            monitor_error = self.monitors.make_monitor(device, port, self.cycles_completed)
            if monitor_error == self.monitors.NO_ERROR:
                text = _("Successfully made monitor.")
                print("Successfully made monitor.\n")
            else:
                text = _("Error! Could not make monitor.")
                print("Error! Could not make monitor.\n")

        self.canvas.render()
        self.write_to_dialogue(text)
        self.reset_monitor_lists()

    def get_monitor_IDs(self, monitor_name):
        """Extract monitor's device and port IDs and return them."""
        device_name_list = []
        port_name_list = []
        is_device = True  # keep track of when '.' is hit.
        for i in monitor_name:
            if i.isalnum() is True and is_device is True:
                device_name_list.append(i)
            elif i.isalnum() is True:
                port_name_list.append(i)
            else:
                is_device = False

        device_name = ''.join(device_name_list)
        port_name = ''.join(port_name_list)

        device_id = self.names.query(device_name)
        if port_name == '':
            port_id = None
        else:
            port_id = self.names.query(port_name)

        monitor = [device_id, port_id]
        return monitor

    def reset_monitor_lists(self):
        """Reset lists available to add and zap monitors from."""
        self.monitored.Clear()
        self.monitored_list = self.monitors.get_signal_names()[0]
        self.monitored.SetItems(self.monitored_list)

        self.not_monitored.Clear()
        self.unmonitored_list = self.monitors.get_signal_names()[1]
        self.not_monitored.SetItems(self.unmonitored_list)

    def write_to_dialogue(self, text):
        """Write text to the dialogue box and print to the console."""
        self.dialogue_box.write("{} \n".format(text))

    def on_toggle_view_button(self, event):
        """Handle the user requesting to change between 2D and 3D view."""
        text = _("Toggle view button pressed")
        self.write_to_dialogue(text)

        self.canvas.reset_transformation_variables()
        self.canvas.init = False

        # handle the change of view

        if self.canvas.choose_3D is False:
            self.canvas.choose_3D = True
            self.canvas.pan_x = -300  # move origin to be visible on init
            self.canvas.pan_y = 300
        else:
            self.canvas.choose_3D = False
            self.canvas.__init__(self.scrollable, wx.DefaultPosition,
                                 wx.Size(1000, 1000), self.devices, self.monitors)
        self.canvas.render()

    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
        for i in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                text = _("Error! Network oscillating.")
                print("Error! Network oscillating.\n")
                self.write_to_dialogue(text)
                return False
        self.monitors.display_signals()
        return True

    def define_long_texts(self):
        """Initialise long texts used in the GUI."""
        self.help_text = _(u"""HELP MENU: \n
To run the simulation for N cycles, select N with the scroll menu and click 'Run'. \n
To continue the simulation for N cycles, select N with the scroll menu.
Then click 'Continue'. \n
To toggle a switch, select the switch from the 'Manage Switches' drop-down menu.
Then select a state for the switch to be in. Then click 'Switch'. \n
To remove a monitor point, choose one from the first 'Manage Monitors' drop-down menu.
Then click 'Zap'. \n
To add a monitor point, choose one from the second 'Manage Monitors' drop-down menu.
Then click 'Add'. \n
To toggle between the 2D and 3D view, click the 'toggle 2D/3D' button.
It is located in the bottom left of the window. \n
When in 2D view, holding 'left' or 'right' click and dragging will translate the view. \n
When in 3D view, holding 'right click' and dragging will translate the view.
Holding 'left click' and dragging will rotate the view. \n
Scrolling in either view will zoom in and out.""")

        self.EBNF_text = """EBNF RULES:

digit = ???0??? | ???1??? | ???2??? | ???3??? | ???4??? | ???5??? | ???6??? | ???7??? | ???8??? | ???9??? ;

letter = "A" | "B" | "C" | "D" | "E" | "F" | "G"
       | "H" | "I" | "J" | "K" | "L" | "M" | "N"
       | "O" | "P" | "Q" | "R" | "S" | "T" | "U"
       | "V" | "W" | "X" | "Y" | "Z" | "a" | "b"
       | "c" | "d" | "e" | "f" | "g" | "h" | "i"
       | "j" | "k" | "l" | "m" | "n" | "o" | "p"
       | "q" | "r" | "s" | "t" | "u" | "v" | "w"
       | "x" | "y" | "z" ;

file = {definition | connection | monitor}, "END" ;

definition =  ???define???, name, {name}, ???as???,
 ( ???XOR??? | ???DTYPE??? | switch | gate | clock | generator), ???;??? ;
name = letter, {letter | digit} ;
switch = ???SWITCH???, (???0??? | ???1???), ???state??? ;
gate = (???NAND??? | ???AND??? | ???OR??? | ???NOR??? ), digit, {digit}, ???inputs???;
clock = ???CLOCK???, ???period???, digit, {digit} ;
generator = "SIGGEN", ("0"|"1"), "for", digit, {digit}, "cycles",
{("0" | "1"), "for", digit, {digit}, "cycles"} ;

connection = ???connect???, output, ???to???, input, ???;??? ;
output = name, [???.Q??? | ???.QBAR???] ;
input = name, ???.???, (???DATA??? | ???CLK??? | ???SET??? | ???CLEAR??? | ???I???, digit, {digit}) ;

monitor = ???monitor???, output, {output}, ???;??? ;

Comments:
Line comments must be started with a '%' and ended by a newline.
Paragraph comments must be enclosed between two '#' characters.
"""
