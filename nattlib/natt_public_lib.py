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
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#####################################################################################
from .natt_logging import dong_log, subprocess
log = dong_log()
log.json_filename = 'config/natt_config.json'
if log.json_load('debug', 'debug_print') == '1':
    log.d_p_flag = True
else:
    log.d_p_flag = False
log.error_exit = True
#####################################################################################

# 清除终端信息
def clear_p():
    subprocess.run("clear")

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
    if log.u_in("Do you want to Continue ? (y/n) : ").lower() == 'n':
        return False
    else:
        return True

# 打印小提示信息
def print_tips(tips):
    print("=" * 60)
    log.n_p(f"[+] {tips} waiting 30s runstart! [Ctrl + C] Exit!")
    log.n_p("[+] Print the execution command below [Ctrl +C] Exit!")
    print("=" * 60)
    log.n_p("Command Show : ")


def config_check():
    if log.json_load('Bound_nucleus', 'Bound_nucleus_type_1').strip() == log.json_load('Bound_nucleus',
                                                                                       'Bound_nucleus_type_2').strip() == '1':
        log.n_p("Config json File Error!Please Check Bound_nucleus Type 1 and 2!")
        exit()
    elif log.json_load('Bound_nucleus', 'Bound_nucleus_type_2').strip() == log.json_load('Bound_nucleus',
                                                                                         'Bound_nucleus_type_3').strip() == '1':
        log.n_p("Config json File Error!Please Check Bound_nucleus Type 2 and 3!")
        exit()
    elif log.json_load('Bound_nucleus', 'Bound_nucleus_type_1').strip() == log.json_load('Bound_nucleus',
                                                                                         'Bound_nucleus_type_3').strip() == '1':
        log.n_p("Config json File Error!Please Check Bound_nucleus Type 1 and 3!")
        exit()
    elif log.json_load("DiskInfo", "nvme_info") != '' and log.json_load("DiskInfo", "sata_info") != '':
        log.n_p("Please check config.json nvme_info and sata_info ! ")

    else:
        log.n_p("Config json File check Success!")


# fio iostat监控
def fio_iostat_monitor(log_name, test_type, iostat_flags,running_time):
    log.n_p("Running FIO/IOSTAT Process : ")
    print(log.popen("ps -aux | grep -iE 'fio|iostat' | grep -v grep").strip())
    print("=" * 60)
    log.n_p("持续监控fio和iostat进程，不要操作，等待进程结束!")
    log.n_p("Continuously monitor the fio and iostat processes, do not operate, wait for the process to end!")
    print("=" * 60)
    start_end_time(running_time)
    if test_type == "" or log_name == "":
        tmp_if = False
    else:
        if log.json_load("Monitor", "numa_info") == "1":
            tmp_if = True
        else:
            tmp_if = False
    if iostat_flags == "1":
        log.d_p("Test iostat pkill !")
        log.d_p("iostat_flags : " + iostat_flags)
        iostat_num = str(subprocess.Popen("ps -aux | grep iostat | grep -v grep | wc -l", stdout=subprocess.PIPE,shell=True).stdout.read().decode(str(log.system_code)).strip())
        log.d_p("iostat num : " + iostat_num)
        if iostat_num == "0":
            log.exitt("Iostat Process Not Found!Please check cmd.log")
    while True:
        if tmp_if: numa_info(log_name, test_type)
        iostat_num = str(subprocess.Popen("ps -aux | grep fio | grep filename | grep -v grep | wc -l", stdout=subprocess.PIPE,
                                          shell=True).stdout.read().decode(str(log.system_code)).strip())
        fio_num = str(subprocess.Popen("ps -aux | grep 'iostat -xm 1 -s'| grep 'ALL' | grep -v grep | wc -l",
                                       stdout=subprocess.PIPE, shell=True).stdout.read().decode(
            str(log.system_code)).strip())
        if iostat_num == "0" and fio_num == "0":
            log.n_p('检测到Fio / Iostat进程结束!')
            log.n_p('Fio/Iostat process end detected!')
            break
def start_end_time(time):
    runtime = timedelta(seconds=int(time))
    now = datetime.now()
    end_time = now + runtime
    print("=" * 60)
    log.n_p("Time:")
    print(f'StartTime   : {now.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'EndTime     : {end_time.strftime("%Y-%m-%d %H:%M:%S")}')
    print("=" * 60)


def monitor_start(runtime, file_name, disk_name, log_name):
    # ------------------------------------------------------------------------------------------
    tags = ''
    if "dd" in disk_name:
        log.run(f"iostat -xm 1 -s {runtime} ALL >> /tmp/iostat-dd-{file_name} & ")
        return

    if log.popen("ps -aux | grep 'iostat -g all -xm 1' | grep -v grep | wc -l").strip() == "0":
        if "nvme" in disk_name:
            tags = 'nvme'
        elif "sd" in disk_name:
            tags = 'sata'
        else:
            log.n_p("Uknown disk type!")
            exit()
    else:
        log.n_p("iostat not exist!")

    log.run(f"iostat -g all -xm 1 {runtime} >> {log_name}/{tags}-{file_name} & ")

    # ------------------------------------------------------------------------------------------
    if not os.path.exists(log_name + "/debug"):
        log.run(f"mkdir -p {log_name}/debug")
    if str(log.json_load("Monitor", "sar_d")).strip() == "1":
        if log.popen("ps -aux | grep 'sar -b'| grep -v grep | wc -l").strip() == "0":
            log.run(f"sar -b 1 {runtime} >> {log_name}/debug/sar_d-{file_name} & ")
    if str(log.json_load("Monitor", "vmstat_w")).strip() == "1":
        if log.popen("ps -aux | grep -i 'vmstat -w' | grep -v grep | wc -l").strip() == "0":
            log.run(f"vmstat -w 1 {runtime} >> {log_name}/debug/vmstat_w-{file_name} & ")
    if str(log.json_load("Monitor", "mpstat_p_all")).strip() == "1":
        if log.popen("ps -aux | grep -i 'mpstat -P ALL 1' | grep -v grep | wc -l").strip() == "0":
            log.run(f"mpstat -P ALL 1 {runtime} >> {log_name}/debug/mpstat_p_all-{file_name} & ")
    if str(log.json_load("Monitor", "pidstat_d")).strip() == "1":
        if log.popen("ps -aux | grep -i 'pidstat -d 1' | grep -v grep | wc -l").strip() == "0":
            log.run(f"pidstat -d 1 {runtime} >> {log_name}/debug/pidstat_d-{file_name} & ")
    if str(log.json_load("Monitor", "dstat")).strip() == "1":
        if log.popen("ps -aux | grep -i 'dstat 1' | grep -v grep | wc -l").strip() == "0":
            log.run(f"dstat 1 {runtime} >> {log_name}/debug/dstat-{file_name} & ")
    # ------------------------------------------------------------------------------------------


def soft_info(log_name):
    with open(log_name + "/debug/soft_ver.log", "a") as f:
        f.write("=" * 60 + "\n")
        f.write("[Fio.Ver]\n")
        f.write(log.popen("fio -v") + "\n")
        f.write("=" * 60 + "\n")
        f.write("[Iostat.Ver]\n")
        f.write(log.popen("iostat -V") + "\n")
        f.write("=" * 60 + "\n")
        f.write("[OS.Ver]\n")
        f.write(log.popen("cat /etc/os-release") + "\n")
        f.write("=" * 60 + "\n")
        f.write("[Uname]\n")
        f.write(log.popen("uname -a") + "\n")
        f.write("=" * 60 + "\n")
        f.write("[cmdline]\n")
        f.write(log.popen("cat /proc/cmdline") + "\n")
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
        log.popen(f"mkdir -p {log_path}/blktrace_files")
    for i in range(0,len(disk_info),3):
        disk_name = disk_info[i]
        folder_name = f"{disk_name.strip()}_{test_type}"
        if not os.path.exists(f"{log_path}/blktrace_files/{folder_name}"):
            log.popen(f"mkdir -p {log_path}/blktrace_files/{folder_name}")
        log.run(f"blktrace /dev/{disk_name} -D {log_path}/blktrace_files/{folder_name} -o {folder_name} -w {runtime} & ")
    log.n_p("已开启blktrace 追踪I/O层的信息")
    log.n_p("BLKTRACE tracking of I/O layer information enabled")
    print("=" * 60)
#blktrace result
def blktrace_result(log_path):
    print("=" * 60)
    log.n_p("Start processing BLKTRACE data information")
    log.n_p("开始处理blktrace数据信息")
    print("=" * 60)
    folder_path = log_path+"/blktrace_files"
    for path, dirs, files in os.walk(folder_path):
        if path == folder_path:continue
        file_name = path.replace(folder_path+"/","")
        log.run(f"cd {path} && blkparse -i {file_name} -d {file_name}.blktrace.bin")
        log.run(f"cd {path} && iowatcher -t {file_name}.blktrace.bin -o {log_path}/blktrace_files/{file_name}.svg")
    log.popen(f"cp {folder_path}/*.svg {log_path}")
    log.n_p("处理完毕，请检查结果文件夹中.svg文件")
    print("=" * 60)
# debug输出及运行
def debug_run_print(debug, command):
    if debug == "1":
        log.run(command)
    elif debug == "0":
        with open("./cmd.log", "a") as p:
            p.write("[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]\n")
            p.write(command + "\n")
            p.flush()
        if "fio" in command and "nohup" in command:
            with open("./fio_command.log", "a") as p:
                p.write("[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]\n")
                p.write(command + "\n")
                p.flush()
        print(command)


# 初始化log文件夹
def init_log():
    if "natt_log" in log.popen("ls /root").strip():
        if os.path.exists("/root/natt_old"):
            log.run("mv /root/natt_log* /root/natt_old")
        else:
            log.run("mkdir /root/natt_old")
            log.run("mv /root/natt_log* /root/natt_old")
    # 获取当前路径
    create_file_name = f"/root/natt_log_{now_time()}"
    log.run(f"mkdir {create_file_name}")
    log.run(f"mkdir -p {create_file_name}/debug")
    return create_file_name


def numa_info(log_name, test_type):
    if not os.path.exists(log_name + "/debug"):
        log.popen(f"mkdir -p {log_name}/debug")
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
    if log.json_load("debug", "natt_Double_opening") == "0":
        # 禁止双开
        # if int(log.popen('ps -aux | grep -i python | grep -i natt | grep -v grep | wc -l').strip()) != 1:
        #     log.error('Natt Prohibit double opening!Please run command :   natt -k ')
        #     exit()

        # 测试前kill iostat/fio
        if int(log.popen('ps -aux | grep -iE "fio|iostat" | grep -v grep | grep filename | wc -l').strip()) != 0:
            log.n_p("fio/iostat is already running! Now kill all processes!")
            log.run("pkill -9 fio ; pkill -9 iostat")

        # 测试前删除 natt -a遗留的硬盘信息
        if int(log.popen('ls /tmp/ | grep natt | wc -l').strip()) != 0:
            for file_name in os.listdir("/tmp"):
                if "natt" in file_name: log.run(f'rm -rf /tmp/{file_name}')

    elif log.json_load("debug", "natt_Double_opening") == "1":
        log.n_p("\n[-] NATT enables dual mode, performance testing is prohibited!")
        log.n_p("[-] If performance testing is required, please set natt -c debug nattDouble_opening=0")
        log.n_p("[-] natt开启双开模式，请勿进行硬盘性能导入测试!")
        log.n_p("[-] 如需进行性能测试,请使用natt -c 设置debug natt_Double_opening = 0\n")
        if warning_tips():
            log.n_p("wait 3s start natt.....")
            wait(3)
        else:
            log.error('You Chose N!')
    else:
        log.error(
            '<natt> Debug natt_Double_opening Config Error! Please Check natt_config.json! natt_Double_opening set 0 / 1 !')

    # 测试前删除 natt -a遗留的硬盘信息
    try:
        if int(log.popen('ls /tmp/ | grep natt | wc -l').strip()) != 0:
            for file_name in os.listdir("/tmp"):
                if "natt" in file_name: log.run(f'rm -rf /tmp/{file_name}')
    except:
        pass
    try:
        cmd_log_size_kb = int(int(log.popen("ls -al /opt/natt/cmd.log 2>/dev/null | awk '{{print $5}}'")) / 1024)
        max_size = int(log.json_load("natt", "cmd_log_size_kb"))
        if cmd_log_size_kb > max_size:
            log.n_p("cmd.log大小超过设定的最大值,现在进行备份处理!")
            log.n_p("The size of the cmd.log file exceeds the set maximum value!Now proceed with backup processing")
            log.run("mkdir -p /opt/natt/Cache_File")
            log.run(f"mv /opt/natt/cmd.log /opt/natt/Cache_File/cmd_bak_{str(now_time())}.log")
            time.sleep(2)
    except:
        pass
    # Clear system cache
    log.run("echo 3 > /proc/sys/vm/drop_caches")
    log.run("sync")

# 判断字符串是否为空
def str_null(strings, text):
    if text == 1:
        if not strings.isdigit():
            log.n_p("Input Error!")
            exit()
        if strings == "exit":
            log.n_p("User Input Exit!")
            exit()
        if strings == '':
            log.n_p("Input Error!")
            exit()
        if int(strings) > 22:
            log.n_p("Input Error!")
            exit()
        elif strings == "19":
            log.n_p("Disk Quickly Check (null)")
            exit()
        elif strings == "21":
            log.n_p("DD Test (null)")
            exit()
        elif strings == "22":
            log.n_p("Waiting for development (null)")
            exit()
    else:
        log.n_p("check judge input type!")


def show_sys_info():
    try:
        os_info = log.popen('cat /etc/system-release').strip()
        platform_info = platform.platform()
        processor_architecture = platform.processor()
        BMC_IP = log.popen(
            "ipmitool lan print | grep -i 'ip address' | grep -vi source | awk '{{print $4}}'").strip()
        if BMC_IP == "": BMC_IP = "GetFail!"
        SYS_IP = log.popen("hostname -I").split()[0]
        if SYS_IP == "": SYS_IP = "GetFail!"
        log.n_p("System name            : " + os_info)
        log.n_p("System version         : " + os_info)
        log.n_p("System release         : " + platform_info)
        log.n_p("System architecture    : " + processor_architecture)
        log.n_p("BMC IP                 : " + BMC_IP)
        log.n_p("SYS IP                 : " + SYS_IP)
        log.n_p("=========================================================")
    except:
        log.n_p("System name            : Getfail!")
        log.n_p("System version         : Getfail!")
        log.n_p("System release         : Getfail!")
        log.n_p("System architecture    : Getfail!")
        log.n_p("BMC IP                 : Getfail!")
        log.n_p("SYS IP                 : Getfail!")
        log.n_p("[+]Failed acquisition does not affect hard drive testing")
        log.n_p("[+]获取失败不影响硬盘测试!")


def readme():
    clear_p()
    print(log.popen(r"cat /opt/natt/README.md"))
    log.n_p("\n")

def nvme_judge_mem():
    # 获取CPU node memory信息
    node_memory = log.popen("numactl -H | grep free | awk '{{print $4}}'").split()
    # 获取nvme硬盘名称 和 pciebus信息
    nvme_bus_list = log.popen("nvme list-subsys | grep +- | awk '{print $2,$4}'").split()
    # 循环对比nvme硬盘所在node memory信息
    for i in range(0, len(nvme_bus_list)):
        if i % 2 == 0: continue
        # 获取当前循环nvme硬盘node信息
        nvme_node = log.popen(f"lspci -vvvs {nvme_bus_list[i]} | grep -i node | awk '{{print $3}}'").strip()
        # 对比nvme_node 与 cpu_node 中 memory信息
        if node_memory[int(nvme_node)] == 0:
            log.n_p(f"nvme_name:{nvme_bus_list[i - 1]} Node:{nvme_node} Node_memory:{node_memory[int(nvme_node)]}")
            log.n_p(
                f"he node where the current NVME hard disk is located has insufficient memory. Please check the memory access status!")
            log.n_p(f"Memory check failed, program automatically closes!")
            exit()
        else:
            continue
    log.n_p("Check Nvme disk memory Success!")

    if '0' in node_memory:
        print(node_memory)
        print(log.popen('numactl -H'))
        log.n_p("你的测试环境Node存在内存确失，可能会影响性能测试是否继续？")
        log.n_p(
            "There is a memory error in your testing environment Node, which may affect performance testing. Do you want to continue?")
        if 'n' in input("You chose [ y / n ]: "):
            exit()


# 等待时间
def wait(sleep_time):
    time.sleep(sleep_time)


# fio每个进程运行等待时长
def wait_disk_run():
    json_time = str(log.json_load("debug", "fio_process_wait_time")).strip()
    if json_time == '':
        time.sleep(3)
    else:
        time.sleep(int(json_time))


# 打印fio后等待时长
def wait_disk_print():
    json_time = str(log.json_load("debug", "fio_print_wait_time")).strip()
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
    smtp_server = log.json_load("email", "smtp_server")
    smtp_port = log.json_load("email", "smtp_port")
    sender_email = log.json_load("email", "sender_email")
    receiver_email = log.json_load("email", "receiver_email")
    password = log.json_load("email", "password")
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

