 # Filename : natt_main.py
# Release time : 2024.07.09
# Version:1.1.2
# by:Dong

from nattlib.natt_disk_lib import *
from nattlib.natt_public_lib import *
import json
import sys
import os

#####################################################################################
# Use sost_logging instead of natt_logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
from lib.sost_logging import dong_log as sost_dong_log

# init log
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
log.fail_exit = True

#####################################################################################
def bug():
    print('''
/**
 *
 * ━━━━━━━━━━神兽出没━━━━━━━━━━
 *
 * 　　　　　　　　┏┓　　　┏┓
 * 　　　　　　　┏┛┻━━━┛┻┓
 * 　　　　　　　┃　　　　　　　┃ 　
 * 　　　　　　　┃　　　━　　　┃
 * 　　　　　　　┃　＞　　　＜　┃
 * 　　　　　　　┃　　　　　　　┃
 * 　　　　　　　┃...　⌒　...　┃
 * 　　　　　　　┃　　　　　　　┃
 * 　　　　　　　┗━┓　　　┏━┛
 * 　　　　　　　　　┃　　　┃　Code is far away from bug with the animal protecting　　　　　　　　　　
 * 　　　　　　　　　┃　　　┃   神兽保佑,代码无bug
 * 　　　　　　　　　┃　　　┃　　　　　　　　　　　
 * 　　　　　　　　　┃　　　┃  　　　　　　
 * 　　　　　　　　　┃　　　┃
 * 　　　　　　　　　┃　　　┃　　　　　　　　　　　
 * 　　　　　　　　　┃　　　┗━━━┓
 * 　　　　　　　　　┃　　　　 　┣━━━━━━━━━━━━━━━┓
 * 　　　　　　　　　┃　　　　　┏┛
 * 　　　　　　　　　┗┓┓┏━┳┓┏┛
 * 　　　　　　　　 　┃┫┫ ┃┫┫
 * 　　　　　　　　 　┗┻┛ ┗┻┛
 *
 * ━━━━━━━━━━感觉萌萌哒━━━━━━━━━━
 */
 natt硬盘自动化测试系统，如果在测试过程中您发现任何bug或需要改进的地方，请在下方的腾讯文档中详细指出，感谢您的使用。
 【腾讯文档】Natt-buglist : https://docs.qq.com/sheet/DV2tJWUlEdndPbG9X?tab=BB08J2
    ''')


def tips():
    print('''
|---------------------------------------------------------------------------------------------------------|
| [Tips]                                                                                                  |
| [!] Please set the system to disable sleep and automatically turn off the monitor.                      |     
| [!] Do not continue to use fio commands during operation!                                               |
| [!] seq = sequence =  / ran = Random / NULL = Under development / All models can be modified(natt -c)   |
| [Now Test Strategy]                                                                                     |
| [!] HDD     -> seq_write seq_read  bs=512K/128K numa=True(raid_numa)                                    |
|             -> default random no Test                                                                   |
| [!] NVME    -> seq_write seq_read  bs=128K      numa=True                                               |
|             -> ran_write ran_read  bs=4K        numa=True                                               |
| [!] iostat  -> MB/s = fio -> Mib/s                                                                      | 
|---------------------------------------------------------------------------------------------------------|
''')


def mode_list():
    print(r'''
        |===============[Sequence Test]================|   |================[Random Test]=================|
        |  < 1> Seq_Read                               |   |  < 9> Ran_Read                               |
        |  < 2> Seq_Write                              |   |  <10> Ran_Write                              |
        |  < 3> Seq_prewriting                         |   |  <11> Ran_prewriting                         |
        |  < 4> Seq_Write_Read                         |   |  <12> Ran_Write_Read                         |
        |  < 5> Seq_prewriting + Seq_Read              |   |  <13> Ran_prewriting + Ran_Read              |
        |  < 6> Seq_prewriting + Seq_Write             |   |  <14> Ran_prewriting + Ran_Write             |
        |  < 7> Seq_readwrite R=70% W=30%              |   |  <15> Ran_randrw R=70% W=30%                 |
        |  < 8> Seq_prewriting + Seq_Write + Seq_Read  |   |  <16> Ran_prewriting + Ran_Write + Ran_read  |
        |==============================================|   |==============================================|

        |==================[All Test]==================|   |==============[Fio Other Test]================|
        |  <17> Ran_ALL + Seq_ALL (loops)              |   |  <20> Other FIO Test Command                 |
        |  Sequential pre writing using loops          |   |  <21> N/A                                    |
        |                                              |   |  <22> N/A                                    |
        |  <18> Ran_ALL + Seq_ALL (Runtime)            |   |  <23> N/A                                    |
        |  Sequential pre writing using Times          |   |  <24> N/A                                    |
        |==============================================|   |==============================================|

        |================[Other Test]==================|   |==============================================|
        |   <25> Smartctl health check                 |   |           _____   _____  __   __             |
        |   <26> DD LongTime Test                      |   |          |_   _| |_   _| \ \ / /             |
        |   <27> Mount / Umount Disk                   |   |            | |     | |    \ V /              |
        |   <28> N/A                                   |   |           _|_|_   _|_|_   _|_|_              |
        |                                              |   |         _|"""""|_|"""""|_| """ |             |
        |----------------------------------------------|   |----------------------------------------------|''')

def main_show():
    clear_p()
    print("=========================================================")
    print("|\033[34m     ████     ██     ██     ██████████ ██████████       \033[0m|")
    print("|\033[34m    ░██░██   ░██    ████   ░░░░░██░░░ ░░░░░██░░░        \033[0m|")
    print("|\033[34m    ░██░░██  ░██   ██░░██      ░██        ░██           \033[0m|")
    print("|\033[34m    ░██ ░░██ ░██  ██  ░░██     ░██        ░██           \033[0m|")
    print("|\033[34m    ░██  ░░██░██ ██████████    ░██        ░██           \033[0m|")
    print("|\033[34m    ░██   ░░████░██░░░░░░██    ░██        ░██           \033[0m|")
    print("|\033[34m    ░██    ░░███░██     ░██    ░██        ░██           \033[0m|")
    print("|\033[34m    ░░      ░░░ ░░      ░░     ░░         ░░            \033[0m|")
    print("|                                                       |")
    print(
        f"|\033[32m Version:{str(log.json_get('Version', 'natt_version', filename='natt', web='no-log')).strip()}   | Author: Xiaodong Fan | Time:20260107 \033[0m|")
    print("=========================================================")


def help_text():
    print("[natt-command]")
    print("[√]    help       natt help document")
    print("[√]    show       show test mode")
    print("[√]    start      start test")
    print("[√]    info       show nvme/sata disk info")
    print("[√]    readme     show readme")
    print("[√]    clear      clear Terminal")
    print("[√]    format     format Disk")
    print("[√]    update     update natt")
    print("[√]    bug        found a bug!")

def user_chose(cho_num, dis_typ):
    test_type_arr = ["", "Seq_Read", "Seq_Write", "Seq_prewriting", "Seq_Write_Read", "Seq_prewriting + Seq_Read",
                     "Seq_prewriting + Seq_Write", "Seq_readwrite R=70% W=30%", "Seq_prewriting + Seq_Write + Seq_Read"
        , "Ran_Read", "Ran_Write", "Ran_prewriting", "Ran_Write_Read", "Ran_prewriting + Ran_Read",
                     "Ran_prewriting + Ran_Write", "Ran_randrw R=70% W=30%", "Ran_prewriting + Ran_Write + Ran_read"
        , "Ran_ALL + Seq_ALL", "Smartctl health check","DD LongTime Test          (NULL)", "Waiting for development   (NULL)"]

    try:
        int(cho_num)
    except:
        home_page('Debug', dis_typ, cho_num)

    # 判断用户选择测试模型
    if test_type_arr[int(cho_num)] != "":
        home_page(test_type_arr[int(cho_num)], dis_typ, cho_num)
    else:
        log._fail("[Fail] User selection Error!")

def home_page(test_type, dis_typ, cho_num):
    disk_info = ''
    with open('./config/natt_config.json', 'r') as file:
        # 格式化config.json数据
        data = json.load(file)
        # 读取config.json中diskinfo数值，如果用户自己输入硬盘信息那么
        if dis_typ == "nvme":
            if data['DiskInfo']['nvme_info'] != '':
                disk_info = str(data['DiskInfo']['nvme_info']).split(',')
        elif dis_typ == "sata":
            if data['DiskInfo']['sata_info'] != '':
                disk_info = str(data['DiskInfo']['sata_info']).split(',')
            else:
                disk_info = ''
        elif dis_typ == "all":
            disk_info = []
            if data['DiskInfo']['nvme_info'] != '':
                disk_info = str(data['DiskInfo']['nvme_info']).split(',')
            if data['DiskInfo']['sata_info'] != '':
                disk_info = disk_info + str(data['DiskInfo']['sata_info']).split(',')
            if disk_info == '':
                disk_info = ''

    log_name = init_log()
    clear_p()

    print("[+]---------------------------------------------------------------------------------------------[+]")
    print(f"[natt] You have chosen {test_type}!")
    print(f"[natt] Test disk type:{dis_typ}")
    print(
        f"[natt] The hard drive information will be output below. After checking for accuracy, press enter and press the [y] key!")
    print("[+]---------------------------------------------------------------------------------------------[+]")
    # DEBUG 用户输入测试硬盘信息进行测试
    if dis_typ == "nvme":
        nvme_info = nvme_disk_info(disk_info)
        log.os_run(f"mv /tmp/natt_nvme_info.log {log_name}")
        if len(nvme_info) == 0:
            log._fail(" No Nvme Disk Info found!")
        else:
            run_start(nvme_info, cho_num, log_name)
    elif dis_typ == "sata":
        sata_info = sata_disk_info(disk_info)
        if len(sata_info) == 0:
            log._pr("No Sata Disk Info found!")
            exit()
        log.os_run(f"mv /tmp/natt_sata_info.log {log_name}")
        run_start(sata_info, cho_num, log_name)
    elif dis_typ == "all":
        if disk_info == []:disk_info = ''
        nvme_info = nvme_disk_info(disk_info)
        sata_info = sata_disk_info(disk_info)
        all_info = nvme_info+sata_info
        log.os_run(f"mv /tmp/natt_all_info.log {log_name}")
        run_start(all_info, cho_num, log_name)
    else:
        log._pr(f"Disk Test Type Error! Now : {dis_typ}")
        exit()

def run_start(disk_info, test_type, log_name):
    if log.json_get("DiskInfo","fio_mode",filename='natt') == "1":
        tmp = log._in(" Do you still want to continue [y/n] : ")
        if tmp == "n":
            exit()
        start_test(test_type, disk_info, log_name)
    else:
        # 用户判断是否进行格式化操作
        format_disk_type = log._in(" Do you want to format Disk? [y/n] : ")
        if format_disk_type == "y":
            print("<natt> format disk info : ", end='')
            print(disk_info)
            if "sd" in disk_info[0]:
                for i in range(0, len(disk_info), 3):
                    sata_format(disk_info[i])
            elif "nvme" in disk_info[0]:
                print("[----[Nvme Format Type]----]")
                print("[    1.mkfs.ext4           ]")
                print("[    2.nvme format         ]")
                print("[--------------------------]")
                nvme_format_type = log._in(" chose : ")
                # for循环取disk_info中硬盘名称所在的数值
                for i in range(0, len(disk_info), 3):
                    nvme_format(disk_info[i], nvme_format_type)
            else:
                log._pr(" You chose No format disk!")
        else:
            log._pr(" You have chosen not to perform formatting operations!")

        tmp = log._in(" Do you still want to continue [y/n] : ")
        if tmp == "n":
            exit()
        # 按照用户所选测试模型进行测试
        start_test(test_type, disk_info, log_name)
    return 0
if __name__ == '__main__':
    # init natt
    
    init_natt()
    main_show()
    Blessings()
    show_sys_info()
    help_text()
    while True:
        # 快速测试模块
        # qk_flags = log.json_get('debug','debug_qk', filename='natt', web='no-log')
        user_input = log._in('')
        if user_input == 'show':
            log._pr("\n" * 6)
            mode_list()
        elif user_input == 'update':
            now_ver = int(log.json_get("Version", "natt_version", filename='natt', web='no-log').strip().replace(".", ""))
            server_ip = log.json_get("Version", "update_Web_server_ip", filename='natt', web='no-log').strip()
            if "0% packet loss" in log.os_popen(f'ping -c 1 {server_ip}'):
                log._pr("WebServerClientOk!")
            else:
                log._pr("WebServerClientError!")
                break
            log._pr(f'Now_Natt.ver : {now_ver}')
            update_ver = int(log.os_popen(f"curl http://{server_ip}/natt/new_version.txt").replace(".",""))
            if now_ver == update_ver:
                log._pr("natt检查为最新版本，无需更新")
                log._pr("NATT check to the latest version, no update required")
            elif now_ver < update_ver:
                log._pr("natt检查为旧版本，是否更新？")
                log._pr("NATT check shows old version, do you want to update it?")
                if log._in("Update ? [ y / n ] : ") == "y":
                    new_ver = log.os_popen(f"curl http://{server_ip}/natt/new_version.txt").strip()
                    command = f"echo 'sleep 3 && cd && wget http://{server_ip}/natt/natt-v{new_ver}-Release.tar && tar -xvf natt-v{new_ver}-Release.tar && cd natt-v{new_ver}-Release && python3 natt_install.py && cd && natt -h && rm -rf /opt/run.sh' >> /opt/run.sh"
                    log.os_run(command)
                    log.os_run("chmod 777 /opt/run.sh")
                    log.os_run("sh /opt/run.sh &")
                    log._pr("==================")
                    print(f'''
|===================================================================|
|    ██     ██              ██             ██   ██                  |
|   ░██    ░██ ██████      ░██            ░██  ░░            █████  |
|   ░██    ░██░██░░░██     ░██  ██████   ██████ ██ ███████  ██░░░██ |
|   ░██    ░██░██  ░██  ██████ ░░░░░░██ ░░░██░ ░██░░██░░░██░██  ░██ | 
|   ░██    ░██░██████  ██░░░██  ███████   ░██  ░██ ░██  ░██░░██████ |
|   ░██    ░██░██░░░  ░██  ░██ ██░░░░██   ░██  ░██ ░██  ░██ ░░░░░██ |
|   ░░███████ ░██     ░░██████░░████████  ░░██ ░██ ███  ░██  █████  |
|    ░░░░░░░  ░░       ░░░░░░  ░░░░░░░░    ░░  ░░ ░░░   ░░  ░░░░░   |
|   Now.ver : {now_ver}                Update.ver : {new_ver} |
|===================================================================|
                    ''')
                    log._pr("==================")
                    time.sleep(60)
                    print("Updating Success!")
                    exit()
            elif now_ver > update_ver:
                log._pr("natt检查为超前版本,太厉害了！")
                log._pr("Natt checked as an advanced version, it's amazing!")
                log._pr("请联系作者email:fanxiaodong@ttyinfo.com")
                log._pr("Please contact the author via email: fanxiaodong@ttyinfo.com")
                log._exitt("Natt.Ver.Err")
            else:
                continue
        elif user_input == 'start':
            # 快速测试模块 基于 1.1.1版本进行开发，于 1.1.3版本删除
            # result = log.os_popen('cat /opt/natt/.qk_flag.txt')
            # if 'False' in result:
            #     log.n_p("检测到快速测试结果失败,请调试后在进行性能测试!")
            #     log.n_p("Quick test result failure detected, please debug before conducting performance testing!")
            #     if qk_flags == '0':
            #         if log.u_in('Continue? [y / n ] : ') == 'n': exit()
            # elif 'True' in result:
            #     log.n_p("快速测试通过,可进行性能测试!")
            # elif '' in result:
            #     log.n_p("检测到未进行快速测试,请进行快速测试后再进行性能测试!")
            #     log.n_p("Detected that no quick test has been conducted. Please conduct a quick test before proceeding with performance testing!")
            #     if qk_flags == "0":
            #         if log.u_in('Continue? [y / n ] : ') == 'n': exit()
            nvme_judge_mem()
            tips()
            mode_list()
            # 用户选择测试模型和测试硬盘类型
            cho_num = log._in(" Please select the testing model (Echo_numg:1) : ")
            log.json_set("Test_tmp","Running_flag","8")
            if cho_num == "25":
                smart_health_check()
            elif cho_num == "26":
                dd_test()
            elif cho_num == "27":
                mount_main()
            elif cho_num == "25":
                log._pr(" Please look natt-v1.1.4-Release.doc")
            else:
                str_null(cho_num, 1)
                dis_typ = log._in(" Now Currently only supported (nvme/sata/all) : ")
                user_chose(cho_num, dis_typ)
                break
        elif user_input == 'info':
            print('|=================[DiskInfo]===================|')
            print('|      all      nvme sata disk info            |')
            print('|      sata     sata disk info                 |')
            print('|      nvme     nvme  disk info                |')
            print('|==============================================|')
            disk_info_type = log._in(" Enter Disk info : ")
            if disk_info_type == 'all':
                nvme_disk_info('')
                sata_disk_info('')
            elif disk_info_type == 'nvme':
                nvme_disk_info('')
            elif disk_info_type == 'sata':
                sata_disk_info('')
            else:
                continue
        elif user_input == 'help':
            help_text()
        elif user_input == 'readme':
            readme()
        elif user_input == 'clear':
            clear_p()
            print("\n")
        elif user_input == 'format':
            print('|=================[FormatDisk]=================|')
            print('|      all      format sata/nvme               |')
            print('|      sata     format sata                    |')
            print('|      nvme     format nvme                    |')
            print('|==============================================|')
            format_disk_type = log._in(" Enter Format Disk type : ")
            if format_disk_type == 'all':
                if warning_tips():
                    disk_info = nvme_disk_info('')
                    log._pr("NVME hard disk formatting operation is about to proceed, timeout 10s,Problem with ctrl+C")
                    print("[----[Nvme Format Type]----]")
                    print("[    1.mkfs.ext4           ]")
                    print("[    2.nvme format         ]")
                    print("[--------------------------]")
                    nvme_format_type = log._in(" chose : ")
                    wait(10)
                    for i in range(0, len(disk_info), 3):
                        nvme_format(disk_info[i], nvme_format_type)
                    mount_type = log._in("Mount? [y/n]: ")
                    if mount_type == "y":
                        for i in range(0, len(disk_info), 3):
                            mount_disk(disk_info[i])
                    disk_info = sata_disk_info('')
                    log._pr("SATA hard disk formatting operation is about to proceed, timeout 10s,Problem with ctrl+C")
                    wait(10)
                    for i in range(0, len(disk_info), 3):
                        sata_format(disk_info[i])
                    mount_type = log._in("Mount? [y/n]: ")
                    if mount_type == "y":
                        for i in range(0, len(disk_info), 3):
                            mount_disk(disk_info[i])
                else:
                    break
            elif format_disk_type == 'sata':
                if warning_tips():
                    disk_info = sata_disk_info('')
                    log._pr("SATA hard disk formatting operation is about to proceed, timeout 10s,Problem with ctrl+C")
                    wait(10)
                    for i in range(0, len(disk_info), 3):
                        sata_format(disk_info[i])
                    mount_type = log._in("Mount? [y/n]: ")
                    if mount_type == "y":
                        for i in range(0, len(disk_info), 3):
                            mount_disk(disk_info[i])
                else:
                    break
            elif format_disk_type == 'nvme':
                if warning_tips():
                    disk_info = nvme_disk_info('')
                    log._pr("NVME hard disk formatting operation is about to proceed, timeout 10s,Problem with ctrl+C")
                    print("[----[Nvme Format Type]----]")
                    print("[    1.mkfs.ext4           ]")
                    print("[    2.nvme format         ]")
                    print("[--------------------------]")
                    nvme_format_type = log._in(" chose : ")
                    wait(10)
                    for i in range(0, len(disk_info), 3):
                        nvme_format(disk_info[i], nvme_format_type)
                    mount_type = log._in("Mount? [y/n]: ")
                    if mount_type == "y":
                        for i in range(0, len(disk_info), 3):
                            mount_disk(disk_info[i])
                else:
                    break
                mount_type = log._in("Mount? [y/n]: ")
            else:
                log._pr('unknown format disk type!')
        elif user_input == 'bug':
            bug()
        elif user_input == 'exit':
            log.json_set("Test_tmp","Running_flag","9")
            break
        elif user_input == "q":
            log.json_set("Test_tmp","Running_flag","9")
            break
        else:
            continue
    
    log.json_set("Test_tmp","Running_flag","9")
    log.os_run('natt -k')
