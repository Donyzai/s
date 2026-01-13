# Filename : natt_disk_lib.py
# Release time : 2024.07.05
# Version:1.1.2
# by:Dong
import os.path

from .natt_public_lib import *
#####################################################################################
from .natt_logging import dong_log
log = dong_log()
log.json_filename = 'config/natt_config.json'
if log.json_load('debug', 'debug_print') == '1':
    log.d_p_flag = True
else:
    log.d_p_flag = False
log.error_exit = True
#####################################################################################
def fio_file_result(log_name, disk_list):
    clear_p()
    disk_info = []
    for i in range(len(disk_list)):
        if i % 3 == 0:
            disk_info.append(disk_list[i])
        else:
            continue
    print(disk_info)

    Backboard_performance = 0
    backboard_arr = []

    collect_flags = "n"
    if "y" in collect_flags:
        backboard_add_num_flags = True
        backboard_arr = log.u_in("Input One Backboard disk arr eg: sda,sdb,sdc :: ").split(",")
    elif 'n' in collect_flags:
        backboard_add_num_flags = False
    else:
        backboard_add_num_flags = False

    print("\n[--------------------------------Test_Result--------------------------------]\n")
    file_names = sorted(os.listdir(log_name))

    print("Disk_name".ljust(15) + "rw_mod".ljust(15) + "IOPS".ljust(15) + "BW".ljust(70) + "Runtime(msec)")
    for file_name in file_names:
        if "iostat" in file_name:
            print(end='')
        else:

            # 按测试顺序进行结果打印
            rw_mode = ""
            for disk_name in disk_info:
                if disk_name in file_name:
                    disk_name = log.popen(
                        f"cat {log_name}/{file_name} | grep -i util | awk '{{print $1}}'").replace(":", "")
                    rw_mode = log.popen(
                        f"cat {log_name}/{file_name} | grep -i myjob | grep -i rw | awk '{{print $3}}'").strip().replace(
                        ",", "").replace("rw=", "")
                    IOPS = log.popen(
                        f"cat {log_name}/{file_name}| grep IOPS= | awk '{{print $2}}'").strip().replace(",",
                                                                                                        "").replace(
                        "IOPS=", "")
                    BW = log.popen(
                        f"cat {log_name}/{file_name} | grep IOPS= | awk '{{print $3,$4}}'").strip().replace("BW=", "")
                    if backboard_add_num_flags:
                        for backboard_disk_name in backboard_arr:
                            if backboard_disk_name in disk_name:
                                Backboard_performance += int(log.popen(
                                    f"cat {log_name}/{file_name} | grep IOPS= | awk '{{print $3}}'").strip().replace(
                                    "BW=", "").replace("MiB/s", ""))
                    runtime = log.popen(
                        f"cat {log_name}/{file_name} | grep -i run= | awk '{{print $8}}'").strip().replace("run=", "")
                    print_save_text(file_path_name=log_name + "/result.log",
                                    text=disk_name.strip().ljust(15) + rw_mode.ljust(15) + IOPS.ljust(15) + BW.ljust(
                                        70) + runtime.ljust(15))
            print_save_text(file_path_name=log_name + "/result.log",text='all'.strip().ljust(15) + rw_mode.ljust(15) + ''.ljust(15) + ''.ljust(70) + ''.ljust(15))

    if int(Backboard_performance) > 0:
        print("Backboard_performance : " + str(Backboard_performance))
    # 保存fio输出到nohup的信息
    log.run(f"mv /opt/natt/nohup.out {log_name}/nohup.log")
    log.run(f"cp /opt/natt/cmd.log {log_name}/cmd.log")
    result = log.popen(f"cat {log_name}/result.log")
    if log.json_load("email", "enable") == "1": smtp_send_result(result)

#####################################################################################
def handle_other_iostat_data(filepath):

    log.run(f"mv /root/natt_iostat_other_data /tmp/other_iostat_other_data_{time.time()}")
    log.run(f"mkdir -p /root/natt_iostat_other_data")

    print("================================================")
    print("<natt> Handle Other IOSTAT Seq Read / Write")
    print("================================================")
    if not os.path.exists(filepath):
        print("No such file or directory: " + filepath)
        exit()

    sysdisk = sysdisk_name()
    print("sysdisk_name : " + sysdisk)
    disk_list = log.popen(f"ls /sys/block/ | grep -viw '{sysdisk}'").split()
    print("disk_list : " + str(disk_list))

    # iostat_type 1 = iostat -m 1
    # iostat_type 2 = iostat -xm 1
    if "wrqm/s" not in log.popen(f"cat {filepath} | head -n 200"):
        print("iostat type : iostat -m ")
        iostat_type = 1
        read_space = '3'
        write_space = '4'
        count = 0
        for disk_name in disk_list:
            print(f"<{disk_name}> Reading!")
            log.run(f"echo '{disk_name}' > /root/natt_iostat_other_data/{disk_name}_read.csv")
            log.run(f"echo '{disk_name}' > /root/natt_iostat_other_data/{disk_name}_write.csv")
            log.run(f"cat {filepath} | grep -w '{disk_name}' | grep -vi ncie | grep -vi read | awk '{{print $3}}' >> /root/natt_iostat_other_data/{disk_name}_read.csv")
            log.run(f"cat {filepath} | grep -w '{disk_name}' | awk '{{print $4}}' >> /root/natt_iostat_other_data/{disk_name}_write.csv")
            print(f"<{disk_name}> Processed successfully!")
    else:
        print("iostat type : iostat -xm ")
        iostat_type = 2
        read_space = '3'
        write_space = '9'
        for disk_name in disk_list:
            print(f"<{disk_name}> Reading!")
            log.run(f"echo '{disk_name}' > /root/natt_iostat_other_data/{disk_name}_read.csv")
            log.run(f"echo '{disk_name}' > /root/natt_iostat_other_data/{disk_name}_write.csv")
            log.run(f"cat {filepath} | grep -w '{disk_name}' | awk '{{print $3}}' >> /root/natt_iostat_other_data/{disk_name}_read.csv")
            log.run(f"cat {filepath} | grep -w '{disk_name}' | awk '{{print $9}}' >> /root/natt_iostat_other_data/{disk_name}_write.csv")
            print(f"<{disk_name}> Processed successfully!")
    log.run("paste *_read.csv >> /root/natt_iostat_other_data/natt_summay_read_data.csv")
    log.run("paste *_write.csv >> /root/natt_iostat_other_data/natt_summay_write_data.csv")
    print("=========================================================")
    print("natt_summay_read_data  path : /root/natt_iostat_other_data/natt_summay_read_data.csv")
    print("natt_summay_write_data path : /root/natt_iostat_other_data/natt_summay_write_data.csv")
    print("=========================================================")

#####################################################################################
def result_handle(log_name):

    log.run(f"natt -a >> {log_name}/natt_disk_info_end.log")

    #save mpstat.txt to {result_folder}
    #log.n_p("Move mpstat.txt success!")
    log.run(f"mv /opt/natt/mpstat.txt {log_name}/mpstat.txt")
    log.n_p("Processing data.....")
    original_list = log.popen(f"cat {log_name}/result.log | awk '{{print $1}}' ").split()
    seen = set()
    disk_list = [x for x in original_list if x not in seen and not seen.add(x)]
    log.run(f"rm -rf {log_name}/data_files")
    log.run(f"mkdir -p {log_name}/data_files")
    for file_names in os.listdir(log_name):
        if "iostat" in file_names:
            test_type = str(file_names.split("-")[3] + '_' + file_names.split("-")[4])
            log.run(f"mkdir -p {log_name}/data_files/{test_type}")
            result_folder = f"{log_name}/data_files/{test_type}"
            files_name = []
            for disk_name in disk_list:
                files_namee = f"{result_folder}/iostat-{disk_name}-{test_type}.log"
                log.run(f"echo {disk_name} >> {files_namee}")
                files_name.append(file_names)
                if "sequence" in test_type:
                    if disk_name != "all":
                        if "read" in file_names:
                            log.run(f"cat {log_name}/{file_names} | grep '^{disk_name}\\b' | awk '{{print $3}}'>> {files_namee}")
                        else:
                            log.run(
                                f"cat {log_name}/{file_names} | grep '^{disk_name}\\b' | awk '{{print $9}}'>> {files_namee}")
                    else:
                        if "read" in file_names:
                            log.run(f"cat {log_name}/{file_names} | grep 'all' | awk '{{print $3}}'>> {files_namee}")
                        else:
                            log.run(f"cat {log_name}/{file_names} | grep 'all' | awk '{{print $9}}'>> {files_namee}")
                elif "random" in test_type:
                    if disk_name != "all":
                        log.run(f"cat {log_name}/{file_names} | grep '^{disk_name}\\b' | awk '{{print $2}}' >> {files_namee}")
                    else:
                        log.run(f"cat {log_name}/{file_names} | grep 'all' | awk '{{print $2}}' >> {files_namee}")
            log.run(f"paste {result_folder}/* >> {result_folder}/{test_type}.csv")
        else:
            continue
    log.n_p(f"Processing data Success! Result Folder : {log_name}/data_files/")

    if log.json_load("Monitor","blktrace")=="1":
        blktrace_result(log_name)
#####################################################################################
def scheduler_info(disk_list,log_path):
    f = open(f"{log_path}/debug/scheduler_info.log","a")
    f.write("="*60+"\n")
    for i in range(0,len(disk_list),3):
        disk_name = disk_list[i].strip()
        f.write(f"Disk_name : {disk_name}\n")
        f.write("Scheduler : "+log.popen(f"cat /sys/block/{disk_name}/queue/scheduler"))
    f.write("="*60+"\n")
#####################################################################################

def dd_kill():
    while_process = log.popen("ps -aux | grep -i sh | grep -i nohup | grep -i 'while' | grep -v grep |  awk '{{print $2}}' ").split()
    dd_process = log.popen("ps -aux | grep -i dd | grep -i if | grep -v sh | grep -v while | grep -v grep | awk '{{print $2}}'").split()
    for pid in while_process:
        log.run(f'kill -9 {str(pid).strip()}')
    for pid in dd_process:
        log.run(f"kill -9 {str(pid).strip()}")
    log.n_p(" Kill natt process success!")
    log.exitt("Normal exit")

def ddr_start(disk_name):
    log.n_p(f"DiskName : {disk_name} Type:DDR Success!")
    ddr_command = f'nohup sh -c `while [ 1 ]; do dd if=/dev/{disk_name.strip()} of=/dev/null bs=1M iflag=direct ; done ` & '
    log.d_p(ddr_command)
    log.run(ddr_command)

def ddw_start(disk_name):
    log.n_p(f"DiskName : {disk_name} Type:DDW Success!")
    ddw_command = f'nohup sh -c `while [ 1 ]; do dd if=/dev/{disk_name.strip()} of=/dev/null bs=1M iflag=direct ; done ` & '
    log.d_p(ddw_command)
    log.run(ddw_command)


def dd_test():
    runtime = ""
    print('|==================[DDTest]====================|')
    print('|      all      nvme & sata                    |')
    print('|      sata     sata   disk                    |')
    print('|      nvme     nvme   disk                    |')
    print('|      other    user input disk list           |')
    print('|      kill     pkill dd process               |')
    print('|==============================================|')
    chos_1 = log.u_in("chose : ").lower()
    if chos_1 == "": log.exitt("User.Input.Null")
    if chos_1 == "kill": dd_kill()
    print('|==================[DDTest]====================|')
    print('|                    ddr                       |')
    print('|                    ddw                       |')
    print('|==============================================|')
    chos_2 = log.u_in("chose : ").lower()
    if chos_2 == "": log.exitt("User.Input.Null")
    print('|==================[Iostat]====================|')
    print('|                    y                         |')
    print('|                    n                         |')
    print('|==============================================|')
    chos_3 = log.u_in("chose : ").lower()
    if chos_3 == "": log.exitt("User.Input.Null")
    if chos_3 == "y":
        print('|==================[Runtime]===================|')
        print('|                 1.43200                      |')
        print('|                 2.86400                      |')
        print('|                 3.other                      |')
        print('|==============================================|')
        chos_4 = log.u_in("chose : ").lower()
        if chos_4 == "":
            runtime = 43200
        if chos_4 == "3":
            runtime = int(log.u_in("Runtime(s) : "))
        elif chos_4 == "2":
            runtime = 86400
        elif chos_4 == "1":
            runtime = 43200
        else:
            runtime = ""
    if chos_1 == "all":
        nvme_Disk = nvme_disk_info('')
        if not warning_tips(): log.exitt("User.Chose.Exit")
        for i in range(0, len(nvme_Disk), 3):
            if chos_2 == "ddr":
                ddr_start(nvme_Disk[i])
            elif chos_2 == "ddw":
                ddw_start(nvme_Disk[i])
        sata_Disk = sata_disk_info('')
        for i in range(0, len(sata_Disk), 3):
            if chos_2 == "ddr":
                ddr_start(sata_Disk[i])
            elif chos_2 == "ddw":
                ddw_start(sata_Disk[i])
        if chos_3 == "y":
            monitor_start(runtime=runtime, file_name=chos_2, disk_name="dd", log_name="")
            log.n_p(f"Iostat File Path : /tmp/iostat-dd-{chos_2}.log")
    elif chos_1 == "nvme":
        nvme_Disk = nvme_disk_info('')
        if not warning_tips(): log.exitt("User.Chose.Exit")
        for i in range(0, len(nvme_Disk), 3):
            if chos_2 == "ddr":
                ddr_start(nvme_Disk[i])
            elif chos_2 == "ddw":
                ddw_start(nvme_Disk[i])
        if chos_3 == "y":
            monitor_start(runtime=runtime, file_name=chos_2, disk_name="dd", log_name="")
            log.n_p(f"Iostat File Path : /tmp/iostat-dd-{chos_2}.log")
    elif chos_1 == "sata":
        sata_Disk = sata_disk_info('')
        if not warning_tips(): log.exitt("User.Chose.Exit")
        for i in range(0, len(sata_Disk), 3):
            if chos_2 == "ddr":
                ddr_start(sata_Disk[i])
            elif chos_2 == "ddw":
                ddw_start(sata_Disk[i])
        if chos_3 == "y":
            monitor_start(runtime=runtime, file_name=chos_2, disk_name="dd", log_name="")
            log.n_p(f"Iostat File Path : /tmp/iostat-dd-{chos_2}.log")
    elif chos_1 == "other":
        disk_list = log.u_in("Disk Arry eg : sda,sdb,nvme0n1,nvme1n1 : ").strip().split(",")
        for disk_name in disk_list:
            if chos_2 == "ddr":
                ddr_start(disk_name)
            elif chos_2 == "ddw":
                ddw_start(disk_name)
        if chos_3 == "y":
            monitor_start(runtime=runtime, file_name=chos_2, disk_name="dd", log_name="")
            log.n_p(f"Iostat File Path : /tmp/iostat-dd-{chos_2}.log")
    else:
        log.exitt("Invalid choice!")

def smart_health_check():
    print('|==============[DiskCheckHealth]===============|')
    print('|      all      nvme & sata                    |')
    print('|      sata     sata   disk                    |')
    print('|      nvme     nvme   disk                    |')
    print('|==============================================|')
    chos_type = log.u_in(" chos_type : ")
    if chos_type == "all":
        disk_info = nvme_disk_info('')
        for i in range(0, len(disk_info), 3):
            result = log.popen(
                f"smartctl -H /dev/{disk_info[i]} | grep -i result | awk '{{print $6}}'").strip()
            log.n_p(f" DiskName : {disk_info[i]}  Result : {result.strip()}")
        disk_info = sata_disk_info('')
        for i in range(0, len(disk_info), 3):
            result = log.popen(
                f"smartctl -H /dev/{disk_info[i]} | grep -i result | awk '{{print $6}}'").strip()
            log.n_p(f" DiskName : {disk_info[i]}  Result : {result.strip()}")
    elif chos_type == "sata":
        disk_info = sata_disk_info('')
        for i in range(0, len(disk_info), 3):
            result = log.popen(
                f"smartctl -H /dev/{disk_info[i]} | grep -i result | awk '{{print $6}}'").strip()
            log.n_p(f" DiskName : {disk_info[i]}  Result : {result.strip()}")
    elif chos_type == "nvme":
        disk_info = nvme_disk_info('')
        for i in range(0, len(disk_info), 3):
            result = log.popen(
                f"smartctl -H /dev/{disk_info[i]} | grep -i result | awk '{{print $6}}'").strip()
            log.n_p(f" DiskName : {disk_info[i]}  Result : {result.strip()}")
    else:
        log.n_p("Invalid chos_type Error!")

# 检查硬盘类型判断是否需要numactl绑核测试
def Bound_nucleus(disk_name, node, numa):
    node = node.strip().replace("\n", "")
    numa = numa.strip().replace("\n", "")
    if 'nvme' in disk_name:
        if log.json_load('Bound_nucleus', 'nvme') == '1':
            if log.json_load("Bound_nucleus", 'Bound_nucleus_type_1') == '1':
                bound_nucleus_command = f'taskset -c {node}'
                return bound_nucleus_command
            elif log.json_load("Bound_nucleus", 'Bound_nucleus_type_2') == '1':
                bound_nucleus_command = f'numactl -C {node}'
                # test
                result = log.popen(bound_nucleus_command + " echo 0")
                if 'libnuma: Warning' in result:
                    log.n_p("Numa空间缺少请检查环境后重新开始测试！")
                    log.n_p("Numa space is missing. Please check the environment and restart testing!")
                    exit()
                return bound_nucleus_command
            elif log.json_load("Bound_nucleus", 'Bound_nucleus_type_3') == '1':
                bound_nucleus_command = f'numactl -N {numa} -m {numa}'
                result = log.popen(bound_nucleus_command + " echo 0")
                if 'libnuma: Warning' in result:
                    log.n_p("Numa空间缺少请检查环境后重新开始测试！")
                    log.n_p("Numa space is missing. Please check the environment and restart testing!")
                    exit()
                return bound_nucleus_command
            else:
                bound_nucleus_command = f'numactl -N {numa} -m {numa}'
                result = log.popen(bound_nucleus_command + " echo 0")
                if 'libnuma: Warning' in result:
                    log.n_p("Numa空间缺少请检查环境后重新开始测试！")
                    log.n_p("Numa space is missing. Please check the environment and restart testing!")
                    exit()
                return bound_nucleus_command
        else:
            return ""
    elif 'sd' in disk_name:
        if log.json_load('Bound_nucleus', 'sata') == '1':
            if log.json_load("Bound_nucleus", 'Bound_nucleus_type_1') == '1':
                bound_nucleus_command = f'taskset -c {node}'
                return bound_nucleus_command
            elif log.json_load("Bound_nucleus", 'Bound_nucleus_type_2') == '1':
                bound_nucleus_command = f'numactl -C {node}'
                result = log.popen(bound_nucleus_command + " echo 0")
                if 'libnuma: Warning' in result:
                    log.n_p("Numa空间缺少请检查环境后重新开始测试！")
                    log.n_p("Numa space is missing. Please check the environment and restart testing!")
                    exit()
                return bound_nucleus_command
            elif log.json_load("Bound_nucleus", 'Bound_nucleus_type_3') == '1':
                bound_nucleus_command = f'numactl -N {numa} -m {numa}'
                result = os.popen(bound_nucleus_command + " echo 0").read()
                if 'libnuma' in result:
                    log.n_p("Numa空间缺少请检查环境后重新开始测试！")
                    log.n_p("Numa space is missing. Please check the environment and restart testing!")
                    exit()
                return bound_nucleus_command
            else:
                bound_nucleus_command = f'numactl -N {numa} -m {numa}'
                result = log.popen(bound_nucleus_command + " echo 0")
                if 'libnuma: Warning' in result:
                    log.n_p("Numa空间缺少请检查环境后重新开始测试！")
                    log.n_p("Numa space is missing. Please check the environment and restart testing!")
                    exit()
                return bound_nucleus_command
        else:
            return ""

def mount_disk(disk_name):
    disk_name = disk_name.strip()
    if disk_name in log.popen("ls /mnt"):
        log.n_p("Folder Already!")
    else:
        log.n_p("CreateFolder!")
        log.run(f"mkdir /mnt/{disk_name}")
    try:
        print(log.popen(f"nohup mount /dev/{disk_name} /mnt/{disk_name}"), end='')
        log.n_p(f"Disk : {disk_name},mounting_Path : /mnt/{disk_name}")
        log.n_p(log.popen(f"df -TH | grep -i {disk_name}").strip())
    except Exception as e:
        log.n_p("Error mounting disk")


def umount_disk(disk_name):
    try:
        log.n_p(log.popen(f"nohup umount /mnt/{disk_name}"))
        log.n_p("Umount Success!")
    except Exception as e:
        log.n_p("Error umounting disk!")


def mount_main():
    log.n_p('|========[U/Mount]======|')
    log.n_p('|         1.mount       |')
    log.n_p('|         2.umount      |')
    log.n_p('|=======================|')
    chose_type = log.u_in(" U/Mount type [1/2]: ")
    if chose_type == "1":
        print("\n\n")
        log.n_p('|========[Mount]======|')
        log.n_p('|         all         |')
        log.n_p('|         sata        |')
        log.n_p('|         nvme        |')
        log.n_p('| Do not place in the |')
        log.n_p('| !!! /mnt folder !!! |')
        log.n_p('|=====================|')
        mount_type = log.u_in(" Mount Disk type : ")
        print("\n\n")
        if warning_tips():
            if mount_type == "nvme":
                disk_list = nvme_disk_info('')
                if log.u_in("Mount? [y/n]: ") == "y":
                    for i in range(0, len(disk_list), 3):mount_disk(disk_list[i])
                else:
                    log.n_p("You chose N!")

                print(log.popen("df -TH"))
            elif mount_type == "sata":
                disk_list = sata_disk_info('')
                if log.u_in("Mount? [y/n]: ") == "y":
                    for i in range(0, len(disk_list), 3):
                        mount_disk(disk_list[i])
                else:
                    log.n_p("You chose N!")
                print(log.popen("df -TH"))
            elif mount_type == "all":

                disk_list = nvme_disk_info('')
                if log.u_in("Mount? [y/n]: ") == "y":
                    for i in range(0, len(disk_list), 3):
                        mount_disk(disk_list[i])
                else:
                    log.n_p("You chose N!")

                disk_list = sata_disk_info('')
                if log.u_in("Mount? [y/n]: ") == "y":
                    for i in range(0, len(disk_list), 3):
                        mount_disk(disk_list[i])
                else:
                    log.n_p("You chose N!")
                print(log.popen("df -TH"))
            else:
                log.n_p("Chose Error!")
    elif chose_type == "2":
        print("\n\n")
        log.n_p('|========[Umount]======|')
        log.n_p('|         all         |')
        log.n_p('|         sata        |')
        log.n_p('|         nvme        |')
        log.n_p('| Do not place in the |')
        log.n_p('| !!! /mnt folder !!! |')
        log.n_p('|=====================|')
        mount_type = log.u_in(" Mount Disk type : ")
        print("\n\n")
        if warning_tips():
            if mount_type == "nvme":
                disk_list = nvme_disk_info('')
                if log.u_in("Umount? [y/n]: ") == "y":
                    for i in range(0, len(disk_list), 3):
                        umount_disk(disk_list[i])
                else:
                    log.n_p("You chose N!")
                print(log.popen("df -TH"))
            elif mount_type == "sata":
                disk_list = sata_disk_info('')
                if log.u_in("Umount? [y/n]: ") == "y":
                    for i in range(0, len(disk_list), 3):
                        umount_disk(disk_list[i])
                else:
                    log.n_p("You chose N!")
                print(log.popen("df -TH"))
            elif mount_type == "all":

                disk_list = nvme_disk_info('')
                if log.u_in("Umount? [y/n]: ") == "y":
                    for i in range(0, len(disk_list), 3):
                        umount_disk(disk_list[i])
                else:
                    log.n_p("You chose N!")
                print(log.popen("df -TH"))

                disk_list = sata_disk_info('')
                if log.u_in("Umount? [y/n]: ") == "y":
                    for i in range(0, len(disk_list), 3):
                        umount_disk(disk_list[i])
                else:
                    log.n_p("You chose N!")
                print(log.popen("df -TH"))
            else:
                log.n_p("Chose Error!")
    else:
        print("Mount chose Err!")

    # nvme硬盘格式化操作


def nvme_format(disk_name, type):
    log.d_p(type)
    print("[+]Check Tips:" + type)
    if type == "2":
        # log.n_p(f"[+] Nvme Format {disk_name} Status : " + log.popen(f"nvme format -s 1 /dev/{disk_name} ").strip())
        log.n_p(f"[+] Nvme Format {disk_name} Status : " + log.popen(f"nvme format /dev/{disk_name} -l 0 -s 1 -i 0 -p 0 -m 0").strip())
        wait(3)
    elif type == "1":
        result = log.popen(f"yes | mkfs.ext4 /dev/{disk_name}").strip()
        log.d_p(result)
        if "已完成" in result:
            log.n_p(f" NVMe Format {disk_name} Status : Success!")
        elif "done" in result:
            log.n_p(f" NVMe Format {disk_name} Status : Success!")
        else:
            log.n_p(f" NVMe Format {disk_name} Status : Format Fail!")
            if log.u_in("Format Fail! Do you want to continue? [y/n] ") == "y":
                log.n_p(f" {disk_name} Format Fail! View detailed information in cmd.log")
                log.n_p(f" Format Fail Disk is : {disk_name} , Command : yes | mkfs.ext4 /dev/{disk_name}")
                exit()
    else:
        log.error("Nvme format Error ! Please check /opt/natt/cmd.log")


# sata硬盘格式化操作
def sata_format(disk_name):
    result = log.popen(f"yes | mkfs.ext4 /dev/{disk_name}")
    log.d_p(result)
    if "已完成" in result.strip():
        log.n_p(f" HDD Format {disk_name} Status : Success!")
    elif "done" in result.strip():
        log.n_p(f" HDD Format {disk_name} Status : Success!")
    else:
        log.n_p(f" HDD Format {disk_name} Status : Format Fail!")
        if log.u_in("Format Fail! Do you want to continue? [y/n] ") == "y":
            log.n_p(f" {disk_name} Format Fail! View detailed information in cmd.log")
            log.error(f" Format Error Disk is : {disk_name} , Command : yes | mkfs.ext4 /dev/{disk_name}")


def return_disk_raid_node(raid_pcie_bus):
    return log.popen(f" lspci -vvvs {raid_pcie_bus} | grep -i 'node' | awk '{{print $3}}' ")

def return_disk_raid_numa(raid_pcie_bus):
    log.d_p(raid_pcie_bus)
    node = log.popen(f" lspci -vvvs {raid_pcie_bus} | grep -i 'node' | awk '{{print $3}}' ").strip()
    log.d_p(node)
    numa = log.popen(f" numactl -H | grep -i 'node {node} cpus' ").replace(f'node {node} cpus: ', '').split(' ')
    log.d_p(numa)
    numa = str(numa[0]).strip() + "-" + str(numa[-1]).strip()
    log.d_p(numa)
    return numa

def sata_collect_info(disk_name):
    result = []
    # 获取sata硬盘列表
    # sata_disk_inch  0
    sata_disk_inch = log.popen(f"smartctl -i /dev/{disk_name} | grep -i 'inches' ").replace("Form Factor:",
                                                                                            "").replace(
        "inches", "").strip()
    if sata_disk_inch == "":
        result.append("-.-")
    else:
        result.append(sata_disk_inch)
    # sata_disk_temp  1
    temp = log.popen((f"smartctl -a /dev/{disk_name} | grep -i Temperature_Celsius | grep Old_age | awk '{{print $10}}' ").strip().split("\n")[0])
    if temp == "":
        temp = log.popen(f"smartctl -a /dev/{disk_name} | grep -i 'Current Drive Temperature:' | awk '{{print $4}}' ").strip().split("\n")[0]
        if temp == "":
            temp = log.popen(f"smartctl -a /dev/{disk_name} | grep -i Temperature_Celsius | awk '{{print $10}}'").strip().split("\n")[0]
            if temp == "":
                temp = log.popen(f"smartctl -a /dev/{disk_name} | grep -i 'current drive temperature' | awk '{{print $4}}'")
        if temp == "":
            result.append("NA")
        else:
            result.append(temp.strip().split("\n")[0])
    else:
        result.append(temp.strip().split("\n")[0])
    # sata_disk_model 2
    model = log.popen(f"smartctl -i /dev/{disk_name} | grep -i 'device model' ").replace("Device Model:", "").strip()
    if model == "":
        model = log.popen(f"smartctl -i /dev/{disk_name} | grep -i 'Product:' | awk '{{print $2}}'").strip()
        if model == "":
            result.append("NA/NA/NA/NA")
        else:
            result.append(model)
    else:
        result.append(model)

    # sata_disk_seri  3
    sata_disk_seri = log.popen(
        f"smartctl -i /dev/{disk_name} | grep -i 'Serial Number' | awk '{{print $3}}'").strip()
    if sata_disk_seri == "":
        result.append("N/A")
    else:
        result.append(sata_disk_seri)
    # sata_disk_size  4
    sata_disk_size = log.popen(
        f"smartctl -i /dev/{disk_name} | grep -i 'User Capacity' | grep -oP '\[\K[^]]+'").strip()
    if sata_disk_size == "":
        result.append("N/A")
    else:
        result.append(sata_disk_size)
    # sata_disk_rpmm  5
    sata_disk_rpmm = log.popen(
        f"smartctl -i /dev/{disk_name} | grep -i 'Rotation Rate' | awk '{{print $3}}'").strip()
    if sata_disk_rpmm == "":
        result.append("N/A")
    else:
        result.append(sata_disk_rpmm)
    # sata_disk_fwve  6
    fwve = log.popen(f"smartctl -i /dev/{disk_name} | grep -i 'firmware version' | awk '{{print $3}}'").strip()
    if fwve == "":
        fwve = log.popen(f"smartctl -i /dev/{disk_name} | grep -i Revision | awk '{{print $2}}'").strip()
        if fwve == "":
            result.append("N/A")
        else:
            result.append(fwve)
    else:
        result.append(fwve)
    # sata disk type 7
    if result[5] == 'Solid':
        result.append("SSD")
    else:
        if 'SAS' in log.popen(" smartctl -i /dev/sda | grep -i 'Transport protocol:' | awk '{print $3}' "):
            result.append("SAS")
        else:
            result.append("SATA")
    # sata lnk type 8
    sata_speed = log.popen(f" smartctl -i /dev/{disk_name}| grep -i 'sata version is:' | awk '{{print $6,$7}}' ").strip()
    if sata_speed == "":
        result.append("N/A")
    else:
        result.append(sata_speed)
    # sata interface version  9
    if "6" in sata_speed:
        result.append("3.0")
    elif "3" in sata_speed:
        result.append("2.0")
    elif "1.5" in sata_speed:
        result.append("1.0")
    else:
        result.append("N/A")
    log.d_p(disk_name)
    log.d_p(result)
    return result

# 返回系统硬盘名称
def sysdisk_name():
    # 判断系统硬盘是否为nvme
    nvme_disk_name = log.popen("mount | grep nvme.* | grep -v cgr | sed 's/\/dev\///g' | sed '2,$d' | awk '{print $1}'").strip()
    log.d_p(nvme_disk_name)
    # 判断系统硬盘是否为sata
    sata_disk_name = log.popen("mount | grep sd.* | grep -v cgr | sed 's/\/dev\///g'| sed '2,$d' | awk '{print $1}' | cut -b 1-4").strip()
    for i in range(6):
        sata_disk_name = sata_disk_name.replace(str(i),"")
    log.d_p(sata_disk_name)
    # 判断return返回系统盘信息
    if len(nvme_disk_name) == 0:
        if "sd" in sata_disk_name:
            return sata_disk_name
        else:
            log.fail("[fail]Check system disk Error!")
    else:
        log.d_p(nvme_disk_name)
        return nvme_disk_name


# 获取nvme硬盘信息
def nvme_disk_info(disk_arr):
    print("\033[92m" + r'''
===========================================================
|   ________   ___      ___ _____ ______   _______        |
|  |\   ___  \|\  \    /  /|\   _ \  _   \|\  ___ \       |
|  \ \  \\ \  \ \  \  /  / | \  \\\__\ \  \ \   __/|      |
|   \ \  \\ \  \ \  \/  / / \ \  \\|__| \  \ \  \_|/_     |
|    \ \  \\ \  \ \    / /   \ \  \    \ \  \ \  \_|\ \   |
|     \ \__\\ \__\ \__/ /     \ \__\    \ \__\ \_______\  |
|      \|__| \|__|\|__|/       \|__|     \|__|\|_______|  |
===========================================================''' + "\033[0m")
    if disk_arr == '':
        print(
            "\n\033[94m[=======|=============|==========|====|======|=========|=======|========|==============|=======================================|=========================]\033[0m")
        print_save_text(file_path_name=f"/tmp/natt_nvme_info.log",
                        text="[Order]".ljust(10) + "[Disk_Name]".ljust(16) + "[Size]".ljust(8) + "[Ns]".ljust(
                            5) + "[Node]".ljust(
                            8) + "[CPUs]".ljust(18) + "[Temp]".ljust(7) + "[Health]".ljust(11) + "[Pcie_bus]".ljust(
                            25) + "[LnkSta]".ljust(39) + "[SN]".ljust(20)+"[Model]")

        nvme_list_array = log.popen("nvme list | grep -i /dev/nvme | awk '{{print $1}}'").replace("/dev/","").strip().split("\n")

        nvme_list = []

        if nvme_list_array[0]=="":
            log.n_p("Not Found Nvme Disk!")
            exit()

        disk_black_list = log.json_load("DiskInfo", "disk_black_list").strip().split(',')
        if disk_black_list != ['']:
            for disk_name in nvme_list_array:
                if disk_name not in disk_black_list:
                    nvme_list.append(disk_name)
        else:
            nvme_list = nvme_list_array
            log.d_p("Not Found Nvme Blacklist Disk!")

        if len(nvme_list) == 0:
            log.n_p("Not Found Nvme Disk!")
            exit()

    # 增加无硬盘退出不报错
    else:
        nvme_list = disk_arr
        if nvme_list[0] == "":
            log.n_p("Not Found Nvme Disk!")
            exit()

    nvme_test_arr = []
    disk_num = 0
    for nvme_name in nvme_list:
        if nvme_name not in log.popen("ls /syds/block"):
            log.n_p(f"{nvme_name} Not Found ! ")
            continue
        nvme_SN = log.popen(f"nvme list | grep -i {nvme_name} | awk '{{print $2}}'").strip()
        if "/dev/" in nvme_SN:
            nvme_SN = log.popen(f"nvme list | grep -i {nvme_name} | awk '{{print $3}}'").strip()
        nvme_Model = log.popen(f"smartctl -i /dev/{nvme_name} | grep -i 'Model Number'").split(":")[1].strip()
        if nvme_Model == '':
            nvme_Model = 'GetFail!'
        nvme_Namespace = log.popen(
            f"nvme id-ns /dev/{nvme_name} | grep -i namespace | awk '{{print $4}}'").strip().replace(":", "")
        nvme_Pciebus = log.popen(
            f"nvme list-subsys | grep -i {nvme_name.replace('n1', '')} | awk '{{print $4}}' ").strip().split()[0]
        nvme_Node = log.popen(f"lspci -vvvs {nvme_Pciebus} | grep -i node |awk '{{print $3}}'").strip()
        nvme_lnksta = log.popen(f"lspci -vvvs {nvme_Pciebus} | grep -i 'lnksta:'").strip().replace('LnkSta:',"")

        try:
            # add new nvme_cpus
            if 'rhel' in log.popen("cat /etc/os-release").lower():
                if int(log.popen("lscpu  | grep node | grep , | wc -l")) > 0:
                    nvme_cpus = log.popen(f"lscpu | grep -i 'node{nvme_Node.strip()} cpu' | cut -d ':' -f 2 ").strip()
                    nvme_cpus = str(nvme_cpus[0] + "-" + nvme_cpus[-1])
                else:
                    nvme_cpus = log.popen(f"numactl -H | grep -i 'node {nvme_Node} cpus' ").replace(f"node {nvme_Node} cpus:", "").strip().split()
                    nvme_cpus = str(nvme_cpus[0] + "-" + nvme_cpus[-1])
            else:
                nvme_cpus = log.popen(f"numactl -H | grep -i 'node {nvme_Node} cpus' ").replace(f"node {nvme_Node} cpus:", "").strip().split()
                nvme_cpus = str(nvme_cpus[0] + "-" + nvme_cpus[-1])

            try:
                log.d_p(nvme_cpus)
            except:
                nvme_cpus = log.popen(f"lscpu | grep -i '节点{nvme_Node.strip()} cpu' | cut -d '：' -f 2 ").strip()

            try:
                log.d_p(nvme_cpus)
            except:
                nvme_cpus = "Get-FAIL!"
        except:
            nvme_cpus = '0-16'

        nvme_Temp = log.popen(f" nvme smart-log /dev/{nvme_name} | grep temperature | awk '{{print $3}}' ").strip()
        nvme_health = log.popen(f"smartctl -H /dev/{nvme_name} | grep -i result | awk '{{print $6}}'").strip()
        nvme_Size = log.popen(f"smartctl -i /dev/{nvme_name} | grep -i 'Total NVM Capacity:' | awk 'match($0, /\[([^][]+)\]/, arr) {{print arr[1]}}' ").strip()
        if nvme_Size.strip()=="":
            nvme_Size = log.popen(f"smartctl -i /dev/{nvme_name}| grep -i 'Namespace 1 Size/Capacity:' | awk 'match($0, /\[([^][]+)\]/, arr) {{print arr[1]}}'").strip()
        if nvme_name not in sysdisk_name():
            log.d_p(nvme_name)
            log.d_p(nvme_Size)
            log.d_p(nvme_list)
            log.d_p(nvme_Temp)
            log.d_p(nvme_health)
            log.d_p(nvme_lnksta)
            log.d_p(nvme_Namespace)
            log.d_p(nvme_SN)
            log.d_p(nvme_cpus)
            log.d_p(nvme_Node)

            nvme_test_arr.append(nvme_name)
            nvme_test_arr.append(nvme_Node)
            nvme_test_arr.append(nvme_cpus)
            print_save_text(file_path_name=f"/tmp/natt_nvme_info.log",
                            text="".ljust(3) + str(disk_num).ljust(9) + nvme_name.ljust(14) + nvme_Size.ljust(
                                10) + nvme_Namespace.ljust(
                                6) + nvme_Node.ljust(6) + nvme_cpus.ljust(18) + nvme_Temp.ljust(6) + nvme_health.ljust(
                                9) + nvme_Pciebus.ljust(13) + nvme_lnksta.ljust(45) + nvme_SN.ljust(23) +nvme_Model.ljust(25))
        else:
            print_save_text(file_path_name=f"/tmp/natt_nvme_info.log",
                            text="\033[91m" + "".ljust(3) + str(disk_num).ljust(9) + nvme_name.ljust(
                                14) + nvme_Size.ljust(10) + nvme_Namespace.ljust(6) + nvme_Node.ljust(
                                6) + nvme_cpus.ljust(
                                18) + nvme_Temp.ljust(6) + nvme_health.ljust(9) + nvme_Pciebus.ljust(
                                13) + nvme_lnksta.ljust(45) + nvme_SN.ljust(23) +nvme_Model.ljust(25)+"\033[0m")
        disk_num += 1
    print(
        "\033[94m[=======|=============|==========|====|======|=========|=======|========|==============|=======================================|=========================]\033[0m")
    log.n_p("Nvme Disk Array Tips:Default removal of system disk")
    log.n_p("nvme test arr : " + str(nvme_test_arr))

    return nvme_test_arr

# 获取sata硬盘信息
def sata_disk_info(disk_arr):
    print("\033[92m" + r'''
    ===================================================
    |   ________  ________  _________  ________       |
    |  |\   ____\|\   __  \|\___   ___\\   __  \      |
    |  \ \  \___|\ \  \|\  \|___ \  \_\ \  \|\  \     |
    |   \ \_____  \ \   __  \   \ \  \ \ \   __  \    |
    |    \|____|\  \ \  \ \  \   \ \  \ \ \  \ \  \   |
    |      ____\_\  \ \__\ \__\   \ \__\ \ \__\ \__\  |
    |     |\_________\|__|\|__|    \|__|  \|__|\|__|  |
    |      \|_________|                               |
    ===================================================''' + "\033[0m")
    # Globalvalue
    sata_info = []
    sys_disk_name = sysdisk_name()
    if disk_arr == '':
        # 合并计算服务器硬盘列表
        contrast_result = []
        lsblk_array = os.popen("lsblk -o NAME,HCTL,VENDOR |  grep -vE 'nvme|├─|└─|NAME|HCTL|media|USB' | awk '{{print $1}}'").read().split()

        lsblk_arr = []

        if lsblk_array == ['']:
            log.n_p("Not Found Nvme Disk!")
            exit()

        disk_black_list = log.json_load("DiskInfo", "disk_black_list").strip().split(',')
        if disk_black_list != ['']:
            for disk_name in lsblk_array:
                if disk_name not in disk_black_list:
                    lsblk_arr.append(disk_name)
        else:
            lsblk_arr = lsblk_array

        log.d_p(lsblk_arr)
        for i in lsblk_arr:
            # if "media_change" in log.popen(f"cat /sys/block/{str(i).replace('/dev/', '')}/events"):
            #     continue
            # else:
            disk_name = str(i).replace('/dev/', '')
            log.d_p(disk_name)
            if disk_name in lsblk_arr:
                contrast_result.append(disk_name)
            else:
                continue
        log.d_p(contrast_result)
    else:
        contrast_result = disk_arr
        lsblk_info = log.popen("ls /sys/block")
        for disk_name in disk_arr:
            if disk_name not in lsblk_info:
                log.n_p(f"{disk_name} Not Found !")
        log.d_p(contrast_result)

    log.d_p(contrast_result)
    # Raid
    raid_num = int(os.popen("lspci | grep -i sas | grep -v USB | grep -vi huawei | wc -l ").read())
    log.d_p(raid_num)
    Board_disk = []

    if int(raid_num) == 0:
        log.n_p("<Dong> The server did not find the Raid card!")
        Board_disk = []
        for disk_name in contrast_result:
            log.n_p(f"disk_name : {disk_name}")
            log.d_p(f"sys_disk_name : {sys_disk_name}")
            if disk_name == sys_disk_name:continue
            Board_disk.append(disk_name)
            sata_info.append(disk_name)
            sata_info.append("Board_disk")
            sata_info.append("Board_disk")
        log.n_p("Board_disk : " + str(Board_disk))
        log.d_p(Board_disk)
        log.d_p(sata_info)

    elif int(raid_num) == 1:
        Raid1_arr = []
        Raid1_pcie_busid = os.popen("lspci | grep -i sas | grep -v USB | grep -vi huawei | grep -vi scsi| awk '{print $1}'").read().strip()
        for disk_name in contrast_result:
            disk_path = '/dev/'+disk_name
            tmp_result = os.popen(f" lsscsi -v 2>/dev/null | grep -A1 {disk_path} ").read().strip().replace("\n",
                                                                                                        '').replace(' ',
                                                                                                                    '')
            #print("disk_path : "+  disk_path + " BoardPCI : " + Raid1_pcie_busid + " " + disk_name + " -> " + tmp_result)
            if Raid1_pcie_busid in tmp_result:
                Raid1_arr.append(disk_name)
                if disk_name != sys_disk_name:
                    sata_info.append(disk_name.replace("\n",''))
                    sata_info.append(return_disk_raid_node(Raid1_pcie_busid).replace("\n",''))
                    sata_info.append(return_disk_raid_numa(Raid1_pcie_busid).replace("\n",''))
            else:
                if 'USB' not in os.popen(f'smartctl -i /dev/{disk_name}').read():
                    Board_disk.append(disk_name)
                    if disk_name != sys_disk_name:
                        sata_info.append(disk_name)
                        sata_info.append("Board_disk")
                        sata_info.append("Board_disk")
        print("Raid1_arr     :  " + str(Raid1_arr))
        print("Raid1_address => " + str(Raid1_pcie_busid))
        print("Board_disk    :  " + str(Board_disk))

    elif int(raid_num) == 2:
        Raid1_arr = []
        Raid2_arr = []
        raid_arr = os.popen("lspci | grep -i sas | awk '{print $1}'").read().split()
        log.d_p(raid_arr)
        for disk_name in contrast_result:
            disk_path = '/dev/' + disk_name
            tmp_result = os.popen(f" lsscsi -v 2>/dev/null | grep -A1 {disk_path} ").read().strip().replace("\n",
                                                                                                            '').replace(
                ' ',
                '')
            log.d_p(tmp_result)
            if tmp_result in raid_arr[0]:
                Raid1_arr.append(disk_name)
                if disk_name != sys_disk_name:
                    sata_info.append(disk_name)
                    sata_info.append(return_disk_raid_node(raid_arr[0]).replace("\n",''))
                    sata_info.append(return_disk_raid_numa(raid_arr[0]).replace("\n",''))
            elif tmp_result in raid_arr[1]:
                Raid2_arr.append(disk_name)
                if disk_name != sys_disk_name:
                    sata_info.append(disk_name)
                    sata_info.append(return_disk_raid_node(raid_arr[1]).replace("\n",''))
                    sata_info.append(return_disk_raid_numa(raid_arr[1]).replace("\n",''))
            else:
                if 'USB' not in os.popen(f'smartctl -i /dev/{disk_name}').read():
                    Board_disk.append(disk_name)
                    if disk_name != sys_disk_name:
                        sata_info.append(disk_name)
                        sata_info.append("Board_disk")
                        sata_info.append("Board_disk")
        print("Raid1_arr  :     " + str(Raid1_arr))
        print("Raid1_address => " + str(raid_arr[0]))
        print("Raid2_arr  :     " + str(Raid2_arr))
        print("Raid2_address => " + str(raid_arr[1]))
        print("Board_disk :     " + str(Board_disk))

    elif raid_num == 3:
        Raid1_arr = []
        Raid2_arr = []
        Raid3_arr = []
        raid_arr = os.popen("lspci | grep -i sas | awk '{print $1}'").read().split()
        log.d_p(raid_arr)
        for disk_name in contrast_result:
            disk_path = '/dev/' + disk_name
            tmp_result = os.popen(f" lsscsi -v 2>/dev/null | grep -A1 {disk_path} ").read().strip().replace("\n",
                                                                                                            '').replace(
                ' ',
                '')
            log.d_p(tmp_result)
            if tmp_result.find(raid_arr[0]) >= 0:
                Raid1_arr.append(disk_name)
                if disk_name != sys_disk_name:
                    sata_info.append(disk_name)
                    sata_info.append(return_disk_raid_node(raid_arr[0]).replace("\n",''))
                    sata_info.append(return_disk_raid_numa(raid_arr[0]).replace("\n",''))
            elif tmp_result.find(raid_arr[1]) >= 0:
                Raid2_arr.append(disk_name)
                if disk_name != sys_disk_name:
                    sata_info.append(disk_name)
                    sata_info.append(return_disk_raid_node(raid_arr[1]).replace("\n",''))
                    sata_info.append(return_disk_raid_numa(raid_arr[1]).replace("\n",''))
            elif tmp_result.find(raid_arr[2]) >= 0:
                Raid3_arr.append(disk_name)
                if disk_name != sys_disk_name:
                    sata_info.append(disk_name)
                    sata_info.append(return_disk_raid_node(raid_arr[2]).replace("\n",''))
                    sata_info.append(return_disk_raid_numa(raid_arr[2]).replace("\n",''))
            else:
                if 'USB' not in os.popen(f'smartctl -i /dev/{disk_name}').read():
                    Board_disk.append(disk_name)
                    if disk_name != sys_disk_name:
                        sata_info.append(disk_name)
                        sata_info.append("Board_disk")
                        sata_info.append("Board_disk")
        print("Board_disk :     " + str(Board_disk))
        print("Raid1_arr  :     " + str(Raid1_arr))
        print("Raid1_address => " + str(raid_arr[0]))
        print("Raid2_arr  :     " + str(Raid2_arr))
        print("Raid2_address => " + str(raid_arr[1]))
        print("Raid3_arr  :     " + str(Raid3_arr))
        print("Raid3_address => " + str(raid_arr[2]))

    elif raid_num == 4:
        Raid1_arr = []
        Raid2_arr = []
        Raid3_arr = []
        Raid4_arr = []
        raid_arr = os.popen("lspci | grep -i sas | awk '{print $1}'").read().split()
        log.d_p(raid_arr)
        for disk_name in contrast_result:
            disk_path = '/dev/' + disk_name
            tmp_result = os.popen(f" lsscsi -v 2>/dev/null | grep -A1 {disk_path} ").read().strip().replace("\n",
                                                                                                            '').replace(
                ' ',
                '')
            log.d_p(tmp_result)
            if tmp_result.find(raid_arr[0]) >= 0:
                Raid1_arr.append(disk_name)
                if disk_name != sys_disk_name:
                    sata_info.append(disk_name)
                    sata_info.append(return_disk_raid_node(raid_arr[0]))
                    sata_info.append(return_disk_raid_numa(raid_arr[0]))
            elif tmp_result.find(raid_arr[1]) >= 0:
                Raid2_arr.append(disk_name)
                if disk_name != sys_disk_name:
                    sata_info.append(disk_name)
                    sata_info.append(return_disk_raid_node(raid_arr[1]))
                    sata_info.append(return_disk_raid_numa(raid_arr[1]))
            elif tmp_result.find(raid_arr[2]) >= 0:
                Raid3_arr.append(disk_name)
                if disk_name != sys_disk_name:
                    sata_info.append(disk_name)
                    sata_info.append(return_disk_raid_node(raid_arr[2]))
                    sata_info.append(return_disk_raid_numa(raid_arr[2]))
            elif tmp_result.find(raid_arr[3]) >= 0:
                Raid4_arr.append(disk_name)
                if disk_name != sys_disk_name:
                    sata_info.append(disk_name)
                    sata_info.append(return_disk_raid_node(raid_arr[3]))
                    sata_info.append(return_disk_raid_numa(raid_arr[3]))
            else:
                if 'USB' not in os.popen(f'smartctl -i /dev/{disk_name}').read():
                    Board_disk.append(disk_name)
                    if disk_name != sys_disk_name:
                        sata_info.append(disk_name)
                        sata_info.append("Board_disk")
                        sata_info.append("Board_disk")
        print("Board_disk : " + str(Board_disk))
        print("Raid1_arr  :     " + str(Raid1_arr))
        print("Raid1_address => " + str(raid_arr[0]))
        print("Raid2_arr  :     " + str(Raid2_arr))
        print("Raid2_address => " + str(raid_arr[1]))
        print("Raid3_arr  :     " + str(Raid3_arr))
        print("Raid3_address => " + str(raid_arr[2]))
        print("Raid4_arr  :     " + str(Raid3_arr))
        print("Raid4_address => " + str(raid_arr[3]))
    elif raid_num == 5:
        Raid1_arr = []
        Raid2_arr = []
        Raid3_arr = []
        Raid4_arr = []
        Raid5_arr = []
        raid_arr = os.popen("lspci | grep -i sas | awk '{print $1}'").read().split()
        log.d_p(raid_arr)
        for disk_name in contrast_result:
            tmp_result = os.popen(f" lsscsi -v 2>/dev/null | grep -A1 '/dev/{disk_name} ' ").read().strip().replace("\n",
                                                                                                        '').replace(' ',
                                                                                                                    '')
            if tmp_result.find(raid_arr[0]) >= 0:
                Raid1_arr.append(disk_name)
                if disk_name != sys_disk_name:
                    sata_info.append(disk_name)
                    sata_info.append(return_disk_raid_node(raid_arr[0]))
                    sata_info.append(return_disk_raid_numa(raid_arr[0]))
            elif tmp_result.find(raid_arr[1]) >= 0:
                Raid2_arr.append(disk_name)
                if disk_name != sys_disk_name:
                    sata_info.append(disk_name)
                    sata_info.append(return_disk_raid_node(raid_arr[1]))
                    sata_info.append(return_disk_raid_numa(raid_arr[1]))
            elif tmp_result.find(raid_arr[2]) >= 0:
                Raid3_arr.append(disk_name)
                if disk_name != sys_disk_name:
                    sata_info.append(disk_name)
                    sata_info.append(return_disk_raid_node(raid_arr[2]))
                    sata_info.append(return_disk_raid_numa(raid_arr[2]))
            elif tmp_result.find(raid_arr[3]) >= 0:
                Raid4_arr.append(disk_name)
                if disk_name != sys_disk_name:
                    sata_info.append(disk_name)
                    sata_info.append(return_disk_raid_node(raid_arr[3]))
                    sata_info.append(return_disk_raid_numa(raid_arr[3]))
            elif tmp_result.find(raid_arr[4]) >= 0:
                Raid4_arr.append(disk_name)
                if disk_name != sys_disk_name:
                    sata_info.append(disk_name)
                    sata_info.append(return_disk_raid_node(raid_arr[4]))
                    sata_info.append(return_disk_raid_numa(raid_arr[4]))
            else:
                if 'USB' not in os.popen(f'smartctl -i /dev/{disk_name}').read():
                    Board_disk.append(disk_name)
                    if disk_name != sys_disk_name:
                        sata_info.append(disk_name)
                        sata_info.append("Board_disk")
                        sata_info.append("Board_disk")
        print("Board_disk : " + str(Board_disk))
        print("Raid1_arr  :     " + str(Raid1_arr))
        print("Raid1_address => " + str(raid_arr[0]))
        print("Raid2_arr  :     " + str(Raid2_arr))
        print("Raid2_address => " + str(raid_arr[1]))
        print("Raid3_arr  :     " + str(Raid3_arr))
        print("Raid3_address => " + str(raid_arr[2]))
        print("Raid4_arr  :     " + str(Raid3_arr))
        print("Raid4_address => " + str(raid_arr[3]))
        print("Raid5_arr  : " + str(Raid5_arr))
        print("Raid5_address => " + str(raid_arr[4]))
    data_arr = []
    disk_num = 0
    print(
        "\n\033[94m[======|===========|======|========|======|===============|==========|=======|===========|============|===================|==========================]\033[0m")
    print_save_text(file_path_name=f"/tmp/natt_sata_info.log",
                    text='[Order]'.ljust(8) + "[Disk_Name]".ljust(12) + "[Temp]".ljust(7) + "[Inches]".ljust(
                        9) + "[Size]".ljust(
                        7) + "[Rotation_Rate]".ljust(16) + "[DiskType]".ljust(11) + "[Speed]".ljust(
                        9) + "[SATA_Ver]".ljust(
                        11) + "[Fireware]".ljust(15) + "[SerialNum]".ljust(25) + "[Dev_Model]")
    for sata_disk in contrast_result:
        if sata_disk not in log.popen('ls /sys/block'):
            log.d_p(f"{sata_disk} Not Found !")
            continue
        if 'sd' not in sata_disk:
            continue
        if sys_disk_name != sata_disk:
            sata_collect_info_tmp = sata_collect_info(sata_disk)
            log.d_p(sata_disk)
            log.d_p(sata_collect_info_tmp)
            print_save_text(file_path_name="/tmp/natt_sata_info.log",
                            text="".ljust(3) + str(disk_num).ljust(8) + sata_disk.ljust(11) + sata_collect_info_tmp[
                                1].ljust(7) +
                                 sata_collect_info_tmp[0].ljust(7) + sata_collect_info_tmp[4].ljust(12) +
                                 sata_collect_info_tmp[5].ljust(13) + sata_collect_info_tmp[7].ljust(10) +
                                 sata_collect_info_tmp[8].ljust(11) + sata_collect_info_tmp[9].ljust(11) +
                                 sata_collect_info_tmp[6].ljust(14) + sata_collect_info_tmp[3].ljust(22) +
                                 sata_collect_info_tmp[2].ljust(5))
            data_arr.append(sata_disk)
            disk_num += 1
        else:
            sata_collect_info_tmp = sata_collect_info(sata_disk)
            log.d_p(sata_disk)
            log.d_p(sata_collect_info_tmp)
            print_save_text(file_path_name="/tmp/natt_sata_info.log",
                            text="\033[91m" + "".ljust(3) + str(disk_num).ljust(8) + sata_disk.ljust(11) +
                                 sata_collect_info_tmp[1].ljust(7) + sata_collect_info_tmp[0].ljust(7) +
                                 sata_collect_info_tmp[4].ljust(12) + sata_collect_info_tmp[5].ljust(13) +
                                 sata_collect_info_tmp[7].ljust(10) +
                                 sata_collect_info_tmp[8].ljust(11) + sata_collect_info_tmp[9].ljust(11) +
                                 sata_collect_info_tmp[6].ljust(14) + sata_collect_info_tmp[3].ljust(22) +
                                 sata_collect_info_tmp[2].ljust(5) + "\033[0m")
            disk_num += 1
    print("\033[94m[======|===========|======|========|======|===============|==========|=======|===========|============|===================|==========================]\033[0m")
    log.d_p(sata_info)
    return sata_info

# 随机预写
def random_prewriting(disk_name, numa, node, bs, numjobs, iodepth, runtime, debug):
    # 判断传参
    if numjobs == "": numjobs = 8
    if iodepth == "": iodepth = 32
    if runtime == "": runtime = 7200
    if bs == "": bs = "4k"
    log.d_p(disk_name)
    log.d_p(numjobs)
    log.d_p(iodepth)
    log.d_p(runtime)
    log.d_p(bs)
    # 输出运行
    debug_run_print(debug,command=f"nohup {Bound_nucleus(disk_name, node, numa)} fio -filename=/dev/{disk_name} -ioengine=libaio -direct=1 -thread -rw=randwrite -bs={bs} -numjobs={numjobs} -iodepth={iodepth} -runtime={runtime} -time_based -norandommap -name=mytest & ")


# 随机预写执行函数
def random_prewriting_start(disk_info):
    # 随机预写
    numjobs = log.json_load('Testmode', 'random_write_prewriting_numjobs')
    iodepth = log.json_load('Testmode', 'random_write_prewriting_iodepth')
    runtime = log.json_load('Testmode', 'random_write_prewriting_runtime')
    bs = log.json_load('Testmode', 'random_write_prewriting_bs')

    clear_p()
    if "nvme" in disk_info[0]:
        print_tips("Nvme_random_prewriting!")
    elif "sd" in disk_info[0]:
        print_tips("Sata_random_prewriting!")
    for num in range(0, 2):
        a = 0
        for i in range(int(len(disk_info) / 3)):
            if str(num) == "1":
                wait_disk_run()
            disk = disk_info[a:a + 3]
            random_prewriting(disk_name=disk[0], numa=disk[1], node=disk[2], bs=bs, numjobs=numjobs, iodepth=iodepth,runtime=runtime, debug=str(num))
            a += 3
        if str(num) == "0":
            wait_disk_print()
    fio_iostat_monitor("","","",runtime)
    

# 顺序预写
def sequen_prewriting(disk_name, numa, node, bs, numjobs, iodepth, loops, runtime, debug, flags):
    seq_sata_bs = str(log.json_load("DiskInfo", "seq_sata_bs")).strip()
    seq_ssd_bs = str(log.json_load("DiskInfo", "seq_ssd_bs")).strip()
    if 'sd' in disk_name:
        if seq_sata_bs == "" and seq_ssd_bs == "":
            if log.popen(
                    f"smartctl -i /dev/{disk_name} | grep -i 'Rotation Rate' | awk '{{print $3}}'").strip() == "Solid":
                bs = "128k"
            else:
                bs = "512k"
        elif str(log.json_load("DiskInfo", "seq_sata_bs")).strip() != "" and str(
                log.json_load("DiskInfo", "seq_ssd_bs")).strip() == "":
            if log.popen(
                    f"smartctl -i /dev/{disk_name} | grep -i 'Rotation Rate' | awk '{{print $3}}'").strip() == "Solid":
                bs = "128k"
            else:
                bs = str(log.json_load("DiskInfo", "seq_sata_bs")).strip()
        elif str(log.json_load("DiskInfo", "seq_sata_bs")).strip() == "" and str(
                log.json_load("DiskInfo", "seq_ssd_bs")).strip() != "":
            if log.popen(
                    f"smartctl -i /dev/{disk_name} | grep -i 'Rotation Rate' | awk '{{print $3}}'").strip() == "Solid":
                bs = str(log.json_load("DiskInfo", "seq_ssd_bs")).strip()
            else:
                bs = "512k"
        elif str(log.json_load("DiskInfo", "seq_sata_bs")).strip() != "" and str(
                log.json_load("DiskInfo", "seq_ssd_bs")).strip() != "":
            if log.popen(
                    f"smartctl -i /dev/{disk_name} | grep -i 'Rotation Rate' | awk '{{print $3}}'").strip() == "Solid":
                bs = str(log.json_load("DiskInfo", "seq_ssd_bs")).strip()
            else:
                bs = str(log.json_load("DiskInfo", "seq_sata_bs")).strip()
    else:
        bs = "128k"
    # 判断传参
    if numjobs == "": numjobs = 1
    if iodepth == "": iodepth = 32
    if loops == "": loops = 3
    if runtime == "": runtime = 7200
    log.d_p(disk_name)
    log.d_p(numjobs)
    log.d_p(iodepth)
    log.d_p(loops)
    log.d_p(runtime)
    log.d_p(bs)
    # 输出运行
    if flags == 'loops':
        debug_run_print(debug,
                        command=f"nohup {Bound_nucleus(disk_name, node, numa)} fio -filename=/dev/{disk_name}  -ioengine=libaio -direct=1 -thread -rw=write -bs={bs} -iodepth={iodepth} -numjobs={numjobs} -loops={loops} -norandommap -name=mytest &")
    elif flags == 'runtime':
        debug_run_print(debug,
                        command=f"nohup {Bound_nucleus(disk_name, node, numa)} fio -filename=/dev/{disk_name}  -ioengine=libaio -direct=1 -thread -rw=write -bs={bs} -iodepth={iodepth} -numjobs={numjobs} -runtime={runtime} -norandommap -name=mytest --time_based &")
    else:
        log.error('sequen_prewriting flags Error!')


# 顺序预写执行函数
def sequen_prewriting_start(disk_info, flags):
    numjobs = log.json_load('Testmode', 'sequen_write_prewriting_numjobs')
    iodepth = log.json_load('Testmode', 'sequen_write_prewriting_iodepth')
    loops = log.json_load('Testmode', 'sequen_write_prewriting_loops')
    bs = log.json_load('Testmode', 'sequen_write_prewriting_bs')
    runtime = log.json_load('Testmode', 'sequen_write_prewriting_runtime')

    clear_p()
    if "nvme" in disk_info[0]:
        print_tips("Nvme_sequence_prewriting!")
    elif "sd" in disk_info[0]:
        print_tips("Sata_sequenc_prewriting!")
    for num in range(0, 2):
        a = 0
        for i in range(int(len(disk_info) / 3)):
            if str(num) == "1":
                wait_disk_run()
            disk = disk_info[a:a + 3]
            sequen_prewriting(disk[0], disk[1], disk[2], bs=bs, numjobs=numjobs, iodepth=iodepth, loops=loops,
                              runtime=runtime, debug=str(num), flags=flags)
            a += 3
        if str(num) == "0":
            wait_disk_print()
    fio_iostat_monitor("","","",runtime)


# 随机读
def random_read(disk_name, numa, node, bs, numjobs, iodepth, runtime, debug, log_name):
    if log.json_load('DiskInfo', 'ramp_time') == '':
        ramp_time = 30
    else:
        ramp_time = log.json_load('DiskInfo', 'ramp_time')
    log.d_p(disk_name)
    log.d_p(numjobs)
    log.d_p(iodepth)
    log.d_p(runtime)
    log.d_p(bs)
    title = log.json_load("Testmode","description")
    debug_run_print(debug,command=f"nohup {Bound_nucleus(disk_name, node, numa)} fio --filename=/dev/{disk_name} --description='{title}_randread' --randrepeat=0 --norandommap --thread --direct=1 --name=myjob --bs={bs} --ioengine=libaio --runtime={runtime} --time_based  -rw=randread --iodepth={iodepth} --ramp_time={ramp_time} --numjobs={numjobs} --group_reporting --output={log_name}/random_read_{bs}_all-{disk_name}.log &")

# 随机读执行函数
def random_read_start(disk_info, log_name, end_flags):
    numjobs = log.json_load('Testmode', 'random_read_numjobs')
    iodepth = log.json_load('Testmode', 'random_read_iodepth')
    runtime = log.json_load('Testmode', 'random_read_runtime')
    bs = log.json_load('Testmode', 'random_read_bs')

    if numjobs == "": numjobs = 8
    if iodepth == "": iodepth = 32
    if runtime == "": runtime = 3600
    if bs == "": bs = "4k"

    clear_p()
    test_type = ''
    if "nvme" in disk_info[0]:
        print_tips("NVME_random_read_start!")
        test_type = f'nvme-random-read-{bs}'
    elif "sd" in disk_info[0]:
        print_tips("SATA_random_read_start!")
        test_type = f'sata-random-read-{bs}'
    for num in range(0, 2):
        a = 0
        for i in range(int(len(disk_info) / 3)):
            if str(num) == "1":
                wait_disk_run()
            disk = disk_info[a:a + 3]
            random_read(disk[0], disk[1], disk[2], bs=bs, numjobs=numjobs, iodepth=iodepth, runtime=runtime,
                        debug=str(num), log_name=log_name)
            a += 3
        if str(num) == "0":
            wait_disk_print()

    monitor_start(runtime=runtime, file_name=f'iostat-{test_type.strip()}-{bs}.log', disk_name=disk_info[0],log_name=log_name)
    if runtime == "":
        runtime = 3600
    if log.json_load("Monitor","blktrace") == "1":
        blktrace_start(disk_info,log_name,"random_read",runtime)
    fio_iostat_monitor(log_name,"random_read","1",runtime)
    # 判断是否最后一个执行
    if end_flags:
        fio_file_result(log_name, disk_info)
# 随机写
def random_write(disk_name, numa, node, bs, numjobs, iodepth, runtime, debug, log_name):
    if log.json_load('DiskInfo', 'ramp_time') == '':
        ramp_time = 30
    else:
        ramp_time = log.json_load('DiskInfo', 'ramp_time')
    log.d_p(disk_name)
    log.d_p(numjobs)
    log.d_p(iodepth)
    log.d_p(runtime)
    log.d_p(bs)
    title = log.json_load("Testmode", "description")
    debug_run_print(debug,command=f"nohup {Bound_nucleus(disk_name, node, numa)} fio --filename=/dev/{disk_name} --description='{title}_randwrite' --randrepeat=0 --norandommap --thread --direct=1 --name=myjob --bs={bs} --ioengine=libaio --runtime={runtime} --time_based --rw=randwrite --iodepth={iodepth} --ramp_time={ramp_time} --numjobs={numjobs} --group_reporting --output={log_name}/random_write_{bs}_all-{disk_name}.log &")


# 随机写执行函数
def random_write_start(disk_info, log_name, end_flags):
    numjobs = log.json_load('Testmode', 'random_write_numjobs')
    iodepth = log.json_load('Testmode', 'random_write_iodepth')
    runtime = log.json_load('Testmode', 'random_write_runtime')
    bs = log.json_load('Testmode', 'random_write_bs')

    # 判断传参
    if numjobs == "": numjobs = 8
    if iodepth == "": iodepth = 32
    if runtime == "": runtime = 3600
    if bs == "": bs = "4k"
    clear_p()
    test_type = ''
    if "nvme" in disk_info[0]:
        print_tips("NVME_random_write_start!")
        test_type = f'nvme-random-write-{bs}'
    elif "sd" in disk_info[0]:
        print_tips("SATA_random_write_start!")
        test_type = f'sata-random-write-{bs}'
    for num in range(0, 2):
        a = 0
        for i in range(int(len(disk_info) / 3)):
            if str(num) == "1":
                wait_disk_run()
            disk = disk_info[a:a + 3]
            random_write(disk[0], disk[1], disk[2], bs=bs, numjobs=numjobs, iodepth=iodepth, runtime=runtime,
                         debug=str(num), log_name=log_name)
            a += 3
        if str(num) == "0":
            wait_disk_print()

    if runtime == "": runtime = 3600
    monitor_start(runtime=runtime, file_name=f'iostat-{test_type.strip()}-{bs}.log', disk_name=disk_info[0],
                 log_name=log_name)
    if runtime == "":
        runtime = 3600
    if log.json_load("Monitor","blktrace") == "1":
        blktrace_start(disk_info,log_name,"random_write",runtime)

    fio_iostat_monitor(log_name,"random_write","1",runtime)
    # 判断是否最后一个执行
    if end_flags:
        fio_file_result(log_name, disk_info)


# 顺序读
def sequence_read(disk_name, numa, node, bs, numjobs, iodepth, runtime, debug, log_name):
    seq_sata_bs = str(log.json_load("DiskInfo", "seq_sata_bs")).strip()
    seq_ssd_bs = str(log.json_load("DiskInfo", "seq_ssd_bs")).strip()
    if 'sd' in disk_name:
        if seq_sata_bs == "" and seq_ssd_bs == "":
            if log.popen(
                    f"smartctl -i /dev/{disk_name} | grep -i 'Rotation Rate' | awk '{{print $3}}'").strip() == "Solid":
                bs = "128k"
            else:
                bs = "512k"
        elif str(log.json_load("DiskInfo", "seq_sata_bs")).strip() != "" and str(
                log.json_load("DiskInfo", "seq_ssd_bs")).strip() == "":
            if log.popen(
                    f"smartctl -i /dev/{disk_name} | grep -i 'Rotation Rate' | awk '{{print $3}}'").strip() == "Solid":
                bs = "128k"
            else:
                bs = str(log.json_load("DiskInfo", "seq_sata_bs")).strip()
        elif str(log.json_load("DiskInfo", "seq_sata_bs")).strip() == "" and str(
                log.json_load("DiskInfo", "seq_ssd_bs")).strip() != "":
            if log.popen(
                    f"smartctl -i /dev/{disk_name} | grep -i 'Rotation Rate' | awk '{{print $3}}'").strip() == "Solid":
                bs = str(log.json_load("DiskInfo", "seq_ssd_bs")).strip()
            else:
                bs = "512k"
        elif str(log.json_load("DiskInfo", "seq_sata_bs")).strip() != "" and str(
                log.json_load("DiskInfo", "seq_ssd_bs")).strip() != "":
            if log.popen(
                    f"smartctl -i /dev/{disk_name} | grep -i 'Rotation Rate' | awk '{{print $3}}'").strip() == "Solid":
                bs = str(log.json_load("DiskInfo", "seq_ssd_bs")).strip()
            else:
                bs = str(log.json_load("DiskInfo", "seq_sata_bs")).strip()
    if log.json_load('DiskInfo', 'ramp_time') == '':
        ramp_time = 30
    else:
        ramp_time = log.json_load('DiskInfo', 'ramp_time')
    log.d_p(disk_name)
    log.d_p(numjobs)
    log.d_p(iodepth)
    log.d_p(runtime)
    log.d_p(bs)
    title = log.json_load("Testmode", "description")
    debug_run_print(debug,command=f"nohup {Bound_nucleus(disk_name, node, numa)} fio --filename=/dev/{disk_name} --description='{title}_seqread' --randrepeat=0 --thread --direct=1 --name=myjob --bs={bs} --ioengine=libaio --runtime={runtime} --time_based  --rw=read --iodepth={iodepth} --ramp_time={ramp_time} --numjobs={numjobs} --group_reporting --output={log_name}/sequence_read_{bs}_{disk_name}.log &")
    return bs


# 顺序读执行函数
def sequence_read_start(disk_info, log_name, end_flags):
    numjobs = log.json_load('Testmode', 'sequen_read_numjobs')
    iodepth = log.json_load('Testmode', 'sequen_read_iodepth')
    runtime = log.json_load('Testmode', 'sequen_read_runtime')
    bs = log.json_load('Testmode', 'sequen_read_bs')

    # 判断传参
    if numjobs == "": numjobs = 1
    if iodepth == "": iodepth = 32
    if runtime == "": runtime = 3600
    if bs == "": bs = "128k"
    clear_p()
    test_type = ''
    if "nvme" in disk_info[0]:
        print_tips("NVME_sequence_read!")
        test_type = f'nvme-sequence-read'
    elif "sd" in disk_info[0]:
        print_tips("SATA_sequence_read!")
        test_type = f'sata-sequence-read'
    for num in range(0, 2):
        a = 0
        for i in range(int(len(disk_info) / 3)):
            if str(num) == "1":
                wait_disk_run()
            disk = disk_info[a:a + 3]
            bs = sequence_read(disk[0], disk[1], disk[2], bs=bs, numjobs=numjobs, iodepth=iodepth, runtime=runtime,debug=str(num), log_name=log_name)
            a += 3
        if str(num) == "0":
            wait_disk_print()

    monitor_start(runtime=runtime, file_name=f'iostat-{test_type.strip()}-{bs}.log', disk_name=disk_info[0],
                 log_name=log_name)
    if log.json_load("Monitor","blktrace") == "1":
        blktrace_start(disk_info,log_name,"sequence_read",runtime)
    fio_iostat_monitor(log_name,"sequence_read","1",runtime)
    # 判断是否最后一个执行
    if end_flags:
        fio_file_result(log_name, disk_info)


# 顺序写
def sequence_write(disk_name, numa, node, bs, numjobs, iodepth, runtime, debug, log_name):
    seq_sata_bs = str(log.json_load("DiskInfo", "seq_sata_bs")).strip()
    seq_ssd_bs = str(log.json_load("DiskInfo", "seq_ssd_bs")).strip()
    if 'sd' in disk_name:
        if seq_sata_bs == "" and seq_ssd_bs == "":
            if log.popen(
                    f"smartctl -i /dev/{disk_name} | grep -i 'Rotation Rate' | awk '{{print $3}}'").strip() == "Solid":
                bs = "128k"
            else:
                bs = "512k"
        elif str(log.json_load("DiskInfo", "seq_sata_bs")).strip() != "" and str(
                log.json_load("DiskInfo", "seq_ssd_bs")).strip() == "":
            if log.popen(
                    f"smartctl -i /dev/{disk_name} | grep -i 'Rotation Rate' | awk '{{print $3}}'").strip() == "Solid":
                bs = "128k"
            else:
                bs = str(log.json_load("DiskInfo", "seq_sata_bs")).strip()
        elif str(log.json_load("DiskInfo", "seq_sata_bs")).strip() == "" and str(
                log.json_load("DiskInfo", "seq_ssd_bs")).strip() != "":
            if log.popen(
                    f"smartctl -i /dev/{disk_name} | grep -i 'Rotation Rate' | awk '{{print $3}}'").strip() == "Solid":
                bs = str(log.json_load("DiskInfo", "seq_ssd_bs")).strip()
            else:
                bs = "512k"
        elif str(log.json_load("DiskInfo", "seq_sata_bs")).strip() != "" and str(
                log.json_load("DiskInfo", "seq_ssd_bs")).strip() != "":
            if log.popen(
                    f"smartctl -i /dev/{disk_name} | grep -i 'Rotation Rate' | awk '{{print $3}}'").strip() == "Solid":
                bs = str(log.json_load("DiskInfo", "seq_ssd_bs")).strip()
            else:
                bs = str(log.json_load("DiskInfo", "seq_sata_bs")).strip()

    if log.json_load('DiskInfo', 'ramp_time') == '':
        ramp_time = 30
    else:
        ramp_time = log.json_load('DiskInfo', 'ramp_time')
    log.d_p(disk_name)
    log.d_p(numjobs)
    log.d_p(iodepth)
    log.d_p(runtime)
    log.d_p(bs)
    title = log.json_load("Testmode", "description")
    debug_run_print(debug,command=f"nohup {Bound_nucleus(disk_name, node, numa)} fio --filename=/dev/{disk_name} --description='{title}_seqwrite' --randrepeat=0 --thread --direct=1 --name=myjob --bs={bs} --ioengine=libaio --runtime={runtime} --time_based  --rw=write --iodepth={iodepth} --ramp_time={ramp_time} --numjobs={numjobs} --group_reporting --output={log_name}/sequence_write_{bs}_{disk_name}.log &")
    return bs

# 顺序写执行函数
def sequence_write_start(disk_info, log_name, end_flags):
    numjobs = log.json_load('Testmode', 'sequen_write_numjobs')
    iodepth = log.json_load('Testmode', 'sequen_write_iodepth')
    runtime = log.json_load('Testmode', 'sequen_write_runtime')
    bs = log.json_load('Testmode', 'sequen_write_bs')

    # 判断传参
    if numjobs == "": numjobs = 1
    if iodepth == "": iodepth = 32
    if runtime == "": runtime = 3600
    if bs == "": bs = "128k"
    clear_p()
    test_type = ''
    if "nvme" in disk_info[0]:
        print_tips("NVME_sequence_write")
        test_type = f'nvme-sequence-write'
    elif "sd" in disk_info[0]:
        print_tips("SATA_sequence_write")
        test_type = f'sata-sequence-write'
    for num in range(0, 2):
        a = 0
        for i in range(int(len(disk_info) / 3)):
            if str(num) == "1":
                wait_disk_run()
            disk = disk_info[a:a + 3]
            bs = sequence_write(disk[0], disk[1], disk[2], bs=bs, numjobs=numjobs, iodepth=iodepth, runtime=runtime,
                                debug=str(num), log_name=log_name)
            a += 3
        if str(num) == "0":
            wait_disk_print()

    monitor_start(runtime=runtime, file_name=f'iostat-{test_type.strip()}-{bs}.log', disk_name=disk_info[0],
                 log_name=log_name)
    if log.json_load("Monitor","blktrace") == "1":
        blktrace_start(disk_info,log_name,"sequence_write",runtime)
    fio_iostat_monitor(log_name,"sequence_write","1",runtime)
    # 判断是否最后一个执行
    if end_flags:
        fio_file_result(log_name, disk_info)


def ran_rx(disk_name, numa, node, numjobs, bs, iodepth, runtime, debug, log_name, rwmixread_percentage):
    if log.json_load('DiskInfo', 'ramp_time') == '':
        ramp_time = 30
    else:
        ramp_time = log.json_load('DiskInfo', 'ramp_time')
    log.d_p(disk_name)
    log.d_p(numjobs)
    log.d_p(iodepth)
    log.d_p(runtime)
    log.d_p(bs)
    log.d_p(rwmixread_percentage)
    title = log.json_load("Testmode", "description")
    debug_run_print(debug,command=f"nohup {Bound_nucleus(disk_name, node, numa)} fio --filename=/dev/{disk_name} --description='{title}_random_rw' --thread --direct=1 --name=myjob --rw=randrw --bs={bs} -rwmixread={rwmixread_percentage} --ioengine=libaio --runtime={runtime} --time_based --iodepth={iodepth} --numjobs={numjobs} --ramp_time={ramp_time} --group_reporting --output={log_name}/random_randrw_all-{disk_name}.log &")


def ran_rx_start(disk_info, log_name, end_flags):
    numjobs = log.json_load('Testmode', 'random_rx_numjobs')
    iodepth = log.json_load('Testmode', 'random_rx_iodepth')
    runtime = log.json_load('Testmode', 'random_rx_runtime')
    bs = log.json_load('Testmode', 'random_rx_bs')
    rwmixread_percentage = log.json_load('Testmode', 'random_rx_rwmixread_percentage')

    # 判断传参
    if numjobs == "": numjobs = 8
    if iodepth == "": iodepth = 32
    if runtime == "": runtime = 3600
    if bs == "": bs = "4k"
    if rwmixread_percentage == "": rwmixread_percentage = 70

    clear_p()
    test_type = ''
    if "nvme" in disk_info[0]:
        print_tips("NVME_random_rw")
        test_type = f'nvme-random-rw-{bs}'
    elif "sd" in disk_info[0]:
        print_tips("SATA_Sequence_rw")
        test_type = f'sata-random-rw-{bs}'

    for num in range(0, 2):
        a = 0
        for i in range(int(len(disk_info) / 3)):
            if str(num) == "1":
                wait_disk_run()
            disk = disk_info[a:a + 3]
            ran_rx(disk[0], disk[1], disk[2], numjobs=numjobs, bs=bs, iodepth=iodepth, runtime=runtime, debug=str(num),
                   log_name=log_name, rwmixread_percentage=rwmixread_percentage)
            a += 3
        if str(num) == "0":
            wait_disk_print()

    if runtime == "": runtime = 3600
    monitor_start(runtime=runtime, file_name=f'iostat-{test_type.strip()}-{bs}.log', disk_name=disk_info[0],
                 log_name=log_name)
    fio_iostat_monitor(log_name,"ran_rx","1",runtime)
    # 判断是否最后一个执行
    if end_flags:
        fio_file_result(log_name, disk_info)

def seq_rx(disk_name, numa, node, numjobs, bs, iodepth, runtime, debug, log_name, rwmixread_percentage):
    if log.json_load('DiskInfo', 'ramp_time') == '':
        ramp_time = 30
    else:
        ramp_time = log.json_load('DiskInfo', 'ramp_time')
    log.d_p(disk_name)
    log.d_p(numjobs)
    log.d_p(iodepth)
    log.d_p(runtime)
    log.d_p(bs)
    log.d_p(rwmixread_percentage)
    title = log.json_load("Testmode", "description")
    debug_run_print(debug,command=f"nohup {Bound_nucleus(disk_name, node, numa)} fio --filename=/dev/{disk_name} --description='{title}_seq_rw' --thread --direct=1 --name=myjob --rw=rw --bs={bs} -rwmixread={rwmixread_percentage} --ioengine=libaio --runtime={runtime} --time_based --iodepth={iodepth} --numjobs={numjobs} --ramp_time={ramp_time} --group_reporting --output={log_name}/sequence_rw_all-{disk_name}.log &")


def seq_rx_start(disk_info, log_name, end_flags):
    numjobs = log.json_load('Testmode', 'seq_rx_numjobs')
    iodepth = log.json_load('Testmode', 'seq_rx_iodepth')
    runtime = log.json_load('Testmode', 'seq_rx_runtime')
    bs = log.json_load('Testmode', 'seq_rx_bs')
    rwmixread_percentage = log.json_load('Testmode', 'seq_rx_rwmixread_percentage')

    # 判断传参
    if numjobs == "": numjobs = 8
    if iodepth == "": iodepth = 32
    if runtime == "": runtime = 3600
    if bs == "": bs = "128k"
    if rwmixread_percentage == "": rwmixread_percentage = 70
    clear_p()
    test_type = ''
    if "nvme" in disk_info[0]:
        print_tips("NVME_Sequence_rw")
        test_type = f'sata-sequence-rw-{bs}'
    elif "sd" in disk_info[0]:
        print_tips("SATA_Sequence_rw")
        test_type = f'sata-sequence-rw-{bs}'
    for num in range(0, 2):
        a = 0
        for i in range(int(len(disk_info) / 3)):
            if str(num) == "1":
                wait_disk_run()
            disk = disk_info[a:a + 3]
            seq_rx(disk[0], disk[1], disk[2], numjobs=numjobs, bs=bs, iodepth=iodepth, runtime=runtime, debug=str(num),
                   log_name=log_name, rwmixread_percentage=rwmixread_percentage)
            a += 3
        if str(num) == "0":
            wait_disk_print()

    if runtime == "": runtime = 3600
    monitor_start(runtime=runtime, file_name=f'iostat-{test_type.strip()}-{bs}.log', disk_name=disk_info[0],
                 log_name=log_name)

    fio_iostat_monitor(log_name,"seq_rx","1",runtime)
    # 判断是否最后一个执行
    if end_flags:
        fio_file_result(log_name, disk_info)

def start_test(test_type, disk_info, log_name):
    log.run(f"cp /opt/natt/config/natt_config.json {log_name}/debug/")
    soft_info(log_name)
    if log.json_load("Monitor","scheduler")=="1":scheduler_info(disk_info,log_name)
    if test_type == "1":
        sequence_read_start(disk_info=disk_info, log_name=log_name, end_flags=True)
        result_handle(log_name=log_name)
    elif test_type == "2":
        sequence_write_start(disk_info=disk_info, log_name=log_name, end_flags=True)
        result_handle(log_name=log_name)
    elif test_type == "3":
        log.n_p("请选择你想要进行的顺序预写方式 : 0.按照loops圈数进行预写 1.按照runtime时间进行预写")
        tmp = log.u_in('What kind of pre writing do you want to do? 0.loops   1.runtime [0/1]? : ')
        if tmp == "0":
            flags = 'loops'
        elif tmp == "1":
            flags = 'runtime'
        else:
            flags = 'loops'
        sequen_prewriting_start(disk_info=disk_info, flags=flags)
    elif test_type == "4":
        sequence_write_start(disk_info=disk_info, log_name=log_name, end_flags=False)
        sequence_read_start(disk_info=disk_info, log_name=log_name, end_flags=True)
        result_handle(log_name=log_name)
    elif test_type == "5":
        log.n_p("请选择你想要进行的顺序预写方式 : 0.按照loops圈数进行预写 1.按照runtime时间进行预写")
        tmp = log.u_in('What kind of pre writing do you want to do? 0.loops   1.runtime [0/1]? : ')
        if tmp == "0":
            flags = 'loops'
        elif tmp == "1":
            flags = 'runtime'
        else:
            flags = 'loops'
        sequen_prewriting_start(disk_info=disk_info, flags=flags)
        sequence_read_start(disk_info=disk_info, log_name=log_name, end_flags=True)
        result_handle(log_name=log_name)
    elif test_type == "6":
        log.n_p("请选择你想要进行的顺序预写方式 : 0.按照loops圈数进行预写 1.按照runtime时间进行预写")
        tmp = log.u_in('What kind of pre writing do you want to do? 0.loops   1.runtime [0/1]? : ')
        if tmp == "0":
            flags = 'loops'
        elif tmp == "1":
            flags = 'runtime'
        else:
            flags = 'loops'
        sequen_prewriting_start(disk_info=disk_info, flags=flags)
        sequence_write_start(disk_info=disk_info, log_name=log_name, end_flags=True)
        result_handle(log_name=log_name)
    elif test_type == "7":
        seq_rx_start(disk_info=disk_info, log_name=log_name, end_flags=True)
        result_handle(log_name=log_name)
    elif test_type == "8":
        log.n_p("请选择你想要进行的顺序预写方式 : 0.按照loops圈数进行预写 1.按照runtime时间进行预写")
        tmp = log.u_in('What kind of pre writing do you want to do? 0.loops   1.runtime [0/1]? : ')
        if tmp == "0":
            flags = 'loops'
        elif tmp == "1":
            flags = 'runtime'
        else:
            flags = 'loops'
        sequen_prewriting_start(disk_info=disk_info, flags=flags)
        sequence_write_start(disk_info=disk_info, log_name=log_name, end_flags=False)
        sequence_read_start(disk_info=disk_info, log_name=log_name, end_flags=True)
        result_handle(log_name=log_name)
    elif test_type == "9":
        random_read_start(disk_info=disk_info, log_name=log_name, end_flags=True)
        result_handle(log_name=log_name)
    elif test_type == "10":
        random_write_start(disk_info=disk_info, log_name=log_name, end_flags=True)
        result_handle(log_name=log_name)
    elif test_type == "11":
        random_prewriting_start(disk_info=disk_info)
    elif test_type == "12":
        random_write_start(disk_info=disk_info, log_name=log_name, end_flags=False)
        random_read_start(disk_info=disk_info, log_name=log_name, end_flags=True)
        result_handle(log_name=log_name)
    elif test_type == "13":
        random_prewriting_start(disk_info=disk_info)
        random_read_start(disk_info=disk_info, log_name=log_name, end_flags=True)
        result_handle(log_name=log_name)
    elif test_type == "14":
        random_prewriting_start(disk_info=disk_info)
        random_write_start(disk_info=disk_info, log_name=log_name, end_flags=True)
        result_handle(log_name=log_name)
    elif test_type == "15":
        ran_rx_start(disk_info=disk_info, log_name=log_name, end_flags=True)
        result_handle(log_name=log_name)
    elif test_type == "16":
        random_prewriting_start(disk_info=disk_info)
        random_write_start(disk_info=disk_info, log_name=log_name, end_flags=False)
        random_read_start(disk_info=disk_info, log_name=log_name, end_flags=True)
        result_handle(log_name=log_name)
    elif test_type == "17":
        random_prewriting_start(disk_info=disk_info)
        random_write_start(disk_info=disk_info, log_name=log_name, end_flags=False)
        random_read_start(disk_info=disk_info, log_name=log_name, end_flags=False)
        sequen_prewriting_start(disk_info=disk_info, flags='loops')
        sequence_write_start(disk_info=disk_info, log_name=log_name, end_flags=False)
        sequence_read_start(disk_info=disk_info, log_name=log_name, end_flags=True)
        result_handle(log_name=log_name)
    elif test_type == "18":
        random_prewriting_start(disk_info=disk_info)
        random_write_start(disk_info=disk_info, log_name=log_name, end_flags=False)
        random_read_start(disk_info=disk_info, log_name=log_name, end_flags=False)
        sequen_prewriting_start(disk_info=disk_info, flags='runtime')
        sequence_write_start(disk_info=disk_info, log_name=log_name, end_flags=False)
        sequence_read_start(disk_info=disk_info, log_name=log_name, end_flags=True)
        result_handle(log_name=log_name)
    elif test_type == "lmq":
        random_prewriting_start(disk_info=disk_info)
        random_write_start(disk_info=disk_info, log_name=log_name, end_flags=False)
        random_read_start(disk_info=disk_info, log_name=log_name, end_flags=False)
        sequence_write_start(disk_info=disk_info, log_name=log_name, end_flags=False)
        sequence_read_start(disk_info=disk_info, log_name=log_name, end_flags=True)
        result_handle(log_name=log_name)
    elif test_type == "19":
        log.n_p("Disk Quickly Check")
    elif test_type == "21":
        log.n_p("DD LongTime Test")
    elif test_type == "22":
        log.n_p("Waiting for development")
    else:
        log.n_p("invalid test type Error!")
        exit()
