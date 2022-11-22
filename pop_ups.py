"""pop_ups module"""
from pathlib import Path
import shutil
import threading
import constants as CONST
import curses
from display import Display
#from key_press import KeyPress
from queue_window_refresh import QueueWinRefresh
from reset_window import ResetWindow
from copy_file import CopyFile
from progress_checker import ProgressChecker
from button import Button
from text_box import TextBox

class PopUpBase:
    """Creates a new window with basic sizing and formatting for various popups"""
    def __init__(self, nlines, ncols, begin_y, begin_x, stdscr):
        self.par_win_size_y, self.par_win_size_x = stdscr.getmaxyx()
        self.y = int(self.par_win_size_y/4)
        self.x = int(self.par_win_size_x/4)
        self.h = int(self.par_win_size_y/2)
        self.w = 25 # int(self.par_win_size_x*.5)
        self.win = curses.newwin(nlines, ncols, begin_y, begin_x)
        self.win.attron(curses.color_pair(2))
        self.win.bkgd(curses.color_pair(2))
        self.win.border()
        QueueWinRefresh(self.win) 

    def msg(self, msg):
        """Will act as an alert/error window, where the msg argument can be an exception to print"""
        self.win.addstr(1,1, msg, curses.color_pair(2))
        QueueWinRefresh(self.win)
        
class PopUpNewDir(PopUpBase):
    """Creates a pop up and creates a new directory"""
    def __init__(self, obj, KeyPress):
        self.obj = obj
        stdscr = self.obj.win_manager.stdscr
        self.left_file_explorer = self.obj.left_file_explorer
        self.right_file_explorer = self.obj.right_file_explorer
        y,x = stdscr.getmaxyx()
        nlines = int(y/3)
        ncols = int(x/2)
        begin_y = int(y/3)*1
        begin_x = int(x/4)*1
        super().__init__(nlines, ncols, begin_y, begin_x, stdscr)
        self.win.bkgd(curses.color_pair(2))
        self.win.addstr(1, 1, 'New Directory:', curses.color_pair(2))
        QueueWinRefresh(self.win)
        self.new_dir_textbox = TextBox(ncols-2, begin_y + 1, begin_x + 1)
        self.new_dir_button = Button(self.win, ['OK', 'CANCEL'])
        self.new_dir_form(KeyPress)

    def new_dir_form(self,KeyPress):   
        return_to_loop = False
        ready = False

        while ready is not True:

            self.text_and_status = self.new_dir_textbox.action()
            ready = self.text_and_status[1]
            self.new_dir_name = self.text_and_status[0]
            self.new_dir_button.event(ready)
            #self.new_dir_button.display()
            while return_to_loop is not True:
                key_press = KeyPress(self.new_dir_button, self.new_dir_button.item_list, self.new_dir_button.position)
                Display(self.new_dir_button)
                if key_press.key in (CONST.CONST_ENTER_KEY, CONST.CONST_TAB_KEY):
                    return_to_loop = True
                

            if self.new_dir_button.button_press_cancel:
                break
            elif self.new_dir_button.button_press_ok:
                ready = True
        
        if ready:
            self.create_dir()
        else:
            self.cancel()

    def create_dir(self):
        if self.obj.win_manager.active_panel == 0:
            new_directory_location = self.left_file_explorer.full_path + '/'
        else:
            new_directory_location = right_file_explorer.full_path + '/'
        p = Path(new_directory_location, self.new_dir_name)
        p.mkdir()
        #os.mkdir(new_directory_location + self.new_dir_name)
        #self.left_file_explorer.explorer(self.left_file_explorer.full_path)
        #self.right_file_explorer.explorer(self.right_file_explorer.full_path)
        self.close() 

    def cancel(self):           
        self.win.addstr(2,1, 'action cancelled', curses.color_pair(2))
        self.close() 

    def close(self):
        QueueWinRefresh(self.win)
        ResetWindow(self.left_file_explorer)
        ResetWindow(self.right_file_explorer)

class PopUpDelete(PopUpBase):
    """Creates a pop up and deletes a file after ok/cancel"""
    def __init__(self, obj, sel_file):
        self.obj = obj
        stdscr = self.obj.win_manager.stdscr
        self.sel_file = sel_file.replace('//','/')
        y, x = stdscr.getmaxyx()
        nlines = int(y/3)
        ncols = int(x/2)
        begin_y = int(y/3)*1
        begin_x = int(x/4)*1
        super().__init__(nlines, ncols, begin_y, begin_x, stdscr)
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_RED)
        self.win.bkgd(curses.color_pair(8))
        self.win.addstr(1, 1, 'delete file: ' + self.sel_file, curses.color_pair(8))
        QueueWinRefresh(self.win) 
        self.del_button = Button(self.win, ['OK', 'CANCEL'])
        self.action()

    def action(self):
        while True:
            self.del_button.display()
            self.sel_file = self.sel_file.replace('//','/')
            if self.del_button.position == 0:
                if os.path.isdir(self.sel_file):
                    try:
                        self.action_delete_folder(self.sel_file)
                    except FileNotFoundError:
                        self.action_delete_tree(self.sel_file)
                else:
                    try:
                        self.action_delete_file(self.sel_file)
                    except PermissionError:
                        self.win.addstr(2,1,'permission denied', curses.color_pair(8))
                        QueueWinRefresh(self.win) 
                self.left_file_explorer.explorer(self.left_file_explorer.abs_path)
                self.right_file_explorer.explorer(self.right_file_explorer.abs_path)
            else:
                self.win.addstr(2,1, 'Delete cancelled.', curses.color_pair(8))
            QueueWinRefresh(self.win) 
            time.sleep(.5)
            ResetWindow(self.left_file_explorer)
            ResetWindow(self.right_file_explorer)
            return

    def action_delete_file(self, file_to_delete):
        os.remove(file_to_delete)

    def action_delete_folder(self, folders):
        os.removedirs(folders)

    def action_delete_tree(self, tree):
        self.win.addstr(2, 1, 'directory not empty, ok?', curses.color_pair(8))
        QueueWinRefresh(self.win)
        self.del_button.display()
        if self.del_button.position == 0:
            shutil.rmtree(tree)
        else:
            pass    


class PopUpFileOpener(PopUpBase):        
    def __init__(self, file_explorers, stdscr, file_info, event=None, sftp=None, sftp_path=None):
        y, x = stdscr.getmaxyx()
        self.left_file_explorer = file_explorers[0]
        self.right_file_explorer = file_explorers[1]
        super().__init__(y - 5, x - 5, 2, 2, stdscr)
        #now using self.win from base
        self.pop_up_size_y = y
        self.pop_up_size_x = x
        self.win.attron(curses.color_pair(2))
        self.win.bkgd(curses.color_pair(2))
        self.win.box(0,0)
        self.win.addstr(0, 2, str(file_info).replace('//','/') + ' - press q to exit')
        QueueWinRefresh(self.win)

        file, file_lines = self.open_file(file_info)
        self.display_file(file, file_lines)


    def open_file(self, file_info):
        try:
            file1 = open(file_info,'r', encoding='utf-8')
            file_lines = file1.readlines()
        except PermissionError:
            file_lines = "Permission Denied"
        except UnicodeDecodeError:
            file_lines = 'Error'
        except:
            file_lines ='other error'
            try:
                remote_file = sftp.file(sftp_path + file_info, 'r')
                file_lines = remote_file.readlines()
            except Exception as e:
                print(e)
        return file1, file_lines

    def display_file(self, file, file_lines):
        num_of_rows = 0
        for line in file_lines:
            num_of_rows += 1
        pop_up_pad = curses.newpad(num_of_rows + 2, self.pop_up_size_x -2)
        pop_up_pad.bkgd(curses.color_pair(2))
        
        num_of_cols = 0
        for line in file_lines:
            num_of_cols += 1
            if len(line) > self.pop_up_size_x:
                pop_up_pad.addstr(num_of_cols, 1,  'toolong', curses.color_pair(2))
                break
            pop_up_pad.addstr(num_of_cols, 1,  line, curses.color_pair(2))
        
        self.win.keypad(1)
        pop_up_panel = curses.panel.new_panel(self.win)
        pop_up_panel.top()
        pop_up_panel.show()
        width = self.pop_up_size_x-5
        scroller = 0
        scroller_hor = 0

        def pop_up_pad_refresh(): pop_up_pad.noutrefresh(
            scroller, scroller_hor, 3, 3, self.pop_up_size_y-5, width)
        while True:
            pop_up_pad_refresh()
            curses.doupdate()
            self.win.nodelay(1)
            ###pop up getch
            ch = self.win.getch()
            cursor = pop_up_pad.getyx()
            if ch == curses.KEY_UP and num_of_rows > self.pop_up_size_y:
                scroller  -= 1
                if scroller <= 0:
                    scroller = 0
            elif ch == curses.KEY_DOWN and num_of_rows > self.pop_up_size_y:
                scroller += 1
                if scroller >= cursor[0]:
                    scroller = cursor[0]
            elif ch == CONST.CONST_LET_B_LWRCSE_KEY:
                scroller = cursor[0] - self.pop_up_size_y + 7
            elif ch == CONST.CONST_LET_T_LWRCSE_KEY:
                scroller = 0
            elif ch == curses.KEY_RIGHT and len(line) > width:
                scroller_hor += 1
            if ch == CONST.CONST_LET_Q_LWRCSE_KEY:
                pop_up_panel.hide()
                curses.panel.update_panels()
                pop_up_pad.erase()
                self.win.erase()
                QueueWinRefresh(self.win)
                ResetWindow(self.left_file_explorer)
                ResetWindow(self.right_file_explorer)
                curses.doupdate()
                try:
                    file.close()
                except:
                    self.win.nodelay(0)
                    break
                self.win.nodelay(0)
                break
    
def callbackFunc(thread):
    thread._is_stopped = True

class PopUpCopyFile(PopUpBase):
    """CopyFile pop up, this is called from key 5 when SSH is not active.

    This class kicks off a second thread to copy the file so it can continue
    comparing the destination size to the source size and print a progress
    to the user.
    """
    t = None
    def __init__(self, file_explorers, stdscr, from_file, to_path, file_name):
        self.left_file_explorer = file_explorers[0]
        self.right_file_explorer = file_explorers[1]
        screen_height, screen_width = stdscr.getmaxyx()
        super().__init__(7, int(screen_width/2), int(screen_height/3), int(screen_width/4), stdscr)
        self.bar_width = self.set_bar_width(screen_width)
        QueueWinRefresh(self.win)
        curses.doupdate()

        #try:
        # Start copying on a separate thread
        t = threading.Thread(
            name='CopyThread', target=CopyFile, args=(from_file, to_path), daemon=True)
        t.start()
        t.is_started = True
        progress = ProgressChecker(from_file, to_path, file_name, t, callback=callbackFunc)
        try:
            while True:
                progress.status()
                self.win.addstr(1, 1, 'from: ' + from_file, curses.color_pair(2) )
                self.win.addstr(2, 1, 'to: ' + to_path,curses.color_pair(2))
                self.win.addstr(3, 1, str(progress.des_size) + ' / ' + str(progress.src_size),curses.color_pair(2))
                self.percentage = self.get_bar_percentage(self.bar_width, progress.src_num, progress.des_num)

                self.stars = '*' * self.percentage
                self.win.addstr(4, 1, "{0}{1}".format('[',self.stars))
                self.win.addstr(4,self.bar_width, ']')
                QueueWinRefresh(self.win) 
                curses.doupdate()
                self.is_bar_complete(progress.src_size, progress.des_size, self.win, thread=t)

        except PermissionError as error:
            self.win.addstr(4, 1, str(error) )

        except KeyboardInterrupt:
            callbackFunc(t)
            
        QueueWinRefresh(self.win)
        curses.doupdate()

        if win_manager.active_panel == 0:
            self.right_file_explorer.explorer(self.right_file_explorer.cwd)
            ResetWindow(self.right_file_explorer)
        else:
            self.left_file_explorer.explorer(self.left_file_explorer.cwd)
            ResetWindow(self.left_file_explorer)

    @staticmethod
    def set_bar_width(screen_width):
        return int(screen_width/2) - 2

    @staticmethod
    def get_bar_percentage(bar_width, src_num, des_num):
        return int(float(des_num / src_num)* bar_width)

    @staticmethod
    def is_bar_complete(src_size, des_size, win, thread):
        if des_size == src_size:
            win.addstr(5, 1, 'Complete')
            QueueWinRefresh(win)
            curses.doupdate()
            callbackFunc(thread)
            time.sleep(3)
            return