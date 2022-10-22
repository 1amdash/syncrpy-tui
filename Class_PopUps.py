from Class_QueueWinRefresh import QueueWinRefresh
import constants as CONST
import curses

from Class_PopUpBase import PopUpBase
class PopUpNewDir(PopUpBase):
    """Creates a pop up and creates a new directory"""
    def __init__(self):
        y, x = win_manager.screen_size()
        nlines = int(y/3)
        ncols = int(x/2)
        begin_y = int(y/3)*1
        begin_x = int(x/4)*1
        super().__init__(nlines, ncols, begin_y, begin_x, stdscr)
        self.win.bkgd(curses.color_pair(2))
        self.win.addstr(1, 1, 'new dir: ', curses.color_pair(2))
        QueueWinRefresh(self.win) 
        new_dir_textbox = TextBox(ncols-2, begin_y + 1, begin_x + 1)
        self.new_dir_button = Button(self.win, ['OK', 'CANCEL'])
        ready = False
        while ready is not True:
            self.text_and_status = new_dir_textbox.action()
            ready = self.text_and_status[1]
            self.new_dir_name = self.text_and_status[0]
            self.new_dir_button.event(ready)
            self.new_dir_button.display()

            if self.new_dir_button.button_press_cancel:
                break
        
        if ready:
            self.create_dir()
        else:
            self.cancel()

    def create_dir(self):
        if win_manager.active_panel == 0:
            new_directory_location = left_file_explorer.abs_path + '/'
        else:
            new_directory_location = right_file_explorer.abs_path + '/'
        os.mkdir(new_directory_location + self.new_dir_name)
        left_file_explorer.explorer(left_file_explorer.abs_path)
        right_file_explorer.explorer(right_file_explorer.abs_path)
        self.close() 

    def cancel(self):           
        self.win.addstr(2,1, 'action cancelled', curses.color_pair(2))
        self.close() 

    def close(self):
        QueueWinRefresh(self.win)
        ResetWindow(left_file_explorer)
        ResetWindow(right_file_explorer)

class PopUpDelete(PopUpBase):
    """Creates a pop up and deletes a file after ok/cancel"""
    def __init__(self, sel_file):
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
                left_file_explorer.explorer(left_file_explorer.abs_path)
                right_file_explorer.explorer(right_file_explorer.abs_path)
            else:
                self.win.addstr(2,1, 'Delete cancelled.', curses.color_pair(8))
            QueueWinRefresh(self.win) 
            time.sleep(.5)
            ResetWindow(left_file_explorer)
            ResetWindow(right_file_explorer)
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
    def __init__(self, stdscr, file_info, event=None, sftp=None, sftp_path=None):
        y, x = stdscr.getmaxyx()
        super().__init__(y - 5, x - 5, 2, 2, stdscr)
        #now using self.win from base
        pop_up_size_y, pop_up_size_x = stdscr.getmaxyx()
        self.win.attron(curses.color_pair(2))
        self.win.bkgd(curses.color_pair(2))
        self.win.box(0,0)
        self.win.addstr(0, 2, str(file_info).replace('//','/') + ' - press q to exit')
        QueueWinRefresh(self.win)
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
        count = 0
        for line in file_lines:
            count += 1
        pop_up_pad = curses.newpad(count + 2, pop_up_size_x -2)
        pop_up_pad.bkgd(curses.color_pair(2))
        count = 0

        for line in file_lines:
            count += 1
            if len(line) > pop_up_size_x:
                pop_up_pad.addstr(count, 1,  'toolong', curses.color_pair(2))
                break
            pop_up_pad.addstr(count, 1,  line, curses.color_pair(2))
        
        self.win.keypad(1)
        pop_up_panel = curses.panel.new_panel(self.win)
        pop_up_panel.top()
        pop_up_panel.show()
        width = pop_up_size_x-5
        scroller = 0
        scroller_hor = 0
        def pop_up_pad_refresh(): pop_up_pad.noutrefresh(
            scroller, scroller_hor, 3, 3, pop_up_size_y-5, width)
        while True:
            pop_up_pad_refresh()
            curses.doupdate()
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
            elif ch == CONST.CONST_LET_B_LWRCSE_KEY:
                scroller = cursor[0] - pop_up_size_y + 7
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
                ResetWindow(left_file_explorer)
                ResetWindow(right_file_explorer)
                curses.doupdate()
                try:
                    file1.close()
                except:
                    self.win.nodelay(0)
                    break
                self.win.nodelay(0)
                break
    


class PopUpCopyFile(PopUpBase):
    """CopyFile pop up, this is called from key 5 when SSH is not active.

    This class kicks of a second thread to copy the file so it can continue
    comparing the destination size to the source size and print a progress
    to the user.
    """
    t = None
    def __init__(self, window, from_file, to_path, file_name):
        y, x = stdscr.getmaxyx()
        super().__init__(7, int(x/2), int(y/3)*1, int(x/4)*1, stdscr)
        self.bar_width = int(x/2) - 2
        try:
            # Start copying on a separate thread
            t = threading.Thread(
                name='CopyThread', target=CopyFile, args=(from_file, to_path), daemon=True)
            t.start()
            t.is_started = True
        except Exception as e:
            error
        if error:
            progress = ProgressChecker(from_file, to_path, file_name, t, callback=callbackFunc)
        try:
            while True:
                if e == None:
                    progress.status()
                    self.win.addstr(1, 1, 'from: ' + from_file )
                    self.win.addstr(2, 1, 'to: ' + to_path)
                    self.win.addstr(3, 1, str(progress.des_size) + ' / ' + str(progress.src_size))
                    self.percentage = int(
                        float(progress.des_num / progress.src_num)* self.bar_width
                        )
                    self.stars = '*' * self.percentage
                    self.win.addstr(4, 1, "{0}{1}".format('[',self.stars))
                    self.win.addstr(4,self.bar_width, ']')
                else:
                    self.win.addstr(3, 1, str(error))
                    time.sleep(5)
                QueueWinRefresh(self.win) 
                curses.doupdate()
                if progress.des_size == progress.src_size:
                    self.win.addstr(5, 1, 'Complete')
                    QueueWinRefresh(self.win)
                    curses.doupdate()
                    callbackFunc(t)
                    time.sleep(3)
                    return
        except KeyboardInterrupt:
            callbackFunc(t)
            QueueWinRefresh(self.win)
            curses.doupdate()

        if win_manager.active_panel == 0:
            right_file_explorer.explorer(right_file_explorer.cwd)
            ResetWindow(right_file_explorer)
        else:
            left_file_explorer.explorer(left_file_explorer.cwd)
            ResetWindow(left_file_explorer)