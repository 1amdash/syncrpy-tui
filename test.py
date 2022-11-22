from pathlib import Path


class pathandstuff:
    def __init__(self, path='/'):
        self.main(path)
        self.path_depth = 0




    def main(self, path):
        path_obj = self.obj_or_str(path)
        self.get_path_depth(path)
        #self.set_full_path(path_obj, path)
        #path_obj = Path(path)
        
        # / turn into path object
        # .. get path from list
        # /path turn to path objct and append

        #_full_path = self.get_full_path(path)               #create full path
        file_dir_list = self.walk_tree(path_obj)            #get files and folders from directory
        data_list = self.file_dir_iter(file_dir_list)       #parse files, identify if file is dir, get size
        data_list = self.sort_file_list(data_list)          #sort the list of files and folder
        data_list = self.create_list_index(data_list)       #add index
        data = self.list_to_dict(data_list)                 #convert list to index
        self.data = self.root_or_dot_dot(path_obj, data)  #determine if parent dir exists



    def get_path_depth(self, path):
        if self.path_depth <= 2:
            if path.startswith('/'):

                if len(path) > 1:
                    self.path_parts.append(path)
                    self.depth += 1
                else:
                    self.path_parts = [path]
            elif path == ('..'):
                if self.depth != 0:
                    
                    self.path_parts.pop()
                    self.depth -= 1

            self.full_path = self.join_path(self.path_parts)

            #else:
            #   self.path_info.append(path)
            #  self.depth += 1

    def join_path(self, path_parts):
        path = '/'.join(map(str, path_parts))
        return path.replace('//','/')

    def obj_or_str(self, path):
        if type(path) is str:
            return Path(path)
        else:
            return path

    def get_parent_path(self, path_obj):
        return path_obj.parent

    def path_up_or_down(self, path):
        root = '/'
        up_level = '..'
        if path is root:
            return Path(root)
        elif path is up_level:
            return self.parent_path
        else:
            return Path(path)

    def get_full_path_new(self, path_obj):
        self.parent = path_obj.parent
        self.path_obj_full_path = path_obj.parent / path_obj.stem
        self.full_path = self.path_obj_full_path._str

    def get_full_path(self, path):
        #self.depth_test = len(path.parts)
        if path == '/':
            self.path_info.append('/')
            self.depth = 0
        elif path == ('..'):
            if self.depth != 0:
                
                self.path_info.pop()
                self.depth -= 1
        else:
            self.path_info.append(path)
            self.depth += 1
        self.full_path = ''.join(map(str, self.path_info))
        return self.full_path.replace('//','/')


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

    def file_dir_iter(self, files_dirs):
        """Requires list object"""
        data_list = list()
        for item in files_dirs:
            #_full_path = os.path.join(self.full_path, item)
            _full_path = Path(self.full_path, item)
            #is_dir = os.path.isdir(_full_path)
            is_dir = Path.is_dir(_full_path)
            size = os.path.getsize(_full_path)
            #size = Path.stat().st_size
            size = human_readable_size(size, suffix="B")
            if is_dir:
                #item = os.path.join(' ',item)
                item = '/' + item
                item = item.strip()
                # item = os.path.normpath(item).strip()
            else:
                item 
            data_list.append([item, size])
        return data_list

    def create_list_index(self, list):
        """Requires list object"""
        i = 1
        for item in list:
            item.insert(0,i)
            i = i + 1
        return list

    def use_ssh_explorer(self, path):
        if self.win_manager.active_panel == 1:
            self.right_file_explorer.ssh_explorer(path)

    def walk_tree(self, path):
        file_dir_list = list()
        for file_obj in path.iterdir():
            file_dir_list.append(file_obj.name)
        return file_dir_list

    def sort_file_list(self, list):
        """Requires list object"""
        data_list = sorted(list, key=lambda x:x[:1])
        return data_list

    def get_file_explorers(self, file_explorers):
        '''imports file explorers'''
        self.file_explorers = file_explorers
        self.left_file_explorer = file_explorers[0]
        self.right_file_explorer = file_explorers[1]

    def clean_path(self, path):
        return path.replace('//','/')

    def list_to_dict(self, data_list):
        item = 0
        data_dict = dict()
        data_dict = {item[0]: item[1:] for item in data_list}
        return data_dict

    def root_or_dot_dot(self, path_obj, data):
        if len(path_obj.parts) > 1:
        #if path == '/':
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

    def enter(self):
        """Changes the directory or opens file when enter key is called
        
        
        Expects full path string"""
        _selected_path = self.get_file_name()
        is_dir = _selected_path.startswith('/')

        if self.position != 0:
            _path_to_open = self.join_path_str(self.full_path,_selected_path)
            if is_dir:
                if WinManager.active_panel == 1:
                    if self.ssh_obj.is_enabled:
                        self.new_path =  self.path                    
                self.pad_refresh()
                self.position = self.scroller = 0
                self.paths[self.win_manager.active_panel] = _path_to_open
                self.set_paths(_path_to_open)
                self.explorer(_path_to_open)
            else:
                PopUpFileOpener(self.file_explorers, self.win_manager.stdscr, _path_to_open)
        else:
            path_parent = Path(self.full_path).parent

            if self.ssh_obj:
                    if self.ssh_obj.is_enabled and self.win_manager.active_panel == 1:
                        self.par_dir = '..'
            self.set_paths(self.full_path)
            self.explorer(_selected_path)

        self.win_manager.upd_panel(self.win_manager.active_panel, self.full_path)


pands = pathandstuff('/')