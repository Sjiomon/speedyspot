# speedyspot
A simple and fast way to add a spot layer to an image. Could, for example, be used to generate a spot layer for DTF printers or other more complex printers that may require it. There seems to be no one-fits-all combination for the settings due to the fact that many printers (and their RIP programs) have different ways to interpret how the spot layer is represented in the image. The best way to find out what settings to use is to just test or ask the manufacturer (for example, the spot layer name can be really hard to find out by guessing)

The input image can be a PNG, TIFF or EPS, and the output will be a TIFF image (either CMYK or RGB) with a spot layer.
---
### Running the program
To start the program, you need to have Python installed, then install all the required modules (can be done with the following command: ```pip install -r requirements.txt```). Then you should be able to just run the main.py file. If using the prebuilt .exe file, just double-click to launch it. Just like you would start any other program. 

---
### EPS
Eps is supported with Ghostscript, and it can be installed in two ways. Way 1 is the recommended and simpler way. However, if way 2 is installed, it will be prioritized.

#### Way 1 (Recommended)
Install it as standard, and the program should find it. To check if it was found, press the "Select image" button and check if eps is listed as one of the formats that can be selected. If not, make sure it was added to the environment variables. If it was not done by default: do it manually.

#### Way 2
*Only recommended if you want a specific Ghostscript version for this program or don't want to install Ghostscript (as a whole) on your computer*

1. Download Ghostscript as standard and open the .exe file with a program like 7-Zip. 

2. Find the following files:
    - gsdll64.dll
    - gsdll64.lib
    - gswin64c.exe

3. Copy the files into the data folder.

---
### ICC Profiles
To use an ICC profile, place it in the data/presets folder that will be created upon running the script for the first time and select it from the dropdown. It might require a restart of the program for it to show up.

---
### Presets
Any saved preset will be found in the data/presets folder and can be transferred between two installations of the program. Simply move a copy of the preset's JSON file to the other program's data/presets folder. You will need to restart the program to see the new presets after moving them into the folder.

---
### Compile the program
If you want to compile the program yourself into an .exe, use the following command: ```pyinstaller --name "Speedyspot" --onefile --icon "icon.ico" --noconsole --add-data=icon.ico:. main.py``` then look in the dist folder. For more documentation, look at the documentation for PyInstaller itself: https://pyinstaller.org/
