from PIL import Image, ImageCms
import numpy as np

def getScales() -> tuple:
    # Constants for scaling, these can be adjusted based on the desired output range
    rgbScale = 255.0
    cmykScale = 255.0
    return rgbScale, cmykScale

class ColorConverter():
    def rgbToCmykArray(self, r: np.ndarray, g: np.ndarray, b: np.ndarray) -> tuple:
        rgbScale, cmykScale = getScales()
    
        # Normalize RGB
        r = np.array(r).astype(np.float32) / rgbScale
        g = np.array(g).astype(np.float32) / rgbScale
        b = np.array(b).astype(np.float32) / rgbScale
    
        # CMY intialization
        c = 1.0 - r
        m = 1.0 - g
        y = 1.0 - b
    
        k = np.minimum.reduce([c, m, y])
        # Avoid division by zero
        mask = k < 1.0
        # Normalize CMY values
        # Only apply normalization where k < 1 to avoid division by zero
        c[mask] = (c[mask] - k[mask]) / (1 - k[mask])
        m[mask] = (m[mask] - k[mask]) / (1 - k[mask])
        y[mask] = (y[mask] - k[mask]) / (1 - k[mask])
    
        c[~mask] = 0
        m[~mask] = 0
        y[~mask] = 0
    
        return (
            (c * cmykScale).astype(np.uint8),
            (m * cmykScale).astype(np.uint8),
            (y * cmykScale).astype(np.uint8),
            (k * cmykScale).astype(np.uint8)
        )
    
    def cmykToRgbArray(self, c: np.ndarray, m: np.ndarray, y: np.ndarray, k: np.ndarray) -> tuple:
        # Convert CMYK (0-255) to RGB (0-255)
        rgbScale, cmykScale = getScales()
        c = np.array(c).astype(np.float32) / cmykScale
        m = np.array(m).astype(np.float32) / cmykScale
        y = np.array(y).astype(np.float32) / cmykScale
        k = np.array(k).astype(np.float32) / cmykScale
    
        r = (1.0 - np.minimum(1.0, c * (1.0 - k) + k))
        g = (1.0 - np.minimum(1.0, m * (1.0 - k) + k))
        b = (1.0 - np.minimum(1.0, y * (1.0 - k) + k))
    
        return (
            (r * rgbScale).astype(np.uint8),
            (g * rgbScale).astype(np.uint8),
            (b * rgbScale).astype(np.uint8)
        )

class IccColorConverter(ColorConverter):
    def __init__(self, iccPath):
        super()
        self.iccPath = iccPath
        
    def getprofiles(self, image: Image) -> tuple:
        rgb_profile = ImageCms.createProfile("sRGB")
        if ("icc_profile" in image.info):
            rgb_profile = ImageCms.ImageCmsProfile(
                ImageCms.getOpenProfile(image.info["icc_profile"])
            )
                
        cmyk_profile = ImageCms.getOpenProfile(self.iccPath)
        
        return rgb_profile, cmyk_profile
                
    
    def cmykToRgbArray(self, c: np.ndarray, m: np.ndarray, y: np.ndarray, k: np.ndarray) -> tuple:
        cmyk = np.stack([
            np.asarray(c),
            np.asarray(m),
            np.asarray(y),
            np.asarray(k)
        ], axis=-1)

        
        image = Image.fromarray(cmyk, mode="CMYK")
        
        dst_profile, src_profile = self.getprofiles(image)
        
        rgb = ImageCms.profileToProfile(
            image,
            src_profile,
            dst_profile,
            outputMode="RGB",
        )
        
        r, g, b = rgb.split()
        return (
            np.array(r).astype(np.uint8), 
            np.array(g).astype(np.uint8), 
            np.array(b).astype(np.uint8)
        )
    
    def rgbToCmykArray(self, r: np.ndarray, g: np.ndarray, b: np.ndarray) -> tuple:
        rgb = np.stack([
            np.asarray(r),
            np.asarray(g),
            np.asarray(b)
        ], axis=-1)

        image = Image.fromarray(rgb.astype(np.uint8), mode="RGB")
        
        src_profile, dst_profile = self.getprofiles(image)
        
        cmykImg = ImageCms.profileToProfile(
            image,
            src_profile,
            dst_profile,
            outputMode="CMYK",
        )
        
        c, m, y, k = cmykImg.split()
        return (
            np.array(c).astype(np.uint8), 
            np.array(m).astype(np.uint8), 
            np.array(y).astype(np.uint8), 
            np.array(k).astype(np.uint8)
        )

def getColorConverter(perhapsIcc: str) -> ColorConverter:
    if perhapsIcc:
        return IccColorConverter(perhapsIcc)
    return ColorConverter()