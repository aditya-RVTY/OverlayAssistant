import mss
import mss.tools
from PIL import Image

def capture_screen():
    """Captures the screenshot of the first monitor."""
    with mss.mss() as sct:
        # Get the first monitor (which is usually the combined one or primary)
        monitor = sct.monitors[1] # 1 is the primary monitor, 0 is all monitors combined
        
        # Grab the data
        sct_img = sct.grab(monitor)
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        return img
