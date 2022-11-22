"""FileExplorer Class and ResetPath Class"""
import curses
import os
import stat
from pathlib import Path

from ssh import SSH
from human_readable_size import human_readable_size
from window_manager import WinManager
from pop_ups import PopUpFileOpener
from pop_ups import PopUpCopyFile
from pop_ups import PopUpDelete

class ResetPath:
    """Used to reset the path to '/' when FileExplorer messses up"""
    def __init__(self):
        self.errors = 0

    def error(self, obj):
        self.obj = obj
        self.errors += 1
        if self.errors == 2:
            self.obj.path = '/'
            self.errors = 0


class FileExplorer:
    """Work horse of the application

    Does the bulk of the work by taking a path and listing directorys/files within that
    path. Also prints the list of directorys/files and is responsible for navigating
    through those files. The ssh_explorer method is meant to closely mirror the explorer
    method but is modified for paramiko where appropriate.
    """
    paths = [None, None]
    prev_paths = ['/', '/']
    path_errors = ResetPath()
    def __init__(self, win_manager, window, ssh_object=None):
        self.home = self.get_home_path()
        self.path_parts = self.home._parts
        self.path_depth = len(self.path_parts)
        self.full_path = self.join_path(self.path_parts)

        self.ssh_obj = ssh_object
        self.win_manager = win_manager
        self.window = window
        self.screen_height, self.screen_width = self.win_manager.stdscr.getmaxyx()
        height, width = self.window.getmaxyx()
        start_y, start_x = self.window.getbegyx()
        self.ssh_path_depth = 0
        self.depth = 0
        self.height = height
        self.width = width - 2
        self.start_y = start_y + 1
        self.start_x = start_x + 1
        self.position = 0
        self.scroller = 0
        self.event = None
        self.ssh_path = None
        self.ssh_path_hist = ['/']
        self.path_info = list()

        self.draw_pad()
        self.explorer(self.full_path)
        self.menu()

    def get_home_path(self):
        return Path().home()

    def explorer(self, path):
        self.path = path
        if isinstance(self.ssh_obj, SSH):
            if self.ssh_obj.is_enabled:
                self.use_ssh_explorer(path)
                return
        path_obj = self.obj_or_str(path)
        data_list = self.walk_tree(path_obj)
        data_list = self.file_dir_iter(path_obj, data_list)
        data_list = self.sort_file_list(data_list)
        data_list = self.create_list_index(data_list)
        data_dict = self.list_to_dict(data_list)
        self.data = self.root_or_dot_dot(path_obj, data_dict)

    def join_path(self, path_parts=None):
        path = '/'.join(map(str, self.path_parts))
        self.full_path = path.replace('//','/')
        return self.full_path

    def obj_or_str(self, path):
        if isinstance(path, str):
            return Path(path)
        else:
            return path

    def go_up_level(self, path):
        if path == ('..'):
            self.path_parts.pop()
            self.path_depth -= 1

    def go_down_level(self, path):
        if path.startswith('/') and len(path) > 1:
            path = path.replace('/','')
            self.path_parts.append(path)
            self.path_depth += 1

    def file_dir_iter(self, path_obj, files_dirs):
        """parse files, identify if file is dir, get size

        Requires list object"""
        data_list = list()
        for item in files_dirs:
            _full_path = Path(path_obj, item)
            is_dir = Path.is_dir(_full_path)
            size = Path(_full_path).stat().st_size
            size = human_readable_size(size, suffix="B")
            if is_dir:
                item = '/' + item
                item = item.strip()
            else:
                item 
            data_list.append([item, size])
        return data_list

    def create_list_index(self, data_list):
        """add index to list

        Requires list object"""
        i = 1
        for item in data_list:
            item.insert(0,i)
            i = i + 1
        return data_list

    def use_ssh_explorer(self, path):
        if self.win_manager.active_panel == 1:
            self.right_file_explorer.ssh_explorer(path)

    def walk_tree(self, path):
        """get files and folders from directory"""
        file_dir_list = list()
        for file_obj in path.iterdir():
            file_dir_list.append(file_obj.name)
        return file_dir_list

    def sort_file_list(self, data_list):
        """sort the list of files and folder

        Requires list object"""
        data_list = sorted(data_list, key=lambda x:x[:1])
        return data_list

    def get_file_explorers(self, file_explorers):
        '''imports file explorers'''
        self.file_explorers = file_explorers
        self.left_file_explorer = file_explorers[0]
        self.right_file_explorer = file_explorers[1]

    def list_to_dict(self, data_list):
        """convert list to dictionary"""
        item = 0
        data_dict = dict()
        data_dict = {item[0]: item[1:] for item in data_list}
        return data_dict

    def root_or_dot_dot(self, path_obj, data):
        """determine if parent dir exists"""
        if len(path_obj.parts) > 1:
            data[0] = ['..','']
        else:
            data[0] = ['/','']
        return data

    def join_path_str(self, path_1, path_2):
        path = path_1 + '/' + path_2
        return path

    def set_paths(self, path):
        panel = WinManager.active_panel
        if panel == 0:
            oth_panel = 1
        else:
            oth_panel = 0
        if path is None:
            self.paths[panel] = self.prev_paths[panel].replace('//','/')
        else:
            self.prev_paths[panel] = self.paths[panel]
            self.paths[oth_panel] = self.prev_paths[oth_panel]

    def ssh_explorer(self, ssh_path):
        self.next_ssh_path = self.get_full_path(ssh_path)
        ssh_files_folders_dir = self.ssh_obj.sftp.listdir(self.next_ssh_path)
        ssh_files_folders_attr = self.ssh_obj.sftp.listdir_attr(self.next_ssh_path)
        self.ssh_get_abs_path(self.next_ssh_path)
        data_list = self.ssh_parse_files(ssh_files_folders_dir, ssh_files_folders_attr)
        data_list = self.sort_file_list(data_list)
        data_list = self.create_list_index(data_list)
        self.data = self.list_to_dict(data_list)
        self.data = self.root_or_dot_dot(self.next_ssh_path, self.data)

    def ssh_parse_files(self, files_folders_dir, files_folders_attr):
        data_list = list()
        #item = 0
        for file_name, attr in zip(files_folders_dir, files_folders_attr):
            #is_dir = Path.is_dir()
            is_dir = stat.S_ISDIR(attr.st_mode)
            size = attr.st_size
            size = human_readable_size(size, suffix="B")
            if is_dir:
                is_dir = '/'
            else:
                is_dir = ''
            data_list.append([is_dir+file_name, size])
            #item += 1
        return data_list

    def enter(self):
        """Changes the directory or opens file when enter key is called

        Expects full path string"""
        first_position = 0
        _selected_path = self.get_file_name()
        if self.position is first_position:
            self.enter_select_up_level(_selected_path)
        else:
            self.enter_select_folder_file(_selected_path)
        self.win_manager.upd_panel(self.win_manager.active_panel, self.full_path)

    def enter_select_up_level(self, _selected_path):
        if self.ssh_obj:
            if self.ssh_obj.is_enabled and self.win_manager.active_panel == 1:
                self.par_dir = '..'
        self.go_up_level(_selected_path)
        _full_path = self.join_path()
        self.set_paths(_full_path)
        self.explorer(_full_path)

    def enter_select_folder_file(self, _selected_path):
        is_dir = _selected_path.startswith('/')
        _path_to_open = self.join_path_str(self.full_path,_selected_path)
        if is_dir:
            if WinManager.active_panel == 1:
                if self.ssh_obj.is_enabled:
                    self.new_path =  self.path
            #self.pad_refresh()
            self.position = self.scroller = 0
            #self.paths[self.win_manager.active_panel] = _path_to_open
            self.go_down_level(_selected_path)
            _full_path = self.join_path()
            self.set_paths(_path_to_open)
            self.explorer(_path_to_open)
        else:
            PopUpFileOpener(self.file_explorers, self.win_manager.stdscr, _path_to_open)

    def ssh_explorer_attr(self):
        if glbl_opts.low_bandwidth:
            size = 0
        else:
            self.ssh_files_folders_attr = self.ssh_obj.sftp.listdir_attr(
                path=self.next_ssh_path)
            size_list = []
            for entry in self.ssh_files_folders_attr:
                size = entry.st_size
        return size_list

    def ssh_get_abs_path(self, path):
        self.ssh_abs_path = self.ssh_obj.sftp.normalize(path)

    def draw_pad(self):
        '''draws pad larger than the file window so that it is scrollable'''
        self.pad = curses.newpad(self.height + 800, self.width) #size of pad
        self.pad.scrollok(True)
        self.pad.idlok(True)
        self.pad.keypad(True)
        self.pad.bkgd(curses.color_pair(1))

    def menu(self):
        '''creates selectable list of items, files, folders'''
        self.pad.erase()
        self.height, self.width = self.window.getmaxyx()
        self.screen_height, self.screen_width = self.win_manager.stdscr.getmaxyx()
        self.max_height = self.height -2
        self.bottom = self.max_height
        self.scroll_line = self.max_height - 3
        self.pad.setscrreg(0,self.max_height)
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
            msg = f'{index:>3}{" "}{items[0]}{items[1]:>{padding}}'
            self.pad.addstr(index, 0, str(msg), mode)
            if mode == curses.A_REVERSE:
                self.cursor = self.pad.getyx()[0]
        self.pad_refresh()

    def go_to_top(self):
        self.position = 0
        self.scroller = 0

    def go_to_bottom(self):
        data_length = len(self.data)
        self.position = data_length - 1
        self.scroller = data_length - self.scroll_line - 1

    def del_selected_items(self, sel_file):
        PopUpDelete(self, sel_file)

    def copy_selected_items(self):
        file_name = self.get_file_name()
        if self.position != 0:
            if self.win_manager.active_panel == 0:
                #self.from_file = self.path + '/' + file_name
                self.from_file = self.left_file_explorer.full_path + '/' + file_name
                self.to_path = self.right_file_explorer.full_path
            elif self.win_manager.active_panel == 1:
                self.from_file = self.right_file_explorer.full_path + '/' + file_name

                self.to_path = self.left_file_explorer.full_path
            PopUpCopyFile(
                self.file_explorers,
                self.win_manager.stdscr,
                self.from_file,
                self.to_path,
                file_name
                )

    def start_rsync(self):
        file_name = self.data[self.position][0]
        left_panel_path = self.left_file_explorer.abs_path
        right_panel_path = self.right_file_explorer.ssh_abs_path
        if self.win_manager.active_panel == 0:
            self.from_file = left_panel_path + '/' + file_name
            self.to_path = right_panel_path
        elif self.win_manager.active_panel == 1:
            self.from_file =  right_panel_path + '/' + file_name
            self.to_path = left_panel_path
        if self.position != 0:
            rsync_obj = RSync(0).start(self.from_file, self.to_path, file_name)

    def scroll(self):
        if self.cursor > self.scroll_line:
            self.data_length = len(self.data) - 1
            if self.position != self.data_length:
                self.scroller = self.position - self.scroll_line
        if self.scroller == -1:
            self.scroller = 0
        if self.position == 0:
            self.scroller = 0

    def get_file_name(self):
        return self.data[self.position][0]

    def is_dir(self, path):
        if path.startswith('/'):
            self.full_path = os.path.join(path, '')
            return True
        return False
