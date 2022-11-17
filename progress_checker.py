import os
from human_readable_size import human_readable_size

class ProgressChecker:
    """Used to created a progress bar.
    
    Used to check the current size of the source and destination files while the file
    copy runs in the background. This helps to create the appearance of a progress bar.
    """
    def __init__(self, source_path, destination_path, file_name, t, callback):
        self.callback = callback
        self.t = t
        self.full_destination_path = destination_path + '/' + file_name
        while not os.path.exists(self.full_destination_path):
            callback(t)
            break
        self.src_num = os.path.getsize(source_path)
        self.src_size = human_readable_size(self.src_num)
        self.des_num = 0
        self.des_size = 0
        # Keep checking the file size till it's the same as source file, will fail initially because file does not exist
        try: 
            self.des_num = os.path.getsize(self.full_destination_path)
            self.des_size = human_readable_size(self.des_num)
        except FileNotFoundError:
            pass
        if self.des_num == self.src_num:
            callback(t)
            self.complete = 0
            
    def status(self):
        if self.des_num != self.src_num:
            self.des_num = int(float(os.path.getsize(self.full_destination_path)))
            self.des_size = human_readable_size(self.des_num)
        else:
            self.callback(self.t)
            self.complete = 0