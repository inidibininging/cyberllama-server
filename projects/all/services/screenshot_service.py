import pyautogui
import base64
from PIL import Image
from io import BytesIO
# needs api for getting window titles. OS dependent I'd guess
# CYBERPUNK_WINDOW_TITLE='Cyberpunk 2077 (C) 2020 by CD Projekt RED'


class ScreenshotService:
    def __init__(self):
        pass        
    
    def jpeg_to_base64(self, pil_image):
        buffered = BytesIO()
        pil_image.save(buffered, format="JPEG") 
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def take_screenshot(self, screenshot_path):
        try:
            image = pyautogui.screenshot(screenshot_path)
            print(f"Screenshot saved at: {screenshot_path}")

        except Exception as e:
            print(f"An error occurred: {e}")

