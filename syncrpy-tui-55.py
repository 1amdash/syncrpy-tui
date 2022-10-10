#!/usr/bin/env python3.6
from asyncio import transports
import os
import sys
import time
import curses
import io
import paramiko
import shutil
import threading
import subprocess
import shlex
import tempfile
from curses import panel, textpad
from stat import S_ISDIR, S_ISREG
from getpass import getpass

class PopUpBase:
    """Creates a new window with basic sizing and formatting for various popups"""
    def __init__(self, nlines, ncols, begin_y, begin_x):
        self.par_win_size_y, self.par_win_size_x = stdscr.getmaxyx()
        self.y = int(self.par_win_size_y/4)
        self.x = int(self.par_win_size_x/4)
        self.h = int(self.par_win_size_y/2)
        self.w = 25 # int(self.par_win_size_x*.5)
        self.win = curses.newwin(nlines, ncols, begin_y, begin_x)
        self.win.attron(curses.color_pair(5))
        self.win.bkgd(curses.color_pair(5))
        self.win.border()
        self.win.noutrefresh()

    def msg(self, msg):
        """Will act as an alert/error window, where the msg argument can be an exception to print"""
        self.win.addstr(1,1, msg, curses.color_pair(3))
        self.win.noutrefresh()

class OptionsMenu(PopUpBase):
    """Popup menu meant to act as a 'preferences/settings' meant to affect the program globally"""
    menu_items = ['[ ] low bandwidth', '[ ] test item']
    position = 0
    low_bandwidth = None
    def __init__(self):
        self.y, self.x = stdscr.getmaxyx()
        self.y = int(self.y/3)
        self.x = int (self.x/3)

    def __call__(self):
        super().__init__(int(self.y), int(self.x), self.y, self.x)
        self.y, self.x = stdscr.getmaxyx()

    def menu(self):
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
        self.__call__()
        self.win.keypad(1)
        while True:
            self.menu()
            ### MenuBar getch
            CH = self.win.getch()
            if CH == curses.KEY_UP:
                self.position = navigate(-1, self.menu_items, self.position)
            elif CH == curses.KEY_DOWN:
                self.position = navigate(1, self.menu_items, self.position)
            elif CH == ord('\n') and self.position == 0:
                if self.low_bandwidth is True:
                    self.menu_items = ['[ ] low bandwidth']
                    self.low_bandwidth = False
                    self.menu()
                    return 0

                self.menu_items = ['[x] low bandwidth']
                self.low_bandwidth = True
                self.menu()
                
            elif CH == ord('\t'):
                self.win.erase()
                self.win.noutrefresh()
                curses.doupdate()
                return 0

def exit_program(window=None):
    try:
        ssh_obj.ssh.close()
        del window
    except:
        try:
            del window
        except:
            pass
        pass
    del globals()['menu']
    if file_explorer_0:
        del globals()['file_explorer_0']
    if file_explorer_1:
        del globals()['file_explorer_1']
    del globals()['window_0']
    del globals()['window_1']
    del globals()['status']
    stdscr.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()
    os.system('reset')

def navigate(direction, item, position):
    item_length = len(item)
    position += direction
    if position < 0:
        position = 0
    elif position >= item_length:
        position = item_length - 1
    return position

class MenuBar(PopUpBase):
    """Creates the menubar

    Used to create either the File or Options menu, draws a window depending
    on if f or o is called.
    """
    position = 0
    sub_menu = ['ssh','rsync','exit']
    sub_menu2 = ['settings']
    menubarwindow = ''
    def __init__(self):
        stdscr.addstr(0,1, 'File Options', curses.A_NORMAL)
        stdscr.noutrefresh()
    
    def menubar_act(self, menu_event):
        if menu_event == ord('f'):
            super().__init__(10, 15, 1, 1)
            #now using self.win from base
            stdscr.addstr(0,1, 'File', curses.A_STANDOUT)
            stdscr.addstr(0,4+2, 'Options', curses.A_NORMAL)
            stdscr.noutrefresh()
            self.menu_item = self.sub_menu

        if menu_event == ord('o'):
            super().__init__(10, 15, 1, 6)
            stdscr.addstr(0,1, 'File', curses.A_NORMAL)
            stdscr.addstr(0,4+2, 'Options', curses.A_STANDOUT)    
            stdscr.noutrefresh()
            self.menu_item = self.sub_menu2
        
    def menu(self):
        #print list as basis for menu, the item selector is the A_REVERSE (highlighted) item
        for index, item in enumerate(self.menu_item):
            if index == self.position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL
            self.win.addstr(1+ index, 1, item, mode)
        self.win.noutrefresh()
        curses.doupdate()

    def noutrefresh(self):
        stdscr.addstr(0,1, 'File Options', curses.A_NORMAL)
        stdscr.noutrefresh()

    def display(self):
        self.win.keypad(1)
        while True:
            self.menu()
            ### menuBar getch
            ch = self.win.getch()
            if ch == curses.KEY_UP:
                self.position = navigate(-1, self.menu_item, self.position)
            elif ch == curses.KEY_DOWN:
                self.position = navigate(1, self.menu_item, self.position)
            elif ch == ord('\n') and self.menu_item[self.position] == 'ssh':
                if ssh_obj.is_enabled is False:
                    self.win.erase()
                    del self.win
                    reset_window(file_explorer_0)
                    ssh_obj.start()
                    return 0
            elif ch == ord('\n') and self.menu_item[self.position] == 'rsync':
                self.win.erase()
                del self.win
                reset_window(file_explorer_0)
                reset_window(file_explorer_1)
                RSync('m')
                return 0
            elif ch == ord('\n') and self.menu_item[self.position] == 'settings':
                self.win.erase()
                del self.win
                reset_window(file_explorer_0)
                glbl_opts.display()
                return 0
            elif ch == ord('\n') and self.menu_item[self.position] == 'exit':
                return ord('q')
                #ch = ord('q')
                #return ch
            elif ch in (ord('f'), ord('o'), ord('\t'), ord('q')):
                stdscr.addstr(0,1, 'File', curses.A_NORMAL)
                stdscr.addstr(0,4+2, 'Options', curses.A_NORMAL)
                stdscr.noutrefresh()
                curses.doupdate()
                reset_window(file_explorer_0)
                return ch


class SSH:
    """
    Sets up and enables a paramiko ssh client.

    Takes users input (ip address, username) by calling ssh_form and
    feeds the paramiko ssh client. During setup curses is suspended to 
    use getpass and enter the password.
    """
    def __init__(self):
        self.is_enabled = False
        self.server_info = []
        self.ssh = ''
        self.sftp = None
        self.ssh_path = None

    def start(self):
        form = ssh_form()        
        ssh_obj.server_info.append(form.info[0]) # Ip address
        ssh_obj.server_info.append(form.info[1]) # Username
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        x = 1
        with SuspendCurses():
            try:
                if form.info[0] == '' or form.info[1] == '':
                    print('\nNah dawg... enter a hostname/ip and username')
                    time.sleep(3)
                    return 0
                passwd = getpass()
                print('\nAuthenticating...')
                self.ssh.connect(form.info[0], username=form.info[1], password=passwd, compress=True)
                self.get_transport(self.ssh)
                self.enabled()
                self.sftp = self.ssh.open_sftp()
                wins.set_active_panel(1)
                status.refresh()
            except Exception as err:
                x = 0
                print('\nSomething went wrong...')
                print('\n' + str(err))
                try:
                    self.ssh.close()
                except Exception as err:
                    print('\n' + str(err))
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

    def get_transport(self, ssh):
        self.transport = ssh.get_transport()

    def enabled(self):
        if self.transport.is_active():
            self.is_enabled = True
        else:
            self.is_enabled = False

class ssh_form(PopUpBase):
    """PopUp form which relies on PopUpBase and TextBox to create a IP address/username form."""
    info = []
    def __init__(self):
        nlines, ncols = stdscr.getmaxyx()
        nlines = int(nlines/4)
        ncols = int(ncols/4)
        begin_y = nlines
        begin_x = ncols
        super().__init__(10,ncols, begin_y,begin_x)
        self.win.bkgd(curses.color_pair(3))
        self.win.attron(curses.color_pair(3))
        self.win.border()
        self.win.addstr(1,1, 'IP Address')
        self.win.addstr(5,1, 'Username')
        self.win.noutrefresh()
        self.textbox1 = TextBox(ncols-5, begin_y + 1, begin_x + 1)
        self.textbox2 = TextBox(ncols-5, begin_y + 5, begin_x + 1)
        curses.doupdate()
        self.input()

    def input(self):  
        status = 1
        while status == 1:
            curses.curs_set(2)
            self.win.move(3, 2)
            self.win.noutrefresh()
            curses.doupdate()
            textbox1_info = self.textbox1.action()
            status = textbox1_info[1]
            self.win.move(7, 2)
            self.win.noutrefresh()
            curses.doupdate()
            textbox2_info = self.textbox2.action()
            status = textbox2_info[1]

        if status == 0:
            self.info.append(textbox1_info[0])
            self.info.append(textbox2_info[0])

        self.win.noutrefresh()
        self.win.erase()
        self.win.noutrefresh()
        reset_window(file_explorer_0)
        reset_window(file_explorer_1)
        curses.doupdate()
        return self.info

class PopUpFileOpener(PopUpBase):        
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
        def pop_up_pad_refresh(): pop_up_pad.noutrefresh(
            scroller, scroller_hor, 3, 3, pop_up_size_y-5, width)
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
            if ch == ord('q'):
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
    """Used to reset the path to '/' when file_explorer messses up"""
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
    """Work horse of the application

    Does the bulk of the work by taking a path and listing directorys/files within that 
    path. Also prints the list of directorys/files and is responsible for navigating
    through those files. The ssh_explorer method is meant to closely mirror the explorer
    method but is modified for paramiko where appropriate.
    """
    path = '/'
    paths = [None, None]
    prev_paths = ['/', '/']
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
        self.event = None
        self.selected_path = ''
        self.ssh_path = None
        self.ssh_path_hist = ['/']
        self.draw_pad()
        self.explorer(path)
        self.menu()

    def explorer(self, path):
        if wins.active_panel == 1 and ssh_obj.is_enabled == True:
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
            s = human_readable_size(s, suffix="B")
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
        #since paramiko doesnt produce an absolute path, this creates a path
        #history by appending and pop'ing an array as you move through the file
        #structure
        if ssh_path == '/':
            self.par_dir = '/'
            self.ssh_path = ssh_path
            self.ssh_path_par_hist = ['/']
            self.ssh_path_hist = ['/']
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

    def ssh_explorer_attr(self):
        if glbl_opts.low_bandwidth == True:
            s = 0
        else:
            self.ssh_files_folders_attr = ssh_obj.sftp.listdir_attr(
                path=self.next_ssh_path)
            size_list = []
            for entry in self.ssh_files_folders_attr:
                s = entry.st_size

        return size_list

    def ssh_get_abs_path(self, path):
        try:
            self.ssh_abs_path = ssh_obj.sftp.normalize(path) 
        except:
            pass

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
        #insert an index and use the size function to make size human readable
        i = 0
        for x in data_list:
            i += 1
            x.insert(0,i)
            s = human_readable_size(x[2], suffix="B")
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
            rsync_obj = RSync(0).start(self.from_file, self.to_path, file_name)

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
        file_name = self.data[self.position][0]
        if wins.active_panel == 0:
            self.from_file = self.path + '/' + file_name
            self.to_path = file_explorer_1.path
        elif wins.active_panel == 1:
            self.from_file = self.path + '/' + file_name
            self.to_path = file_explorer_0.path
        if self.position != 0:
            PopUpCopyFile(stdscr, self.from_file, self.to_path, file_name)

    def scroll(self):
        if self.cursor > self.scroll_line:
            self.data_length = len(self.data) - 1
            if self.position != self.data_length:
                self.scroller = self.position - self.scroll_line
        if self.scroller == -1:
            self.scroller = 0
        if self.position == 0:
            self.scroller = 0

    def change_dir(self):
        dir = self.data[self.position][0]
        if dir.startswith('/'):
            is_dir = True
            dir = dir + '/'
        else:
            is_dir = False
        if self.position != 0 and is_dir is True:
            if ssh_obj.is_enabled == True and wins.active_panel == 1:
                self.new_path =  dir
            else:
                self.new_path = self.path + dir
            self.cwd = self.new_path
            #self.selected_path = self.path + self.data[self.position][0] + '/'
            self.pad_refresh()
            self.position = self.scroller = 0
            self.paths[wins.active_panel] = self.new_path.replace('//','/')
            self.set_paths()
            self.explorer(self.new_path)
        elif self.position != 0 and is_dir is not True:
            sel_file = self.path + '/' + dir
            PopUpFileOpener(sel_file, self.screen, None)
        else:
            self.cwd = self.new_path = self.par_dir
            if ssh_obj.is_enabled == True and wins.active_panel == 1:
                self.par_dir = '..'
            self.set_paths()
            self.explorer(self.par_dir)
        wins.upd_panel()

    def display(self):
        self.event = event = None
        while event not in (ord('\t'), ord('q'), ord('f'), ord('o')):
            self.pad.keypad(1)
            self.menu()
            curses.doupdate()
            event = self.pad.getch()         
            event = KeyPress.event(KeyPress, event, self, self.data, self.position)
            self.event = event

class KeyPress:
    #def __init__(self, explorer):
    #    self._exp = explorer
    #    self.event(key_press, items, position)

    def event(self, key_press, explorer, items=None, position=None):
        self._exp = explorer
        event = self.key_or_arrow(self, key_press)
        return event(self, key_press, items, position)

    def key_or_arrow(self, key_press):
        if key_press in (curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN):
            return self.arrow_event
        else:
            return self.key_event

    def arrow_event(self, event, items, position):
        if event == curses.KEY_UP:
            self._exp.position = navigate(-1, items, position)
            self._exp.scroll()
        elif event == curses.KEY_DOWN:
            self._exp.position = navigate(1, items, position)
            self._exp.scroll()
        elif event == curses.KEY_RIGHT:
            return navigate(1, items, position)
        elif event == curses.KEY_LEFT:
            return navigate(-1, items, position)
    
    def key_event(self, event, items=None, position=None): 
        if event == ord('\n'):
            self.enter_key(self, event)
        elif event == ord('\t'):
            return event
        elif event in (ord('f'), ord('o')):
            return event
        elif event == ord('q'):
            return event
        elif event == ord('x'):
            self.close_ssh_key(self, event)
        elif event == ord('5'):
            self.copy_key(self,event)
        elif event == ord('n'):
            self.new_dir_key()
        elif event == ord('b'):
            self.to_bottom_key(self)
        elif event == ord('t'):
            self.to_top_key(self)
        elif event == ord('9'):
            self.delete_key(items, position)
        else:
            pass

    def to_top_key(self):
        self._exp.go_to_top()

    def to_bottom_key(self):
        self._exp.go_to_bottom()

    def delete_key(self, items, position):
        item = items[position][0]
        self._exp.del_selected_items(self._exp.path + '/' + item)

    def new_dir_key(self, event):
        self._exp.popUpNewDir()

    def enter_key(self, event):
        self._exp.change_dir()
    
    def close_ssh_key(self,event):
        if ssh_obj.is_enabled == True:
            ssh_obj.ssh.close()
            ssh_obj.enabled()
            wins.upd_panel()
            file_explorer_1.explorer(file_explorer_1.path)
            file_explorer_1.menu()
            reset_window(file_explorer_1)
        else:
            pass

    def copy_key(self,event):
        if ssh_obj.is_enabled:
            self._exp.start_rsync()
        else:
            self._exp.copy_selected_items()
            reset_window(file_explorer_0)
            reset_window(file_explorer_1) 
    
def human_readable_size(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(int(num)) < 1024.0:
            return f"{num:3.2f}{unit}{suffix}"
        num /= 1024.0
    return num

class reset_window:
    """When called, redraws windows, touched method is not used right now"""
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
    """Meant to be a portable button"""
    def __init__(self, window, list):
        self.position = 0
        self.status = 1
        self.list = list
        self.window = window
        self.window.keypad(1)
        self.menu()

    def display(self):
        while True:
            self.menu()
            if self.status == 0:
                KEY_PRESS = 10
            else:
                KEY_PRESS = self.window.getch()
            if KEY_PRESS == 10 and self.position == 0:
                self.status = 0
                self.action = 0
                return
            elif KEY_PRESS == 10 and self.position == 1:
                self.status = 0
                self.action = 1
                return
            elif KEY_PRESS == curses.KEY_LEFT:
                self.position = navigate(-1, self.list, self.position)
            elif KEY_PRESS == curses.KEY_RIGHT:
                self.position = navigate(1, self.list, self.position)
            elif KEY_PRESS == ord('\t'):
                return

    def event(self, status):
        self.status = status

    def menu(self):
        space = 10
        for index, x in enumerate(self.list):
            if index == self.position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL
            self.window.addstr(5, space, str(x), mode)
            space += 10
        self.window.noutrefresh()
        curses.doupdate()

class TextBox:
    """create single text box, meant to be portable"""
    def __init__(self, width, start_y, start_x):
        self.start_y = start_y
        self.start_x = start_x
        curses.curs_set(2)
        self.win = curses.newwin(3, width, start_y+1, start_x)
        self.win.bkgdset(curses.color_pair(3))
        self.win.border()
        self.text_win = curses.newwin(1, width-2, start_y+2, start_x+1)
        self.win.noutrefresh()
        curses.doupdate()
        self.text_win.keypad(1)
        self.text_win.bkgdset(curses.color_pair(3))
        self.text_win.bkgd(curses.color_pair(3))
        self.text_win.attron(curses.color_pair(3))
        self.tb = curses.textpad.Textbox(self.text_win)
        self.text_win.noutrefresh()
        curses.doupdate()
        
    def action(self):
        while True:
            self.form_ready = 1
            self.text = self.tb.edit(self.validate)
            self.text = self.text.strip()
            return (self.text, self.form_ready)

    def validate(self, ch):
        if ch in (9, ord('\t'), curses.KEY_DOWN):
            return ord('\n')
        elif ch == 10 or ch == ord('\n'):
            self.form_ready = 0
            curses.curs_set(0)
            return ch
        
        else: 
            return ch

class popUpNewDir(PopUpBase):
    """Creates a pop up and creates a new directory"""
    def __init__(self):
        y, x = wins.stdscr.getmaxyx()
        nlines = int(y/3)
        ncols = int(x/2)
        begin_y = int(y/3)*1
        begin_x = int(x/4)*1
        super().__init__(nlines, ncols, begin_y, begin_x)
        self.win.bkgd(curses.color_pair(3))
        self.win.addstr(1, 1, 'new dir: ', curses.color_pair(3))
        self.win.noutrefresh()
        new_dir_textBox = TextBox(ncols-5, begin_y + 1, begin_x + 1)
        new_dir_button = button(self.win, ['OK', 'CANCEL'])
        new_dir_button.status = 1
        while new_dir_button.status == 1:
            status = new_dir_textBox.action()
            new_dir_button.event(status[1])
            new_dir_button.display()

        if wins.active_panel == 0:
            path = file_explorer_0.abs_path + '/'
        else:
            path = file_explorer_1.abs_path + '/'

        if new_dir_button.action == 0:
            os.mkdir(path + new_dir_textBox.text)
            file_explorer_0.explorer(file_explorer_0.abs_path)
            file_explorer_1.explorer(file_explorer_1.abs_path)
        elif new_dir_button.action == 1:
            self.win.addstr(2,1, 'action cancelled', curses.color_pair(3))

        self.win.noutrefresh()
        time.sleep(2)  
        reset_window(file_explorer_0)
        reset_window(file_explorer_1)

class PopUpDelete(PopUpBase):
    """Creates a pop up and deletes a file after ok/cancel"""
    def __init__(self, sel_file):
        sel_file = sel_file.replace('//','/')
        y, x = wins.stdscr.getmaxyx()
        nlines = int(y/3)
        ncols = int(x/2)
        begin_y = int(y/3)*1
        begin_x = int(x/4)*1
        super().__init__(nlines, ncols, begin_y, begin_x)
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_RED)
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

class PopUpCopyFile(PopUpBase):
    """CopyFile pop up, this is called from key 5 when SSH is not active.

    This class kicks of a second thread to copy the file so it can continue 
    comparing the destination size to the source size and print a progress 
    to the user.
    """
    t = None
    def __init__(self, window, from_file, to_path, file_name):
        y, x = wins.stdscr.getmaxyx()
        super().__init__(7, int(x/2), int(y/3)*1, int(x/4)*1)
        self.bar_width = int(x/2) - 2
        e = None
        try:
            # Start copying on a separate thread
            t = threading.Thread(
                name='CopyThread', target=CopyFile, args=(from_file, to_path), daemon=True)
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
    """Used to created a progress bar.
    
    Used to check the current size of the source and destination files while the file
    copy runs in the background. This helps to create the appearance of a progress bar.
    """
    def __init__(self, source_path, destination_path, file_name, t, callback):
        self.callback = callback
        self.t = t
        self.full_qual_dest_path = destination_path + '/' + file_name
        while not os.path.exists(destination_path):
            callback(t)
            break
        self.src_num = os.path.getsize(source_path)
        self.src_size = human_readable_size(self.src_num)
        self.des_num = 0
        self.des_size = 0
        # Keep checking the file size till it's the same as source file
        try: 
            self.des_num = os.path.getsize(self.full_qual_dest_path)
            self.des_size = human_readable_size(self.des_num)
        except:
            pass
        if self.des_size == self.src_size:
            callback(t)
            self.complete = 0
            
    def status(self):
        if self.des_size != self.src_size:
            try:
                self.des_num = int(float(os.path.getsize(self.full_qual_dest_path)))
                self.des_size = human_readable_size(self.des_num)
            except:
                time.sleep(.05)
                self.des_num = int(float(os.path.getsize(self.full_qual_dest_path)))
                self.des_size = human_readable_size(self.des_num)
        else:
            self.callback(self.t)
            self.complete = 0

class CopyFile:
    """Actual file copy function called when SSH not active and key 5 pressed"""
    def __init__(self, *args):
        source_path, destination_path = args
        length = len(source_path) + len(destination_path) + 13
        try:
            shutil.copy(source_path, destination_path)
            self.action = 0
        except Exception as e:
            self.error = e

class StatusBar:
    """Creates a statusbar at the bottom of the main screen and can be called to update the bar"""
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
        if ssh_obj.is_enabled == True:
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
        self.update()
        curses.doupdate()
        
class init:
    """Possibly equivalent of main.

    Should probably move most of the global stuff at the end of the file to within
    this class.
    """
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
        #future function to detect if termainl is resized
        #resize_check = curses.is_term_resized(nlines, ncols)
        #self.height_main, self.width_main = stdscr.getmaxyx()
        #if resize_check == True:
            #self.term_resize()
        pass

    def term_resize(self):
        #future function to detect if termainl is resized
        curses.resizeterm(self.height_main, self.width_main)

class RSync(PopUpBase):
    """Main Rsync function

    When SSH is activated, this function called by key 5 starts an rsync subprocess using Popen.
    It is meant to run while temporarily suspending curses and returning to the terminal.
    """
    has_been_called = False
    def __init__(self, called_from):
        self.has_been_called = True
        if self.has_been_called == True and called_from == 0:
            msg = 'rsync starting...'
        elif self.has_been_called == False and called_from == 'm':
            if ssh_obj.is_enabled == True:
                msg = 'ssh enabled, rsync ready\n use key c'
        elif ssh_obj == True and called_from == 'm':
            msg = 'ssh must enabled, use rsync'
        elif called_from == 'm':
            msg = 'ssh must be enabled first'
        y, x = wins.stdscr.getmaxyx()
        super().__init__(7, int(x/2), int(y/3)*1, int(x/4)*1)
        self.win.addstr(1, 1, msg)
        self.win.noutrefresh()
        curses.doupdate()
        time.sleep(3)

    def start(self, from_file, to_file, file_name):
        with SuspendCurses():
            print('\nfrom: ' + from_file)
            print('\nto: ' + to_file)
            self.transfer_files(from_file, to_file)
        stdscr.redrawln(0,height_main)
        menu.noutrefresh()
        stdscr.noutrefresh()
        window_0.border()
        window_1.border()
        status.refresh()
        reset_window(file_explorer_0)
        reset_window(file_explorer_1)
        wins.upd_panel()
    
    def transfer_files(self, from_file, to_file):
        """Start subprocess by feeding in server_info from ssh object and selected folders"""
        from_file = shlex.quote(from_file)
        to_file = shlex.quote(to_file)
        server = [ssh_obj.server_info[0],ssh_obj.server_info[1],from_file, to_file]
        if wins.active_panel == 0:
            my_args = [
                "rsync",
                "-Ppav",
                server[2],
                f"{server[1]}@{server[0]}:{server[3]}"
                ]
        elif wins.active_panel == 1:
            my_args = [
                "rsync", 
                "-Ppav", 
                f"{server[1]}@{server[0]}:{server[2]}",
                server[3] 
                + f"/"
                ]

            #my_args = ["rsync", "-Ppave ssh -F /home/apollo/.ssh/ssh_config ",
            #  "{1}@{0}:{2}".format(server[0],server[1],server[2],server[3]),server[3]]

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

class SuspendCurses:
    """Temporarily leave curses while rsync runs"""
    def __enter__(self):
        stdscr.clear()
        stdscr.noutrefresh()
        curses.doupdate()
        stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        os.system('reset')
        print('\nLeaving curses...')
        time.sleep(.5)

    def __exit__(self, exc_type, exc_val, tb):
        print('\nReturning to curses...')
        print('\n')
        time.sleep(.5)
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(1)

class WinManager:
    """Window manager to setup left and right window panels

    This class is meant to setup the left and right windows (panels) for the file explorers,
    select and set the active panel, and update the panels respective file path.
    """
    cur_win = None
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.window_height = my_inst.height_main -2
        self.window_width = int(my_inst.width_main/2)
        self.other_panel = 1
        self.active_panel = 0

    def draw_win(self, window, h, w, y, x, title):
        #draws the initial left and right windows
        window = window.derwin(h, w, y, x)
        window.bkgd(curses.color_pair(4))
        window.box(0,0)
        window.keypad(1)
        window.addstr(0,2,str(title))
        return window

    def left_panel(self):
        #calls draw window and adds parameters for the left panel
        window_0_x_start = 0
        self.window_0 = self.draw_win(
                self.stdscr, 
                self.window_height, 
                self.window_width, 
                1, 
                window_0_x_start, 
                str(start_path)
                )
        return self.window_0

    def right_panel(self):
        #calls draw window and adds parameters for the right panel
        window_1_x_start = int(width_main/2)
        self.window_1 = self.draw_win(
                self.stdscr, 
                self.window_height, 
                self.window_width, 
                1,
                window_1_x_start, 
                str(start_path)
                )
        return self.window_1

    def panel_headers(self):
        #needed to update the left and right panel headers/curent workding directory paths
        #also keeps the headers updated when switching windows
        self.left_head_path = file_explorer_0.abs_path
        self.right_head_path = file_explorer_1.abs_path
        if ssh_obj.is_enabled == True and wins.active_panel == 1:
            try:
                self.right_head_path = ssh_obj.server_info[0] + ':' + file_explorer_1.ssh_abs_path
            except:
                self.right_head_path = file_explorer_1.abs_path
        elif ssh_obj.is_enabled == True and wins.active_panel == 0:
            try:
                self.right_head_path = ssh_obj.server_info[0] + ':' + file_explorer_1.ssh_abs_path
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
        #redraws the panel headers and borders when switching windows
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
        #redraws the panel headers and borders when switching windows
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
            self.other_win = window_1
            self.left_panel_sel()
            #file_explorer_0.display()
        elif i == 1:
            self.other_panel = 0
            self.cur_win = window_1
            self.other_win = window_0
            self.right_panel_sel()
            #file_explorer_1.display()
        self.refreshln1()
        curses.doupdate()

    def upd_panel(self):
        self.set_active_panel(self.active_panel)

"""
Setup curses and begin initializing various packages to draw the menubar,
left and right windows, statusbar, a ssh object for storage, a global options object
for storage and setup the file explorers.
"""
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
menu = MenuBar()
wins = WinManager(stdscr)
start_path = os.path.curdir
window_0 = wins.left_panel()
window_1 = wins.right_panel()
window_0.noutrefresh()
window_1.noutrefresh()
ssh_obj = SSH()
file_explorer_0 = file_explorer(stdscr, window_0, start_path, False)
file_explorer_1 = file_explorer(stdscr, window_1, start_path, False)
paths = []
event = 0
i = 0
file_explorers = [file_explorer_0, file_explorer_1]
status = StatusBar(stdscr, height_main, width_main, '', curses.color_pair(1))
wins.set_active_panel(i)
status.refresh()
glbl_opts = OptionsMenu()
while event != ord('q'):
    while True:
        wins.upd_panel()
        file_explorers[i].display()
        event = file_explorers[i].event
        stdscr.noutrefresh()
        if event in (ord('\t'), ord('q')):
            break
        elif event == ord('f') or event == ord ('o'):
            event = menu.menubar_act(event)
            menu.display()
            if ssh_obj.is_enabled == True:
                i = 1
            if event == ord('\t') or event == ord('f'):
                break
            if event == ord('q'):
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
if ssh_obj.is_enabled == True:
    ssh_obj.ssh.close()

exit_program()
