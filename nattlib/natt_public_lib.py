# Filename : natt_public_lib.py
# Release time : 2024.07.05
# Version:1.1.2
# by:Dong

import time
from datetime import datetime, timedelta
import os
import platform
import random
import smtplib
import sys
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#####################################################################################
# Use sost_logging instead of natt_logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.sost_logging import dong_log as sost_dong_log

log = sost_dong_log()
# Set debug flags from natt config
try:
    debug_print = log.json_get('debug', 'debug_print', filename='natt', web='no-log')
    if debug_print == '1':
        log.debug_flags = "1"  # Enable debug print
    else:
        log.debug_flags = "0"
except:
    log.debug_flags = "0"
log.error_exit = True
#####################################################################################

# 清除终端信息
def clear_p():
    os.system("clear")

# 返回当前时间
def now_time():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%H-%M-%S")
    return formatted_time

def warning_tips():
    print('[==============================================================================]')
    print('[   Warning! Are you sure you want to continue with the dangerous operation?   |')
    print('[  （警告你确定要继续进行危险的操作吗?)                                           |')
    print('[==============================================================================]')
    if log._in("Do you want to Continue ? (y/n) : ").lower() == 'n':
        return False
    else:
        return True

# 打印小提示信息
def print_tips(tips):
    print("=" * 60)
    log._pr(f"[+] {tips} waiting 30s runstart! [Ctrl + C] Exit!")
    log._pr("[+] Print the execution command below [Ctrl +C] Exit!")
    print("=" * 60)
    log._pr("Command Show : ")

def config_check():
    if log.json_get('Bound_nucleus', 'Bound_nucleus_type_1', filename='natt', web='no-log').strip() == log.json_get('Bound_nucleus',
                                                                                       'Bound_nucleus_type_2', filename='natt', web='no-log').strip() == '1':
        log._pr("Config json File Error!Please Check Bound_nucleus Type 1 and 2!")
        exit()
    elif log.json_get('Bound_nucleus', 'Bound_nucleus_type_2', filename='natt', web='no-log').strip() == log.json_get('Bound_nucleus',
                                                                                         'Bound_nucleus_type_3', filename='natt', web='no-log').strip() == '1':
        log._pr("Config json File Error!Please Check Bound_nucleus Type 2 and 3!")
        exit()
    elif log.json_get('Bound_nucleus', 'Bound_nucleus_type_1', filename='natt', web='no-log').strip() == log.json_get('Bound_nucleus',
                                                                                         'Bound_nucleus_type_3', filename='natt', web='no-log').strip() == '1':
        log._pr("Config json File Error!Please Check Bound_nucleus Type 1 and 3!")
        exit()
    elif log.json_get("DiskInfo", "nvme_info", filename='natt', web='no-log') != '' and log.json_get("DiskInfo", "sata_info", filename='natt', web='no-log') != '':
        log._pr("Please check config.json nvme_info and sata_info ! ")

    else:
        log._pr("Config json File check Success!")


# fio iostat监控
def fio_iostat_monitor(log_name, test_type, iostat_flags,running_time,prewriting_flags=False):
    log._pr("Running FIO/IOSTAT Process : ")
    print(log.os_popen("ps -aux | grep -iE 'fio|iostat' | grep -v grep").strip())
    print("=" * 60)
    log._pr("持续监控fio和iostat进程，不要操作，等待进程结束!")
    log._pr("Continuously monitor the fio and iostat processes, do not operate, wait for the process to end!")
    print("=" * 60)
    start_end_time(running_time)
    
    if test_type == "" or log_name == "":
        tmp_if = False
    else:
        if log.json_get("Monitor", "numa_info", filename='natt', web='no-log') == "1":
            tmp_if = True
        else:
            tmp_if = False
            
    if iostat_flags == "1":
        log._dp("Test iostat pkill !")
        log._dp("iostat_flags : " + iostat_flags)
        iostat_num = str(subprocess.Popen("ps -aux | grep iostat | grep -v grep | wc -l", stdout=subprocess.PIPE,shell=True).stdout.read().decode(str(log.system_code)).strip())
        log._dp("iostat num : " + iostat_num)
        if iostat_num == "0":
            log._exitt("Iostat Process Not Found!Please check cmd.log")
            
    while True:
        if tmp_if: numa_info(log_name, test_type)
        iostat_num = str(subprocess.Popen("ps -aux | grep fio | grep filename | grep -v grep | wc -l", stdout=subprocess.PIPE,shell=True).stdout.read().decode(str(log.system_code)).strip())
        fio_num = str(subprocess.Popen("ps -aux | grep 'iostat -g all -xm' | grep -v grep | wc -l",stdout=subprocess.PIPE, shell=True).stdout.read().decode(str(log.system_code)).strip())
        if prewriting_flags:
            if fio_num == "0":
                log._pr('检测到预写Fio进程结束 Pre-write Fio process end detected!')
                time.sleep(3)
                log.os_run("pkill -9 iostat")
                log._pr('已结束iostat进程 Iostat process has been ended!')
                break
        
        if iostat_num == "0" and fio_num == "0":
            log._pr('检测到Fio / Iostat进程结束!')
            log._pr('Fio/Iostat process end detected!')
            break
def start_end_time(time):
    runtime = timedelta(seconds=int(time))
    now = datetime.now()
    end_time = now + runtime
    print("=" * 60)
    log._pr("Time:")
    print(f'StartTime   : {now.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'EndTime     : {end_time.strftime("%Y-%m-%d %H:%M:%S")}')
    print("=" * 60)

def monitor_start(runtime, file_name, disk_name, log_name):
    log._dp("monitor_start disk_name : " + disk_name)
    log._dp("monitor_start log_name : " + log_name)
    log._dp("monitor_start file_name : " + file_name)
    log._dp("monitor_start runtime : " + str(runtime))
    # ------------------------------------------------------------------------------------------
    tags = ''
    if "ddtest" in disk_name:
        log._dp("dd test iostat monitor start!")
        log.os_run(f"iostat -xm 1 -s {runtime} ALL >> /tmp/iostat-dd-{file_name} & ")
        return

    if log.os_popen("ps -aux | grep 'iostat -g all -xm 1' | grep -v grep | wc -l").strip() == "0":
        if "nvme" in disk_name:
            tags = 'nvme'
        elif "sd" in disk_name:
            tags = 'sata'
        else:
            log._pr("Uknown disk type!")
            exit()
    else:
        log._pr("iostat not exist!")

    log._dp("iostat command : " + f"iostat -g all -xm 1 {runtime} >> {log_name}/{tags}-{file_name} & " )
    data = log.os_popen(f"iostat -g all -xm 1 {runtime} >> {log_name}/{tags}-{file_name} & ")
    log._dp("monitor_start iostat data : " + data)

    # ------------------------------------------------------------------------------------------
    if not os.path.exists(log_name + "/debug"):
        log.os_run(f"mkdir -p {log_name}/debug")
        
    if str(log.json_get("Monitor", "sar_d", filename='natt', web='no-log')).strip() == "1":
        if log.os_popen("ps -aux | grep 'sar -b'| grep -v grep | wc -l").strip() == "0":
            log.os_run(f"sar -b 1 {runtime} >> {log_name}/debug/sar_d-{file_name} & ")
    if str(log.json_get("Monitor", "vmstat_w", filename='natt', web='no-log')).strip() == "1":
        if log.os_popen("ps -aux | grep -i 'vmstat -w' | grep -v grep | wc -l").strip() == "0":
            log.os_run(f"vmstat -w 1 {runtime} >> {log_name}/debug/vmstat_w-{file_name} & ")
    if str(log.json_get("Monitor", "mpstat_p_all", filename='natt', web='no-log')).strip() == "1":
        if log.os_popen("ps -aux | grep -i 'mpstat -P ALL 1' | grep -v grep | wc -l").strip() == "0":
            log.os_run(f"mpstat -P ALL 1 {runtime} >> {log_name}/debug/mpstat_p_all-{file_name} & ")
    if str(log.json_get("Monitor", "pidstat_d", filename='natt', web='no-log')).strip() == "1":
        if log.os_popen("ps -aux | grep -i 'pidstat -d 1' | grep -v grep | wc -l").strip() == "0":
            log.os_run(f"pidstat -d 1 {runtime} >> {log_name}/debug/pidstat_d-{file_name} & ")
    if str(log.json_get("Monitor", "dstat", filename='natt', web='no-log')).strip() == "1":
        if log.os_popen("ps -aux | grep -i 'dstat 1' | grep -v grep | wc -l").strip() == "0":
            log.os_run(f"dstat 1 {runtime} >> {log_name}/debug/dstat-{file_name} & ")
    # ------------------------------------------------------------------------------------------


def soft_info(log_name):
    with open(log_name + "/debug/soft_ver.log", "a") as f:
        f.write("=" * 60 + "\n")
        f.write("[Fio.Ver]\n")
        f.write(log.os_popen("fio -v") + "\n")
        f.write("=" * 60 + "\n")
        f.write("[Iostat.Ver]\n")
        f.write(log.os_popen("iostat -V") + "\n")
        f.write("=" * 60 + "\n")
        f.write("[OS.Ver]\n")
        f.write(log.os_popen("cat /etc/os-release") + "\n")
        f.write("=" * 60 + "\n")
        f.write("[Uname]\n")
        f.write(log.os_popen("uname -a") + "\n")
        f.write("=" * 60 + "\n")
        f.write("[cmdline]\n")
        f.write(log.os_popen("cat /proc/cmdline") + "\n")
        f.write("=" * 60 + "\n")
        # BMC
        a = os.popen(" ipmitool mc info |grep 'Firmware Revision' |awk '{ print $4}' ").read().strip()
        b = os.popen(" ipmitool mc info |grep -A2 'Aux' |sed -n '2p' |awk '{ print $1}'|sed 's/0x//g' ").read().strip()
        c = os.popen(" ipmitool mc info |grep -A2 'Aux' |sed -n '3p' |awk '{ print $1}'|sed 's/0x//g' ").read().strip()
        BMC_Ver = f"BMC.ver : {a}.{b}{c}"
        f.write("[BMC.Ver]\n")
        f.write(BMC_Ver + "\n")
        f.write("=" * 60 + "\n")
        # Bios
        Bios_Ver = "Bios.ver : " + str(
            os.popen(" dmidecode -t bios | grep Version: | awk '{print $2}' ").read().strip()).strip()
        f.write("[Bios.Ver]\n")
        f.write(Bios_Ver + "\n")
        f.write("=" * 60 + "\n")
    f.close()

# 输出打印并保存
def print_save_text(file_path_name, text):
    with open(file_path_name, "a") as f:
        print(text)
        f.write(text + "\n")
    f.close()

#blktrace_start
def blktrace_start(disk_info,log_path,test_type,runtime):
    if not os.path.exists(f"{log_path}/blktrace_files"):
        log.os_popen(f"mkdir -p {log_path}/blktrace_files")
    for i in range(0,len(disk_info),3):
        disk_name = disk_info[i]
        folder_name = f"{disk_name.strip()}_{test_type}"
        if not os.path.exists(f"{log_path}/blktrace_files/{folder_name}"):
            log.os_popen(f"mkdir -p {log_path}/blktrace_files/{folder_name}")
        log.os_run(f"blktrace /dev/{disk_name} -D {log_path}/blktrace_files/{folder_name} -o {folder_name} -w {runtime} & ")
    log._pr("已开启blktrace 追踪I/O层的信息")
    log._pr("BLKTRACE tracking of I/O layer information enabled")
    print("=" * 60)
#blktrace result
def blktrace_result(log_path):
    print("=" * 60)
    log._pr("Start processing BLKTRACE data information")
    log._pr("开始处理blktrace数据信息")
    print("=" * 60)
    folder_path = log_path+"/blktrace_files"
    for path, dirs, files in os.walk(folder_path):
        if path == folder_path:continue
        file_name = path.replace(folder_path+"/","")
        log.os_run(f"cd {path} && blkparse -i {file_name} -d {file_name}.blktrace.bin")
        log.os_run(f"cd {path} && iowatcher -t {file_name}.blktrace.bin -o {log_path}/blktrace_files/{file_name}.svg")
    log.os_popen(f"cp {folder_path}/*.svg {log_path}")
    log._pr("处理完毕，请检查结果文件夹中.svg文件")
    print("=" * 60)

# debug输出及运行
def debug_run_print(debug, command):
    if debug == "1":
        log.os_run(command)
    elif debug == "0":
        with open("/opt/sost/log/natt_cmd.log", "a") as p:
            p.write("[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]\n")
            p.write(command + "\n")
            p.flush()
        if "fio" in command and "nohup" in command:
            with open("/opt/sost/log/fio_command.log", "a") as p:
                p.write("[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]\n")
                p.write(command + "\n")
                p.flush()
        print(command)
    else:
        return


# 初始化log文件夹
def init_log():
    if "natt_log" in log.os_popen("ls /root").strip():
        if os.path.exists("/root/natt_old"):
            log.os_run("mv /root/natt_log* /root/natt_old")
        else:
            log.os_run("mkdir /root/natt_old")
            log.os_run("mv /root/natt_log* /root/natt_old")
    # 获取当前路径
    create_file_name = f"/root/natt_log_{now_time()}"
    log.os_run(f"mkdir {create_file_name}")
    log.os_run(f"mkdir -p {create_file_name}/debug")
    return create_file_name


def numa_info(log_name, test_type):
    if not os.path.exists(log_name + "/debug"):
        log.os_popen(f"mkdir -p {log_name}/debug")
    log_path = f"{log_name}/debug"
    # [root@localhost]# numastat -v
    # Per-node numastat info (in MBs):
    #                           Node 0          Node 1           Total
    #                  --------------- --------------- ---------------
    # Numa_Hit               270051.60       206495.95       476547.54
    # Numa_Miss                   0.00            0.00            0.00
    # Numa_Foreign                0.00            0.00            0.00
    # Interleave_Hit             10.76           10.10           20.86
    # Local_Node             270005.93       206390.38       476396.31
    # Other_Node                 45.67          105.57          151.23
    # miss值和foreign值越高，就要考虑绑定的问题。
    with open(f"{log_path}/{test_type}_numastat.log", "a") as f:
        f.write(subprocess.Popen("numastat -v", stdout=subprocess.PIPE, shell=True).stdout.read().decode(
            str(log.system_code)).strip())
    with open(f"{log_path}/{test_type}_numactl_H.log", "a") as f:
        f.write(subprocess.Popen("numactl -H", stdout=subprocess.PIPE, shell=True).stdout.read().decode(
            str(log.system_code)).strip())
    with open(f"{log_path}/{test_type}_softirqs.log", "a") as f:
        f.write(subprocess.Popen("cat /proc/softirqs", stdout=subprocess.PIPE, shell=True).stdout.read().decode(
            str(log.system_code)).strip())

def init_natt():
    config_check()
    if log.json_get("debug", "natt_Double_opening", filename='natt', web='no-log') == "0":
        # 禁止双开
        # if int(log.os_popen('ps -aux | grep -i python | grep -i natt | grep -v grep | wc -l').strip()) != 1:
        #     log._error('Natt Prohibit double opening!Please run command :   natt -k ')
        #     exit()

        # 测试前kill iostat/fio
        if int(log.os_popen('ps -aux | grep -iE "fio|iostat" | grep -v grep | grep filename | wc -l').strip()) != 0:
            log._pr("fio/iostat is already running! Now kill all processes!")
            log.os_run("pkill -9 fio ; pkill -9 iostat")

        # 测试前删除 natt -a遗留的硬盘信息
        if int(log.os_popen('ls /tmp/ | grep natt | wc -l').strip()) != 0:
            for file_name in os.listdir("/tmp"):
                if "natt" in file_name: log.os_run(f'rm -rf /tmp/{file_name}')

    elif log.json_get("debug", "natt_Double_opening", filename='natt', web='no-log') == "1":
        log._pr("\n[-] NATT enables dual mode, performance testing is prohibited!")
        log._pr("[-] If performance testing is required, please set natt -c debug nattDouble_opening=0")
        log._pr("[-] natt开启双开模式，请勿进行硬盘性能导入测试!")
        log._pr("[-] 如需进行性能测试,请使用natt -c 设置debug natt_Double_opening = 0\n")
        if warning_tips():
            log._pr("wait 3s start natt.....")
            wait(3)
        else:
            log._error('You Chose N!')
    else:
        log._error(
            '<natt> Debug natt_Double_opening Config Error! Please Check natt_config.json! natt_Double_opening set 0 / 1 !')

    # 测试前删除 natt -a遗留的硬盘信息
    if int(log.os_popen('ls /tmp/ | grep natt | wc -l').strip()) != 0:
        for file_name in os.listdir("/tmp"):
            if "natt" in file_name: log.os_run(f'rm -rf /tmp/{file_name}')
    try:
        cmd_log_size_kb = int(int(log.os_popen("ls -al /opt/sost/log/natt_cmd.log 2>/dev/null | awk '{{print $5}}'")) / 1024)
        max_size = int(log.json_get("natt", "cmd_log_size_kb", filename='natt', web='no-log'))
        if cmd_log_size_kb > max_size:
            log._pr("natt_cmd大小超过设定的最大值,现在进行备份处理!")
            log._pr("The size of the natt_cmd file exceeds the set maximum value!Now proceed with backup processing")
            log.os_run("mkdir -p /opt/natt/Cache_File")
            log.os_run(f"mv /opt/sost/log/natt_cmd.log 2>/dev/null /opt/natt/Cache_File/cmd_bak_{str(now_time())}.log")
            time.sleep(2)
    except:
        pass
    # Clear system cache
    log.os_run("echo '' > /opt/sost/log/fio_command.log")
    log.os_run("echo 3 > /proc/sys/vm/drop_caches")
    log.os_run("sync")

# 判断字符串是否为空
def str_null(strings, text):
    if text == 1:
        if not strings.isdigit():
            log._pr("Input Error!")
            exit()
        if strings == "exit":
            log._pr("User Input Exit!")
            exit()
        if strings == '':
            log._pr("Input Error!")
            exit()
        if int(strings) > 22:
            log._pr("Input Error!")
            exit()
        elif strings == "19":
            log._pr("Disk Quickly Check (null)")
            exit()
        elif strings == "21":
            log._pr("DD Test (null)")
            exit()
        elif strings == "22":
            log._pr("Waiting for development (null)")
            exit()
    else:
        log._pr("check judge input type!")


def show_sys_info():
    try:
        os_info = log.os_popen('cat /etc/system-release').strip()
        platform_info = platform.platform()
        processor_architecture = platform.processor()
        BMC_IP = log.os_popen(
            "ipmitool lan print | grep -i 'ip address' | grep -vi source | awk '{{print $4}}'").strip()
        if BMC_IP == "": BMC_IP = "GetFail!"
        SYS_IP = log.os_popen("hostname -I").split()[0]
        if SYS_IP == "": SYS_IP = "GetFail!"
        log._pr("System name            : " + os_info)
        log._pr("System version         : " + os_info)
        log._pr("System release         : " + platform_info)
        log._pr("System architecture    : " + processor_architecture)
        log._pr("BMC IP                 : " + BMC_IP)
        log._pr("SYS IP                 : " + SYS_IP)
        log._pr("=========================================================")
    except:
        log._pr("System name            : Getfail!")
        log._pr("System version         : Getfail!")
        log._pr("System release         : Getfail!")
        log._pr("System architecture    : Getfail!")
        log._pr("BMC IP                 : Getfail!")
        log._pr("SYS IP                 : Getfail!")
        log._pr("[+]Failed acquisition does not affect hard drive testing")
        log._pr("[+]获取失败不影响硬盘测试!")


def readme():
    clear_p()
    print(log.os_popen(r"cat /opt/natt/README.md"))
    log._pr("\n")

def nvme_judge_mem():
    # 获取CPU node memory信息
    node_memory = log.os_popen("numactl -H | grep free | awk '{{print $4}}'").split()
    # 获取nvme硬盘名称 和 pciebus信息
    nvme_bus_list = log.os_popen("nvme list-subsys | grep +- | awk '{print $2,$4}'").split()
    # 循环对比nvme硬盘所在node memory信息
    for i in range(0, len(nvme_bus_list)):
        if i % 2 == 0: continue
        # 获取当前循环nvme硬盘node信息
        nvme_node = log.os_popen(f"lspci -vvvs {nvme_bus_list[i]} | grep -i node | awk '{{print $3}}'").strip()
        # 对比nvme_node 与 cpu_node 中 memory信息
        if node_memory[int(nvme_node)] == 0:
            log._pr(f"nvme_name:{nvme_bus_list[i - 1]} Node:{nvme_node} Node_memory:{node_memory[int(nvme_node)]}")
            log._pr(
                f"he node where the current NVME hard disk is located has insufficient memory. Please check the memory access status!")
            log._pr(f"Memory check failed, program automatically closes!")
            exit()
        else:
            continue
    log._pr("Check Nvme disk memory Success!")

    if '0' in node_memory:
        print(node_memory)
        print(log.os_popen('numactl -H'))
        log._pr("你的测试环境Node存在内存确失，可能会影响性能测试是否继续？")
        log._pr(
            "There is a memory error in your testing environment Node, which may affect performance testing. Do you want to continue?")
        if 'n' in input("You chose [ y / n ]: "):
            exit()


# 等待时间
def wait(sleep_time):
    time.sleep(sleep_time)


# fio每个进程运行等待时长
def wait_disk_run():
    json_time = str(log.json_get("debug", "fio_process_wait_time", filename='natt', web='no-log')).strip()
    if json_time == '':
        time.sleep(3)
    else:
        time.sleep(int(json_time))


# 打印fio后等待时长
def wait_disk_print():
    json_time = str(log.json_get("debug", "fio_print_wait_time", filename='natt', web='no-log')).strip()
    if json_time == '':
        time.sleep(1)
    else:
        time.sleep(int(json_time))


def Blessings():
    Blessings_strings = '''When all else is lost the future still remains.就是失去了一切别的，也还有未来。
    Sow nothing, reap nothing.春不播，秋不收。
    Keep on going never give up.勇往直前， 决不放弃！
    The wealth of the mind is the only wealth.精神的财富是唯一的财富。
    Never say die.永不气馁！
    Nurture passes nature.教养胜过天性。
    There is no garden without its weeds.没有不长杂草的花园。
    The best preparation for tomorrow is doing your best today.对明天做好的准备就是今天做到最好！
    The reason why a great man is great is that he resolves to be a great man.伟人之所以伟大，是因为他立志要成为伟大的人。
    Suffering is the most powerful teacher of life.苦难是人生最伟大的老师。
    If you don't make the time to work on creating the life you want, you're eventually going to be forced to spend a lot of time dealing with a life you don't want.若不抽出时间来创造自己想要的生活，你最终将不得不花费大量的时间来应付自己不想要的生活。
    A man can't ride your back unless it is bent.你的腰不弯，别人就不能骑在你的背上。
    Although again sweet candy, also has a bitter day.即使再甜的糖，也有苦的一天。
    Sharp tools make good work.工欲善其事，必先利其器。
    Never put off what you can do today until tomorrow.今日事今日毕！
    Wasting time is robbing oneself.浪费时间就是掠夺自己。
    The greatest test of courage on earth is to bear defeat without losing heart.世界上对勇气的最大考验是忍受失败而不丧失信心。
    A man's best friends are his ten fingers.人最好的朋友是自己的十个手指。
    Only they who fulfill their duties in everyday matters will fulfill them on great occasions.只有在日常生活中尽责的人才会在重大时刻尽责。
    The shortest way to do many things is to only one thing at a time.做许多事情的捷径就是一次只做一件事。
    There's only one corner of the universe you can be sure of improving, and that's your own self.这个宇宙中只有一个角落你肯定可以改进，那就是你自己。
    The first step is as good as half over.第一步是最关键的一步。
    Do one thing at a time, and do well.一次只做一件事，做到最好！
    Believe that god is fair.相信上帝是公平的。
    Wealth is the test of a man's character.财富是对一个人品格的试金石。
    The best hearts are always the bravest.心灵最高尚的人，也总是最勇敢的人。
    Don't aim for success if you want it; just do what you love and believe in, and it will come naturally.如果你想要成功，不要去追求成功；尽管做你自己热爱的事情并且相信它，成功自然到来。
    All things come to those who wait.苍天不负有心人。
    Victory won''t come to me unless I go to it.胜利是不会向我们走来的，我必须自己走向胜利。
    A man is not old as long as he is seeking something. A man is not old until regrets take the place of dreams.只要一个人还有追求，他就没有老。直到后悔取代了梦想，一个人才算老。
    While there is life there is hope.一息若存，希望不灭。
    I am a slow walker,but I never walk backwards.我走得很慢，但是我从来不会后退。
    Cease to struggle and you cease to live. 生命不止，奋斗不息。
    Never underestimate your power to change yourself!永远不要低估你改变自我的能力！
    Nothing is impossible!没有什么不可能！
    Do what you say,say what you do.做你说过的，说你能做的。
    The man who has made up his mind to win will never say "impossible ".凡是决心取得胜利的人是从来不说"不可能的"。
    Live a noble and honest life. Reviving past times in your old age will help you to enjoy your life again.过一种高尚而诚实的生活。当你年老时回想起过去，你就能再一次享受人生。
    You have to believe in yourself . That''s the secret of success.人必须相信自己，这是成功的秘诀。
    If you fail, don't forget to learn your lesson.如果你失败了，千万别忘了汲取教训。
    You cannot improve your past, but you can improve your future. Once time is wasted, life is wasted.你不能改变你的过去，但你可以让你的未来变得更美好。一旦时间浪费了，生命就浪费了。
    There is but one secret to sucess---never give up!成功只有一个秘诀－－永不放弃！
    For man is man and master of his fate.人就是人，是自己命运的主人。
    What makes life dreary is the want of motive.没有了目的，生活便郁闷无光。
    Difficult circumstances serve as a textbook of life for people.困难坎坷是人们的生活教科书。
    Gods determine what you're going to be.人生的奋斗目标决定你将成为怎样的人。
    Living without an aim is like sailing without a compass.生活没有目标，犹如航海没有罗盘。
    All things in their being are good for something.天生我才必有用。
    The good seaman is known in bad weather.惊涛骇浪，方显英雄本色。
    The secret of success is constancy to purpose.成功的秘诀在于对目标的忠实
    '''
    print("<natt-Blessings> : " + Blessings_strings.split("\n")[random.randint(1, 50)].strip())
    print("<natt-Tips>Good luck to you !")
    print("=========================================================")


def smtp_send_result(result):
    global server_stmp
    smtp_server = log.json_get("email", "smtp_server", filename='natt', web='no-log')
    smtp_port = log.json_get("email", "smtp_port", filename='natt', web='no-log')
    sender_email = log.json_get("email", "sender_email", filename='natt', web='no-log')
    receiver_email = log.json_get("email", "receiver_email", filename='natt', web='no-log')
    password = log.json_get("email", "password", filename='natt', web='no-log')
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = 'Natt Result email'
    msg.attach(MIMEText(result, 'plain'))
    try:
        server_stmp = smtplib.SMTP(smtp_server, smtp_port)
        if smtp_port == 465:
            server_stmp.starttls()
        server_stmp.login(sender_email, password)
        server_stmp.sendmail(sender_email, receiver_email, msg.as_string())
        print('Email sent successfully!')
    except Exception as e:
        print(f'Error occurred: {e}')
    finally:
        server_stmp.quit()
