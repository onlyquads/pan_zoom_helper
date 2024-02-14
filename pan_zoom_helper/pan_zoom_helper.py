'''
Pan Zoom Helper

This script facilitates users in manipulating Maya's pan and zoom
functionalities. You must specify the camera you intend to use. You can either
set a production camera in the SHOTCAM variable or specify it when calling
the script (refer to Pipeline integration below). In doing so, the tool
will automatically configure it if it's present in the scene.

Tested maya 2020, 2022

# Installation
## On the go:
Copy/Paste this whole page of code in maya python console and run.

As simple shelf button:
Copy this script into your maya/scripts folder.
Create a shelf button with these lines in python:

```
from pan_zoom_helper import pan_zoom_helper;
window = pan_zoom_helper.PanZoomHelper();
window.show();
````

## Pipeline integration:
You can also directly specify the camera you want to set by default.
Copy this script into your maya/scripts folder. Create a shelf button with
these lines:

```
from pan_zoom_helper import pan_zoom_helper;
window = pan_zoom_helper.PanZoomHelper(shotcam='your_shotcam_shape_name');
window.show();
```

Make sure to replace the 'your_shotcam_shape_name' with youre camera shape name

'''

import os
import sys
from PySide2 import QtWidgets, QtCore
from PySide2.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QFrame,
    QDoubleSpinBox, QLineEdit, QLabel, QCheckBox)
import maya.cmds as cmds

# Set production camera here below
SHOTCAM = 'perspShape'
# Change default move step value below
MOVE_STEP_VALUE = 0.1
# Change default zoom step value below
ZOOM_STEP_VALUE = 0.1

TOOLNAME = 'PAN ZOOM HELPER'
VERSION = '1.4'


# FOR MAC OS WE NEED THIS LINE FOR PYTHON 2.7
os.environ['QT_MAC_WANTS_LAYER'] = '1'

window = None


def maya_main_window():
    """Return Maya's main window"""
    for obj in QtWidgets.QApplication.topLevelWidgets():
        if obj.objectName() == 'MayaWindow':
            return obj
    raise RuntimeError('Could not find MayaWindow instance')


class SeparatorLine(QFrame):
    def __init__(self, parent=None):
        super(SeparatorLine, self).__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class PanZoomHelper(QMainWindow):

    def __init__(self, parent=None, shotcam=SHOTCAM):

        if not parent:
            parent = maya_main_window()

        super(PanZoomHelper, self).__init__(parent)
        self.setWindowTitle('%s %s' % (TOOLNAME, VERSION))
        self.setWindowFlags(QtCore.Qt.Tool)

        self.shotcam = shotcam

        # Load layout
        self.load_ui()

        # Set all buttons disabled by default
        self.enable_zoom_option_buttons(False)
        self.enable_zoom_buttons(False)
        self.enable_move_buttons(False)

        # Check if preference shotcam exists in scene
        self.get_production_camera()

        # Set default step values according to preferences
        self.set_default_move_zoom_step()

    def load_ui(self):

        # Create main layout
        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)

        # Create a two row layout for camera name and button
        self.camera_setup_layout = QHBoxLayout(central_widget)

        self.set_camera_button = QPushButton('Set Cam')
        self.set_camera_button.clicked.connect(self.set_camera)

        self.camera_name_text_field = QLineEdit()
        self.camera_name_text_field.setText('set_camera')
        self.camera_name_text_field.setDisabled(True)

        self.camera_setup_layout.addWidget(self.set_camera_button, 1)
        self.camera_setup_layout.addWidget(self.camera_name_text_field)

        # Add to layout
        main_layout.addLayout(self.camera_setup_layout)

        # Add separator
        camera_name_separator = SeparatorLine(self)
        main_layout.addWidget(camera_name_separator)

        # Create PanZoom Enable/Disable and reset options
        self.layout_pan_zoom_options = QHBoxLayout()

        self.enable_pan_zoom_checkbox = QCheckBox('Pan Zoom')
        self.enable_pan_zoom_checkbox.stateChanged.connect(
            self.on_pan_zoom_enable)
        self.reset_all_button = QPushButton('Reset')
        self.reset_all_button.clicked.connect(self.reset_all)

        self.layout_pan_zoom_options.addWidget(self.enable_pan_zoom_checkbox)
        self.layout_pan_zoom_options.addWidget(self.reset_all_button)

        # Add to layout
        main_layout.addLayout(self.layout_pan_zoom_options)

        # Add separator
        pan_zoom_options_separator = SeparatorLine(self)
        main_layout.addWidget(pan_zoom_options_separator)

        # Create the Zoom buttons
        self.layout_zoom_in_out_buttons = QHBoxLayout()

        self.zoom_in_button = QPushButton('Zoom In')
        self.zoom_in_button.clicked.connect(self.zoom)

        self.zoom_out_button = QPushButton('Zoom Out')
        self.zoom_out_button.clicked.connect(self.zoom)

        self.layout_zoom_in_out_buttons.addWidget(self.zoom_in_button)
        self.layout_zoom_in_out_buttons.addWidget(self.zoom_out_button)

        main_layout.addLayout(self.layout_zoom_in_out_buttons)

        # Create the Reset Zoom button
        self.reset_zoom_button = QPushButton('Reset Zoom')
        self.reset_zoom_button.clicked.connect(self.reset_zoom)

        # Add to layout
        main_layout.addWidget(self.reset_zoom_button)

        # Add separator
        zoom_buttons_separator = SeparatorLine(self)
        main_layout.addWidget(zoom_buttons_separator)

        # Create the move buttons
        self.layout_left_right_buttons = QHBoxLayout()
        self.move_up_button = QPushButton('Up')
        self.move_up_button.clicked.connect(self.move)
        self.move_left_button = QPushButton('Left')
        self.move_left_button.clicked.connect(self.move)
        self.move_right_button = QPushButton('Right')
        self.move_right_button.clicked.connect(self.move)
        self.move_down_button = QPushButton('Down')
        self.move_down_button.clicked.connect(self.move)
        self.reset_move_button = QPushButton('Reset Move')
        self.reset_move_button.clicked.connect(self.reset_move)

        self.layout_left_right_buttons.addWidget(self.move_left_button)
        self.layout_left_right_buttons.addWidget(self.move_right_button)

        # Add to layout
        main_layout.addWidget(self.move_up_button)
        main_layout.addLayout(self.layout_left_right_buttons)
        main_layout.addWidget(self.move_down_button)
        main_layout.addWidget(self.reset_move_button)

        # Add separator
        move_buttons_separator = SeparatorLine(self)
        main_layout.addWidget(move_buttons_separator)

        # Create user zoom step options
        self.layout_user_zoom_step = QHBoxLayout()

        zoom_step_label = QLabel('Zoom Step Value')
        self.zoom_step_spinbox = QDoubleSpinBox()
        self.zoom_step_spinbox.setMaximum(100)
        self.zoom_step_spinbox.setMinimum(0)
        self.zoom_step_spinbox.setSingleStep(0.01)

        self.layout_user_zoom_step.addWidget(zoom_step_label, 1)
        self.layout_user_zoom_step.addWidget(self.zoom_step_spinbox)

        # Add to layout
        main_layout.addLayout(self.layout_user_zoom_step)

        # Create user move step options
        self.layout_user_move_step = QHBoxLayout()

        move_step_label = QLabel('Move Step Value')
        self.move_step_spinbox = QDoubleSpinBox()
        self.move_step_spinbox.setMaximum(100)
        self.move_step_spinbox.setMinimum(0)
        self.move_step_spinbox.setSingleStep(0.01)

        self.layout_user_move_step.addWidget(move_step_label, 1)
        self.layout_user_move_step.addWidget(self.move_step_spinbox)

        # Add to layout
        main_layout.addLayout(self.layout_user_move_step)

        # Add separator
        hint_text_separator = SeparatorLine(self)
        main_layout.addWidget(hint_text_separator)

        # Add user hint text
        user_hint_text = QLabel('Use SHIFT + Click on move/zoom buttons '
                                'to divide step value by 2')
        user_hint_text.setWordWrap(True)
        main_layout.addWidget(user_hint_text)

        self.setCentralWidget(central_widget)

    def on_pan_zoom_enable(self, state):

        if state == 2:
            # Checked state (ON)
            shotcam = self.camera_name_text_field.text()
            cmds.setAttr(shotcam+'.panZoomEnabled', 1)
            self.enable_zoom_buttons(True)
            self.enable_move_buttons(True)

        else:
            # Unchecked state (OFF)
            shotcam = self.camera_name_text_field.text()
            cmds.setAttr(shotcam+'.panZoomEnabled', 0)
            self.enable_zoom_buttons(False)
            self.enable_move_buttons(False)

    def enable_zoom_option_buttons(self, bool):

        self.enable_pan_zoom_checkbox.setEnabled(bool)
        self.reset_all_button.setEnabled(bool)
        self.zoom_step_spinbox.setEnabled(bool)
        self.move_step_spinbox.setEnabled(bool)

    def enable_zoom_buttons(self, bool):

        self.zoom_in_button.setEnabled(bool)
        self.zoom_out_button.setEnabled(bool)
        self.reset_zoom_button.setEnabled(bool)

    def enable_move_buttons(self, bool):

        self.move_up_button.setEnabled(bool)
        self.move_down_button.setEnabled(bool)
        self.move_left_button.setEnabled(bool)
        self.move_right_button.setEnabled(bool)
        self.reset_move_button.setEnabled(bool)

    def set_camera(self):

        selected_cam = cmds.ls(selection=True)

        if len(selected_cam) == 0:
            return cmds.warning("Please select a camera.")

        if len(selected_cam) >= 2:
            return cmds.warning("Please select only one camera.")

        if cmds.objectType(selected_cam[0]) == 'transform':
            selected_cam_shape = cmds.listRelatives(selected_cam, s=True)
            if cmds.objectType(selected_cam_shape[0]) == 'camera':
                shotcam = selected_cam_shape[0]
                self.camera_name_text_field.setText(str(shotcam))

                # Turn UI Buttons ON
                self.enable_zoom_option_buttons(True)
                pan_zoom_enabled = self.get_current_pan_zoom_status()
                self.enable_pan_zoom_checkbox.setChecked(pan_zoom_enabled)

                return shotcam
            return cmds.warning("The selected object is not a camera")

        camera = cmds.objectType(selected_cam)
        if camera in ['camera', 'stereoRigCamera']:
            shotcam = selected_cam[0]
            self.camera_name_text_field.setText(str(shotcam))

            return shotcam
        return cmds.warning("The selected object is not a camera")

    def activate(self, shotcam):
        '''If Camera exists in scene, set it as text_field and activate
        UI buttons'''
        # Set textfield text
        self.camera_name_text_field.setText(str(shotcam))
        # Enable buttons
        self.enable_zoom_option_buttons(True)

        # Get current shotcam status
        pan_zoom_enabled = self.get_current_pan_zoom_status()
        self.enable_pan_zoom_checkbox.setChecked(pan_zoom_enabled)

    def get_production_camera(self):

        # Try to set shotcam from external
        shotcam = self.shotcam
        if cmds.objExists(shotcam):
            self.activate(shotcam)
            return

        # Try to set shotcam from script's SHOTCAM var
        shotcam = SHOTCAM
        if cmds.objExists(shotcam):
            self.activate(shotcam)
            return

        # If no shotcam found
        shotcam = 'Camera Is Not Set!'
        self.camera_name_text_field.setText(str(shotcam))
        print("No production or prefered camera found in scene.")
        self.enable_zoom_option_buttons(False)

    def get_current_pan_zoom_status(self):
        shotcam = self.camera_name_text_field.text()

        if cmds.objExists(shotcam):
            pan_zoom_enabled = cmds.getAttr('%s.panZoomEnabled' % shotcam)
            return pan_zoom_enabled

    def set_default_move_zoom_step(self):

        default_move_step_value = MOVE_STEP_VALUE
        default_zoom_step_value = ZOOM_STEP_VALUE

        if default_move_step_value:
            self.move_step_spinbox.setValue(default_move_step_value)

        if default_zoom_step_value:
            self.zoom_step_spinbox.setValue(default_zoom_step_value)

    def zoom(self):

        sender_button = self.sender()
        zoom_type = sender_button.text()

        zoom_step_value = self.zoom_step_spinbox.value()
        shotcam = self.camera_name_text_field.text()
        current_value = cmds.getAttr('%s.zoom' % shotcam)

        # If mod key pressed
        mod = cmds.getModifiers()
        modifier_factor = 0.5 if mod == 1 else 1.0

        if zoom_type == "Zoom In":
            new_value = current_value - (zoom_step_value * modifier_factor)
        elif zoom_type == "Zoom Out":
            new_value = current_value + (zoom_step_value * modifier_factor)
        else:
            return cmds.warning("Invalid zoom type")

        if new_value <= 0:
            return cmds.warning("The value you try to set is below zero")

        cmds.setAttr('%s.zoom' % shotcam, new_value)

    def reset_zoom(self):
        shotcam = self.camera_name_text_field.text()
        cmds.setAttr('%s.zoom' % shotcam, 1)

    def move(self):
        sender_button = self.sender()
        direction = sender_button.text()
        mod = cmds.getModifiers()
        move_step_value = self.move_step_spinbox.value()
        shotcam = self.camera_name_text_field.text()

        if direction == "Up":
            axis = "verticalPan"
        elif direction == "Down":
            axis = "verticalPan"
        elif direction == "Left":
            axis = "horizontalPan"
        elif direction == "Right":
            axis = "horizontalPan"
        else:
            return cmds.warning("Invalid direction")

        current_value = cmds.getAttr('%s.%s' % (shotcam, axis))

        modifier_factor = 0.5 if mod == 1 else 1.0

        if direction in ["Up", "Right"]:
            new_value = current_value + (move_step_value * modifier_factor)
        elif direction in ["Down", "Left"]:
            new_value = current_value - (move_step_value * modifier_factor)
        else:
            return cmds.warning("Invalid direction")

        cmds.setAttr('%s.%s' % (shotcam, axis), new_value)

    def reset_move(self):
        shotcam = self.camera_name_text_field.text()
        cmds.setAttr('%s.verticalPan' % shotcam, 0)
        cmds.setAttr('%s.horizontalPan' % shotcam, 0)

    def reset_all(self):
        self.reset_zoom()
        self.reset_move()


if __name__ == '__main__':

    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()

    window = PanZoomHelper()
    window.show()
    app.exec_()


def show():
    global window
    if window is not None:
        window.close()
    window = PanZoomHelper(parent=maya_main_window(), shotcam=SHOTCAM)
    window.show()
