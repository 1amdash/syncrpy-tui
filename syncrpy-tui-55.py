import os, sys, time, curses, io, time, paramiko, shutil, threading, subprocess, shlex, tempfile
from curses import panel, textpad
from stat import S_ISDIR, S_ISREG
from getpass import getpass


class popUpBase:
    def __init__(self, nlines, ncols, begin_y, begin_x):
        self.par_win_size_y, self.par_win_size_x = stdscr.getmaxyx()
        self.y = int(int(self.par_win_size_y*.5)/2)
        self.x = int(int(self.par_win_size_x*.5)/2)
        self.h = int(self.par_win_size_y*.5)
        self.w = 25 # int(self.par_win_size_x*.5)
        self.win = curses.newwin(nlines, ncols, begin_y, begin_x)
       #self.win.keypad(1)
        self.win.attron(curses.color_pair(5))
        self.win.bkgd(curses.color_pair(5))
        self.win.border()
        self.win.noutrefresh()

    def msg(self, msg):
        self.win.addstr(1,1, msg, curses.color_pair(3))
        self.win.noutrefresh()

class optionsMenu(popUpBase):
    menu_items = ['[ ] low bandwidth']
    position = 0
    low_bandwidth = None
    def __init__(self):
        self.y, self.x = stdscr.getmaxyx()
        self.y = int(self.y/3)
        self.x = int (self.x/3)
        #self.menu()

    def menu(self):
        x_box = '[ ]'
        for index, item in enumerate(self.menu_items):
            if index == self.position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL
            msg = "%s" % (item)
            self.win.addstr(1 + index, 2, str(msg), mode)
        self.win.noutrefresh()
        curses.doupdate()

    def display(self):
        self.__init__()
        super().__init__(int(self.y), int(self.x), self.y, self.x)

        self.win.keypad(1)
        while True:
            self.menu()
            ### menuBar getch
            ch = self.win.getch()
            if(ch == curses.KEY_UP):
                self.navigate(-1)
                if self.position < 0:
                    self.position = 0
            elif(ch == curses.KEY_DOWN):
                if self.position >= 0 and self.position <= len(self.menu_items) - 1:
                    self.navigate(1)
            elif(ch == ord('\n')) and self.position == 0:
                if self.low_bandwidth == True:
                    self.menu_items = ['[ ] low bandwidth']
                    self.low_bandwidth = False
                    self.menu()
                    return 0

                self.menu_items = ['[x] low bandwidth']
                self.low_bandwidth = True
                self.menu()
                
            elif(ch == ord('\t')):
                self.win.erase()
                self.win.noutrefresh()
                curses.doupdate()
                return 0
                
    def navigate(self, n):
        self.position += n
        if self.position < 0:
            self.position = 0
        elif self.position >= len(self.menu_items):
            self.position = len(self.menu_items) - 1
class menuBar(popUpBase):
    position = 0
    sub_menu = ['ssh','rsync','exit']
    sub_menu2 = ['settings','test2','hello','fish']
    menuBarwindow = ''
    def __init__(self, stdscr):
        stdscr.addstr(0,1, 'File Options', curses.A_NORMAL)
        stdscr.noutrefresh()
    
    def menuBar_act(self, menu_event):

        if(menu_event == ord('f')):
            super().__init__(10, 15, 1, 1)
            #now using self.win from base
            stdscr.addstr(0,1, 'File', curses.A_STANDOUT)
            stdscr.addstr(0,4+2, 'Options', curses.A_NORMAL)
            stdscr.noutrefresh()
            self.menu_item = self.sub_menu

        elif(menu_event == ord('o')):
            super().__init__(10, 15, 1, 6)
            stdscr.addstr(0,1, 'File', curses.A_NORMAL)
            stdscr.addstr(0,4+2, 'Options', curses.A_STANDOUT)    
            stdscr.noutrefresh()
            self.menu_item = self.sub_menu2
        
    def menu(self):
        for index, item in enumerate(self.menu_item):
            if index == self.position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL
            msg = "%s" % (item)
            self.win.addstr(1+ index, 1, str(msg), mode)
        self.win.noutrefresh()
        curses.doupdate()

    def display(self):
        self.win.keypad(1)
        while True:
            self.menu()
            ### menuBar getch
            ch = self.win.getch()
            if(ch == curses.KEY_UP):
                self.navigate(-1)
                if self.position < 0:
                    self.position = 0
            elif(ch == curses.KEY_DOWN):
                if self.position >= 0 and self.position <= len(self.menu_item) - 1:
                    self.navigate(1)
            elif(ch == ord('\n')) and self.menu_item[self.position] == 'ssh':         
                if ssh_obj.enabled is False:
                    self.win.erase()
                    del self.win
                    reset_window(file_explorer_0)
                    ssh_obj.start()
                    return 0
            elif(ch == ord('\n')) and self.menu_item[self.position] == 'rsync':
                self.win.erase()
                del self.win
                reset_window(file_explorer_0)
                rsync('m')
                return 0
            elif(ch == ord('\n')) and self.menu_item[self.position] == 'settings':
                self.win.erase()
                del self.win
                reset_window(file_explorer_0)
                glbl_opts.display()
                return 0
            elif(ch == ord('\n')) and self.menu_item[self.position] == 'exit':
                ch = ord('q')
                return ch
            elif ch in (ord('f'), ord('o'), ord('\t'), ord('q')):    
                stdscr.addstr(0,1, 'File', curses.A_NORMAL)
                stdscr.addstr(0,4+2, 'Options', curses.A_NORMAL)    
                stdscr.noutrefresh()
                curses.doupdate()
                reset_window(file_explorer_0)
                return ch
                break
    def noutrefresh(self):
        stdscr.addstr(0,1, 'File Options', curses.A_NORMAL)
        stdscr.noutrefresh()
                
    
    def navigate(self, n):
        self.position += n
        if self.position < 0:
            self.position = 0
        elif self.position >= len(self.menu_item):
            self.position = len(self.menu_item) - 1

    def navigate_old(self, position, n, items):
        if position == 0:
            position += n
            if position < 0:
                position = 0
            return position
        elif (position > 0) and (position < len(items)):
            position += n
            if position == (len(items)):
                return position -1
            return position

class ssh:
    def __init__(self):
        self.enabled = False
        self.server_info = []
        self.ssh = ''
        self.sftp = None
        self.ssh_path = None
        #self.ssh_config = tempfile.TemporaryFile(mode='w+b')

    def ssh_config(self):
        ssh_config = 'HostName '+self.server_info[0]+\
                        '\nUser ~'\
        '\nControlMaster auto'\
        '\nControlPath ~/.ssh/%C'          
        self.ssh_config = paramiko.config.SSHConfig.from_text(ssh_config)


    def start(self):
        server_info = []
        form = text_box_form()
        self.server_info = form.ssh_form(('IP','U','P'))
        ssh_ip = self.server_info[0] #'localhost' #
        #self.server_info.append('localhost')
        ssh_user = self.server_info[1]#'apollo'#
        #ssh_pass = self.server_info[2]
        self.ssh = paramiko.SSHClient()
       # self.ssh_config()
        self.ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy())
        x = 1

        with ssh_suspend_curses():
            try:
                if ssh_ip == '' or ssh_user == '':
                    print('\nNah dawg... enter a hostname/ip and username')
                    time.sleep(3)
                    return 0
                passwd = getpass()
                print('\nAuthenticating...')
                time.sleep(.001)
                self.ssh.connect(ssh_ip, username=ssh_user, password=passwd, compress=True)
                self.transport = self.ssh.get_transport()
                self.enabled = self.transport.is_active()
                self.sftp = self.ssh.open_sftp()
                wins.set_active_panel(1)
                status.refresh()

            except Exception as e:
                x = 0
                print('\nSomething went wrong...')
                try:
                    self.ssh.close()
                except Exception as e:
                    print('\n' + str(e))
                print('\n' + str(e))
                time.sleep(3)
        

        stdscr.bkgd(curses.color_pair(4))
        stdscr.redrawln(0,height_main)
        menu.noutrefresh()
        stdscr.noutrefresh()
        window_0.border()
        window_1.border()
        reset_window(file_explorer_0)
        reset_window(file_explorer_1)
        wins.upd_panel()

        
        wins.set_active_panel(1)            

        if x == 1:
            file_explorer_1.ssh_explorer('/')
        else:
            pass

    def ret_code(self):           
        return stdout.channel.recv_exit_status()    

class ssh_suspend_curses:
    """Context Manager to temporarily leave curses mode"""
    def __enter__(self):
        stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        os.system('reset')

    def __exit__(self, exc_type, exc_val, tb):
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(1)

class text_box_form:
    text = ''
    def __init__(self):
        self.par_win_size_y, self.par_win_size_x = stdscr.getmaxyx()
        self.c = curses.color_pair(5)
        self.y = int(int(self.par_win_size_y*.5)/2)
        self.x = int(int(self.par_win_size_x*.5)/2)
       # self.h = int(self.par_win_size_y*.5)
        self.w = 25 # int(self.par_win_size_x*.5)
        self.form_win = curses.newwin(6,self.w,self.y, self.x)
        self.form_win.bkgd(self.c)
        self.form_win.attron(self.c)

        self.form_win.border()
        self.form_win.noutrefresh()

    def ssh_form(self, *fields):
        while True:
            curses.curs_set(2)
            self.form_win.addstr(1,1, 'IP Address',self.c)
            self.form_win.addstr(3,1, 'Username',  self.c)

            box1 = self.form_win.derwin(1, self.w - 2, 2,1)
            box2 = self.form_win.derwin(1, self.w - 2, 4,1)
            self.form_win.noutrefresh()
            curses.doupdate()
            info = []

            try:
                self.form_ready = 0
                while self.form_ready != 1:
                    self.field = 1
                    self.form_win.move(2,1)
                    self.tb1 = curses.textpad.Textbox(box1).edit(self.validate)
                    info.append(self.tb1.strip())
                    self.form_win.move(4,1)
                    self.field = 2
                    self.tb2 = curses.textpad.Textbox(box2).edit(self.validate)
                    info.append(self.tb2.strip())
            except KeyboardInterrupt:
                break

            self.form_win.noutrefresh()
            self.form_win.erase()
            self.form_win.noutrefresh()
            curses.echo()

            reset_window(file_explorer_0)
            reset_window(file_explorer_1)
            curses.doupdate()
            curses.curs_set(0)

            return info
    
    def make_new_folder(self, *fields):
        new_folder_button = button(self.win, ['OK', 'CANCEL'])
        curses.curs_set(2)
        self.form_win.addstr(1,1, 'Folder Name: ',self.c)
        box1 = self.form_win.derwin(1, self.w - 2, 2,1)
        self.form_win.noutrefresh()
        curses.doupdate()
        while True:

            try:
                self.form_ready = 0
                while self.form_ready != 1:
                    self.field = 1
                    self.form_win.move(2,1)
                    self.tb1 = curses.textpad.Textbox(box1).edit(self.validate)
                    info.append(self.tb1.strip())
            except KeyboardInterrupt:
                break

            self.form_win.noutrefresh()
            self.form_win.erase()
            self.form_win.noutrefresh()
            curses.echo()

            reset_window(file_explorer_0)
            reset_window(file_explorer_1)
            curses.doupdate()
            curses.curs_set(0)

            return info
            status = new_dir_textBox.action()
            new_folder_button.event(status)
            new_dir_button.display()

            if wins.active_panel == 0:
                path = file_explorer_0.abs_path + '/'
            else:
                path = file_explorer_1.abs_path + '/'

            if new_dir_button.action == 0:
                os.mkdir(path + new_dir_textBox.text)
                file_explorer_0.explorer(file_explorer_0.abs_path)
                file_explorer_1.explorer(file_explorer_1.abs_path)
            else:
                self.win.addstr(2,1, 'action cancelled', curses.color_pair(3))

    def validate(self, ch):
        if ch == ord('\t'):
            self.form_ready = 0
            return ord('\n')
        elif self.field == 2 and ch == ord('\n'):
            self.form_ready = 1
            return ch
        else:
            return ch

    def get_info(self):
        i = 0
        for field in self.fields:
            creds.text.strip()
            self.server_info.append(creds.text.rstrip())
            i = i + 1
            self.text = self.tb.gather()
            if i == 3:
                creds.text_window.erase()
                creds.text_window.noutrefresh()
                stdscr.noutrefresh()
                break

            
class pop_up(popUpBase):        
    def __init__(self, file_info, event,stdscr, sftp=None, sftp_path=None):
        y, x = wins.stdscr.getmaxyx()
        super().__init__(y - 5, x - 5, 2, 2)
        #now using self.win from base
        pop_up_size_y, pop_up_size_x = stdscr.getmaxyx()
        self.win.attron(curses.color_pair(3))
        self.win.bkgd(curses.color_pair(3))

        self.win.box(0,0)

        self.win.addstr(0, 2, str(file_info).replace('//','/') + ' - press q to exit')
        self.win.noutrefresh()

        try:

            file1 = open(file_info,'r', encoding='utf-8')
            Lines = file1.readlines()

        except PermissionError:
            Lines = "Permission Denied"
        except UnicodeDecodeError:
            Lines = 'Error'
        except:
            Lines ='other error'
            try:
                remote_file = sftp.file(sftp_path + file_info, 'r')
                Lines = remote_file.readlines()
            except Exception as e:
                print(e)
                pass
        count = 0
        for line in Lines:
            count += 1

        pop_up_pad = curses.newpad(count + 2, pop_up_size_x -2)
        pop_up_pad.bkgd(curses.color_pair(3))
        count = 0

        for line in Lines:
            count += 1
            if len(line) > pop_up_size_x:
                pop_up_pad.addstr(count, 1,  'toolong', curses.color_pair(3)) 
                break
            pop_up_pad.addstr(count, 1,  line, curses.color_pair(3))       
        
        self.win.keypad(1)
        pop_up_panel = panel.new_panel(self.win)
        pop_up_panel.top()
        pop_up_panel.show()
        width = pop_up_size_x-5
        scroller = 0
        scroller_hor = 0
        pop_up_pad_refresh = lambda: pop_up_pad.noutrefresh(scroller, scroller_hor, 3, 3, pop_up_size_y-5, width)

        while True:
            pop_up_pad_refresh()
            self.win.nodelay(1)
            ###pop up getch
            ch = self.win.getch()
            cursor = pop_up_pad.getyx()
            if ch == curses.KEY_UP and count > pop_up_size_y:
                scroller  -= 1
                if scroller <= 0:
                    scroller = 0
            elif ch == curses.KEY_DOWN and count > pop_up_size_y:
                scroller += 1
                if scroller >= cursor[0]:
                    scroller = cursor[0]
            elif ch == ord('b'):
                scroller = cursor[0] - pop_up_size_y + 7
            elif ch == ord('t'):
                scroller = 0
            elif ch == curses.KEY_RIGHT and len(line) > width:
                scroller_hor += 1

            if (ch == ord('q')):
                pop_up_panel.hide()
                panel.update_panels()
                pop_up_pad.erase()
                self.win.erase()
                self.win.noutrefresh()
                reset_window(file_explorer_0)
                reset_window(file_explorer_1)
                curses.doupdate()
                try:
                    file1.close()
                except:
                    self.win.nodelay(0)
                    break
                self.win.nodelay(0)
                break
    

class reset_path:
    def __init__(self):
        self.errors = 0
    def error(self):
        self.errors += 1
        if self.errors == 2:
            if wins.active_panel == 0:
                file_explorer_0.path = '/'
                self.errors = 0
            elif wins.active_panel == 1:
                file_explorer_1.path = '/'
                self.errors = 0

class file_explorer:
    path = prev_path_0 = prev_path_1 = '/'
    paths = [None,None]
    prev_paths = [prev_path_0, prev_path_1]
    path_errors = reset_path()

    def __init__(self, stdscr, window, path, is_ssh):
        self.marked_item = None
        self.window = window
        self.screen = stdscr
        self.screen_height, self.screen_width = self.screen.getmaxyx()
        height, width = self.window.getmaxyx()
        start_y, start_x = self.window.getbegyx()

        self.p = 0
        self.height = height
        self.width = width - 2
        self.start_y = start_y + 1
        self.start_x = start_x + 1
        self.position = 0
        self.scroller = 0
        self.explorer(path)
        self.draw_pad()
        self.event = ''
        self.selected_path = ''
        self.ssh_path = None
        self.ssh_path_hist = ['/']

    def explorer(self, path):
        if wins.active_panel == 1 and ssh_obj.enabled == True:
            #self.ssh_path = path
            file_explorer_1.ssh_explorer(path)
            return 0
        self.path = path
        try:
            self.abs_path = os.path.abspath(self.path)
            self.par_dir = os.path.dirname(self.abs_path).replace('//','/')
        except Exception as e:
            pass
        try:      
            self.files_folders = os.listdir(self.abs_path)
        except:
            self.abs_path = '/'
            self.files_folders = os.listdir(self.abs_path)
            self.path_errors.error()
            pass

        data_list = []

        for x in self.files_folders:

            i = os.path.isdir(self.abs_path + '/' + x)
            try:
                s = os.path.getsize(self.abs_path + '/' + x)
            except:
                s = 0
            s = sizeof_fmt(s, suffix="B")
            if i == True:
                i = '/'
            else:
                i = ''
            data_list.append([i+x, s])
        
        #sort list based on file names
        data_list = sorted(data_list, key=lambda x:x[:1])

        #insert an index
        i = 1
        for x in data_list:
            x.insert(0,i)
            i = i + 1

        #turn data list into a dictionary
        x = 0
        self.data = dict()
        self.data = {x[0]: x[1:] for x in data_list}

        if self.abs_path == '/':
            self.data[0] = ['/','']
        else:
            self.data[0] = ['..','']

    def ssh_path_hist_func(self, ssh_path):
        if ssh_path == '/':
            self.par_dir = '/'
            self.ssh_path = ssh_path
            self.ssh_path_hist = self.ssh_path_par_hist = ['/']
            self.p = 0
            pass
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

    #@ssh_path()

    def ssh_explorer_attr(self):
        if glbl_opts.low_bandwidth == True:
            s = 0
        else:
            self.ssh_files_folders_attr = ssh_obj.sftp.listdir_attr(path=self.next_ssh_path)
            size_list = []
            for entry in self.ssh_files_folders_attr:
                s = entry.st_size

        return size_list

    def ssh_explorer(self, ssh_path):
        self.ssh_path_hist_func(ssh_path)

        self.ssh_files_folders_dir = ssh_obj.sftp.listdir(path=self.next_ssh_path)
        self.ssh_files_folders_attr = ssh_obj.sftp.listdir_attr(path=self.next_ssh_path)
        #attr = ssh_explorer_attr
        try:
            self.ssh_abs_path = ssh_obj.sftp.normalize(self.next_ssh_path)
        except:
            pass

        item = 0
        data_list = []
        for x, entry in zip(self.ssh_files_folders_dir, self.ssh_files_folders_attr):
            i = S_ISDIR(entry.st_mode)
            s = entry.st_size
            if i == True:
                i = '/'
            else:
                i = ''
            data_list.append([i+x, s])
            item += 1
            
        #sort list based on file names
        data_list = sorted(data_list, key=lambda x:x[:1])

        #insert an index
        i = 0
        for x in data_list:
            i += 1
            x.insert(0,i)
            s = sizeof_fmt(x[2], suffix="B")
            x[2]=s

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
        self.pad.keypad(1)
        self.pad.bkgd(curses.color_pair(4))

    def select_item(self,mylist, x, v):
        item_to_edit = mylist[x]
        item_index = mylist.index(item_to_edit)

        for index, item in enumerate(mylist):
            itemlist = list(item)
            if index == item_index:
                itemlist[1] = v
            item = tuple(itemlist)
            mylist[index] = item
        self.tup = mylist
        return mylist

    def deselect_item(self,mylist, x, v):
        item_to_edit = mylist[x]
        item_index = mylist.index(item_to_edit)
        for index, item in enumerate(mylist):
            itemlist = list(item)
            if index == item_index:
                itemlist[1] = v
            item = tuple(itemlist)
            mylist[index] = item
        self.tup = mylist
        return mylist

    def get_selected_items(self, tup):
        new_list = []
        i = -1
        for ind, sel, item in tup:
            
            if sel == '[x]':
                i += 1
                tups = tuple((i,item))
                new_list.append(tups)
        self.marked_item = self.path + '/' + new_list[0][1]

    def del_selected_items(self, sel_file):
        popUpDel(sel_file)

    def copy_selected_items(self):
        file_name = self.data[self.position][0]
        left_panel_path = file_explorer_0.abs_path
        right_panel_path = file_explorer_1.abs_path

        if wins.active_panel == 0:
            self.from_file = self.path + '/' + file_name
            self.to_path = file_explorer_1.path
        elif wins.active_panel == 1:
            self.from_file = self.path + '/' + file_name
            self.to_path = file_explorer_0.path

        if self.position != 0:
            popUpCp(stdscr, self.from_file, self.to_path, file_name)

    def start_rsync(self):
        file_name = self.data[self.position][0]
        left_panel_path = file_explorer_0.abs_path
        right_panel_path = file_explorer_1.ssh_abs_path

        if wins.active_panel == 0:
            self.from_file = left_panel_path + '/' + file_name
            self.to_path = right_panel_path
        elif wins.active_panel == 1:
            self.from_file =  right_panel_path + '/' + file_name
            self.to_path = left_panel_path

        if self.position != 0:

            rsync_obj = rsync(0).start(self.from_file, self.to_path, file_name)
            #self.pad_refresh()

    def menu(self):
        self.pad.erase()
        self.height, self.width = self.window.getmaxyx()
        self.screen_height, self.screen_width = self.screen.getmaxyx()

        self.max_height = self.height -2
        self.bottom = self.max_height #+ len(self.tup) #self.max_height
        self.scroll_line = self.max_height - 3
        self.pad.setscrreg(0,self.max_height) #self.bottom -2)
        self.width = self.width - 2
        self.pad_refresh = lambda: self.pad.noutrefresh(self.scroller, 
        0, self.start_y, self.start_x, self.bottom, self.screen_width -2)
        par = '[ ]'
        for index, items in self.data.items():
            x = self.width - len(items[0])-4
            if index == self.position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL
            try:
                msg = "{4:>{5}}{6}{1:<}{2:>{3}}".format(par,items[0],items[1],x,index, int(2),str(" "))
            except:
                msg = "{4:>{5}}{6}{1:<}".format(par,items[0],items[1],x,index, int(2),str(" "))

            self.pad.addstr(index, 0, str(msg), mode)
            if mode == curses.A_REVERSE:
                self.cursor = self.pad.getyx()[0]
        self.pad_refresh()

    def navigate(self, n):
        self.position += n
        if self.position < 0:
            self.position = 0
        elif self.position >= len(self.data):
            self.position = len(self.data) - 1
    
    def set_paths(self):
        x = wins.active_panel
        if x == 0:
            oth_panel = 1
        else:
            oth_panel = 0
        if self.new_path == None:
            self.paths[x] = self.prev_paths[x].replace('//','/')
        else:
            self.prev_paths[x] = self.paths[x]
            self.paths[oth_panel] = self.prev_paths[oth_panel]

    def display(self):
        while True:
            self.menu()
            curses.doupdate()
            KEY_PRESS = None
            try:
                #self.pad.keypad(1)
                KEY_PRESS = self.pad.getch()
            except KeyboardInterrupt:
                KEY_PRESS = ord('q')
                self.event = KEY_PRESS
                break

            if KEY_PRESS == ord("\n"):
                if '/' in self.data[self.position][0]:
                    itsadir = True
                else:
                    itsadir = False

                if self.position != 0 and itsadir == True:
                    if ssh_obj.enabled == True and wins.active_panel == 1:
                        self.new_path =  self.data[self.position][0] + '/'
                    else:
                        self.new_path = self.path + self.data[self.position][0] + '/'
                    self.cwd = self.new_path
                    #self.selected_path = self.path + self.data[self.position][0] + '/'
                    self.pad_refresh()
                    self.position = self.scroller = 0
                    #self.event = KEY_PRESS
                    self.paths[wins.active_panel] = self.new_path.replace('//','/')
                    self.set_paths()
                    self.explorer(self.new_path)
                    wins.upd_panel()
                elif self.position != 0 and itsadir == False:
                    sel_file = self.path + '/' + self.data[self.position][0]
                    pop_up(sel_file, KEY_PRESS,self.screen, None)
                else:
                    
                    self.cwd = self.new_path = self.par_dir
                    if ssh_obj.enabled == True and wins.active_panel == 1:
                        self.par_dir = '..'
                    self.set_paths()
                    self.explorer(self.par_dir)
                    wins.upd_panel()
            elif KEY_PRESS == curses.KEY_UP:
                self.navigate(-1)
                if self.cursor > self.scroll_line:
                    self.scroller  -= 1
                    if self.scroller == -1:
                        self.scroller = 0
                if self.position == 0:
                    self.scroller = 0
            elif KEY_PRESS == curses.KEY_DOWN:
                self.navigate(1)
                if len(self.data) == 1:
                    self.position = 0
                elif self.cursor >= self.scroll_line:
                    if self.position != len(self.data):
                        self.scroller = self.cursor - self.scroll_line
            elif KEY_PRESS == ord('n'):
                popUpNewDir()
                ##form = text_box_form()
                #form.make_new_folder(('New Folder:'))


            #elif KEY_PRESS == ord('m'):
            #    if self.position != 0:
            #        self.select_item(self.tup, self.position, '[x]')
            #elif KEY_PRESS == ord('u'):
            #    if self.position != 0:
            #        self.deselect_item(self.tup, self.position, '[ ]')
           #elif KEY_PRESS == ord ('g'):
            #    self.get_selected_items(self.tup)
            elif KEY_PRESS == ord('b'):
                self.position = len(self.data)-1
                self.scroller = len(self.data) - self.scroll_line -1                    
            elif KEY_PRESS == ord('t'):
                self.position = 0
                self.scroller = 0
            elif KEY_PRESS == ord('9'):
                self.del_selected_items(self.path + '/' + self.data[self.position][0])
            elif KEY_PRESS == ord('5'):
                if ssh_obj.enabled == False:
                    self.copy_selected_items()
                    reset_window(file_explorer_0)
                    reset_window(file_explorer_1) 
                elif ssh_obj.enabled == True:
                    self.start_rsync()

            elif KEY_PRESS == ord('x') and ssh_obj.enabled == True:
                ssh_obj.ssh.close()
                ssh_obj.enabled = False
                wins.upd_panel()
                file_explorer_1.explorer(file_explorer_1.path)
                file_explorer_1.menu()
                reset_window(file_explorer_1)
            elif KEY_PRESS in(ord('f'), ord('o'), ord('q'), ord('\t')):
                #status.refresh()
                self.event = KEY_PRESS
                break

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(int(num)) < 1024.0:
            size = "{num:3.2f}{unit}{suffix}".format(num=num, unit=unit, suffix=suffix)
            return size
        num /= 1024.0
    return size

class reset_window:
    def __init__(self, explorer):
        self.explorer = explorer
        self.redraw()

    def __getattr__(self, attr):
        return getattr(self.explorer, attr)

    def touched(self):
        touched = self.window.is_wintouched()
        self.redraw()

    def redraw(self):
        self.window.redrawwin()
        self.window.noutrefresh()
        self.pad_refresh()
        self.menu()

class button:
    def __init__(self, window, list):
        self.position = 0
        self.status = 1
        self.list = list
        self.window = window
        self.window.keypad(1)
        self.menu()

    def navigate(self, n):
        self.position += n
        if self.position < 0:
            self.position = 0
        elif self.position >= len(self.list):
            self.position = len(self.list) - 1

    def display(self):
        while True:
            self.menu()
            if self.status == 0:
                KEY_PRESS = 10
            else:
                KEY_PRESS = self.window.getch()
            if KEY_PRESS == 10 and self.position == 0:
                self.action = 0
                break
            elif KEY_PRESS == 10 and self.position == 1:
                self.action = 1
                break
            elif KEY_PRESS == curses.KEY_LEFT:
                self.navigate(-1)
            elif KEY_PRESS == curses.KEY_RIGHT:
                self.navigate(1)

    def event(self, status):
        self.status = status

    def menu(self):
        space = 10
        for index, x in enumerate(self.list):
            if index == self.position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL
            msg = "{0}".format(x)
            self.window.addstr(4, space, str(msg), mode)
            space += 10
        self.window.noutrefresh()

class textBox:
    def __init__(self,win, y, x):
        self.win = win.derwin(1, x, 2, 10)
        self.win.box()
        self.tb = curses.textpad.Textbox(self.win)
        self.win.noutrefresh()
        
    def action(self):
        
        self.tb.edit()
        self.text = self.tb.gather()
        if self.text != None:
            return 0
        else:
            return 1

class popUpNewDir(popUpBase):
    def __init__(self):
        y, x = wins.stdscr.getmaxyx()
        nlines = int(y/3)
        ncols = int(x/2)
        begin_y = int(y/3)*1
        begin_x = int(x/4)*1
        super().__init__(nlines, ncols, begin_y, begin_x)
        #self.color = curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_RED)
        self.win.bkgd(curses.color_pair(3))
        self.win.addstr(1, 1, 'new dir: ', curses.color_pair(3))
        self.win.noutrefresh()
        new_dir_textBox = textBox(self.win, y, int(begin_x/2))
        new_dir_button = button(self.win, ['OK', 'CANCEL'])

        
        while True:
            status = new_dir_textBox.action()
            new_dir_button.event(status)
            new_dir_button.display()
            if wins.active_panel == 0:
                path = file_explorer_0.abs_path + '/'
            else:
                path = file_explorer_1.abs_path + '/'

            if new_dir_button.action == 0:
                os.mkdir(path + new_dir_textBox.text)
                file_explorer_0.explorer(file_explorer_0.abs_path)
                file_explorer_1.explorer(file_explorer_1.abs_path)
            else:
                self.win.addstr(2,1, 'action cancelled', curses.color_pair(3))

            self.win.noutrefresh()
            time.sleep(2)  
            reset_window(file_explorer_0)
            reset_window(file_explorer_1)
            break

class popUpDel(popUpBase):
    def __init__(self, sel_file):
        sel_file = sel_file.replace('//','/')
        y, x = wins.stdscr.getmaxyx()
        nlines = int(y/3)
        ncols = int(x/2)
        begin_y = int(y/3)*1
        begin_x = int(x/4)*1
        super().__init__(nlines, ncols, begin_y, begin_x)
        self.color = curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_RED)
        self.win.bkgd(curses.color_pair(8))
        self.win.addstr(1, 1, 'delete file: ' + sel_file, curses.color_pair(8))
        self.win.noutrefresh()
        del_button = button(self.win, ['OK', 'CANCEL'])
        while True:
            del_button.display()
            if del_button.action == 0:
                if os.path.isdir(sel_file) == True:
                    sel_file = sel_file.replace('//','/')

                    try:
                        os.removedirs(sel_file)
                    except:
                        self.win.addstr(2, 1, 'directory not empty, ok?', curses.color_pair(8))
                        self.win.noutrefresh()
                        del_button.display()
                        if del_button.action == 0:
                            shutil.rmtree(sel_file)
                        else:
                            pass
                elif os.path.isdir(sel_file) == False:
                    try:
                        os.remove(sel_file)
                    except PermissionError:
                        self.win.addstr(2,1,'permission denied', curses.color_pair(8))
                        self.win.noutrefresh()
                        time.sleep(2)
                file_explorer_0.explorer(file_explorer_0.abs_path)
                file_explorer_1.explorer(file_explorer_1.abs_path)
            else:
                self.win.addstr(2,1, 'action cancelled', curses.color_pair(8))
            self.win.noutrefresh()
            time.sleep(2)  
            reset_window(file_explorer_0)
            reset_window(file_explorer_1)
            break

class popUpCp(popUpBase):
    t = None
    def __init__(self, window, from_file, to_path, file_name):
        y, x = wins.stdscr.getmaxyx()
        super().__init__(7, int(x/2), int(y/3)*1, int(x/4)*1)
        self.bar_width = int(x/2) - 2
        e = None
        try:
            # Start copying on a separate thread
            t = threading.Thread(name='CopyThread', target=copy_file, args=(from_file, to_path), daemon=True)
            t.start()
            t.is_started = True
        except Exception as e:
            error = e
        if e == None:
            check = checker(from_file, to_path, file_name, t, callback=callbackFunc)
        try:
            while True:
                if e == None:
                    check.status()
                    self.win.addstr(1, 1, 'from: ' + from_file )
                    self.win.addstr(2, 1, 'to: ' + to_path)
                    self.win.addstr(3, 1, str(check.des_size) + ' / ' + str(check.src_size))
                    self.percentage = int(float(check.des_num / check.src_num)* self.bar_width)
                    self.stars = '*' * self.percentage
                    self.win.addstr(4, 1, "{0}{1}".format('[',self.stars))
                    self.win.addstr(4,self.bar_width, ']')
                else:
                    self.win.addstr(3, 1, str(error))
                    time.sleep(5)
                self.win.noutrefresh()
                curses.doupdate()

                if check.des_size == check.src_size:
                    self.win.addstr(5, 1, 'Complete')
                    self.win.noutrefresh()
                    curses.doupdate()

                    callbackFunc(t)
                    time.sleep(3)
                    if wins.other_panel == 0:
                        file_explorer_1.explorer(file_explorer_1.cwd)
                    else:
                        file_explorer_0.explorer(file_explorer_0.cwd)
                    break
        except:
            callbackFunc(t)
            self.win.noutrefresh()
            curses.doupdate()
            pass

def callbackFunc(t):
    t._is_stopped = True

class checker:
    def __init__(self, source_path, destination_path, file_name, t, callback):
        self.callback = callback
        self.t = t
        self.full_qual_dest_path = destination_path + '/' + file_name
        while not os.path.exists(destination_path):
            callback(t)
            break
        self.src_num = os.path.getsize(source_path)
        self.src_size = sizeof_fmt(self.src_num)
        self.des_num = 0
        self.des_size = 0
        # Keep checking the file size till it's the same as source file
        try: 
            self.des_num = os.path.getsize(self.full_qual_dest_path)
            self.des_size = sizeof_fmt(self.des_num)
        except:
            pass
        if self.des_size == self.src_size:
            callback(t)
            self.complete = 0
            
    def status(self):
        if self.des_size != self.src_size:
            try:
                self.des_num = int(float(os.path.getsize(self.full_qual_dest_path)))
                self.des_size = sizeof_fmt(self.des_num)
            except:
                time.sleep(.05)
                self.des_num = int(float(os.path.getsize(self.full_qual_dest_path)))
                self.des_size = sizeof_fmt(self.des_num)
        else:
            self.callback(self.t)
            self.complete = 0

class copy_file:
    def __init__(self, *args):
        source_path, destination_path = args
        length = len(source_path) + len(destination_path) + 13
        try:
            shutil.copy(source_path, destination_path)
            self.action = 0
        except Exception as e:
            self.error = e

class statusbar:
    statusbarstr = ''
    text = ''
    def __init__(self, stdscr, height_main, width_main, text, color):
        self.color = color
        stdscr.move(height_main-1, len(self.statusbarstr))
        stdscr.clrtoeol()
        self.statusbarstr = text
        stdscr.addstr(height_main-1, 0, self.statusbarstr, self.color)
        self.statusbar_len = len(self.statusbarstr)
        self.statusbar_remaining = width_main - len(self.statusbarstr) - 1
        stdscr.addstr(height_main-1, self.statusbar_len, " " * self.statusbar_remaining,self.color)
        stdscr.redrawln(height_main-1,0)
        stdscr.noutrefresh()

    def update(self):
        y, width_main = stdscr.getmaxyx()
        stdscr.move(height_main-1, 0)
        stdscr.clrtoeol()
        panel = 'active panel: ' + str(wins.active_panel)
        if ssh_obj.enabled == True:
            ssh_status = 'SSH Enabled'
        else:
            ssh_status = 'SSH Disabled'

        self.statusbar_remaining = width_main - len(panel) - len(ssh_status) - 1
        spaces = ' ' * self.statusbar_remaining

        self.statusbarstr = "{0}{1}{2}".format(panel, spaces, ssh_status)
        self.statusbar_len = len(self.statusbarstr)


        if self.statusbar_len < width_main:
            stdscr.addstr(height_main-1, 0, self.statusbarstr, self.color)

        stdscr.redrawln(height_main-1,0)
        stdscr.noutrefresh()

    def refresh(self):
        #while True:
            #time.sleep(.005)
            self.update()
            curses.doupdate()
        
class init:
    height_main = None
    width_main = None
    def __init__(self, stdscr):
        stdscr.erase()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(1)
        curses.curs_set(0)
        curses.start_color()
        self.height_main, self.width_main = stdscr.getmaxyx()
    
    def is_term_resized(self):
        resize_check = curses.is_term_resized(nlines, ncols)
        self.height_main, self.width_main = stdscr.getmaxyx()
        if resize_check == True:
            self.term_resize()

    def term_resize(self):
        curses.resizeterm(self.height_main, self.width_main)

class rsync(popUpBase):
    has_been_called = False

    def __init__(self, called_from):
        self.has_been_called = True
        if self.has_been_called == True and called_from == 0:
            msg = 'rsync starting...'
        elif self.has_been_called == False and called_from == 'm':
            if ssh_obj.enabled == True:
                msg = 'ssh enabled, rsync ready\n use key c'
        elif ssh_obj == True and called_from == 'm':
            msg = 'ssh must enabled, use rsync'
        elif called_from == 'm':
            msg = 'ssh must be enabled first'

        y, x = wins.stdscr.getmaxyx()
        super().__init__(7, int(x/2), int(y/3)*1, int(x/4)*1)

        self.win.addstr(1, 1, msg)
        time.sleep(1)


    def start(self, from_file, to_file, file_name):
        with suspend_curses(from_file,to_file):
            self.xfer(from_file, to_file)
        stdscr.bkgd(curses.color_pair(3))
        stdscr.redrawln(0,height_main)
        menu.noutrefresh()
        stdscr.noutrefresh()
        window_0.border()
        window_1.border()
        reset_window(file_explorer_0)
        reset_window(file_explorer_1)
        wins.upd_panel()
    
    def xfer(self, from_file, to_file):
        from_file = shlex.quote(from_file)
        to_file = shlex.quote(to_file)
        server = [ssh_obj.server_info[0],ssh_obj.server_info[1],from_file, to_file]
        #server = ssh_obj.server_info
        if wins.active_panel == 0:
            #my_args = ["rsync", "-Ppave ssh -F /home/apollo/.ssh/ssh_config ", server[2], "{1}@{0}:{3}".format(server[0],server[1],server[2],server[3])]
            my_args = ["rsync", "-Ppav", server[2], "{1}@{0}:{3}".format(server[0],server[1],server[2],server[3])]
        elif wins.active_panel == 1:
            my_args = ["rsync", "-Ppav", "{1}@{0}:{2}".format(server[0],server[1],server[2],server[3]),server[3] + '/']
            #my_args = ["rsync", "-Ppave ssh -F /home/apollo/.ssh/ssh_config ", "{1}@{0}:{2}".format(server[0],server[1],server[2],server[3]),server[3]]

        proc = subprocess.Popen(
            my_args,
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            bufsize=0,
            universal_newlines=True
            )
        i = 0
        try:
            for line in iter(proc.stdout.readline, ''):
                if not line:
                    break
                elif line.startswith('total'):
                    print('\n')
                    print(line.rstrip(), end='\n')
                    break
                elif i < 2:
                    print(line.rstrip(),end='\n')
                elif i > 2:
                    print(line.rstrip(),end='\r')
                i+=1
            time.sleep(5)
        except KeyboardInterrupt:
            time.sleep(2)

            return KeyboardInterrupt

class suspend_curses:
    """Context Manager to temporarily leave curses mode"""
    def __init__(self, from_file,to_file):
        self.from_file = from_file
        self.to_file = to_file
    def __enter__(self):
        stdscr.clear()
        stdscr.noutrefresh()
        curses.doupdate()
        time.sleep(3)
        stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        os.system('reset')
        time.sleep(1)
        #print('\n')
        #print('\nLeaving curses...')
        print('\nfrom: ' + self.from_file)
        print('to: ' + self.to_file)
        #print('')
        time.sleep(2)

    def __exit__(self, exc_type, exc_val, tb):
        #print('\n')
        print('\nReturning to curses...')  
        time.sleep(1)
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(1)
        #time.sleep(1)
        
class rsync_checker:
    def __init__(self, from_file, to_file):
        if wins.active_panel == 0:
            self.src_num = os.path.getsize(to_file)
            self.ssh_info = ssh_obj.sftp.listdir_attr(path=from_file)
            ssh_size = []
            for entry in self.ssh_info: 
                ssh_size.append(entry.st_size)
                self.des_num = entry.st_size
        elif wins.active_panel == 1:
            self.ssh_info = ssh_obj.sftp.listdir_attr(path=source_path)
            self.des_num = os.path.getsize(to_file)
            ssh_size = []
            for entry in self.ssh_info: 
                ssh_size.append(entry.st_size)
                self.src_num = entry.st_size
            self.src_size = sizeof_fmt(self.src_num)
            self.des_size = sizeof_fmt(self.des_num)
                


def draw_win(window, h, w, y, x, title):
    window = window.derwin(h, w, y, x)
    window.bkgd(curses.color_pair(4))
    window.box(0,0)
    window.keypad(1)
    window.addstr(0,2,str(title))
    return window

class win_mgr:
    cur_win = None
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.window_height = my_inst.height_main -2
        self.window_width = int(my_inst.width_main/2)
        self.other_panel = 1
        self.active_panel = 0

    def left_panel(self):
        window_0_x_start = 0
        self.window_0 = draw_win(self.stdscr, self.window_height, self.window_width, 1, window_0_x_start, str(start_path))
        return self.window_0

    def right_panel(self):
        window_1_x_start = int(width_main/2)
        self.window_1 = draw_win(self.stdscr, self.window_height, self.window_width, 1,window_1_x_start, str(start_path))
        return self.window_1

    def panel_headers(self):
        self.left_head_path = file_explorer_0.abs_path 
        self.right_head_path = file_explorer_1.abs_path 
        if ssh_obj.enabled == True and wins.active_panel == 1:
            try:
                self.right_head_path = ssh_obj.server_info[0] + ':' + file_explorer_1.ssh_path 
            except:
                self.right_head_path = file_explorer_1.abs_path 
        elif ssh_obj.enabled == True and wins.active_panel == 0:
            try:
                self.right_head_path = ssh_obj.server_info[0] + ':' + file_explorer_1.ssh_path 
            except:
                self.right_head_path = file_explorer_1.abs_path 

        self.panel_widths = window_0.getmaxyx()[1] -2
        self.left_panel_head_len = len(self.left_head_path)
        self.left_panel_head_rem = self.left_panel_head_len - self.panel_widths
        self.right_panel_head_len = len(self.right_head_path)
        self.right_panel_head_rem = self.right_panel_head_len - self.panel_widths

        if self.left_panel_head_len > self.panel_widths:
            self.left_trimmed_chars = self.left_panel_head_len - self.panel_widths
            self.left_head_path = self.left_head_path[self.left_trimmed_chars:]

        elif self.right_panel_head_len > self.panel_widths:
            self.right_trimmed_chars = self.right_panel_head_len - self.panel_widths
            self.right_head_path = self.right_head_path[self.right_trimmed_chars:]
        else:
            pass

    def left_panel_sel(self):
        self.window_0.move(0,1)
        self.window_0.clrtoeol()
        self.window_0.border()
        self.window_0.addstr(0,1,str(self.left_head_path),curses.A_REVERSE)
        self.window_1.border()
        self.window_1.addstr(0,1,str(self.right_head_path),curses.A_NORMAL)

    def refreshln1(self):
        self.window_0.untouchwin()  
        self.window_1.untouchwin()   
        self.window_0.redrawln(0,1)
        self.window_1.redrawln(0, 1)
        self.window_0.noutrefresh()
        self.window_1.noutrefresh()
        stdscr.noutrefresh()

    def right_panel_sel(self):
        self.window_0.border()
        self.window_0.addstr(0,1,str(self.left_head_path),curses.A_NORMAL)
        self.window_1.move(0,1)
        self.window_1.clrtoeol()
        self.window_1.border()
        self.window_1.addstr(0,1,str(self.right_head_path),curses.A_REVERSE)

    def set_active_panel(self, i):
        self.active_panel = i
        self.panel_headers()
        if i == 0:
            self.other_panel = 1
            self.cur_win = window_0
            #self.active_panel = i
            self.other_win = window_1
            self.left_panel_sel()
        elif i == 1:
            self.other_panel = 0
            self.cur_win = window_1
            #self.active_panel = i

            self.other_win = window_0
            self.right_panel_sel()
        self.refreshln1()
        curses.doupdate()

    def upd_panel(self):
        self.set_active_panel(self.active_panel)

stdscr = curses.initscr()
curses.start_color()
curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
curses.init_pair(5, curses.COLOR_CYAN,curses.COLOR_WHITE)
stdscr.bkgd(curses.color_pair(4))

my_inst = init(stdscr)
height_main = my_inst.height_main
width_main = my_inst.width_main
menu = menuBar(stdscr)
wins = win_mgr(stdscr)
start_path = os.path.curdir

window_0 = wins.left_panel()
window_1 = wins.right_panel()
window_0.noutrefresh()
window_1.noutrefresh()
ssh_obj = ssh()
file_explorer_0 = file_explorer(stdscr, window_0, start_path, False)
file_explorer_1 = file_explorer(stdscr, window_1, start_path, False)
file_explorer_0.menu()
file_explorer_1.menu()
paths = []
event = 0
i = 0
wins.set_active_panel(i)
file_explorers = [file_explorer_0, file_explorer_1]
status = statusbar(stdscr, height_main, width_main, '', curses.color_pair(1))
wins.set_active_panel(i)
status.refresh()
#s = threading.Thread(name='StatusBarThread', target=status.refresh, daemon=True)
#s.start()
glbl_opts = optionsMenu()
while event != ord('q'):
    while True:
        wins.upd_panel()
        file_explorers[i].event = None
        file_explorers[i].display()
        event = file_explorers[i].event
        stdscr.noutrefresh()

        if event in (ord('\t'), ord('q')):
            break 
        elif event == ord('f') or event == ord ('o'):
            event = menu.menuBar_act(event)
            menu.display()
            if ssh_obj.enabled == True:
                i = 1
            if event == ord('\t') or event == ord('f'):
                break

    if event == ord('\t'):   
        if i == 0:
            i = i + 1
        elif i > 0:
            i = 0

    elif event == ord('q'):
        break

    wins.set_active_panel(i)
    status.refresh()
if ssh_obj.enabled == True:
    ssh_obj.ssh.close()

del menu
del file_explorer_0
del file_explorer_1
del window_0
del window_1
del status
stdscr.keypad(0)
curses.echo()
curses.nocbreak()
curses.endwin()
os.system('reset')
