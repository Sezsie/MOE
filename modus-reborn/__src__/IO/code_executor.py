# a suite of tools designed to execute code in a safe and secure manner on the user's machine.

import os 
import subprocess
import threading

from __src__.UTILS.utils import Utilities

utils = Utilities()
OS = utils.getOS()

class CodeExecutor:
    def __init__(self):
        pass

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
            with open("modus-reborn\\__bin__\\temp.bat", "w") as f:
                f.write(code)
            process = subprocess.Popen(["cmd", "/c", "modus-reborn\\__bin__\\temp.bat"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            os.remove("modus-reborn\\__bin__\\temp.bat")
            return output.decode("utf-8")
        except Exception as e:
            return str(e)

    def execute_linux_code(self, code):
        try:
            with open("modus-reborn/__bin__/temp.sh", "w") as f:
                f.write(code)
            process = subprocess.Popen(["bash", "modus-reborn/__bin__/temp.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            os.remove("modus-reborn/__bin__/temp.sh")
            return output.decode("utf-8")
        except Exception as e:
            return str(e)