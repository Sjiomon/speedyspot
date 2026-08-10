import os
import time
import PIL
import numpy as np
import tifffile
from handleEPS import HandleEPS
from colorConverter import ColorConverter

# EPS "flag" and the temp filename
usedEPS = False
epsOutputName = None

def getType(src: str) -> list:
    global usedEPS
    global epsOutputName
    
    # Determine the type of image based on its file extension and properties
    # Is it a tiff or png? And is it RGB or CMYK?
    ext = src.split(".")[-1].lower()
    if ext == "tif" or ext == "tiff":
        with tifffile.TiffFile(src) as tif:
            photometric = tif.pages[0].photometric
            # Determine the color space of the TIFF image
            imgInfo = ["Unknown", "tiff"]
            if photometric == 2:
                imgInfo[0] = "RGB"
            elif photometric == 5:
                imgInfo[0] = "CMYK"
            return imgInfo
            
    elif ext == "png":
        img = PIL.Image.open(src)
        mode = img.mode
        
        # Check if image has transparency in any form
        hasTransparency = (
            mode in ("RGBA", "LA", "PA") or 
            (mode == "P" and "transparency" in img.info) or
            (mode in ("RGB", "L") and "transparency" in img.info)
        )
        
        img.close()
        
        # Determine the color space of the PNG image
        imgInfo = ["Unknown", "png", hasTransparency]  # Add transparency flag
        if mode in ("RGBA", "RGB", "LA", "L", "P"):
            imgInfo[0] = "RGB"
        elif mode == "CMYK":
            imgInfo[0] = "CMYK"
        
        return imgInfo
    
    elif ext == "eps":
        eps = HandleEPS(src)
        eps.open()
        while (not eps.isClosed()):
            time.sleep(1)
        if (eps.convertNotFailed()):
            # Set usedEPS "flag"
            usedEPS = True
            # remeber temp path for eps convertion
            epsOutputName = eps.getOutputFilename()
            imgInfo = getType(os.path.abspath(eps.getOutputFilename()))
            return imgInfo
        else:
            raise ValueError("EPS convertion failed")

def splitImageToCmyk(src: str, converter: ColorConverter) -> tuple:
    global usedEPS
    global epsOutputName
    # Make sure to reset usedEPS "flag"
    usedEPS = False
    epsOutputName = None
    # Create a CMYK image from an RGB or CMYK source image, using information from the function getType
    imgInfo = getType(src) # Get image type and color space (RGB or CMYK)
    c, m, y, k, alphaChannel = 0,0,0,0,0 # Initialize variables
    if imgInfo[1]== "tiff":
        # Read the TIFF image using tifffile
        imgSrc = tifffile.imread(src)  # shape (H,W,4)
        if imgInfo[0] == "RGB":
            c,m,y,k = converter.rgbToCmykArray(imgSrc[..., 0], imgSrc[..., 1], imgSrc[..., 2])
            alphaChannel = imgSrc[..., 3].astype(np.uint8)
        elif imgInfo[0] == "CMYK":
            c, m, y, k = imgSrc[..., 0], imgSrc[..., 1], imgSrc[..., 2], imgSrc[..., 3]
            alphaChannel = imgSrc[..., 4].astype(np.uint8)
        else:
            raise ValueError("Unknown image type")
        
    elif imgInfo[1] == "png":
        # If it has a temp path for .png
        if (usedEPS):
            src = epsOutputName
        # Read the PNG image using PIL
        imgSrc = PIL.Image.open(src)
        
        # Check if has transparency flag (3rd element in imgInfo)
        hasTransparency = len(imgInfo) > 2 and imgInfo[2]
        # Convert to RGBA if it has transparency to ensure alpha channel exists
        if hasTransparency:
            imgSrc = imgSrc.convert("RGBA")
        else:
            imgSrc = imgSrc.convert("RGB")
        # Check if the image is RGB or CMYK and convert if needed
        if imgInfo[0] == "RGB":
            c, m, y, k = converter.rgbToCmykArray(imgSrc.getchannel("R"), imgSrc.getchannel("G"), imgSrc.getchannel("B"))
            # Get alpha channel—guaranteed to exist if has transparency is True
            if hasTransparency:
                alphaChannel = np.array(imgSrc.getchannel("A"))
            else:
                alphaChannel = np.full(imgSrc.size[::-1], 255, dtype=np.uint8)
        
        elif imgInfo[0] == "CMYK":
            c, m, y, k = imgSrc.split()
            # Get alpha channel if it exists
            if hasTransparency:
                alphaChannel = np.array(imgSrc.getchannel("A"))
            else:
                # Create opaque (255) alpha channel
                alphaChannel = np.full(imgSrc.size[::-1], 255, dtype=np.uint8)
        else:
            raise ValueError("Unknown image type")
    return c, m, y, k, alphaChannel
    
