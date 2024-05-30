# a suite of tools designed to execute code in a safe and secure manner on the user's machine.

import os 
import subprocess
import threading

from __src__.IO.handle_ui import ConfirmationUI
from __src__.DATA.manage_files import FileManager

files = FileManager()
OS = files.OS

# for code moderation we use a fairly naive approach by checking for dangerous keywords in the code
# this isn't foolproof, and these lists are absolutely not comprehensive, but they should keep most common garbage code from being ran, since the user is shown the code in combination with this.
dangerous_keywords_windows = [
    "format", "del", "erase", "rd", "rmdir", "shutdown", "reg", "diskpart", 
    "cipher", "vssadmin", "bootrec", "bcdedit", "chkdsk", "fsutil", 
    "taskkill", "sfc", "powershell", "wpeutil", "takeown", "icacls", "sc", 
    "netsh", "attrib", "mklink", "schtasks", "wusa", "msiexec", "reagentc", 
    "diskshadow", "bdehdcfg", "wbadmin", "defrag", "gpupdate", "secedit", 
    "lodctr", "wevtutil"
]

dangerous_keywords_linux = [
    "rm", "dd", "mkfs", "fdisk", "parted", "chmod", "chown", "init", 
    "shutdown", "reboot", "halt", "poweroff", "kill", "killall", "pkill", 
    "wget", "curl", "mount", "umount", "passwd", "useradd", "userdel", 
    "usermod", "groupadd", "groupdel", "groupmod", "iptables", "systemctl", 
    "service", "cron", "crontab", "visudo", "sudo", "su", "ddrescue", "ln", 
    "mktemp", "echo", "tar", "gzip", "bzip2", "unzip", "rsync", "scp", "ftp", 
    "nc", "ifconfig", "ip", "route", "hostname", 
    "sysctl", "chroot", "lsattr", "chattr"
]

# returns a list of dangerous keywords found in the code
def check_for_dangerous_keywords(code, OS):
    lines = code.split("\n")
    dangerous_keywords = []
    for line in lines:
        # skip comment lines
        if line.strip().startswith("#") or line.strip().startswith("//") or line.strip().startswith("REM") or line.strip().startswith("::"):
            continue
        
        keywords = dangerous_keywords_windows if OS == "Windows" else dangerous_keywords_linux
        for keyword in keywords:
            if keyword in line:
                # add the keyword to the list of dangerous keywords if its not already there
                if keyword not in dangerous_keywords:
                    dangerous_keywords.append(keyword)
                break
    return dangerous_keywords

def format_message(danger_keys):
    if len(danger_keys) > 1:
        message = f"WARNING: The code you are about to run contains potentially dangerous keywords: {', '.join(danger_keys[:-1])} and {danger_keys[-1]}.\nAre you sure you want to run this code?"
    else:
        message = f"WARNING: The code you are about to run contains a potentially dangerous keyword: {danger_keys[0]}.\nAre you sure you want to run this code?"
    return message

class CodeExecutor:
    def __init__(self):
        self.executeableFolder = files.locateDirectory("scripts")
        print(f"Executeable Folder: {self.executeableFolder}")
    
    # TODO: this current ui is extremely sloppy!! make it scale to the text inside of the label later.
    def display_confirmation_dialog(self, code, danger_keys):
        confirmation_ui = ConfirmationUI()
        # unpack the list of dangerous keys into a string
        message = format_message(danger_keys)
        confirmation_ui.set_label(message)
        # enable word wrap
        confirmation_ui.label.setWordWrap(True)
        # add a button to run the code if the user greenlights it
        confirmation_ui.add_button("Yes", lambda: (confirmation_ui.close(), self.execute_code(code)))
        # add a button to close the dialog
        confirmation_ui.add_button("No", lambda: confirmation_ui.close())
        confirmation_ui.setFixedSize(600, 150)
        confirmation_ui.show()
    
    def moderate_code(self, code):
        
        dangerous_keys = check_for_dangerous_keywords(code, OS)
        
        # if the dangerous keywords are found, return the lines of code that contain them
        if dangerous_keys:
            self.display_confirmation_dialog(code, dangerous_keys)
        else: 
            # otherwise just execute the code
            self.execute_code(code)
        
        
    def execute_code(self, code):
        thread = None
        
        print(f"Executing code: {code}")
        # in separate threads, execute the code based on the user's operating system
        if OS == "Windows":
            thread = threading.Thread(target=self.execute_windows_code, args=(code,))
        else:
            thread = threading.Thread(target=self.execute_linux_code, args=(code,))
            
        thread.start()

    def execute_windows_code(self, code):
        try:
            # create a file with the code to execute
            script = files.createFile(self.executeableFolder, "windows_executing.bat", code)
            
            print(f"Script: {script}")
            
            # execute the script
            process = subprocess.Popen(["cmd", "/c", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # get the output and error from the process
            output, error = process.communicate()
            
            # delete the script after execution
            files.deleteFile("windows_executing.bat")
            return output.decode("utf-8")
        except Exception as e:
            return str(e)

    def execute_linux_code(self, code):
        try:
            # create a file with the code to execute
            script = files.createFile(self.executeableFolder, "linux_executing.sh", code)
            
            # execute the script
            process = subprocess.Popen(["bash", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # get the output and error from the process
            output, error = process.communicate()
            
            # delete the script after execution
            files.deleteFile("linux_executing.sh")
            return output.decode("utf-8")
        except Exception as e:
            return str(e)