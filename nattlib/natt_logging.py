# Filename : natt_logging.py
# Release time : 2024.07.09
# Version:1.1.2
# by:Xiaodong Fan
import time
import locale
import json
import subprocess

def now_time():
    return str(time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))

class dong_log:

    def __init__(self):
        self.debug_filename = '/opt/sost/log/natt_cmd.log'
        self.json_filename = '/opt/natt/config/natt_config.json'
        self.system_code = locale.getpreferredencoding()
        self.popen_debug = False
        #控制报错打印是否退出
        self.error_exit = False
        self.fail_exit = False
        self.warning_exit = False
        #增加debug控制点
        self.d_p_flag = False

    def warning(self,text):
        with open(self.debug_filename, 'a') as f:
            f.write('============================================================\n')
            f.write(f'Type    : warning\n')
            f.write(f'Time    : {now_time()}\n')
            f.write(f'details : {text}\n')
            f.write('============================================================\n')
        print(f"<natt> Warning : {str(text).strip()}")
        if self.warning_exit:exit()

    def tips(self,text):
        with open(self.debug_filename, 'a') as f:
            f.write('============================================================\n')
            f.write(f'Type    : tips\n')
            f.write(f'Time    : {now_time()}\n')
            f.write(f'details : {text}\n')
            f.write('============================================================\n')
        print(f"<natt> Tips {str(text).strip()}")

    def error(self,text):
        with open(self.debug_filename, 'a') as f:
            f.write('============================================================\n')
            f.write(f'Type    : error\n')
            f.write(f'Time    : {now_time()}\n')
            f.write(f'details : {text}\n')
            f.write('============================================================\n')
        print(f"<natt> Error : {str(text).strip()}")
        if self.error_exit:exit()

    def fail(self,text):
        with open(self.debug_filename, 'a') as f:
            f.write('============================================================\n')
            f.write(f'Type    : fail\n')
            f.write(f'Time    : {now_time()}\n')
            f.write(f'details : {text}\n')
            f.write('============================================================\n')
        print(f"<natt> Fail : {str(text).strip()}")
        if self.fail_exit: exit()
    def exitt(self,text):
        with open(self.debug_filename, 'a') as f:
            f.write('============================================================\n')
            f.write(f'Type    : exit()\n')
            f.write(f'Time    : {now_time()}\n')
            f.write(f'details : {text}\n')
            f.write('============================================================\n')
        exit()
    #SaveCommandResult
    def popen(self,command):
        with open(self.debug_filename, "a",encoding = "utf-8") as f:
            f.write('============================================================\n')
            f.write(f'Type    : subprocess.Popen\n')
            f.write(f'Command : {command}\n')
            f.write(f'RunTime : {now_time()}\n')
            f.write(f'Result  : \n')
            result = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).stdout.read().decode(str(self.system_code))
            f.write(result.replace("\n","").replace("\n\n",""))
            f.write('\n============================================================\n')
            if self.popen_debug:print(f"Nowtime : {now_time()}\nCommand : {command}\nResult ： {str('='*60)} {result}")
        return result
    #RunCommandNoSaveResult
    def run(self,command):
        with open(self.debug_filename, 'a',encoding = 'utf-8') as f:
            f.write('============================================================\n')
            f.write(f'Type    : subprocess.run\n')
            f.write(f'Command : {command}\n')
            f.write(f'RunTime : {now_time()}\n')
            result = subprocess.run(command,shell=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            f.write('============================================================\n')
    #save to ile
    def save_to_file(self,filename,text,mode):
        with open(filename, mode,encoding = 'utf-8') as f:
            f.write('============================================================\n')
            f.write(f"Filename: {filename}\n")
            f.write(f"NowTime : {str(now_time())}\n")
            f.write(f"saveText: {text}\n")
            f.write('============================================================\n')
    #debug print
    def d_p(self,text):
        if self.d_p_flag:
            print(f"<natt> Debug info : {text}")
            with open(self.debug_filename, 'a') as f:
                f.write('============================================================\n')
                f.write(f'Time      : {now_time()}')
                f.write(f'Type      : dprint\n')
                f.write(f'Text      : {text}\n')
                f.write('============================================================\n')
    #normal print
    def n_p(self,text):
        with open(self.debug_filename, 'a') as f:
            f.write('============================================================\n')
            f.write(f'Time      : {now_time()}')
            f.write(f'Type      : dprint\n')
            f.write(f'Text      : {text}\n')
            f.write('============================================================\n')
        print(f"<natt> {text}")
    #user input
    def u_in(self,text):
        text = f"<natt> {text}"
        result = input(text)
        with open(self.debug_filename, 'a') as f:
            f.write('============================================================\n')
            f.write(f'Time     : {now_time()}')
            f.write(f'Type     : User.Input\n')
            f.write(f'Text     : {text}\n')
            f.write(f'Result   : {result}\n')
            f.write('============================================================\n')
        return result
        #json load
    def json_load(self,key,value):
        config = open(self.json_filename, "r")
        config = json.load(config)
        data = config[key][value]
        with open(self.debug_filename, 'a') as f:
            f.write('============================================================\n')
            f.write(f'Type     : Json.load\n')
            f.write(f'key      : {key}\n')
            f.write(f'value    : {value}\n')
            f.write(f'Data     : {data}\n')
            f.write('============================================================\n')
        return data