"""CopyFile Class"""
import shutil


class CopyFile:
    """Actual file copy function called when SSH not active and key 5 pressed"""
    def __init__(self, *args):
        source_path, destination_path = args
        #length = len(source_path) + len(destination_path) + 13
        try:
            shutil.copy(source_path, destination_path)
            self.action = 0
        except Exception as error:
            self.error = error
            