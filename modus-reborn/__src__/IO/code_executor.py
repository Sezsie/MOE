# a suite of tools designed to execute code in a safe and secure manner on the user's machine.

import os 
import subprocess

from __src__.UTILS.utils import Utilities

utils = Utilities()
OS = utils.getOS()

# a class that executes code on the user's machine, depending on the operating system.

class CodeExecutor:
    def __init__(self):
        pass

    def execute_code(self, code):
        print(f"Executing code: {code}")
        if OS == "Windows":
            # remove the pause keyword from the code if it exists
            code = code.replace("pause", "")
            return self.execute_windows_code(code)
        else:
            return self.execute_linux_code(code)

    def execute_windows_code(self, code):
        try:
            with open("modus-reborn\\__bin__\\temp.bat", "w") as f:
                f.write(code)
            process = subprocess.Popen(["cmd", "/c", "modus-reborn\\__bin__\\temp.bat"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            os.remove("modus-reborn\\__bin__\\temp.bat")
            return output.decode("utf-8")
        except Exception as e:
            print(e)
            return str(e)



    def execute_linux_code(self, code):
        try:
            with open("modus-reborn/__bin__/temp.sh", "w") as f:
                f.write(code)
            process = subprocess.call(["bash", "modus-reborn/__bin__/temp.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            os.remove("modus-reborn/__bin__/temp.sh")
            return output.decode("utf-8")
        except Exception as e:
            return str(e)