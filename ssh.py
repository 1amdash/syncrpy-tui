from multiprocessing import AuthenticationError
import paramiko
import curses
from raise_api_error import RaiseAPIError
from pop_ups import PopUpBase
from queue_window_refresh import QueueWinRefresh
from text_box import TextBox
from suspend_curses import SuspendCurses 
from time import sleep
from getpass import getpass


class SSH:
    """
    Sets up and enables a paramiko ssh client.

    Takes users input (ip address, username) by calling SSHForm and
    feeds the paramiko ssh client. During setup curses is suspended to 
    use getpass and enter the password.
    """
    is_enabled = False
    def __init__(self):
        self.server_info = []
        self.ssh = ''
        self.sftp = None
        self.ssh_path = None

    def setup_SSHForm(self, stdscr):
        return SSHForm
        
    def start(self, win_manager, stdscr, status):
        self.win_manager = win_manager
        form = SSHForm(stdscr) 
        self.server_info.append(form.info[0]) # Ip address
        self.server_info.append(form.info[1]) # Username
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        with SuspendCurses(stdscr):
            return_to_curses = False
            while return_to_curses is not True:
                try:
                    if form.info[0] == '' or form.info[1] == '':
                        print('\nNah dawg... enter a hostname/ip and username')
                        sleep(3)
                        return 0
                    passwd = getpass()
                    print('\nAuthenticating...')
                    self.ssh.connect(
                        form.info[0],
                        username=form.info[1],
                        password=passwd,
                        compress=True
                        )
                    self.get_transport(self.ssh)
                    self.sftp = self.ssh.open_sftp()
                    self.win_manager.update_headers(1)
                    return_to_curses = self.enabled()
                except AuthenticationError as error:
                    print(error)
                    continue
                except (ConnectionError, ConnectionRefusedError) as error:
                    print(error)
                    print('\n')
                    sleep(3)
                    return_to_curses = True
                except Exception as error:
                    print(error)
                    print('Returning to curses.')
                    sleep(3)
                    return_to_curses = True

    def get_transport(self, ssh):
        self.transport = ssh.get_transport()

    def enabled(self):
        if self.transport.is_active():
            self.is_enabled = True
            return True
        else:
            self.is_enabled = False
            return False

    def ssh_close(self):
        if self.is_enabled:
            self.ssh.close()

class SSHForm(PopUpBase):
    """PopUp form which relies on PopUpBase and TextBox to create a IP address/username form."""
    info = []
    def __init__(self, stdscr):
        nlines, ncols = stdscr.getmaxyx()
        nlines = int(nlines/4)
        ncols = int(ncols/4)
        begin_y = nlines
        begin_x = ncols
        super().__init__(10,ncols, begin_y,begin_x, stdscr)
        self.win.bkgd(curses.color_pair(2))
        self.win.attron(curses.color_pair(2))
        self.win.border()
        self.win.addstr(1,1, 'IP Address')
        self.win.addstr(5,1, 'Username')
        QueueWinRefresh(self.win) 
        self.textbox1 = TextBox(ncols-5, begin_y + 1, begin_x + 1)
        self.textbox2 = TextBox(ncols-5, begin_y + 5, begin_x + 1)
        curses.doupdate()
        self.input()

    def input(self):  
        form_ready = False
        while form_ready != True:
            curses.curs_set(2)
            self.win.move(3, 2)
            QueueWinRefresh(self.win)
            curses.doupdate()
            textbox1_info = self.textbox1.action()
            form_ready = textbox1_info[1]
            self.win.move(7, 2)
            QueueWinRefresh(self.win)
            curses.doupdate()
            textbox2_info = self.textbox2.action()
            form_ready = textbox2_info[1]
        if form_ready:
            self.info.append(textbox1_info[0])
            self.info.append(textbox2_info[0])
        self.win.erase()
        return self.info
