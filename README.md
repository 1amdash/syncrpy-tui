<img width="784" alt="image" src="https://user-images.githubusercontent.com/79387780/233872359-97f2235d-e21e-4932-a63d-1c1a15f25ea1.png">

SyncRPy - Python Terminal User Interface File Manager

This is a Python terminal user interface program that allows you to manage files and folders using a rsync, a powerful file transfer and synchronization tool. With this program, you can easily synchronize files between two directories, copy files to and from remote servers, and backup your files to a remote server.

Installation

Clone the repository:

bash

Copy code

git clone https://github.com/1amdash/rsync-tui/main.git

Navigate to the project directory:

bash

Copy code

cd rsync-tfm

Install the dependencies:

Copy code

pip install -r requirements.txt

Usage

To start the program, run the following command:

python rsync-tui.py

Arrow Keys: Move throughout the menus

Tab Key: Switch between left and right file panels

Q Key: Quit

9 Key: Delete File OR Directory

5 Key: Copy File or Directory

--if SSH is activated, use RSync

N Key: Make New Directory

X Key: Close SSH Connection, if established

Dependencies:

Curses
Paramiko

The program will launch in the terminal. You can choose from the following options:

Sync files: This option allows you to synchronize files between two directories. You will be prompted to enter the source directory and the destination directory. The program will then use rsync to copy any new or modified files from the source directory to the destination directory.

Copy files to remote server: This option allows you to copy files to a remote server using rsync. You will be prompted to enter the source directory, the remote server address, and the destination directory on the remote server. The program will then use rsync to copy the files to the remote server.

Copy files from remote server: This option allows you to copy files from a remote server using rsync. You will be prompted to enter the remote server address, the source directory on the remote server, and the destination directory on your local machine. The program will then use rsync to copy the files from the remote server to your local machine.

Backup files to remote server: This option allows you to backup your files to a remote server using rsync. You will be prompted to enter the source directory on your local machine, the remote server address, and the destination directory on the remote server. The program will then use rsync to copy the files to the remote server.

License

This project is licensed under the MIT License. See the LICENSE file for details.

Contributions

Contributions to this project are welcome. If you would like to contribute, please fork the repository and submit a pull request.
