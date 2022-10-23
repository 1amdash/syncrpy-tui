import subprocess
import shlex

class RSync(PopUpBase):
    """Main Rsync function

    When SSH is activated, this function called by key 5 starts an rsync subprocess using Popen.
    It is meant to run while temporarily suspending curses and returning to the terminal.
    """
    has_been_called = False
    def __init__(self, called_from):
        self.has_been_called = True
        if self.has_been_called and called_from == 0:
            msg = 'rsync starting...'
        elif not self.has_been_called and called_from == 'm':
            if SSH.is_enabled:
                msg = 'ssh enabled, rsync ready\n use key c'
        elif ssh_obj and called_from == 'm':
            msg = 'ssh must enabled, use rsync'
        elif called_from == 'm':
            msg = 'ssh must be enabled first'
        screen_y, screen_x = win_manager.stdscr.getmaxyx()
        super().__init__(7, int(screen_x/2), int(screen_y/3), int(screen_x/4))
        self.win.addstr(1, 1, msg)
        QueueWinRefresh(self.win)
        curses.doupdate()
        time.sleep(3)

    def start(self, from_file, to_file, file_name):
        with SuspendCurses():
            print('\nfrom: ' + from_file)
            print('\nto: ' + to_file)
            self.transfer_files(from_file, to_file)
        stdscr.redrawln(0,win_manager.screen_height)
        QueueWinRefresh(stdscr) #stdscr.noutrefresh()
        left_win.border()
        right_win.border()
        status.refresh()
        ResetWindow(left_file_explorer)
        ResetWindow(right_file_explorer)
        win_manager.upd_panel()

    def transfer_files(self, from_file, to_file):
        """Start subprocess by feeding in server_info from ssh object and selected folders"""
        from_file = shlex.quote(from_file)
        to_file = shlex.quote(to_file)
        server = [ssh_obj.server_info[0],ssh_obj.server_info[1],from_file, to_file]
        if win_manager.active_panel == 0:
            my_args = [
                "rsync",
                "-Ppav",
                server[2],
                f"{server[1]}@{server[0]}:{server[3]}"
                ]
        elif win_manager.active_panel == 1:
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
