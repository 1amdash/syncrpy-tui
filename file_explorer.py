"""file_explorer module"""
import curses
import os
from ssh import SSH
from Func_human_readable_size import human_readable_size
from window_manager import WinManager
from pop_ups import PopUpFileOpener
from pop_ups import PopUpCopyFile

class ResetPath:
    """Used to reset the path to '/' when FileExplorer messses up"""
    def __init__(self):
        self.errors = 0
    def error(self):
        self.errors += 1
        if self.errors == 2:
            if win_manager.active_panel == 0:
                left_file_explorer.path = '/'
                self.errors = 0
            elif win_manager.active_panel == 1:
                right_file_explorer.path = '/'
                self.errors = 0

class FileExplorer:
    """Work horse of the application

    Does the bulk of the work by taking a path and listing directorys/files within that 
    path. Also prints the list of directorys/files and is responsible for navigating
    through those files. The ssh_explorer method is meant to closely mirror the explorer
    method but is modified for paramiko where appropriate.
    """
    path = '/'
    paths = [None, None]
    prev_paths = ['/', '/']
    path_errors = ResetPath()
    def __init__(self, win_manager, window, path, ssh_object=None):
        self.ssh_obj = ssh_object
        
        self.win_manager = win_manager
        self.window = window
        self.screen_height, self.screen_width = self.win_manager.stdscr.getmaxyx()
        height, width = self.window.getmaxyx()
        start_y, start_x = self.window.getbegyx()
        self.p = 0
        self.height = height
        self.width = width - 2
        self.start_y = start_y + 1
        self.start_x = start_x + 1
        self.position = 0
        self.scroller = 0
        self.event = None
        self.selected_path = ''
        self.ssh_path = None
        self.ssh_path_hist = ['/']
        self.draw_pad()
        self.explorer(path)
        self.menu()

    def get_file_explorers(self, file_explorers):
        self.file_explorers = file_explorers
        self.left_file_explorer = file_explorers[0]
        self.right_file_explorer = file_explorers[1]

    def explorer(self, path):
        if isinstance(self.ssh_obj, SSH):
            if self.ssh_obj.is_enabled:
                if win_manager.active_panel == 1:
                    right_file_explorer.ssh_explorer(path)
                    return
        self.path = path
        self.abs_path = os.path.abspath(self.path)
        self.par_dir = os.path.dirname(self.abs_path).replace('//','/')
        try:      
            self.files_folders = os.listdir(self.abs_path)
        except PermissionError:
            self.abs_path = '/'
            self.files_folders = os.listdir(self.abs_path)
            self.path_errors.error()
        data_list = []
        for item in self.files_folders:
            is_dir = os.path.isdir(self.abs_path + '/' + item)
            try:
                size = os.path.getsize(self.abs_path + '/' + item)
            except:
                size = 0
            size = human_readable_size(size, suffix="B")
            if is_dir:
                prefix = '/'
            else:
                prefix = ''
            data_list.append([prefix+item, size])
        #sort list based on file names
        data_list = sorted(data_list, key=lambda x:x[:1])
        #insert an index
        i = 1
        for item in data_list:
            item.insert(0,i)
            i = i + 1
        #turn data list into a dictionary
        item = 0
        self.data = dict()
        self.data = {x[0]: x[1:] for x in data_list}
        if self.abs_path == '/':
            self.data[0] = ['/','']
        else:
            self.data[0] = ['..','']

    def ssh_path_hist_func(self, ssh_path):
        #since paramiko doesnt produce an absolute path, this creates a path
        #history by appending and pop'ing an array as you move through the file
        #structure
        if ssh_path == '/':
            self.par_dir = '/'
            self.ssh_path = ssh_path
            self.ssh_path_par_hist = ['/']
            self.ssh_path_hist = ['/']
            self.p = 0
        elif ssh_path.startswith('/'):
            self.ssh_path = ssh_path.lstrip('.')
            self.ssh_path_hist.append(ssh_path)
            self.p +=1
            self.ssh_path_par_hist = list(self.ssh_path_hist)
            self.ssh_path_par_hist.pop()
            self.par_dir = ''.join(map(str, self.ssh_path_par_hist))

        elif ssh_path.startswith('.') and len(self.ssh_path_hist) > 1:

            self.ssh_path_hist.pop(self.p)
            self.p -=1
        else:
            self.par_dir = '/'
            if len(self.ssh_path_par_hist) != 1:
                self.ssh_path_par_hist.pop()
                self.par_dir = ''.join(map(str, self.ssh_path_par_hist))

        self.next_ssh_path = ''.join(map(str, self.ssh_path_hist))

    def ssh_explorer_attr(self):
        if glbl_opts.low_bandwidth:
            size = 0
        else:
            self.ssh_files_folders_attr = ssh_obj.sftp.listdir_attr(
                path=self.next_ssh_path)
            size_list = []
            for entry in self.ssh_files_folders_attr:
                size = entry.st_size
        return size_list

    def ssh_get_abs_path(self, path):
        self.ssh_abs_path = ssh_obj.sftp.normalize(path) 

    def ssh_explorer(self, ssh_path):
        self.ssh_path_hist_func(ssh_path)
        self.ssh_files_folders_dir = ssh_obj.sftp.listdir(
                path=self.next_ssh_path
                )
        self.ssh_files_folders_attr = ssh_obj.sftp.listdir_attr(
                path=self.next_ssh_path
                )
        self.ssh_get_abs_path(self.next_ssh_path)
        item = 0
        data_list = []
        for file_name, attr in zip(self.ssh_files_folders_dir, self.ssh_files_folders_attr):
            is_dir = stat.S_ISDIR(attr.st_mode)
            s = attr.st_size
            if is_dir:
                is_dir = '/'
            else:
                is_dir = ''
            data_list.append([is_dir+file_name, s])
            item += 1
        #sort list based on file names
        data_list = sorted(data_list, key=lambda x:x[:1])
        #insert an index and use the size function to make size human readable
        count = 0
        for item in data_list:
            count += 1
            item.insert(0,count)
            s = human_readable_size(item[2], suffix="B")
            item[2]=s
        #turn data list into a dictionary
        x = 0
        self.data = dict()
        self.data = {x[0]: x[1:] for x in data_list}
        if self.abs_path == '/':
            self.data[0] = ['/','']
        else:
            self.data[0] = ['..','']

    def draw_pad(self):
        self.pad = curses.newpad(self.height + 800, self.width) #size of pad
        self.pad.scrollok(True)
        self.pad.idlok(True)
        self.pad.keypad(True)
        self.pad.bkgd(curses.color_pair(1))

    def start_rsync(self):
        file_name = self.data[self.position][0]
        left_panel_path = left_file_explorer.abs_path
        right_panel_path = right_file_explorer.ssh_abs_path
        if self.win_manager.active_panel == 0:
            self.from_file = left_panel_path + '/' + file_name
            self.to_path = right_panel_path
        elif self.win_manager.active_panel == 1:
            self.from_file =  right_panel_path + '/' + file_name
            self.to_path = left_panel_path
        if self.position != 0:
            rsync_obj = RSync(0).start(self.from_file, self.to_path, file_name)

    def menu(self):
        self.pad.erase()
        self.height, self.width = self.window.getmaxyx()
        self.screen_height, self.screen_width = self.win_manager.stdscr.getmaxyx()

        self.max_height = self.height -2
        self.bottom = self.max_height #+ len(self.tup) #self.max_height
        self.scroll_line = self.max_height - 3
        self.pad.setscrreg(0,self.max_height) #self.bottom -2)
        self.width = self.width - 2
        self.pad_refresh = lambda: self.pad.noutrefresh(
            self.scroller,
            0,
            self.start_y,
            self.start_x,
            self.bottom,
            self.screen_width - 2
            )
        #par = '[ ]' # can be added to the msg below to create a selector, likely to be removed
        for index, items in self.data.items():
            padding = self.width - len(items[0]) - 5
            if index == self.position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL
            try:
                msg = f'{index:>3}{" "}{items[0]}{items[1]:>{padding}}'
            except:
                msg = f'{index:>3}{" "}{items[0]}'
            self.pad.addstr(index, 0, str(msg), mode)
            if mode == curses.A_REVERSE:
                self.cursor = self.pad.getyx()[0]
        self.pad_refresh()

    def set_paths(self):
        panel = WinManager.active_panel
        if panel == 0:
            oth_panel = 1
        else:
            oth_panel = 0
        if self.new_path == None:
            self.paths[panel] = self.prev_paths[panel].replace('//','/')
        else:
            self.prev_paths[panel] = self.paths[panel]
            self.paths[oth_panel] = self.prev_paths[oth_panel]
    
    def go_to_top(self):
        self.position = 0
        self.scroller = 0

    def go_to_bottom(self):
        data_length = len(self.data)
        self.position = data_length - 1
        self.scroller = data_length - self.scroll_line - 1
    
    def del_selected_items(self, sel_file):
        PopUpDelete(sel_file)

    def copy_selected_items(self):
        #if ssh_obj != None:
         #   if ssh_obj.is_enabled:

          #      self._exp.start_rsync()
           # else:
        file_name = self.data[self.position][0]
        if self.win_manager.active_panel == 0:
            self.from_file = self.path + '/' + file_name
            self.to_path = self.right_file_explorer.path
        elif self.win_manager.active_panel == 1:
            self.from_file = self.path + '/' + file_name
            self.to_path = self.left_file_explorer.path
        if self.position != 0:
            PopUpCopyFile(
                self.file_explorers,
                self.win_manager.stdscr,
                self.from_file,
                self.to_path,
                file_name
                )

    def scroll(self):
        if self.cursor > self.scroll_line:
            self.data_length = len(self.data) - 1
            if self.position != self.data_length:
                self.scroller = self.position - self.scroll_line
        if self.scroller == -1:
            self.scroller = 0
        if self.position == 0:
            self.scroller = 0

    def get_path(self):
        return self.data[self.position][0]

    def is_dir(self, path):
        if path.startswith('/'):
            forward_slash = '/'
            self.full_path = path + forward_slash
            return True
        else:
            return False

    def enter(self):
        """Changes the directory or opens file when called,"""
        path = self.get_path()
        is_dir = self.is_dir(path)
        if self.position != 0 and is_dir:
            if WinManager.active_panel == 1:
                if self.ssh_obj.is_enabled:
                    if self.ssh_obj.is_enabled and self.win_manager.active_panel == 1:
                        self.new_path =  self.path
            else:
                self.new_path = self.path + self.full_path
            self.cwd = self.new_path
            #self.selected_path = self.path + self.data[self.position][0] + '/'
            self.pad_refresh()
            self.position = self.scroller = 0
            self.paths[self.win_manager.active_panel] = self.new_path.replace('//','/')
            self.set_paths()
            self.explorer(self.new_path)
        elif self.position != 0 and is_dir is not True:
            sel_file = self.path + '/' + path
            PopUpFileOpener(self.file_explorers, self.win_manager.stdscr, sel_file)
        else:
            self.cwd = self.new_path = self.par_dir
            if self.ssh_obj:
                    if self.ssh_obj.is_enabled and self.win_manager.active_panel == 1:
                        self.par_dir = '..'
            self.set_paths()
            self.explorer(self.par_dir)
        self.win_manager.upd_panel(self.win_manager.active_panel, self.path)
