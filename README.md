# Pan Zoom Helper #

This script facilitates users in manipulating Maya's pan and zoom functionalities. You must specify the camera you intend to use. You can either set a production camera in the SHOTCAM variable or specify it when calling the script (refer to Pipeline integration below). In doing so, the tool will automatically configure it if it's present in the scene.

Tested maya 2020, 2022

![](https://garcia-nicolas.com/wp-content/uploads/2024/02/pan_zoom_helper.png)

# Installation
### On the go:
Copy/Paste this whole page of code in maya python console and run.

### As simple shelf button:
Copy this script into your maya/scripts folder. Create a shelf button with these lines in python:

```python
from pan_zoom_helper import pan_zoom_helper;
window = pan_zoom_helper.PanZoomHelper();
window.show();
```

### Pipeline integration:
You can also directly specify the camera you want to set by default.
Copy this script into your maya/scripts folder.
Create a shelf button with these lines:

```python
from pan_zoom_helper import pan_zoom_helper;
window = pan_zoom_helper.PanZoomHelper(shotcam='your_shotcam_shape_name');
window.show();
```
Make sure to replace the 'your_shotcam_shape_name' with youre camera
shape name
