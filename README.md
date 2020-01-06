# FacialExpression
Facial expression detection on Raspberry Pi with attached Pi camera, using the Xnor AI2GO libraries.

![alt text](https://github.com/rendzina/FacialExpression/blob/master/demonstration/HappyFace.gif "Happy face")

See the [Demonstration](https://github.com/rendzina/FacialExpression/tree/master/demonstration) files

## Project
This project is to develop a Raspberry Pi demonstrator using the Xnor AI2GO library to allow facial expression detection from an attached Pi Camera, and for it to run unattended (no attached keyboard/mouse), changing a 'face' graphic on an attached Raspberry Pi 'Pi Moroni HyperPixel' display. As the camera detects faces with differing expressions, the image onscreen changes accordingly.

The project uses the [Xnor AI2GO](https://ai2go.xnor.ai/home/) libraries, and is based on Matt Welsh's (@mdwelsh) example code at [https://medium.com/@mdwdotla/true-ai-on-a-raspberry-pi-with-no-extra-hardware-dcdbff12d068](https://medium.com/@mdwdotla/true-ai-on-a-raspberry-pi-with-no-extra-hardware-dcdbff12d068)

## Hardware
The following hardware is used:
- [Raspberry Pi 4](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/)
- [Raspberry Pi 4 v2 Camera](https://www.raspberrypi.org/products/camera-module-v2/)
- [HyperPixel 4.0 Square - Hi-Res Display for Raspberry Pi – Touch](https://shop.pimoroni.com/products/hyperpixel-4-square?variant=30138251444307)

## Software
Running on the Pi in Python 3, the following software libraries are used:
- [Xnor AI2GO](https://ai2go.xnor.ai/home/)
An account was registered on the Xnor site, and the SDK file *'xnor-sdk-v1.1.0-rpi3.zip'* was downloaded for the Raspberry Pi (Xnor note this is for the Raspberry Pi model 3 - we were using a Pi 4). Specific AI detection models can be downloaded - in fact we used the libraries held in the SDK.

## Code
The source code *'facial_expression.py'* runs the face detection tool, gathers the results from persons passing the camera and selects an appropriate image to show on the screen. A test mode is also included *'FAKE_DATA = True/False'* to generate fake data for testing purposes.
### Installing Xnor AI2GO
The file *'xnor-sdk-v1.1.0-rpi3.zip'* was copied to the Pi using FileZilla (see below) then, on the Pi:
```
> unzip xnor-sdk-v1.1.0-rpi3.zip
> cd xnor-sdk-rpi3/lib/facial-expression-classifier
> python3 -m pip install xnornet*.whl
```

## Instructions
The Raspberry Pi is configured with the camera and the HyperPixel display. A Pi case was required that allowed the screen to be fitted, the [Pi Moroni Pillow Case](https://shop.pimoroni.com/products/pibow-coupe-4?variant=29210100170835) was used. The screen and camera were fitted with the case. It was discovered that it is not at al easy to reorientate the HyperPixel display so that the touchscreen is similarly rotated - as a result the default position was accepted, meaning the power cable is plugged in from the 'bottom', not ideal.

The Pi was set up to run in 'headless' mode (no monitor/keyboard/mouse) - to do this see our [GeoThread blog](http://www.geothread.net/?s=headless), allowing a remote laptop to ssh in to the Pi, and using [FileZilla](https://filezilla-project.org) to copy files over to it.

A short Python script *'test_camera_works.py'* was used to ensure the camera was functioning and that its orientation was correct.
```
> python3 test_camera_works.py
```

A folder *'/home/pi/Public/faces'* was created and face graphic files copied to it. The HyperPixel screen is 720x720pixels. The face images were resized to fit and after experimentation, images of 720pixels wide by 640 pixels high were created (allowing for the Pi Desktop layout at the top). Facial images such as [https://www.flickr.com/photos/159615760@N04/32442990608](https://www.flickr.com/photos/159615760@N04/32442990608) were used.

## Testing
The code was tested remotely from a laptop running the python script, located in the folder *'/home/pi'*:
```
> python3 facial_expression.py
```
The Mac laptop used for testing had *XQuartz* [https://www.xquartz.org](https://www.xquartz.org) installed, allowing the graphical display to be redirected to the laptop screen for testing. The code 'prints' out the facial expressions detected, meaning that the laptop screen could be used to show both the ssh window with the print statements in the terminal window, as well as the graphical image display in XQuartz.

## Operation
To make the code run unattended on the Pi, there needed to be a means to start the programme automatically on boot. Given that the code uses the graphical tools in tkinter/pillow, the best means to do this was found to be to use an autostart desktop file. A file was therefore created thus:
```
> nano /home/pi/.config/autostart/facial_expression.desktop

[Desktop Entry]
Type=Application
Name=Facial_Expression
Exec=/usr/bin/python3 /home/pi/facial_expression.py
```

In running unattended without an attached keyboard/mouse, it was also found to be necessary to add an onscreen 'halt' button in the Python code to shut the system down (just turning off a Pi at the power is not a good idea). The code was adapted to have an unobtrusive button to do this added onscreen.

The Pi could then be rebooted to run.

## Observations
The code needs some further improvements to handle how it reacts when no faces are detected - an image *'face_makeaface.png'* was added to show an invitation to people passing to make a face at the camera.

The AI2GO facial expression library is capable of detecting a range of expressions, including :smile:'happy', :disappointed:'sad', :angry:'anger', :fearful:'fear', :stuck_out_tongue_closed_eyes:'disgust', :astonished:'surprise', and :expressionless:'neutral'. It should be noted that in practice it seemed very hard to make the model recognise any emotions other than 'neutral' and 'happy'. This could be the camera, the lack of processing power on the Pi4, the room lighting, camera settings or the faces used (!) - a bit frustrating in the end.

## Final steps - a Case
For this project we used the HyperPixel 4.0 Square screen - plugged directly into the GPIO bus. Unfortunately the default orientation of this screen means that the power cable is inserted from below - and this means that the unit cannot stand up on its own. At first we tried to change the orientation of the screen in software - although this is possible, it seems that similarly rotating the orientation of the touch screen is not so easy. In the end a case was required to lift the unit up. A bit of light engineering later and the case is finished:

![alt text](https://github.com/rendzina/FacialExpression/blob/master/demonstration/FaceRecognitionCase_01_thmb.jpg "Front view")

![alt text](https://github.com/rendzina/FacialExpression/blob/master/demonstration/FaceRecognitionCase_02_thmb.jpg "Rear view")
