# Filename : sost_logging.py
# Release time : 2024.11.04
# Version:1.1
# by:Xiaodong Fan
# Role : log_lib
import locale
import json
import subprocess
import time
import datetime
import os

def now_time(type="0"):

    #-----------------------------------------------------------------------------------
    # return NowTime-1
    # 2024-11-04-13-28-12
    if   type == "0":return str(time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
    # 2024-11-04
    elif type == "1":return str(time.strftime("%Y-%m-%d", time.localtime()))
    # 13-28-12
    elif type == "2":return str(time.strftime("%H-%M-%S", time.localtime()))
    #-----------------------------------------------------------------------------------

    #-----------------------------------------------------------------------------------
    # return NowTime-2
    # 2024_11_04_13_28_12
    elif type == "3":return str(time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()))
    # 2024_11_04
    elif type == "4":return str(time.strftime("%Y_%m_%d", time.localtime()))
    # 13_28_12
    elif type == "5":return str(time.strftime("%H_%M_%S", time.localtime()))
    #-----------------------------------------------------------------------------------
    # return NowTime-3
    elif type == "6":return str(time.strftime("%Y%m%d-%H%M%S", time.localtime()))

    #-----------------------------------------------------------------------------------
    # time stamp -> default
    elif type == "7":return str(datetime.datetime.now().timestamp())
    # time stamp -> s
    elif type == "8":return str(int(datetime.datetime.now().timestamp()))
    # time stamp -> ms
    elif type == "9":return str(round(int(datetime.datetime.now().timestamp()) * 1000))
    # time stamp -> us
    elif type == "10":return str(round(int(datetime.datetime.now().timestamp()) * 1000000))
    #-----------------------------------------------------------------------------------
    else:print("now_time value : type -> Input Err");exit()

class dong_log():

    # 私有变量不可直接调用
    # 私有变量放在公有函数中可以被调用

    # __init__ : 构造函数，在生成对象时调用
    # __del__ : 析构函数，释放对象时使用
    # __repr__ : 打印，转换
    # __setitem__ : 按照索引赋值
    # __getitem__: 按照索引获取值
    # __len__: 获得长度
    # __cmp__: 比较运算
    # __call__: 函数调用
    # __add__: 加运算
    # __sub__: 减运算
    #  : 乘运算
    # __truediv__: 除运算
    # __mod__: 求余运算
    # __pow__: 乘方

    # Class fxd_log Private List==============================================================

    # 日志标题名称
    #__private_title_name = '< Input Software Title Name >'
    __private_title_name = 'sost'
    # ----------------------------------------------------------------------------------

    # 用户配置文件路径
    # __private_user_config_file_path = '< Input Software Json / Yaml File Path >'
    __private_user_config_file_path = '/opt/sost/config/sost.json'

    # SWC配置文件路径
    # __private_swc_config_file_path = '< Input swc Json / Yaml File Path >'
    __private_swc_config_file_path = '/opt/sost/config/swc.json'

    # server_info配置文件路径
    # __private_swc_config_file_path = '< Input swc Json / Yaml File Path >'
    __private_serinfo_config_file_path = '/opt/sost/config/server_info.json'

    # dong_debug配置文件路径
    # __private_swc_config_file_path = '< Input swc Json / Yaml File Path >'
    __private_dong_debug_file_path = '/opt/sost/config/debug.json'

    # collect_array配置文件路径
    # __private_swc_config_file_path = '< Input swc Json / Yaml File Path >'
    __private_collect_array_file_path = '/opt/sost/config/collect_array.json'

     # sost_ver配置文件路径
    # __private_swc_config_file_path = '< Input swc Json / Yaml File Path >'
    __sost_ver_file_path = '/opt/sost/config/sost_ver.json'

    # ----------------------------------------------------------------------------------

    # sost_interactive.log 日志文件路径
    # __private_cmdlog_file_path = '< Input Software cmd.log File Path >'
    __private_sost_interactive_file_path = '/opt/sost/log/sost_interactive.log'
    # ----------------------------------------------------------------------------------

    # popen.log 日志文件路径
    # __private_popen_log_file_path = '< Input Software popen.log File Path >'
    __private_popen_log_file_path = '/opt/sost/log/popen.log'
    # ----------------------------------------------------------------------------------

    # run.log 日志文件路径
    # __private_run_log_file_path = '< Input Software run.log File Path >'
    __private_run_log_file_path = '/opt/sost/log/run.log'
    # ----------------------------------------------------------------------------------

    # json.log 日志文件路径
    # __private_json_log_file_path = '< Input Software json.log File Path >'
    __private_json_log_file_path = '/opt/sost/log/json.log'
    # ------------------------------------------------------------------------------

    # debug.log 日志文件路径
    # __private_debug_log_file_path = '< Input Software debug.log File Path >'
    __private_debug_log_file_path = '/opt/sost/log/debug.log'
    # ------------------------------------------------------------------------------

    # alarm.log 日志文件路径
    # __private_alarm_file_path = '< Input Software debug.log File Path >'
    __private_alarm_file_path = '/opt/sost/log/alarm.log'
    # ------------------------------------------------------------------------------
  
    # 设置warning报错后是否退出
    # warning_exit   = '< Input Software warning Exit => False : Continue True : Exit>'
    warning_exit = False

    # 设置fail报错后是否退出
    # fail_exit   = '< Input Software fail Exit => False : Continue True : Exit>'
    fail_exit = True

    # 设置Error报错后是否退出
    # error_exit     = '< Input Software Error Exit => False : Continue True : Exit>'
    error_exit = True

    # 设置critical报错后是否退出
    # critical_exit = '< Input Software critical Exit => False : Continue True : Exit>'
    critical_exit = True

    # 设置debug信息打印按钮
    # level 0 -> 仅打印报错信息
    # level 1 -> 打印python交互信息 + DEBUG信息 + Warning/Fail/Error/Critical信息
    # level 2 -> 打印popen与os_run详细信息
    # level 3 -> 打印所有信息
    # debug_flags = '< Input Software show debug information => level 0-2'
    debug_flags = "0"

    # 设置popen是否进行数据记录，可减小cmd.log日志大小
    # True   不记录
    # False  记录
    popen_save_file_flags = False

    # echo info to dmesg
    def _dmesg(self,text):
        self.os_run(f'echo "{self.__private_title_name} : {text}" | sudo tee /dev/kmsg >> /dev/null')

    # fxd_log init 
    def __init__(self):
        # Return system encoding type 
        try:self.system_code = locale.getpreferredencoding()
        except:self.system_code = 'UTF-8'

    # Software Log Level Area =======================================================================
    
    # exit
    def _exitt(self,text=""):
        text = f"< {self.__private_title_name}_{now_time('6')}_exit     > : "+text
        self.save_to_file(filename=self.__private_alarm_file_path,text=text)
        print(text)
        exit()
    
    # Tips Log
    def _tips(self,text=""):
        text = f"< {self.__private_title_name}_{now_time('6')}_tips     > : "+text
        self.save_to_file(filename=self.__private_alarm_file_path,text=text)
        print(text)
        return

    # Warning Log
    def _warning(self,text=""):
        text = f"\033[33m< {self.__private_title_name}_{now_time('6')}_warning  > : "+text+"\033[0m"
        self.save_to_file(filename=self.__private_alarm_file_path,text=text)
        if self.debug_flags == "1" or self.debug_flags == "3" or self.debug_flags == '0':print(text)
        if self.warning_exit:
            if self.debug_flags == "1" or "3":
                exit()
            print(text)
            exit()
        return
    
    # Fail Log
    def _fail(self,text=""):
        text = f"\033[31m< {self.__private_title_name}_{now_time('6')}_fail     > : "+text+"\033[0m"
        self.save_to_file(filename=self.__private_alarm_file_path,text=text)
        if self.debug_flags == "1" or self.debug_flags == "3" or self.debug_flags == '0':print(text)
        if self.fail_exit:
            if self.debug_flags == "1" or "3":
                exit()
            print(text)
            exit()
        return
    
    # Error log
    def _error(self,text=""):
        text = f"\033[31m< {self.__private_title_name}_{now_time('6')}_error    > : "+text+"\033[0m"
        self.save_to_file(filename=self.__private_alarm_file_path,text=text)
        if self.debug_flags == "1" or self.debug_flags == "3" or self.debug_flags == '0':print(text)
        if self.error_exit:
            if self.debug_flags == "1" or "3":
                exit()
            print(text)
            self.json_set("Test_tmp","Running_flag","6",flags='no-log')
            exit()
        return
    
    # Critical Log
    def _critical(self,text=""):
        text = f"\033[31m< {self.__private_title_name}_{now_time('6')}_critical > : "+text+"\033[0m"
        print(text)
        self.save_to_file(filename=self.__private_alarm_file_path,text=text)
        if self.critical_exit :
            exit()
        return

    # Software saveFile  Area =======================================================================

    # save text to files
    def save_to_file(self,filename="",text="",mode="a"):
        if filename == "" or text == "":return 0
        with open(filename,mode) as f:
            f.write(text+"\n")
            f.flush()
        f.close()
        return
    
    # Python interactive Area =======================================================================
    # Software.Print and save information
    def _pr(self,text,filename=''):
        _text = f"< {self.__private_title_name}_{now_time('6')}_print    > : "+text
        self.save_to_file(filename=self.__private_sost_interactive_file_path,text=_text)
        str_info = f"< {self.__private_title_name} > "+text
        print(str_info)
        if filename!='':
            with open(filename,'a') as f:
                f.write(str_info+"\n")
                f.flush()
        # Force Sync Data
        self.os_run("sync -f && sync",flags='no-log')
        return
    
    # Software.User.Input and save information
    def _in(self,text):
        try:
            text = input(f"< {self.__private_title_name} {text.strip()} > : ")
            _text = f"< {self.__private_title_name}_{now_time('6')}_input    > : " + text
            self.save_to_file(filename=self.__private_sost_interactive_file_path,text=_text)
            # debug_flags 
            # self._tips(f"_in debug_flags : {self.debug_flags}")
            if self.debug_flags == "1" or self.debug_flags == "3":
                print(_text)
        except:
            self._error("User.Exit()")
        return text

    # Software.Debug.Information
    def _dp(self,text):
        text = f"< {self.__private_title_name}_{now_time('6')}_dlev_{self.debug_flags}   > : {text}"
        self.save_to_file(filename=self.__private_debug_log_file_path,text=text)
        if self.debug_flags == "1" or self.debug_flags == "3":
            print(text)
        return 

    # Python RunCommand Area =======================================================================
    # Running Command not save Result to File
    def os_run(self,run_com,flags=''):
        try:
            try:result = subprocess.run(run_com,shell=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:self._error(f"os_run command : {str(run_com).strip()} error!")
        except:
            from .sost_public_lib import defalt_path,result_html
            defalt_path()
            result_html()
            self._error(f"User.Exit.Test!")

        text = f"< {self.__private_title_name}_{now_time('6')}_run_com  > : {result} "
        if flags != 'no-log':
            self.save_to_file(filename=self.__private_run_log_file_path,text=text)
        if self.debug_flags == "2" or self.debug_flags == "3" :print(text)
        if "Failed" in text:
            return "Failed"
        else:
            return 
    
    # Running Command save Result to File
    def os_popen(self,run_com,flags=''):
        tmp_result = ""
        try:
            try:tmp_result = subprocess.Popen(run_com, stdout=subprocess.PIPE, shell=True).stdout.read().decode(str(self.system_code))
            except:self._error(f"os_popen command : {str(run_com).strip()} error!")
            result = '-'*60+"\n"+tmp_result.strip()+"\n"+'-'*60
            if self.popen_save_file_flags:result = ''
        except:
            from .sost_public_lib import defalt_path,result_html
            defalt_path()
            result_html()
            self._error(f"User.Exit.Test!")
            
        text = f"< {self.__private_title_name}_{now_time('6')}_popen_com> : {run_com} -> Result\n"+tmp_result
        if flags != 'no-log':self.save_to_file(filename=self.__private_popen_log_file_path,text=text)
        if self.debug_flags == "2" or self.debug_flags == "3" :print(text)
        return tmp_result

    # Python JsonData Read Write =======================================================================

    # Software.Get.User-JsonFile.Value
    def json_get(self,obj,key,flags='',web='',filename=''):
        typee = 'sost'
        if filename == "":
            filename = self.__private_user_config_file_path
        elif filename == "swc":
            typee = 'swc'
            filename = self.__private_swc_config_file_path
        elif filename == "server_info":
            typee = 'server_info'
            filename = self.__private_serinfo_config_file_path
        elif filename == "debug":
            typee = 'debug'
            filename = self.__private_dong_debug_file_path
        elif filename == "collect":
            filename = self.__private_collect_array_file_path
        elif filename == "ver":
            filename = self.__sost_ver_file_path
        else: 
            filename = self.__private_user_config_file_path
        try:
            with open(filename, "r") as f:
                config = json.load(f)
                os.fsync(f)
            data = config[obj][key]
            text = f"< {self.__private_title_name}_{now_time('6')}_json_get > : type[{typee}] obj[{obj}] key[{key}] value[{data}]"
            if web !='no-log':self.save_to_file(filename=self.__private_json_log_file_path,text=text)
            if self.debug_flags == "1" or self.debug_flags == "3" :
                if flags != '1':print(text)
            # os.system("echo 3 > /proc/sys/vm/drop_caches >/dev/null")
            self.os_run("sync -f && sync",flags='no-log')
            return str(data)
        except Exception as e:
                self._pr(self.os_popen("cat /opt/sost/config/sost.json"))
                self._error(f"json file EXIT! error_info : {e} \n <! sost !>json_get obj : {obj} key : {key}")

    # Software.Set.JsonFile.Value
    def json_set(self,obj, key, new_value,flags='',filename=""):
        if filename == "":
            typee = 'sost'
            filename = self.__private_user_config_file_path
        elif filename == "swc":
            typee = 'swc'
            filename = self.__private_swc_config_file_path
        elif filename == "server_info":
            typee = 'server_info'
            filename = self.__private_serinfo_config_file_path
        else: 
            filename = self.__private_user_config_file_path
            typee = 'sost'
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                os.fsync(file)
            data[obj][key] = new_value
            with open(filename, 'w') as file1:
                json.dump(data, file1, indent=4)
                os.fsync(file1)
            text = f"< {self.__private_title_name}_{now_time('6')}_json_set > : type[{typee}] obj[{obj}] key[{key}] old[{self.json_get(obj,key,web=flags)}] new[{new_value}]"
            if flags.strip() !='no-log':self.save_to_file(filename=self.__private_json_log_file_path,text=text)
            if self.debug_flags == "1" or self.debug_flags == "3" :print(text)
            # os.system("echo 3 > /proc/sys/vm/drop_caches")
            self.os_run("sync -f && sync",flags='no-log')
            return
        except Exception as e:
            print(self.os_popen("cat /opt/sost/config/sost.json"))
            self._error(f"json file EXIT! error_info : {e}")