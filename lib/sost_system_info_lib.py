# Filename : system_info_lib.py
# Release time : 2024-10-18
# Version:1.1
# by:Xiaodong Fan

from .sost_logging import *
import os
import re

log = dong_log()
log.popen_save_file_flags = True
log.debug_flags = str(log.json_get("debug","debug_flags",web='no-log',filename="debug"))

def retry_get_ipmi_info(command='',text=''):
    ipmi_sensdr_retry_count = log.json_get('Test_Config',"ipmi_sensdr_retry_count").strip()
    if ipmi_sensdr_retry_count == '' or ipmi_sensdr_retry_count == '0': return

    now_count = log.json_get("Test_tmp","test_count")
    retry_ipmi_log = log.json_get("Test_tmp","test_folder_path")+"/ipmi_retry.log"
    if now_count == '' or now_count == '0':return
    
    try:
        int(ipmi_sensdr_retry_count)
    except:
        log._tips('sost config ipmi_sensdr_retry_count value Err!')
        return
    if command == '': return 
    if text == '': text = 'ipmi retry count '
    else: text = text + 'Attempt'
    for i in range(int(ipmi_sensdr_retry_count)):
        log._pr(text.ljust(40) + f"\033[33m[      {str(int(i)+1)}      ]\033[0m")
        result = log.os_popen(command)
        log.save_to_file(filename=retry_ipmi_log,text=result)
        
    log._pr(text.ljust(40) + f"\033[32m[   Complete  ]\033[0m")
    log._dp(text.ljust(40) + f'Successfully executed command {str(int(ipmi_sensdr_retry_count)+1)} times in a row')
    

def fail_logo(save_config=True):
    log.json_set("Test_tmp","test_status","FAIL")
    print('''\033[31m
══════════════════════════════════════════════════════
||           ████████     ██     ██ ██              ||
||          ░██░░░░░     ████   ░██░██              ||     
||          ░██         ██░░██  ░██░██              ||     
||          ░███████   ██  ░░██ ░██░██              ||    
||          ░██░░░░   ██████████░██░██              ||   
||          ░██      ░██░░░░░░██░██░██              ||  
||          ░██      ░██     ░██░██░████████        ||
||          ░░       ░░      ░░ ░░ ░░░░░░░░         ||
══════════════════════════════════════════════════════
||  Oh.My.God Stability Fail Please check fail.txt  ||
══════════════════════════════════════════════════════\033[0m''')
    return 0

def failc_logo(save_config=True):
    if save_config:log.json_set("Test_tmp","test_status","FAILc")
    print('''\033[33m
════════════════════════════════════════════════════════
||      ████████           ██  ██         ██████      ||
||     ░██░░░░░           ░░  ░██        ██░░░░██     ||
||     ░██        ██████   ██ ░██       ██    ░░      || 
||     ░███████  ░░░░░░██ ░██ ░██ █████░██            ||
||     ░██░░░░    ███████ ░██ ░██░░░░░ ░██            ||
||     ░██       ██░░░░██ ░██ ░██      ░░██    ██     ||
||     ░██      ░░████████░██ ███       ░░██████      ||
||     ░░        ░░░░░░░░ ░░ ░░░         ░░░░░░       ||
════════════════════════════════════════════════════════
|| Oh.My.God Stability Fail Please check failc.txt    ||
════════════════════════════════════════════════════════\033[0m''')
    return 0

def fail_info(error_type,error_info,file1,file2):
    fail_exit_flags = log.json_get("Test_Config","fail_exit_flags")
    fail_exit_blacklist = log.json_get("Test_Config","fail_exit_blacklist").strip().split(",")
    osIP = log.os_popen(r''' ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' ''').strip().replace("\n","|")
    osVer  = log.os_popen('cat /etc/os-release | grep -i PRETTY_NAME=').replace('PRETTY_NAME=','').strip()
    BMC_IP = log.os_popen('''ipmitool lan print | grep -i 'IP Address' | grep -vi source | awk '{print $4}' ''').strip()
    test_count = log.json_get("Test_tmp","test_count").strip()
    test_typee = log.json_get("Test_tmp","test_type").strip()
    test_folder = log.json_get("Test_tmp","test_folder_path").strip()
    failc_result_folder = test_folder+'/failc_result'
    failc_result_summary_file = failc_result_folder+f'/summary.log'
    failc_error_fail_info = failc_result_folder+f'/{error_type.replace(" ","")}.log'
    # New Add ErrorType Result Folder 
    # FileName : {errtype}.log -> writeType : a
    if fail_exit_flags!='1':
        if not os.path.exists(failc_result_folder):
            log.os_run(f'mkdir -p {failc_result_folder}')
        if not os.path.exists(failc_result_summary_file):
            log.os_run(f'touch {failc_result_summary_file}')

        with open(failc_error_fail_info,'a') as f:
            f.write(f"TestType  : {test_typee.strip()}\n")
            f.write(f"Count     : {test_count.strip()}\n")
            f.write(f"Time      : {str(now_time()).strip()}\n")
            f.write(f"File1     : {file1.strip()}\n")
            f.write(f"File2     : {file2.strip()}\n")
            f.write("-"*55+'\n')
            f.write(str(error_info)+'\n')
            f.write("-"*55+'\n')
            f.flush()

        # Summary Failc Folder File -> Collect Count num in Failc File
        with open(failc_result_summary_file,'w') as f:
            result = log.os_popen(f'''cd "{failc_result_folder}" && for file in *.log; do 
    [[ "$file" != "summary.log" ]] && 
    echo "$(basename "$file" .log) : $(grep -oi "count" "$file" | wc -l)"
done''')
            print(result)
            f.write(result)
            f.flush()
        os.sync()
        
    if fail_exit_flags == "0":
        failc_logo()
        filename = test_folder+'/failc.txt'
    else:
        fail_logo()
        filename = test_folder+'/fail.txt'
    print()
    log._pr(f"BMC_IP    : {BMC_IP.strip()}",filename)
    log._pr(f"osIP      : {osIP.strip()}",filename)
    log._pr(f"osVer     : {osVer.strip()}",filename)
    log._pr(f"TestType  : {test_typee.strip()}",filename)
    log._pr(f"ErrType   : {error_type.strip()}",filename)
    log._pr(f"Count     : {test_count.strip()}",filename)
    log._pr(f"Time      : {str(now_time()).strip()}",filename)
    log._pr(f"File1     : {file1.strip()}",filename)
    log._pr(f"File2     : {file2.strip()}",filename)
    log._pr("-"*55,filename)
    if type(error_info) == list:
        for error_info_line in error_info:
            log._pr(error_info_line,filename)
    else:
        log._pr(error_info,filename)
    log._pr("-"*55,filename)

    time.sleep(int(str(log.json_get('debug','Failc_Waiting_Time',filename='debug'))))

    # dong_log() log.json_get()
    if log.json_get("smtp","Fail_send_email").strip() == "1":
        from .sost_public_lib import smtp_send_result
        smtp_send_result(open(f'{test_folder}/fail.txt',"r").read())
    
    # running Time fail , save 'systemd-analyze' plot to file
    if error_type == 'Running Time for too long':
        log.os_run(f'systemd-analyze plot > {test_folder}/runningTime_Fail_{test_count}_systemd-analyze_plot.html &',flags='no-log')

    if fail_exit_flags == '1':
        from .sost_public_lib import defalt_path,result_html
        defalt_path()
        result_html()
        exit()
    else:
        if error_type in fail_exit_blacklist:
            log._pr(f"error_type : {error_type}")
            log._pr(f"blacklist  : {str(fail_exit_blacklist)}")
            
            log._error("Set error not to exit, trigger blacklist, exit test!")

def bmclog_check(path,count):

    black_list = ["FAN","CMOS","ac","dc"]
    if log.json_get("BMC_Survival_Config","bmc_chip") == 'Hisilicon-Hi1711':
        black_list.append("Power Supply PSU1 Status")
        black_list.append("Power Supply PSU2 Status")

    json_data = json.loads(open("/opt/sost/config/bmcsel_check.json","r").read())
    error_arry = list(json_data["bmcsel_check_items"].keys())

    if path == '':
        path = "/tmp/sost_tmp/bmclog.log"
        log.os_run(f"ipmitool sel list > {path}")

        with open(path, "r") as f:
            lines = f.readlines()
        for error_type in error_arry:
            tmp_array = []
            error_lower = error_type.lower()
            for line in lines:
                if error_lower in line.lower():
                    log._pr(f"bmclog error type : {error_type.ljust(50)} \033[31m[FAIL]\033[0m")
                    print('-'*60 + '\n' + line.strip() + '\n' + '-'*60)
                    tmp_array.append(line.strip())
            if not tmp_array:
                log._pr(f"bmclog error type : {error_type.ljust(50)} \033[32m[Pass]\033[0m")
        log.os_run(f"rm -rf {path}",flags='no-log')
        exit()
    
    for item in black_list:
        if item in error_arry:
            error_arry.remove(item)

    # Check if the BMC sel log contains FAN logs to determine if there is a restart action in BMC
    if "aclost" in str(path).lower():
        log._dp("TestType : AClost -> not add bmclog_strings to error_arry")
    elif "reset" in str(path).lower():
        log._dp("TestType : Bmcreset -> not add bmclog_strings to error_arry")
    elif "cold" in str(path).lower():
        log._dp("TestType : Bmcreset -> not add bmclog_strings to error_arry")
    elif "warm" in str(path).lower():
        log._dp("TestType : Bmcreset -> not add bmclog_strings to error_arry")
    else:
        for item in black_list:
            if item not in error_arry:
                error_arry.append(item)

    log._dp(f"bmc sel check error arry : {str(error_arry)}")

    error_tmp = []
    if str(count) == "0":
        with open(path+f"/system_info/bmclog/bmclog_0.txt","r") as f:
            for strings in f.readlines():
                for error_type in error_arry:
                    if error_type.lower() in strings.lower():
                        if json_data["bmcsel_check_items"][str(error_type)] == "1":
                            error_tmp.append(strings)
                        else:
                            log._dp(f"bmc sel find error : {str(error_type)} , but not set 0 to exit test")
        up_filename = "bmclog_check"
        now_filename = "bmclog_check"
    else:
        up_filename  = path + f"/system_info/bmclog/bmclog_{str(int(count)-1)}.txt"
        now_filename = path + f"/system_info/bmclog/bmclog_{count}.txt"
        try:result = log.os_popen(f''' bash -c 'diff <(cut -d "|" -f2- {up_filename}) <(cut -d "|" -f2- {now_filename})' 2>/dev/null''').replace("-","").replace("<","").replace(">","").replace("   ","").strip().replace(" \n\n","")
        except:result = ''
        for error_type in error_arry:
            if error_type in result:
                log._dp("bmc sel find error : " +(error_type))
                if json_data["bmcsel_check_items"][str(error_type)] == "1":
                    error_tmp.append(result.replace("-",""))

    if len(error_tmp) == "0":
        return ''
    else:
        return error_tmp

def dmesg_check(file1):
    error_result_arry = []
    json_data = json.loads(open("/opt/sost/config/dmesg_check.json","r").read())
    errorType_arry = list(json_data["dmesg_check_items"].keys())

    # while_str = 'str1|str2|str3|str4'
    white_str = 'GHES'
    show_flags = False
    if file1 == '':
        log.os_run("dmesg >> /tmp/sost_tmp/dmesg.log")
        file1 = "/tmp/sost_tmp/dmesg.log"
        show_flags = True

    for errorType in errorType_arry:
        result = log.os_popen(f'cat {file1} | grep -i "{errorType.strip()}" | grep -vE "{white_str}" ').strip()
        if result !="":
            if show_flags:
                log._pr(f"dmesg error type : {errorType.ljust(50)} \033[31m[FAIL]\033[0m")
                print('-'*40+'\n'+result+'\n'+'-'*40)
            else:
                if json_data["dmesg_check_items"][str(errorType)] == "1":
                    log._dp(f"dmesg error type : {errorType} , errstrings : {result}")
                    error_result_arry.append(str(result))
        else:
            if show_flags:
                log._pr(f"dmesg error type : {errorType.ljust(50)} \033[32m[Pass]\033[0m")
                
    log._dp(error_result_arry)
    log.os_run(f"rm -rf /tmp/sost_tmp/dmesg.log",flags='no-log')

    if len(error_result_arry) == 0:
        return True,"Pass"
    else:
        return False,"\n".join(error_result_arry)

def normal_diff(file1,file2,typee,path='',count=''):
    if "cpuinfo" == typee:
        result = log.os_popen(f"bash -c 'diff <(head -n 10 {file1}) <(head -n 10 {file2})' 2>/dev/null").strip()
    #check HDD info head 10 : check disk num /sys/block
    elif "hddinfo" == typee:
        result = log.os_popen(f"bash -c 'diff <(head -n 2 {file1}) <(head -n 2 {file2})' 2>/dev/null").strip()
    elif "usbinfo" == typee:
        result = log.os_popen(f"bash -c 'diff <(head -n 1 {file1}) <(head -n 1 {file2})' 2>/dev/null").strip()
    elif "bmcsensor" == typee:
        # 控制显示的diff格式
        diff_format = '' # "-y -W 50 "
        # 控制显示diff结果的行数
        tail_lines = ''  #'| tail -n +2'#'| tail -n +2'
        # 结果初始化
        result = ''
        # 检查sensor value 数组
        check_strings_array = ['0x0','0x00','0x01','na']
        for check_strings in check_strings_array:
            result_tmp = log.os_popen(f'''bash -c "diff <(cat {file1} | cut -d '|' -f 2,1 | grep -i '{check_strings}' | sort ) <(cat {file2} | cut -d '|' -f 2,1 | grep -i '{check_strings}' | sort ) {diff_format} " {tail_lines} 2>/dev/null''').strip()+'\n'
            # 检查每次diff结果是否为空行，若不是则追加到最终结果中
            if result_tmp != '\n':
                result = result + result_tmp
        # check fan speed rate 0
        fan_name_file2 = log.os_popen(f"cat {file2} | grep -i fan | grep -i speed | cut -d '|' -f 1,2 | grep -vi na | awk '{{print $1}}'").strip().split("\n")
        fan_rate_file2 = log.os_popen(f"cat {file2} | grep -i fan | grep -i speed | cut -d '|' -f 1,2 | grep -vi na | awk '{{print $3}}' | cut -d '.' -f 1").strip().split("\n")
        # 判断转速列表是否为空
        if fan_rate_file2 == ['']:result = result+''
        # 遍历风扇速度列表，检查是否有速度为0的情况
        for num in range(len(fan_rate_file2)):
            try:
                if int(fan_rate_file2[num]) == 0:
                    result = result + f"fan_name : {fan_name_file2[num]} , fan_speed : {fan_rate_file2[num].strip()}\n"
            except:
                continue
        # 检查其他0x状态值变化
        value_0x = log.os_popen(f'''bash -c "diff <(cat {file1} | cut -d '|' -f 1,2 | grep -viE 'na|0x0|0x00' | grep -i 0x | sort ) <(cat {file2} | cut -d '|' -f 1,2 | grep -viE 'na|0x0|0x00' | grep -i 0x | sort ) {diff_format} " {tail_lines} 2>/dev/null''').strip()+'\n'
        if value_0x != '\n':
            result = result + value_0x

    elif "bmcsdr" == typee:
        result = log.os_popen(f'''bash -c "diff <(cat {file1} | cut -d '|' -f 3,1 | grep -i 'ok' | sort ) <(cat {file2} | cut -d '|' -f 3,1 | grep -i 'ok' | sort )" 2>/dev/null''').strip()
        result = result + log.os_popen(f'''bash -c "diff <(cat {file1} | cut -d '|' -f 3,1 | grep -i 'ns' | sort ) <(cat {file2} | cut -d '|' -f 3,1 | grep -i 'ns' | sort )" 2>/dev/null''').strip()
    elif "bmcsdre" == typee:
        result = log.os_popen(f'''bash -c "diff <(cat {file1} | cut -d '|' -f 3,1 | grep -i 'ok' | sort ) <(cat {file2} | cut -d '|' -f 3,1 | grep -i 'ok' | sort )" 2>/dev/null''').strip()
        result = result + log.os_popen(f'''bash -c "diff <(cat {file1} | cut -d '|' -f 3,1 | grep -i 'ns' | sort ) <(cat {file2} | cut -d '|' -f 3,1 | grep -i 'ns' | sort )" 2>/dev/null''').strip()
        result = result + log.os_popen(f'''bash -c "diff <(cat {file1} | cut -d '|' -f 1,5 | grep -i 'no reading' | sort ) <(cat {file2} | cut -d '|' -f 1,5 | grep -i 'no reading' | sort )" 2>/dev/null''').strip()
    elif "ibmcfan" == typee:
        result = log.os_popen(f'''bash -c "diff <(cat {file1} | grep ':0' | wc -l) <(cat {file2} | grep ':0' | wc -l)" 2>/dev/null''').strip()
    elif "ibmcfw" == typee:
        result = log.os_popen(f"bash -c 'diff <(head -n 1 {file1}) <(head -n 1 {file2})' 2>/dev/null").strip()
    elif "ibmcmem" == typee:
        result = log.os_popen(f"bash -c 'diff <(head -n 1 {file1}) <(head -n 1 {file2})' 2>/dev/null").strip()
    elif "ibmcpsu" == typee:
        file1_result = True
        file2_result = True
        file1_arry = log.os_popen(f"cat {file1.strip()}").strip().replace(" ","").split(",")
        file2_arry = log.os_popen(f"cat {file2.strip()}").strip().replace(" ","").split(",")
        if "0" in file1_arry:
            file1_result = False
        if "0" in file2_arry:
            file2_result = False
        if file1_result and file2_result:
            result = ""
        else:
            result = "ibmcfile1 : "+log.os_popen(f"cat {file1.strip()}").strip().replace(" ","")+"   ibmcfile2 : "+log.os_popen(f"cat {file2.strip()}").strip().replace(" ","")
    elif "bmclog" == typee:
        result = bmclog_check(path=path,count=count)
        if result == []:result = ''
        log._dp(f"bmclog diff result : {str(result)}")
    else:
        result = log.os_popen(f"diff {file1} {file2} 2>/dev/null").strip()

    if result == '' or len(str(result).replace('\n','')) == 0:
        return True,result
    else:
        return False,result

def diff_information(count,path,typee):
    if str(count) == "0":return True
    file_first_count = path+"/system_info/"+typee+"/"+f"{typee}_0.txt"
    file_now_count = path+"/system_info/"+typee+"/"+f"{typee}_{count}.txt"
    if typee == "dmesg":
        result_status , result = dmesg_check(file_now_count)
    else:
        result_status , result = normal_diff(file_first_count,file_now_count,typee,path,count)

    if result_status:
        return True
    else:
        fail_info(typee,result,file_first_count,file_now_count)
        return False

def echo_dev_info_sleep(flags,count):
    if count == "0" and flags == "0":
        timess = ""
    else:
        timess = '0'

    if flags == "0": 
        num = 80
        str = "="
        print(str * num + "\n")
    if timess == "0":
        return
    else:
        try:
            time.sleep(int(log.json_get("Test_Config", "frist_sdi_time")))
        except:
            return

def sata_collect_info(disk_name):
    result = []
    # 获取sata硬盘列表
    # sata_disk_inch  0
    sata_disk_inch = log.os_popen(f"smartctl -i /dev/{disk_name} | grep -i 'inches' ").replace("Form Factor:", "").replace(
        "inches", "").strip()
    if sata_disk_inch == "":
        result.append("-.-")
    else:
        result.append(sata_disk_inch)
    # sata_disk_temp  1
    temp = log.os_popen(( f"smartctl -a /dev/{disk_name} | grep -i Temperature_Celsius | grep Old_age | awk '{{print $10}}' ").strip().split("\n")[0])
    if temp == "":
        temp = log.os_popen(
            f"smartctl -a /dev/{disk_name} | grep -i 'Current Drive Temperature:' | awk '{{print $4}}' ").strip().split(
            "\n")[0]
        if temp == "":
            temp = log.os_popen(
                f"smartctl -a /dev/{disk_name} | grep -i Temperature_Celsius | awk '{{print $10}}'").strip().split(
                "\n")[0]
            if temp == "":
                temp = log.os_popen(
                    f"smartctl -a /dev/{disk_name} | grep -i 'current drive temperature' | awk '{{print $4}}'")
        if temp == "":
            result.append("NA")
        else:
            result.append(temp.strip().split("\n")[0])
    else:
        result.append(temp.strip().split("\n")[0])
    # sata_disk_model 2
    model = log.os_popen(f"smartctl -i /dev/{disk_name} | grep -i 'device model' ").replace("Device Model:", "").strip()
    if model == "":
        model = log.os_popen(f"smartctl -i /dev/{disk_name} | grep -i 'Product:' | awk '{{print $2}}'").strip()
        if model == "":
            result.append("NA/NA/NA/NA")
        else:
            result.append(model)
    else:
        result.append(model)

    # sata_disk_seri  3
    sata_disk_seri = log.os_popen(
        f"smartctl -i /dev/{disk_name} | grep -i 'Serial Number' | awk '{{print $3}}'").strip()
    if sata_disk_seri == "":
        result.append("N/A")
    else:
        result.append(sata_disk_seri)
    # sata_disk_size  4
    sata_disk_size = log.os_popen(
        fr"smartctl -i /dev/{disk_name} | grep -i 'User Capacity' | grep -oP '\[\K[^]]+'").strip()
    if sata_disk_size == "":
        result.append("N/A")
    else:
        result.append(sata_disk_size)
    # sata_disk_rpmm  5
    sata_disk_rpmm = log.os_popen(
        f"smartctl -i /dev/{disk_name} | grep -i 'Rotation Rate' | awk '{{print $3}}'").strip()
    if sata_disk_rpmm == "":
        result.append("N/A")
    else:
        result.append(sata_disk_rpmm)
    # sata_disk_fwve  6
    fwve = log.os_popen(f"smartctl -i /dev/{disk_name} | grep -i 'firmware version' | awk '{{print $3}}'").strip()
    if fwve == "":
        fwve = log.os_popen(f"smartctl -i /dev/{disk_name} | grep -i Revision | awk '{{print $2}}'").strip()
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
        if 'SAS' in log.os_popen(f" smartctl -i /dev/{disk_name} | grep -i 'Transport protocol:' | awk '{{print $3}}' "):
            result.append("SAS")
        else:
            result.append("SATA")
    # sata lnk type 8
    sata_speed = log.os_popen(
        f" smartctl -i /dev/{disk_name}| grep -i 'sata version is:' | awk '{{print $6,$7}}' ").strip()
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
    return result

def print_save_text(flags, folder_path, type, count, text):
    
    type_folder = f"{folder_path}/system_info/{type}"

    if str(count) == "0" and not os.path.exists(type_folder):
        log.os_run(f"mkdir -p {type_folder}",flags='no-log')
    if flags == "0":
        print(text)
        log.save_to_file(filename='/opt/sost/log/sost_interactive.log',text=text)
    elif flags == "1":
        try:
            if text == "": 
                text = f"print_save_text -> text is Null => {type}"
                log._warning(text)
            # a = Add Write Data to File
            with open(f"{folder_path}/system_info/{type}/{type}_{count}.txt", "a") as f:
                f.write(text + "\n")
                f.flush()
                os.fsync(f.fileno())
            # Retry text save to file
            if "0" in log.os_popen(f"du {folder_path}/system_info/{type}/{type}_{count}.txt | awk '{{print $1}}'"):
                with open(f"{folder_path}/system_info/{type}/{type}_{count}.txt", "w") as f:
                    f.write(text + "\n")
                    f.flush()
                    os.fsync(f.fileno())
        except Exception as e:
            log._error(f"Error Info : {str(e)}")
    elif flags == "2":
        with open(f"{folder_path}/testconfig.txt", "a") as f:
            f.write(text + "\n")
            f.flush()
            os.fsync(f.fileno())
    else:
        if flags =='show':
            print(text)
            return 0
        log._error("Save.to.File.Err.Exit!")
    
    log.os_run("sync -f && sync",flags='no-log')

def system_info_check(flags, path, count):
    try:
        osip(flags, path, count)
        meminfo(flags, path, count)
        pcieinfo(flags, path, count)
        pcieslot(flags, path, count)
        psuinfo(flags, path, count)
        cpu_info(flags, path, count)
        os_disk_info(flags, path, count)
        os_net_info(flags, path, count)
        usb_info_check(flags, path, count)
        dmesg(flags, path, count)
        storinfo(flags, path, count)
    except Exception as e:
        from .sost_public_lib import defalt_path,result_html
        defalt_path()
        result_html()
        log._error(f"script error : {e}")
    
def bmc_info_check(flags, path, count):
    try:
        bmcip(flags, path, count)
        bmcguid(flags, path, count)
        bmchealth(flags, path, count)
        ipmi_sensor(flags, path, count)
        ipmi_sensor_data(flags, path, count)
        ipmi_sel_log(flags, path, count)
        bmc_sdr_info(flags, path, count)
        bmc_sdre_info(flags, path, count)
        backboard_info(flags, path, count)
        chassis_status(flags, path, count)
        ipmi_mcinfo(flags, path, count)
    except Exception as e:
        from .sost_public_lib import defalt_path,result_html
        defalt_path()
        result_html()
        log._error(f"script error : {e}")
        
def test_config(flags, count, path):
    log.json_set('Test_tmp','Running_flag','2')
    # 0 print 1 to file 2 to testconfig.txt => stability_config.json
    if flags == "1":
        if log.json_get("Test_Config","simple_test_flags")=="simple":
            print('')
            return 0
    elif flags == "2":
        print('''
════════════════════════════════════════════════════════════════
|                     Collect Information                      |
═══════════════════════════════════════════════[Collect]═[Check]''')
        log._pr('Collect To testconfig.log               \033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m')
        pass
    elif flags == "0":
        pass
    else:
        log._error(f"flags Error! flags : {flags}")

    def public_check(flags, path, count):
        fwinfo(flags, path, count)
        check_ipmitool(flags, path, count)
        echo_dev_info_sleep(flags,count)
        if str(count)!='0':
            check_rebooting_time(flags, path, count)
        if flags != '2':
            # other command runks
            tmp = log.json_get("Test_Config", "collect_cmd").strip().split(",")
            if tmp != "":
                if not tmp[0] == "":
                    for cmd_name in tmp:
                        other_collect_info(flags, path, count, cmd_name)
                        if flags == "0": print('='*80 + "\n")
            # check bmc status
            if log.json_get("BMC_Survival_Config", "switch") == "1":
                if bmc_survival_check(flags, path, count):
                    log._pr("BMC Survival Check ".ljust(40) + "\033[31m[FAIL]\033[0m")
            echo_dev_info_sleep(flags,count)
        else:
            pass

    simple_flags = log.json_get("Test_Config","simple_test_flags").strip()
    
    if simple_flags == "bmc":
        log._dp(" TestMode         : bmc")
        bmc_info_check(flags, path, count)
        public_check(flags, path, count)
    elif simple_flags == "os":
        log._dp(" TestMode         : os")
        system_info_check(flags ,path, count)
        public_check(flags, path, count)
    elif simple_flags == "simple":
        log._dp(" TestMode         : simple")
    else:
        system_info_check(flags ,path, count)
        bmc_info_check(flags, path, count)
        public_check(flags, path, count)

#check rtc_time
# def check_rtc_time(flags, path, count):
#     if log.json_get('collect_array',"rtctime",web='no-log',filename='collect').strip() !='1':return 0

#     print_save_text(flags=flags, folder_path=path, type="rtctime", count=count,text=log.os_popen('timedatectl').strip())
    
#     if str(count) == "0":return 0

#     filepath = path + f"/system_info/rtctime/rtctime_{count}.txt"
#     # last_filepath = path + f"/system_info/rtctime/rtctime_{str(int(count)-1)}.txt"

#     rtc_date_time = log.os_popen(f"cat {filepath} | head -n 2 | awk '{{print $4}}' ").split()
#     rtc_hours_time = log.os_popen(f"cat {filepath} | head -n 2 | awk '{{print $5}}' | cut -d ':' -f 1 ").split()
#     rtc_minimumtime = log.os_popen(f"cat {filepath} | head -n 2 | awk '{{print $5}}' | cut -d ':' -f 2 ").split()
#     rtc_seconds_time = log.os_popen(f"cat {filepath} | head -n 2 | awk '{{print $5}}' | cut -d ':' -f 3 ").split()
#     # rtc_time_zone = log.os_popen(f"cat {filepath} | head -n 5 | grep -i 'Time zone' | cut -d ':' -f 2 ").split()

#     if len(rtc_date_time)!=2:
#         log._pr("RTC Time date check".ljust(40) + "\033[31m[FAIL]\033[0m   \033[31m[FAIL]\033[0m")
#         error_tmp = f'RTC Time date check Fail   : {str(rtc_date_time)}\n< sost > {log.os_popen("timedatectl")}'
#         fail_info('RTC Time date check',error_tmp,f'timedatectl',f"timedatectl")
#     elif len(rtc_hours_time)!=2:
#         log._pr("RTC Time h check".ljust(40) + "\033[31m[FAIL]\033[0m   \033[31m[FAIL]\033[0m")
#         error_tmp = f'RTC Time hours check Fail   : {str(rtc_hours_time)}\n< sost > {log.os_popen("timedatectl")}'
#         fail_info('RTC Time hours check',error_tmp,f'timedatectl',f"timedatectl")
#     elif len(rtc_minimumtime)!=2:
#         log._pr("RTC Time m check".ljust(40) + "\033[31m[FAIL]\033[0m   \033[31m[FAIL]\033[0m")
#         error_tmp = f'RTC Time minimum check Fail   : {str(rtc_minimumtime)}\n< sost > {log.os_popen("timedatectl")}'
#         fail_info('RTC Time minimum check',error_tmp,f'timedatectl',f"timedatectl")
#     elif len(rtc_seconds_time)!=2:
#         log._pr("RTC Time s check".ljust(40) + "\033[31m[FAIL]\033[0m   \033[31m[FAIL]\033[0m")
#         error_tmp = f'RTC Time seconds check Fail   : {str(rtc_seconds_time)}\n< sost > {log.os_popen("timedatectl")}'
#         fail_info('RTC Time seconds check',error_tmp,f'timedatectl',f"timedatectl")
#     else:
#         log._pr("RTC Time date/h/m/s check".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")

#     datetime = abs(rtc_date_time[0] - rtc_date_time[1]) 
#     if :
#         error_tmp = f'RTC Time date check Fail   : {str(rtc_date_time)}\n< sost > {log.os_popen("timedatectl")}'
#         fail_info('RTC Time date check',error_tmp,f'timedatectl',f"timedatectl")
#     elif abs(int(rtc_hours_time[0]) - int(rtc_hours_time[1]) ) != 8 or abs(int(rtc_hours_time[0]) - int(rtc_hours_time[1])) != 16:
#         error_tmp = f'RTC Time hours check Fail   : {str(rtc_hours_time)}\n< sost > {log.os_popen("timedatectl")}'
#         fail_info('RTC Time hours check',error_tmp,f'timedatectl',f"timedatectl")
#     elif rtc_minimumtime[0] != rtc_minimumtime[1]:
#         error_tmp = f'RTC Time minimum check Fail   : {str(rtc_minimumtime)}\n< sost > {log.os_popen("timedatectl")}'
#         fail_info('RTC Time minimum check',error_tmp,f'timedatectl',f"timedatectl")
#     elif rtc_seconds_time[0] != rtc_seconds_time[1]:
#         error_tmp = f'RTC Time seconds check Fail   : {str(rtc_seconds_time)}\n< sost > {log.os_popen("timedatectl")}'
#         fail_info('RTC Time seconds check',error_tmp,f'timedatectl',f"timedatectl")
#     else:
#         log._pr("RTC Time check ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
# bmc mc self test result
def bmchealth(flags, path, count):
    if log.json_get('collect_array',"bmchealth",web='no-log',filename='collect').strip() !='1':return 0
    bmc_guid = log.os_popen("ipmitool mc selftest").strip()
    print_save_text(flags=flags, folder_path=path, type="bmchealth", count=count,text=bmc_guid)
    if flags == "1" : 
        if diff_information(count,path,"bmchealth"):
            log._pr("BMC IPMI health ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("BMC IPMI health ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")

# check bmc guid
def bmcguid(flags, path, count):
    if log.json_get('collect_array',"bmcguid",web='no-log',filename='collect').strip() !='1':return 0
    bmc_guid = log.os_popen("ipmitool mc guid | grep 'System GUID' | head -n 1").strip()
    print_save_text(flags=flags, folder_path=path, type="bmcguid", count=count,text=bmc_guid)
    if flags == "1" : 
        if diff_information(count,path,"bmcguid"):
            log._pr("BMC IPMI GUID ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("BMC IPMI GUID ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")


# check RuningTime
def check_running_time(count):

    if log.json_get('collect_array',"running_time",web='no-log',filename='collect').strip() !='1':return 0

    if int(count) < 2:return 0
    running_time_last =  log.json_get('Test_tmp','running_time_last')
    running_time_now =  log.json_get('Test_tmp','running_time_now')
    running_time_max = log.json_get('Test_Config','running_time_max')

    Phase_time = abs(int(running_time_now) - int(running_time_last))

    if running_time_max == '' or '0':running_time_max = '60' 

    if Phase_time > int(running_time_max):
        log._pr("Running Time check ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")
        error_tmp = f'System last Running Time   : {str(running_time_last)}\n< sost > System now Running Time    : {str(running_time_now)}\n< sost > Max Phase difference time  : {str(running_time_max)}s\n< sost > Phase difference time       : {str(Phase_time)}s'
        fail_info('Running Time for too long',error_tmp,f'running_time.txt',f"running_time.txt")
    else:
        log._pr("Running Time check ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")

# check IPMItool
def check_ipmitool(flags, path, count):
    if log.json_get('collect_array',"ipmitool",web='no-log',filename='collect').strip() !='1':return 0
    if log.json_get("Test_Config","simple_test_flags") == "simple":
        return 0
    if flags == '1':
        if log.os_popen("ipmitool mc guid | grep -i 'guid' | wc -l").strip() == "0":
            log._pr("IPMITool Get Info Check ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")
        else:
            log._pr("IPMITool Get Info Check ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")

# check Rebooting Time
def check_rebooting_time(flags, path, count):
    if log.json_get('collect_array',"rebooting_time",web='no-log',filename='collect').strip() !='1':return 0
    # 检查文件是否为空，空文件自动删除。
    if log.os_popen(f"du {path}/failc.txt 2>/dev/null| awk '{{print $1}}' ").strip() == '0':
        log.os_run(f"rm -rf {path}/failc.txt")
    
    if log.os_popen(f"du {path}/fail.txt 2>/dev/null| awk '{{print $1}}' ").strip() == '0':
        log.os_run(f"rm -rf {path}/fail.txt")

    max_time = int(log.json_get("Test_Config","Maximum_restart_time").strip())
    end_time = log.os_popen(f"cat {path}/debug/end_time.txt 2>/dev/null").strip()
    start_time = log.os_popen(f"cat {path}/debug/start_time.txt").strip()
    rebooting_time = int(start_time) - int(end_time)
    if int(rebooting_time) > max_time:
        log._pr("Restart TimeTooLong ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")
        error_tmp = f'System shutdown time   : {str(end_time)}\n< sost > System on time         : {str(start_time)}\n< sost > Phase difference time  : {str(rebooting_time)}s'
        fail_info('restart TimeTool Long',error_tmp,f'{path}/debug/start_time.txt',f"cat {path}/debug/end_time.txt ")
    else:
        log._pr("Restart TimeTooLong ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")


def usb_info_check(flags, folder_path, count):
    if log.json_get('collect_array',"usbinfo",web='no-log',filename='collect').strip() !='1':return 0
    echo_dev_info_sleep(flags,count)
    os_usbinfo = log.os_popen("lsusb")
    # usbinfo 
    print_save_text(flags=flags, folder_path=folder_path, type="usbinfo", count=count,text=f"USB Device num : {log.os_popen('lsusb | wc -l').strip()}\n{os_usbinfo}".strip())
    if flags == "1" : 
        if diff_information(count,folder_path,"usbinfo"):
            log._pr("OS USB Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("OS USB Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")

def osip(flags, folder_path, count):
    echo_dev_info_sleep(flags,count)
    if log.json_get('collect_array',"osip",web='no-log',filename='collect').strip() !='1':return 0
    # filter vir
    nic_name_arry = []
    nic_name_arry_1 = log.os_popen("ls /sys/class/net/ | grep -vi lo | grep -v vir | grep -v veth | grep -vi docker ").strip().split()
    for nic_name in nic_name_arry_1:
        if str(log.os_popen(f'ethtool -i {nic_name} 2>/dev/null| grep -i "CDC Ethernet Device" | wc -l ',flags='no-log')).strip() == "0":
            nic_name_arry.append(nic_name)
    # address：包含以太网接口eth0的物理地址（MAC地址）。
    # carrier：指示以太网接口是否已连接到网络（1表示连接，0表示未连接）。
    # device：指向与以太网接口eth0关联的设备的符号链接。
    # duplex：指示以太网接口eth0的双工模式（全双工或半双工）。
    # flags：列出以太网接口eth0的标志和状态信息，如UP（启用）、BROADCAST（广播）等。
    # ifalias：以太网接口eth0的别名（如果有）。
    # mtu：以太网接口eth0的最大传输单元（Maximum Transmission Unit）大小。
    # operstate：指示以太网接口eth0的操作状态，如UP、DOWN、UNKNOWN等。
    # speed：以太网接口eth0的连接速度。
    na_str = "-"
    print_save_text(flags=flags, folder_path=folder_path, type="osip", count=count,
                    text="[NIC_NAME]".ljust(25) + "[NIC_IPv4]".ljust(25) + "[NIC_MAC]".ljust(20) + "[NIC_MTU]".ljust(
                        15) + "[NIC_Speed]".ljust(15) + "[NIC_State]".ljust(15) + "[NIC_duplex]".ljust(15) + '[NIC_BDF]'.ljust(15)+'[NIC_Node]')
    for nic_name in nic_name_arry:
        nic_ip = log.os_popen(f"ifconfig {nic_name} 2>/dev/null | grep -i 'inet ' | cut -d ' ' -f 10").replace("\n", "")
        if nic_ip == "":
            nic_ip = log.os_popen(f"ifconfig {nic_name} 2>/dev/null | grep -i 'inet ' | awk '{{print $2}}' ").replace("\n","")
            if nic_ip == "": nic_ip = na_str
        nic_mac = log.os_popen(f"cat /sys/class/net/{nic_name}/address 2>/dev/null").replace("\n", "")
        if nic_mac == "": nic_mac = na_str
        nic_mtu = log.os_popen(f"cat /sys/class/net/{nic_name}/mtu 2>/dev/null").replace("\n", "")
        if nic_mtu == "": nic_mtu = na_str
        nic_speed = log.os_popen(f"cat /sys/class/net/{nic_name}/speed 2>/dev/null").replace("\n", "")
        if nic_speed == "-1" or nic_speed == "": nic_speed = na_str
        nic_state = log.os_popen(f"cat /sys/class/net/{nic_name}/operstate 2>/dev/null").replace("\n", "")
        if nic_state == "": nic_state = na_str
        nic_duplex = log.os_popen(f"cat /sys/class/net/{nic_name}/duplex 2>/dev/null").replace("\n", "")
        if nic_duplex == "": nic_duplex = na_str
        nic_bdf = log.os_popen(f"ethtool -i {nic_name} 2>/dev/null| grep bus-info | awk -F': ' '{{print $2}}' ").replace("\n", "")
        if nic_bdf.strip() == "":nic_bdf = na_str
        if nic_bdf == na_str:
            nic_node = na_str
        else:
            nic_node = log.os_popen(f"lspci -vvvs {nic_bdf}  2>/dev/null |grep -i node | cut -d ':' -f 2 | tr -d ' '").replace("\n", "")
            if nic_node.strip()=="":
                nic_node = na_str
        print_save_text(flags=flags, folder_path=folder_path, type="osip", count=count,
                        text=nic_name.ljust(25) + nic_ip.ljust(25) + nic_mac.ljust(20) + nic_mtu.ljust(
                            15) + nic_speed.ljust(
                            15) + nic_state.ljust(15) + nic_duplex.ljust(15)+nic_bdf.ljust(15)+nic_node)
    if flags == "1" : 
        if diff_information(count,folder_path,"osip"):
            print()
            log._pr("OS IP Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            print()
            log._pr("OS IP Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")

def bmcip(flags, folder_path, count):
    if log.json_get('collect_array',"bmcip",web='no-log',filename='collect').strip() !='1':return 0
    echo_dev_info_sleep(flags,count)
    Dedicated_lan_num = log.json_get("Test_Config", "Dedicated_lan_num")
    Share_lan_num = log.json_get("Test_Config", "Share_lan_num")
    log.os_popen(f"ipmitool lan print {str(Dedicated_lan_num).strip()} 2>/dev/null")
    log.os_popen(f"ipmitool lan print {str(Share_lan_num).strip()} 2>/dev/null")
    Dedicated_BMC_IP = log.os_popen(
        f" ipmitool lan print {Dedicated_lan_num} 2>/dev/null | grep 'IP Address' | grep -vi source | awk '{{print $4}}' ").strip()
    Dedicated_BMC_MAC = log.os_popen(
        f"ipmitool lan print {Dedicated_lan_num} 2>/dev/null | grep -i 'mac address' | awk '{{print $4}}' ").strip()
    Dedicated_BMC_IP_Source = log.os_popen(
        f"ipmitool lan print {Dedicated_lan_num} 2>/dev/null | grep -i 'ip address source' | awk '{{print $5}}' ").strip()
    if Dedicated_BMC_IP == "": Dedicated_BMC_IP = "None"
    Share_BMC_IP = log.os_popen(
        f" ipmitool lan print {Share_lan_num} 2>/dev/null | grep 'IP Address' | grep -vi source | awk '{{print $4}}' ").strip()
    if Share_BMC_IP == "": Share_BMC_IP = "None"
    Share_BMC_MAC = log.os_popen(
        f"ipmitool lan print {Share_lan_num} 2>/dev/null | grep -i 'mac address' | awk '{{print $4}}' ").strip()
    Share_BMC_IP_Source = log.os_popen(
        f"ipmitool lan print {Share_lan_num} 2>/dev/null | grep -i 'ip address source' | awk '{{print $5}}' ").strip()
    
    print_save_text(flags=flags, folder_path=folder_path, type="bmcip", count=count,text=f"InterfaceType      BMC_IP            BMC_MAC\nDedicated{Dedicated_BMC_IP_Source}\t{Dedicated_BMC_IP}\t{Dedicated_BMC_MAC}\nShare{Share_BMC_IP_Source}\t{Share_BMC_IP}\t{Share_BMC_MAC}")
    
    if flags == "1" : 
        if diff_information(count,folder_path,"bmcip"):
            log._pr("BMC IP Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("BMC IP Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")
    
def fwinfo(flags, folder_path, count):
    
    if log.json_get('collect_array',"fwinfo",web='no-log',filename='collect').strip() !='1':
        return 0
    # 判断是否为hisi芯片，如果是直接return0
    if log.json_get("BMC_Survival_Config","bmc_chip") != "Hisilicon-Hi1711":
        cpld_version = ""
        try:
            # 32
            device_id = log.os_popen("ipmitool mc info 2>/dev/null | grep -i 'device id' | awk '{{print $4}}'").strip()
            if device_id == "32":
                raw_str = log.os_popen("ipmitool raw 0x0e 0x6f 2>/dev/null").strip()
                for i in range(8):
                    hex_value = raw_str.split()[i]
                    raw = int(hex_value, 16)
                    cpld_version = cpld_version + "".join(chr(raw))
        except:
            cpld_version = "GetFail!"
    else:
        cpld_version = "NA"
        
    BMC_Ver = log.os_popen(''' echo "$(ipmitool mc info 2>/dev/null | grep 'Firmware Revision' | awk '{ print $4 }').$(ipmitool mc info 2>/dev/null | grep -A4 'Aux Firmware Rev Info' | grep -vi 'Firmware' | head -n 4 | awk '{ print $1 }' | sed 's/0x//g' | paste -sd.)" ''').strip()
    Bios_Ver = log.os_popen("dmidecode -s bios-version 2>/dev/null").strip()
    if Bios_Ver == "":Bios_Ver = log.os_popen("dmidecode -t bios | grep -i version | cut -d ':' -f 2").strip()

    Bios_relea_time = log.os_popen("dmidecode -s bios-release-date 2>/dev/null").strip()
    if Bios_relea_time == "":Bios_relea_time = log.os_popen("dmidecode -t bios | grep -i release | cut -d ':' -f 2").strip()
    
    Bios_revision_time = log.os_popen("dmidecode -s bios-revision 2>/dev/null").strip()
    if Bios_revision_time == "":
        Bios_revision_time = log.os_popen("dmidecode -t bios | grep -i Revision | cut -d ':' -f 2").strip()
    try:
        result = log.os_popen( r''' echo -n "$(ipmitool raw 0x0e 0x6f 2>/dev/null | tr -d '\n' | cut -d ' ' -f 22-250)" | xxd -r -p | tr -d '\0' | awk 'BEGIN{RS="REV"; i=1} NR>1 {print "BP" i++ " Version: REV" substr($0,1,17)}' ''',flags='no-log').strip()
        if "Invalid" in result:
            bp_fw = "GetFail!"
        elif result.strip() == '':
            bp_fw = "NA"
        else:
            bp_fw = result
    except:
        bp_fw = "GetFail!"

    print_save_text(flags=flags, folder_path=folder_path, type="fwinfo", count=count,text=f"CPLD.ver : {cpld_version}\nBMC.ver  : {BMC_Ver}\nBIOS.ver : {Bios_Ver}\nBios-ReleaseTime: {Bios_relea_time}\nBios-Revisione: {Bios_revision_time}\nBP_fw    :{bp_fw}")
    
    if flags == "1" : 
        if diff_information(count,folder_path,"fwinfo"):
            log._pr("BMC_Bios_CPLD_FW_Info".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("BMC_Bios_CPLD_FW_Info".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")
    
def meminfo(flags, folder_path, count):
    if log.json_get('collect_array',"meminfo",web='no-log',filename='collect').strip() !='1':return 0
    echo_dev_info_sleep(flags,count)
    print_save_text(flags=flags, folder_path=folder_path, type="meminfo", count=count,
                    text="[Order]".ljust(8) + "[Manufacturer]".ljust(17) + "[PartNumber]".ljust(20) + "[Size]".ljust(
                        8) + "[Volatile_size]".ljust(17) + "[Speed]".ljust(12) + "[Config Speed]".ljust(
                        15) + "[Serial_Number]".ljust(19) + "[Locator]".ljust(13) + "[Bank_Locator]")
    memory_temp_arr = log.os_popen('dmidecode -t memory',flags='no-log').split("Memory Device")[1:]
    order = 0
    for data in memory_temp_arr:
        mem_tmp_arr = []
        mem_tmp_arr.append(order)
        data = data.replace("", "").strip().split("\n")
        for i in data:
            # 5
            if "Manufacturer: " in i:
                tmp = i.replace("Manufacturer: ", "").strip()
                mem_tmp_arr.append(tmp)
            # 6
            if "Serial Number: " in i:
                tmp = i.replace("Serial Number: ", "").strip()
                mem_tmp_arr.append(tmp)
            # 7
            if "Part Number: " in i:
                tmp = i.replace("Part Number: ", "").strip()
                mem_tmp_arr.append(tmp)
            # 4
            if "Speed: " in i and "Configured" not in i:
                tmp = i.replace("Speed: ", "").strip()
                mem_tmp_arr.append(tmp)
            # 1
            if "Size:" in i and "Non-Volatile" not in i and "Volatile Size" not in i and "Cache Size:" not in i and "Logical Size:" not in i:
                tmp = i.replace("Size: ", "").strip()
                mem_tmp_arr.append(tmp)
            # 8
            if "Configured Memory Speed: " in i:
                tmp = i.replace("Configured Memory Speed: ", "").strip()
                mem_tmp_arr.append(tmp)
            # 9
            if "Volatile Size" in i and "Non-" not in i:
                tmp = i.replace("Part Number: ", "").strip().replace("Volatile Size: ", "")
                mem_tmp_arr.append(tmp)
            # 2
            if "Locator: " in i and "Bank" not in i:
                tmp = i.replace("Locator: ", "").strip()
                mem_tmp_arr.append(tmp)
            # 3
            if "Bank Locator:" in i:
                tmp = i.replace("Bank Locator:", "").strip()
                mem_tmp_arr.append(tmp)

        order = mem_tmp_arr[0]
        if mem_tmp_arr[1] == "No Module Installed":
            Manufacturer = "-"
            PartNumber = "-"
            Size = "-"
            Volatile_size = "-"
            Speed = "-"
            Config_Speed = "-"
            Serial_Number = "-"
            print_save_text(flags=flags, folder_path=folder_path, type="meminfo", count=count,
                            text="".ljust(3) + str(order).ljust(7) + Manufacturer.ljust(15) + PartNumber.ljust(
                                21) + Size.ljust(
                                12) + Volatile_size.ljust(12) + Speed.ljust(15) + Config_Speed.ljust(
                                15) + Serial_Number.ljust(15) +mem_tmp_arr[2].ljust(15) + mem_tmp_arr[3])
        else:
            try:
                Manufacturer = mem_tmp_arr[5]
            except:
                Manufacturer = "-"
            try:
                PartNumber = mem_tmp_arr[7]
            except:
                PartNumber = "-"
            try:
                Size = mem_tmp_arr[1]
            except:
                Size = "-"
            try:
                Volatile_size = mem_tmp_arr[9]
            except:
                Volatile_size = "-"
            try:
                Speed = mem_tmp_arr[4]
            except:
                Speed = "-"
            try:
                Config_Speed = mem_tmp_arr[8]
            except:
                Config_Speed = "-"
            try:
                Serial_Number = mem_tmp_arr[6]
            except:
                Serial_Number = "-"
            try:
                Locator = mem_tmp_arr[2]
            except:
                Locator = "-"
            try:
                Bank_Locator = mem_tmp_arr[3]
            except:
                Bank_Locator = "-"
            print_save_text(flags=flags, folder_path=folder_path, type="meminfo", count=count,
                            text="".ljust(3) + str(order).ljust(7) + Manufacturer.ljust(15) + PartNumber.ljust(
                                21) + Size.ljust(
                                12) + Volatile_size.ljust(12) + Speed.ljust(15) + Config_Speed.ljust(
                                15) + Serial_Number.ljust(
                                15) + Locator.ljust(15) + Bank_Locator.ljust(5))
        order += 1

    if flags == "1" : 
        if diff_information(count,folder_path,"meminfo"):
            log._pr("OS Memory ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("OS Memory ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")

def pcieinfo(flags, folder_path, count):
    if log.json_get('collect_array',"pcieinfo",web='no-log',filename='collect').strip() !='1':return 0
    echo_dev_info_sleep(flags,count)
    pci_arry = log.os_popen("lspci 2>/dev/null| grep -ivE 'Bridge|Encryption controller|Non-Essential|iommu|System peripheral' |awk '{print $1}'").strip().split()
    #bak data
    order = 0
    pci_switch = False
    # Huawie project switch slot map
    # [root@localhost sost]# lspci | grep -i 'Broadcom / LSI PCIe Switch management endpoint'
    # 1a:00.0 Serial Attached SCSI controller: Broadcom / LSI PCIe Switch management endpoint (rev b0)
    # 9d:00.0 Serial Attached SCSI controller: Broadcom / LSI PCIe Switch management endpoint (rev b0)
    # [root@localhost sost]# lspci | grep -i 'Broadcom / LSI PCIe Switch management endpoint' | wc -l
    # config -> switch_slot_map_num: 2
    # 逻辑判断是否有PCI switch
    if log.os_popen("lspci | grep -i 'Broadcom / LSI PCIe Switch management endpoint'| grep -vi scsi | wc -l").strip() != "0":
        pci_switch = True
    else:
        if log.os_popen("lspci | grep -i 'PCI bridge: Broadcom' | grep -vi scsi | wc -l").strip() != "0":
            pci_switch = True
        else:
            pci_switch = False

    if pci_switch and flags !='show':
        print_save_text(flags=flags, folder_path=folder_path, type="pcieinfo", count=count,text="[Order]".ljust(10)+"[parent_node]".ljust(15)+"[child_node]".ljust(15)+"[Node]".ljust(10)+"[SN]".ljust(20)+"[PN]".ljust(20)+"[Switch_Slot]".ljust(20)+"[Lnk_Sta]".ljust(45)+"[Subsystem]")
        pci_switch_list = log.os_popen("lspci | grep -i 'PEX890xx PCIe Gen' | grep -i switch | cut -d ' ' -f 1").strip().split()
        if pci_switch_list == []:
            pci_switch_list = log.os_popen("lspci | grep -i 'PCI bridge: Broadcom' | grep -vi scsi | cut -d ' ' -f 1").strip().split()
        
        for switch_bdf in pci_switch_list:
            parent_node_slot = log.os_popen(f"lspci -vvvs {switch_bdf} | grep 'Slot #' | cut -d ',' -f 1 | cut -d '#' -f 2").strip()
            child_node_bdf = log.os_popen(f"lspci -vvvs {switch_bdf.strip()} 2>/dev/null | grep secondary | cut -d ',' -f 2 | cut -d '=' -f 2 ").strip()+':00.0'
            if log.os_popen(f"lspci -vvvs {child_node_bdf.strip()} 2>/dev/null").strip() == "":
                continue
            node = log.os_popen(f"lspci -vvvs {child_node_bdf.strip()} 2>/dev/null| grep -i numa | cut -d ':' -f 2").strip()
            lnk_sta = log.os_popen(f"lspci -vvvs {child_node_bdf.strip()} 2>/dev/null| grep -i LnkSta: | cut -d ':' -f 2").strip()
            if lnk_sta == "":lnk_sta="-"
            try:Subsystem = log.os_popen(f"lspci -vvvs {child_node_bdf.strip()} 2>/dev/null|grep -ie 'Subsystem:' | grep -vi 'Capabilities'").replace("Subsystem:","").strip().split(',')[0]
            except:Subsystem = log.os_popen(f"lspci -vvvs {child_node_bdf.strip()} 2>/dev/null|grep -ie 'Subsystem:' | grep -vi 'Capabilities'").replace("Subsystem:","").strip()
            if Subsystem=="":
                Subsystem = log.os_popen(f"lspci -vvvs {child_node_bdf.strip()} 2>/dev/null| grep -i 'Ethernet controller:' | cut -d ':' -f 3").strip()
                if Subsystem=="":Subsystem="-"
            pci_sn = log.os_popen(f"lspci -vvvs {child_node_bdf.strip()} 2>/dev/null| grep -i 'Serial Number:' | cut -d ':' -f 2").strip()
            if pci_sn == "":pci_sn="-"
            pci_pn = log.os_popen(f"lspci -vvvs {child_node_bdf.strip()} 2>/dev/null| grep -i 'Part Number:' | cut -d ':' -f 2").strip()
            if pci_pn == "":pci_pn="-"
            
            if parent_node_slot == "":
                Switch_Slot = "-"
            else:
                data = json.loads(open(f"/opt/sost/config/switch_slot_map.json","r").read())
                try:
                    Switch_Slot = data['switch_slot'][str(parent_node_slot)].strip()
                except Exception as e:
                    Switch_Slot = "-"
            
            print_save_text(flags=flags, folder_path=folder_path, type="pcieinfo", count=count,text=str(order).ljust(10)+switch_bdf.ljust(15)+child_node_bdf.ljust(15)+node.ljust(10)+pci_sn.ljust(20)+pci_pn.ljust(20)+Switch_Slot.ljust(20)+lnk_sta.ljust(45)+Subsystem)
            order+=1
        # 处理Switch直连设备
        direct_parent_node_bdf = '00:00.0'
        child_node_bdf = log.os_popen(f"lspci -vvvs {direct_parent_node_bdf} | grep Bus: | cut -d ',' -f 2 | cut -d '=' -f 2").strip()+':00.0'
        child_node_pci_info = log.os_popen(f"lspci -vvvs {child_node_bdf.strip()} 2>/dev/null").strip()
        if child_node_pci_info == "":
            return
        node = log.os_popen(f"lspci -vvvs {child_node_bdf.strip()} 2>/dev/null| grep -i numa | cut -d ':' -f 2").strip()
        lnk_sta = log.os_popen(f"lspci -vvvs {child_node_bdf.strip()} 2>/dev/null| grep -i LnkSta: | cut -d ':' -f 2").strip()
        if lnk_sta == "":lnk_sta="-"
        try:Subsystem = log.os_popen(f"lspci -vvvs {child_node_bdf.strip()} 2>/dev/null|grep -ie 'Subsystem:' | grep -vi 'Capabilities'").replace("Subsystem:","").strip().split(',')[0]
        except:Subsystem = log.os_popen(f"lspci -vvvs {child_node_bdf.strip()} 2>/dev/null|grep -ie 'Subsystem:' | grep -vi 'Capabilities'").replace("Subsystem:","").strip()
        if Subsystem=="":
            Subsystem = log.os_popen(f"lspci -vvvs {child_node_bdf.strip()} 2>/dev/null| grep -i 'Ethernet controller:' | cut -d ':' -f 3").strip()
            if Subsystem=="":Subsystem="-"
        pci_sn = log.os_popen(f"lspci -vvvs {child_node_bdf.strip()} 2>/dev/null| grep -i 'Serial Number:' | cut -d ':' -f 2").strip()
        if pci_sn == "":pci_sn="-"
        pci_pn = log.os_popen(f"lspci -vvvs {child_node_bdf.strip()} 2>/dev/null| grep -i 'Part Number:' | cut -d ':' -f 2").strip()
        if pci_pn == "":pci_pn="-"
        Switch_Slot = "Direct"
        print_save_text(flags=flags, folder_path=folder_path, type="pcieinfo", count=count,text=str(order).ljust(10)+direct_parent_node_bdf.ljust(15)+child_node_bdf.ljust(15)+node.ljust(10)+pci_sn.ljust(20)+pci_pn.ljust(20)+Switch_Slot.ljust(20)+lnk_sta.ljust(45)+Subsystem)
    else:
        text = "[Order]".ljust(10)+"[Bus_Addr]".ljust(15)+"[Node]".ljust(10)+"[SN]".ljust(20)+"[PN]".ljust(20)+"[Lnk_Sta]".ljust(45)+"[Subsystem]"
        print_save_text(flags=flags, folder_path=folder_path, type="pcieinfo", count=count,text=text)
        for bus_addr in pci_arry:
            log.os_popen(f"lspci -vvvs {bus_addr.strip()} 2>/dev/null")
            node = log.os_popen(f"lspci -vvvs {bus_addr.strip()} 2>/dev/null| grep -i numa | cut -d ':' -f 2").strip()
            lnk_sta = log.os_popen(f"lspci -vvvs {bus_addr.strip()} 2>/dev/null| grep -i LnkSta: | cut -d ':' -f 2").strip()
            if lnk_sta == "":lnk_sta="-"
            try:Subsystem = log.os_popen(f"lspci -vvvs {bus_addr.strip()} 2>/dev/null|grep -ie 'Subsystem:' | grep -vi 'Capabilities'").replace("Subsystem:","").strip().split(',')[0]
            except:Subsystem = log.os_popen(f"lspci -vvvs {bus_addr.strip()} 2>/dev/null|grep -ie 'Subsystem:' | grep -vi 'Capabilities'").replace("Subsystem:","").strip()
            if Subsystem=="":
                Subsystem = log.os_popen(f"lspci -vvvs {bus_addr.strip()} 2>/dev/null| grep -i 'Ethernet controller:' | cut -d ':' -f 3").strip()
                if Subsystem=="":Subsystem="-"
            pci_sn = log.os_popen(f"lspci -vvvs {bus_addr.strip()} 2>/dev/null| grep -i 'Serial Number:' | cut -d ':' -f 2").strip()
            if pci_sn == "":pci_sn="-"
            pci_pn = log.os_popen(f"lspci -vvvs {bus_addr.strip()} 2>/dev/null| grep -i 'Part Number:' | cut -d ':' -f 2").strip()
            if pci_pn == "":pci_pn="-"
            print_save_text(flags=flags, folder_path=folder_path, type="pcieinfo", count=count,text=str(order).ljust(10)+bus_addr.ljust(15)+node.ljust(10)+pci_sn.ljust(20)+pci_pn.ljust(20)+lnk_sta.ljust(45)+Subsystem)
            order+=1

    if flags == "show":
        return 0
    
    if flags == "1": 
        if diff_information(count,folder_path,"pcieinfo"):
            log._pr("OS Pcie ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("OS Pcie ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")
            
def pcieslot(flags, folder_path, count):
    if log.json_get('collect_array',"pcieslot",web='no-log',filename='collect').strip() !='1':return 0
    echo_dev_info_sleep(flags,count)
    #bak data
    log.os_popen("dmidecode -t slot")
    # Order
    order_num = 0
    handle_num = log.os_popen("dmidecode -t slot | grep -i Handle | cut -d ' ' -f 2").strip().replace(",","").split()
    print_save_text(flags=flags, folder_path=folder_path, type="pcieslot", count=count,text="[Order]".ljust(10)+"[BUS_Addr]".ljust(20)+"[Designation]".ljust(30)+"[Type]".ljust(40)+"[Current Usage]".ljust(20)+"[Length]".ljust(15)+"[Node]")
    for handle in handle_num:
        handle = str(handle).strip()
        Designation = log.os_popen(f"dmidecode -H {handle}| grep -i Designation | cut -d ':' -f 2").strip()
        if Designation=="":Designation="-"
        Type = log.os_popen(f"dmidecode -H {handle} | grep -i type: | cut -d ':' -f 2").strip()
        if Type=="":Type="-"
        Current_Usage = log.os_popen(f"dmidecode -H {handle} | grep -i 'Current Usage' | cut -d ':' -f 2").strip()
        if Current_Usage=="":Current_Usage="-"
        Bus_Address = log.os_popen(f"dmidecode -H {handle} | grep -i 'Bus Address: '").replace("Bus Address: ","").strip()
        if Bus_Address=="":Bus_Address="-"
        Length = log.os_popen(f"dmidecode -H {handle} | grep -i 'Length: '").strip().replace("Length: ","")
        if Length=="":Length="-"
        node = "-"
        if Bus_Address.strip() == "":
            node = "-"
        else:
            node = log.os_popen(f"lspci -vvvs {Bus_Address} 2>/dev/null| grep -i node | cut -d ':' -f 2").strip()
            if node == "":node="-"
        print_save_text(flags=flags, folder_path=folder_path, type="pcieslot", count=count,text=str(order_num).ljust(10)+Bus_Address.ljust(20)+Designation.ljust(30)+Type.ljust(40)+Current_Usage.ljust(20)+Length.ljust(15)+node)
        order_num+=1
    
    if flags == "1" : 
        if diff_information(count,folder_path,"pcieslot"):
            log._pr("OS DMI Slot Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("OS DMI Slot Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")

def psuinfo_ipmitool_fru(flags, path, count):

    # check dmidecode psu info
    log.os_popen("dmidecode -t 39")
    # retry 
    retry_get_ipmi_info('ipmitool fru 2>/dev/null','OS PSU Fru Info IPMI')
    # save ipmitool fru info
    log.os_popen("ipmitool fru 2>/dev/null > /tmp/sost_tmp/sost_tmp && cat /tmp/sost_tmp/sost_tmp")

    if log.os_popen("du -a /tmp/sost_tmp/sost_tmp | awk '{{print $1}}'").strip() == "0":
        log._error("ipmitool fru Not Data! ")

    # err : grep : (standard input) : binary file matches
    # resolvent  : tmp save psu info
    print_save_text(flags=flags, folder_path=path, type="psuinfo", count=count,
                    text="[PSU_NAME]".ljust(12) + "[PSU_Manufacturer]".ljust(22) + "[PSU_Part_Number]".ljust(
                        20) + "[PSU_Version]".ljust(15) + "[PSU_Serial]".ljust(15))

    psu_list = log.os_popen("cat /tmp/sost_tmp/sost_tmp |grep -i 'FRU Device Description : PSU' | awk '{print $5}'").strip().split()

    for psu_name in psu_list:
        # Manufacturer
        Manufacturer = log.os_popen(
            f"cat /tmp/sost_tmp/sost_tmp | grep -A5 {psu_name} | grep -i 'Product Manufacturer' | awk '{{print $4,$5,$6}}'").strip()
        # Name
        Name = log.os_popen(
            f"cat /tmp/sost_tmp/sost_tmp | grep -A5 {psu_name} | grep -i 'Product Name' | awk '{{print $4}}'").strip()
        # Part_Number
        Part_Number = log.os_popen(
            f"cat /tmp/sost_tmp/sost_tmp | grep -A5 {psu_name} | grep -i 'Product Part Number' | awk '{{print $5}}'").strip()
        # Version
        Version = log.os_popen(f"cat /tmp/sost_tmp/sost_tmp | grep -A5 {psu_name} | grep -i 'Version' | awk '{{print $4}}'").strip()
        # Serial
        Serial = log.os_popen(f"cat /tmp/sost_tmp/sost_tmp | grep -A5 {psu_name} | grep -i 'Serial' | awk '{{print $4}}'").strip()
        print_save_text(flags=flags, folder_path=path, type="psuinfo", count=count,
                        text=Name.ljust(19) + Manufacturer.ljust(23) + Part_Number.ljust(18) + Version.ljust(
                            9) + Serial.ljust(11))
    log.os_popen("rm -rf /tmp/sost_tmp/sost_tmp")

    if flags == "1" : 
        if diff_information(count,path,"psuinfo"):
            log._pr("OS PSU FRU Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("OS PSU FRU Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")

def psuinfo_dmidecode_39(flags, path, count):
    # save dmidecode -t 39 -> sost_tmp
    log.os_popen("dmidecode -t 39 > /tmp/sost_tmp/sost_tmp")
    # save sost_tmp info
    log.os_popen("cat /tmp/sost_tmp/sost_tmp")
    # save ipmitool fru psu info
    # log.os_popen("ipmitool fru 2>/dev/null")
    # title
    print_save_text(flags=flags, folder_path=path, type="psuinfo", count=count,
                    text="[PSU_NUM]".ljust(10) + "[PSU_Manufacturer]".ljust(20) + "[PSU_Serial_Number]".ljust(
                        20) + "[PSU_Model_Part_Number]".ljust(25) + "[PSU_Revision]".ljust(
                        16) + "[PSU_Max_Power_Capacity]".ljust(
                        25) + "[PSU_Status]".ljust(14) + "[PSU_Type]".ljust(12) + "[PSU_Hot_Replaceable]")
    for i in log.os_popen("cat /tmp/sost_tmp/sost_tmp | grep -i Location: | cut -d ':' -f 2").strip().split():
        # PSU NUM
        psu_num = str(i)
        # PSU NAME
        psu_name = log.os_popen(f"dmidecode -t 39 | grep -A16 {i} | grep -i Name: | cut -d':' -f 2").strip().replace("\n","")
        # PSU Manufacturer
        psu_Manufacturer = log.os_popen(f"dmidecode -t 39 | grep -A16 {i} | grep -i Manufacturer:  | cut -d':' -f 2").strip().replace("\n", "")
        # PSU Serial Number
        psu_seri_number = log.os_popen(f"dmidecode -t 39 | grep -A16 {i} | grep -i 'Serial Number:'  | cut -d':' -f 2").strip().replace("\n", "")
        # PSU Model Part Number
        psu_model_part_number = log.os_popen(f"dmidecode -t 39 | grep -A16 {i} | grep -i 'Model Part Number:'  | cut -d':' -f 2").strip().replace("\n","")
        # PSU Revision
        psu_revision = log.os_popen(f"dmidecode -t 39 | grep -A16 {i} | grep -i Revision:  | cut -d':' -f 2").strip().replace("\n", "")
        # PSU Max Power Capacity
        psu_max_power_capacity = log.os_popen(f"dmidecode -t 39 | grep -A16 {i} | grep -i 'Max Power Capacity:' | cut -d':' -f 2").strip().replace("\n","")
        # PSU Status
        psu_status = log.os_popen(f"dmidecode -t 39 | grep -A16 {i} | grep -i Status  | cut -d':' -f 2 | cut -d ' ' -f 3").strip().replace("\n", "")
        # PSU Type
        psu_type = log.os_popen(f"dmidecode -t 39 | grep -A16 {i} | grep -i Type: | cut -d':' -f 2").strip().replace("\n","")
        # PSU Hot Replaceable
        psu_hot_repleaceable = log.os_popen(f"dmidecode -t 39 | grep -A16 {i} | grep -i 'Hot Replaceable: ' | cut -d':' -f 2").strip().replace("\n", "")
        print_save_text(flags=flags, folder_path=path, type="psuinfo", count=count,
                        text=psu_num.ljust(11) + psu_Manufacturer.ljust(20) + psu_seri_number.ljust(
                            22) + psu_model_part_number.ljust(23) + psu_revision.ljust(
                            20) + psu_max_power_capacity.ljust(22) + psu_status.ljust(9) + psu_type.ljust(
                            21) + psu_hot_repleaceable)
    log.os_popen("rm -rf /tmp/sost_tmp/sost_tmp")
    
    if flags == "1" : 
        if diff_information(count,path,"psuinfo"):
            log._pr("OS PSU Dmi Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("OS PSU Dmi Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")

def psuinfo(flags, path, count):
    if log.json_get('collect_array',"psuinfo",web='no-log',filename='collect').strip() !='1':return 0
    echo_dev_info_sleep(flags,count)
    if str(log.os_popen("dmidecode -t 39 | grep -i 'Max Power Capacity' | wc -l",flags='no-log').strip()) == "0":
        psuinfo_ipmitool_fru(flags, path, count)
    else:
        psuinfo_dmidecode_39(flags, path, count)

def cpu_info(flags, folder_path, count):
    if log.json_get('collect_array',"cpuinfo",web='no-log',filename='collect').strip() !='1':return 0
    echo_dev_info_sleep(flags,count)
    cpu_model_name = log.os_popen("cat /proc/cpuinfo  | grep -i 'model name' | uniq -c").strip()
    cpu_vendor_id = log.os_popen("cat /proc/cpuinfo | grep -i vendor_id | uniq -c").strip()
    cpu_lscpu_info = log.os_popen("lscpu",flags='no-log').strip()
    print_save_text(flags=flags, folder_path=folder_path, type="cpuinfo", count=count,text=cpu_model_name + "\n" + cpu_vendor_id + "\n" + cpu_lscpu_info + "\n")
    
    if flags == "1" : 
        if diff_information(count,folder_path,"cpuinfo"):
            log._pr("OS CPU Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("OS CPU Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")

def dmesg(flags, folder_path, count):
    if log.json_get('collect_array',"dmesg",web='no-log',filename='collect').strip() !='1':return 0
    if flags == "0" or flags == "2": return 0
    print_save_text(flags=flags, folder_path=folder_path, type="dmesg", count=count, text=log.os_popen("dmesg",flags='no-log'))
    if flags == "1" : 
        if diff_information(count,folder_path,"dmesg"):
            log._pr("OS dmesg Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("OS dmesg Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")


def ipmi_sensor(flags, folder_path, count):
    if log.json_get('collect_array',"bmcsensor",web='no-log',filename='collect').strip() !='1':return 0
    if flags == "0" or flags == "2": return 0

    retry_get_ipmi_info('ipmitool sensor list 2>/dev/null','BMC IPMI Sensor')

    print_save_text(flags=flags, folder_path=folder_path, type="bmcsensor", count=count,text=log.os_popen("ipmitool sensor list 2>/dev/null"))
    
    if flags == "1" : 
        if diff_information(count,folder_path,"bmcsensor"):
            log._pr("BMC IPMI Sensor ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("BMC IPMI Sensor ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")

def ipmi_sensor_data(flags, folder_path, count):
    if log.json_get('collect_array',"bmcsensor_data",web='no-log',filename='collect').strip() !='1':return 0
    if flags == "0" or flags == "2": return 0
    ipmi_sensor_data_folder = f"{folder_path}/system_info/bmcsensor_data"
    # create ipmi_sensor_data_folder 
    if not os.path.exists(ipmi_sensor_data_folder):log.os_run(f"mkdir -p {ipmi_sensor_data_folder}")

    for title in log.os_popen(f"cat {folder_path}/system_info/bmcsensor/bmcsensor_{count}.txt | cut -d '|' -f 1 ",flags='no-log').split():
        log.os_run(f"cat {folder_path}/system_info/bmcsensor/bmcsensor_{count}.txt | grep -i '{title}' | cut -d '|' -f 2  >> {folder_path}/system_info/bmcsensor_data/{title}.txt ",flags='no-log')
    if flags == "1" : 
        if diff_information(count,folder_path,"bmcsensor_data"):
            log._pr("BMC IPMI Sensor Data ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("BMC IPMI Sensor Data ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")

def ipmi_sel_log(flags, folder_path, count):
    if log.json_get('collect_array',"bmclog",web='no-log',filename='collect').strip() !='1':return 0
    if flags == "0" or flags == "2": return 0

    result = log.os_popen("ipmitool sel elist 2>/dev/null").strip()
    if result == "":
        if flags == "1": log._pr("BMC IPMI SEL ".ljust(40) + "\033[33m[Fail]\033[0m   \033[33m[Fail]\033[0m")
        time.sleep(3)
    
    print_save_text(flags=flags, folder_path=folder_path, type="bmclog", count=count,text=result)

    if flags == "1" : 
        if diff_information(count,folder_path,"bmclog"):
            log._pr("BMC IPMI SEL ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("BMC IPMI SEL ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")

def bmc_sdre_info(flags, folder_path, count):
    if log.json_get('collect_array',"bmcsdre",web='no-log',filename='collect').strip() !='1':return 0
    if flags == "0" or flags == "2": return 0

    retry_get_ipmi_info('ipmitool sdr elist 2>/dev/null','BMC SDR info ')

    print_save_text(flags=flags, folder_path=folder_path, type="bmcsdre", count=count,
                    text=log.os_popen("ipmitool sdr elist 2>/dev/null"))
    if flags == "1" : 
        if diff_information(count,folder_path,"bmcsdre"):
            log._pr("BMC SDRe info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("BMC SDRe info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")

def bmc_sdr_info(flags, folder_path, count):
    if log.json_get('collect_array',"bmcsdr",web='no-log',filename='collect').strip() !='1':return 0
    if flags == "0" or flags == "2": return 0

    retry_get_ipmi_info('ipmitool sdr list 2>/dev/null',"BMC SDR info ")

    print_save_text(flags=flags, folder_path=folder_path, type="bmcsdr", count=count,
                    text=log.os_popen("ipmitool sdr list 2>/dev/null"))
    if flags == "1" : 
        if diff_information(count,folder_path,"bmcsdr"):
            log._pr("BMC SDR info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("BMC SDR info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")

def os_disk_info_1(flags, folder_path, count):
    # judgment disk
    # remove dm dm-1 dm-2 dm-3
    _disk_num = log.os_popen('ls /sys/block/ | grep -v dm | wc -l ').strip().replace("\n", "")
    _disk_arry = log.os_popen('ls /sys/block/ | grep -v dm').strip().replace("\n", "")
    print_save_text(flags=flags, folder_path=folder_path, type="hddinfo", count=count,
                    text="-" * 120 + "\n" + f"Sys_disk_num  : {_disk_num}\nSys_disk_arry : {_disk_arry}" + "\n" + "-" * 120)
    # ------------------------------------------------------------------------NVMe------------------------------------------------------------------------
    if not log.os_popen("nvme list | grep -i /dev/nvme | awk '{{print $1}}'") == "":
        print_save_text(flags=flags, folder_path=folder_path, type="hddinfo", count=count,
                        text="[Order]".ljust(10) + "[Disk_Name]".ljust(16) + "[Size]".ljust(8) + "[Ns]".ljust(
                            5) + "[Node]".ljust(
                            8) + "[CPUs]".ljust(10) + "[Health]".ljust(11) + "[Pcie_bus]".ljust(
                            25) + "[LnkSta]".ljust(39) + "[SN]".ljust(20) + "[Model]")
        nvme_list = log.os_popen("nvme list | grep -i /dev/nvme | awk '{{print $1}}'").replace("/dev/", "").strip().split("\n")
        # 增加无硬盘退出不报错
        if len(nvme_list) == 0: log._pr("NVMe Disk Not Found!")
        disk_num = 0

        def strings_judeging(text):
            if text.strip()=="":
                return "NA"
            else:
                return text

        for nvme_name in nvme_list:
            try:
                nvme_SN = strings_judeging(log.os_popen(f"nvme list | grep -i {nvme_name} 2>/dev/null| awk '{{print $2}}'").strip())
                if "/dev/" in nvme_SN:nvme_SN = strings_judeging(log.os_popen(f"nvme list 2>/dev/null| grep -i {nvme_name} | awk '{{print $3}}'").strip())
                nvme_Model = strings_judeging(log.os_popen(f"smartctl -i /dev/{nvme_name} 2>/dev/null| grep -i 'Model Number'").split(":")[1].strip())
                nvme_Namespace = strings_judeging(log.os_popen(f"nvme id-ns /dev/{nvme_name} 2>/dev/null| grep -i namespace | awk '{{print $4}}'").strip().replace(":", ""))
                try:nvme_Pciebus = strings_judeging(log.os_popen(f"nvme list-subsys 2>/dev/null| grep -i {nvme_name.replace('n1', '')} | awk '{{print $4}}' ").strip().split()[0])
                except:nvme_Pciebus = 'GetFail!'
                nvme_Node = strings_judeging(log.os_popen(f"lspci -vvvs {nvme_Pciebus} 2>/dev/null | grep -i node |awk '{{print $3}}'").strip())
                nvme_lnksta = strings_judeging(log.os_popen(f"lspci -vvvs {nvme_Pciebus} 2>/dev/null | grep -i 'lnksta:'").strip().replace('LnkSta:', ""))
                nvme_cpus = strings_judeging(log.os_popen(f"numactl -H | grep -i 'node {nvme_Node} cpus' ").replace(f"node {nvme_Node} cpus:", "")).strip().split()
                try:nvme_cpus = str(nvme_cpus[0] + "-" + nvme_cpus[-1])
                except:nvme_cpus = "GetFail!"
                nvme_health = strings_judeging(log.os_popen(f"smartctl -H /dev/{nvme_name} | grep -i result | awk '{{print $6}}'").strip())
                nvme_Size = strings_judeging(log.os_popen(fr"smartctl -i /dev/{nvme_name} | grep -i 'Total NVM Capacity:' | awk 'match($0, /\[([^][]+)\]/, arr) {{print arr[1]}}' ").strip())
                print_save_text(flags=flags, folder_path=folder_path, type="hddinfo", count=count,
                                text="".ljust(3) + str(disk_num).ljust(9) + nvme_name.ljust(14) + nvme_Size.ljust(
                                    10) + nvme_Namespace.ljust(6) + nvme_Node.ljust(6) + nvme_cpus.ljust(
                                    11) + nvme_health.ljust(9) + nvme_Pciebus.ljust(13) + nvme_lnksta.ljust(
                                    45) + nvme_SN.ljust(23) + nvme_Model.ljust(25))
            except:
                log.tips(f"NvmeDisk.GetInfo.Err DiskName -> {nvme_name}  func : os_disk_info ")
            finally:
                disk_num += 1
    else:
        log._pr("Not Found NVMe Disk!")
    # ------------------------------------------------------------------------NVMe------------------------------------------------------------------------

    # ------------------------------------------------------------------------SATA------------------------------------------------------------------------
    # Globalvalue
    contrast_result = []
    lsblk_arr = log.os_popen("lsblk -o NAME,HCTL,VENDOR |  grep -vE 'BROADCOM|nvme|├─|└─|NAME|HCTL|media|USB' | awk '{{print $1}}' 2> /dev/null").strip()
    if lsblk_arr == "":
        log._pr("Not Found SATA Disk!")
    else:
        for i in lsblk_arr.split():
            # if "media_change" in log.os_popen(f"cat /sys/block/{str(i).replace('/dev/', '')}/events 2>/dev/null"):
            #     continue
            # else:
            disk_name = str(i).replace('/dev/', '')
            if disk_name in lsblk_arr:
                contrast_result.append(disk_name)
            else:
                continue
        # Raid
        print_save_text(flags=flags, folder_path=folder_path, type="hddinfo", count=count,
                        text='[Order]'.ljust(8) + "[Disk_Name]".ljust(12) + "[Size]".ljust(
                            9) + "[Inches]".ljust(
                            7) + "[Rotation_Rate]".ljust(16) + "[DiskType]".ljust(11) + "[Speed]".ljust(
                            9) + "[SATA_Ver]".ljust(
                            11) + "[Fireware]".ljust(15) + "[SerialNum]".ljust(25) + "[Dev_Model]")
        disk_num = 0
        for sata_disk in contrast_result:
            sata_collect_info_tmp = sata_collect_info(sata_disk)
            print_save_text(flags=flags, folder_path=folder_path, type="hddinfo", count=count,
                            text="".ljust(3) + str(disk_num).ljust(8) + sata_disk.ljust(11) + sata_collect_info_tmp[
                                1].ljust(7) + sata_collect_info_tmp[0].ljust(7) + sata_collect_info_tmp[4].ljust(12) +
                                 sata_collect_info_tmp[5].ljust(13) + sata_collect_info_tmp[7].ljust(10) +
                                 sata_collect_info_tmp[8].ljust(11) + sata_collect_info_tmp[9].ljust(11) +
                                 sata_collect_info_tmp[6].ljust(14) + sata_collect_info_tmp[3].ljust(22) +
                                 sata_collect_info_tmp[2].ljust(5))
            disk_num = disk_num + 1
        if flags == "1" : log._pr("OS HDD Info ".ljust(40) + "\033[32m[Pass]\033[0m")

def os_disk_info(flags, folder_path, count):
    if log.json_get('collect_array',"hddinfo",web='no-log',filename='collect').strip() !='1':return 0
    echo_dev_info_sleep(flags,count)
    try:
        _disk_num = log.os_popen('ls /sys/block/ | grep -v dm | grep -vi loop | wc -l ').strip().replace("\n", "")
        _disk_arry = log.os_popen('ls /sys/block/ | grep -v dm | grep -vi loop').strip().replace("\n", "")
        print_save_text(flags=flags, folder_path=folder_path, type="hddinfo", count=count,text="-" * 110 + "\n" + f"Sys_disk_num  : {_disk_num}\nSys_disk_arry : {_disk_arry}\n"+'-'* 110+'\n>> NVMe Disk Info <<\n'+'-'*110)
        nvme_list_arry = log.os_popen('ls /sys/block/ | grep -i nvme').strip().split()
        a = 0
        print_save_text(flags=flags, folder_path=folder_path, type="hddinfo", count=count,text='[Order]'.ljust(10)+'[NAME]'.ljust(15)+'[MODEL]'.ljust(35)+'[SERIAL]'.ljust(20)+'[REV]'.ljust(10)+'[SIZE]'.ljust(9)+'[Format]')
        for nvme_name in nvme_list_arry:
            if nvme_name.strip() == '':continue
            nvme_model = log.os_popen(f'cat /sys/block/{nvme_name.strip()}/device/model 2>/dev/null').strip()
            if nvme_model == "":nvme_model = "-"
            nvme_serial = log.os_popen(f'cat /sys/block/{nvme_name.strip()}/device/serial 2>/dev/null').strip()
            if nvme_serial == "":nvme_serial = "-"
            nvme_rev = log.os_popen(f'cat /sys/block/{nvme_name.strip()}/device/firmware_rev 2>/dev/null').strip()
            if nvme_rev == "":nvme_rev = "-"
            nvme_size = log.os_popen(f'''lsblk -o NAME,SIZE | grep '{nvme_name.strip()} ' | awk '{{print $2}}' ''').strip()
            if nvme_size == "":nvme_size = "-"
            nvme_TRAN = log.os_popen(f'cat /sys/block/{nvme_name.strip()}/device/transport 2>/dev/null').strip()
            if nvme_TRAN == "":nvme_TRAN = "-"
            nvme_format = log.os_popen(f''' lsblk -o NAME,PHY-SEC | grep '{nvme_name.strip()} ' | awk '{{print $2}}' ''').strip()
            if nvme_format == "":nvme_format = "-"
            print_save_text(flags=flags, folder_path=folder_path, type="hddinfo", count=count,text=str(a).ljust(10)+nvme_name.ljust(15)+nvme_model.ljust(35)+nvme_serial.ljust(20)+nvme_rev.ljust(10)+nvme_size.ljust(9)+nvme_format+"B")
            a+=1
    except:
        log._error('os_disk_info -> NVMe Disk Info getFail!')
    try:
        print_save_text(flags=flags, folder_path=folder_path, type="hddinfo", count=count,text='-'*110+'\n>> SATA Disk Info <<\n'+'-'*110)
        print_save_text(flags=flags, folder_path=folder_path, type="hddinfo", count=count,text='[Order]'.ljust(15)+'[NAME]'.ljust(12)+'[TYPE] [MODEL]'.ljust(24)+'[SERIAL]'.ljust(15)+'[REV_][SIZE][TRAN]')
        disk_info_arry = log.os_popen("lsblk -o NAME,TYPE,MODEL,SERIAL,REV,SIZE,TRAN | grep -i sd | grep -viE 'nvme|loop|sr' ").strip()
        a = 0
        if disk_info_arry != '':
            for disk_line in disk_info_arry.split('\n'):
                print_save_text(flags=flags, folder_path=folder_path, type="hddinfo", count=count,text=str(a).ljust(15)+disk_line.ljust(25))
                a+=1
    except:
        log._error('os_disk_info_2() -> SATA Disk Info getFail!')
    
    if flags == "1" : 
        if diff_information(count,folder_path,"hddinfo"):
            log._pr("OS HDD Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("OS HDD Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")

# backboard info collect  IPMI fru
def backboard_info(flags, folder_path, count):
    if log.json_get('collect_array',"backboar",web='no-log',filename='collect').strip() !='1':return 0
    echo_dev_info_sleep(flags,count)

    log.os_run("ipmitool fru > /tmp/sost_tmp/sost_tmp")
    log.os_run('cat /tmp/sost_tmp/sost_tmp')

    if log.os_popen("cat /tmp/sost_tmp/sost_tmp 2>/dev/null| grep 'FRU Device Description :' | grep BP | wc -l").strip()=="0":
        if flags == "1" or flags == "0":
            log._pr("BMC Backboard Info collect WARN!".ljust(40) + "\033[33m[Warn]\033[0m   \033[33m[Warn]\033[0m")
            print_save_text(flags=flags, folder_path=folder_path, type="backboard", count=count,text="BP_INFO : NA")
            return 0

    title_num = log.os_popen("cat /tmp/sost_tmp/sost_tmp | grep 'FRU Device Description :' | grep BP | cut -d ':' -f 2 | cut -d ' ' -f 2 | wc -l ").strip()
    print_save_text(flags=flags, folder_path=folder_path, type="backboard", count=count,text=f"fru backboard title num : {title_num}")


    # if log.os_popen("ipmitool fru 2>/dev/null| grep 'FRU Device Description :' | grep BP | cut -d ':' -f 2 | cut -d ' ' -f 2 | wc -l").strip()=="0":
    #     if flags == "1" or flags == "0":
    #         log._pr("BMC Backboard Info collect WARN!".ljust(40) + "\033[33m[Warn]\033[0m   \033[33m[Warn]\033[0m")
    #         print_save_text(flags=flags, folder_path=folder_path, type="backboard", count=count,text="BP_INFO : NA")
    #         return 0


    # print_save_text(flags=flags, folder_path=folder_path, type="backboard", count=count,
    #                 text="[BP_NAME]".ljust(30) + "[BP_Mfg_Date]".ljust(30) + "[BP_Mfg]".ljust(
    #                     30) + "[BP_Product]".ljust(30) + "[BP_Serial]".ljust(30) + "[BP_Part_Number]".ljust(
    #                     30) + "[BP_Extra]")
    # log.os_run("ipmitool fru > /tmp/sost_tmp/sost_tmp")
    # log.os_run('cat /tmp/sost_tmp/sost_tmp')
    # # 判断FRU中是否有BP信息
    
    # for bp_title in log.os_popen("cat /tmp/sost_tmp/sost_tmp | grep 'FRU Device Description :' | grep BP | cut -d ':' -f 2 | cut -d ' ' -f 2").strip().split():
    #     if log.os_popen(f"cat /tmp/sost_tmp/sost_tmp | grep -vi unknown | grep -A1 ' {bp_title} ' | tail -n 1").strip().replace("\n", "") == "":
    #         continue
    #     bp_name = bp_title

    #     bp_mfg_date = log.os_popen(
    #         f"cat /tmp/sost_tmp/sost_tmp | grep -A7 {bp_title} | grep -i 'mfg date' | cut -d ':' -f 2").replace("\n", "")
    #     if bp_mfg_date == "": var = bp_mfg_date == "-"

    #     bp_mfg = log.os_popen(
    #         f"cat /tmp/sost_tmp/sost_tmp | grep -A7 {bp_title} | grep -i 'mfg' | grep -vi date | cut -d ':' -f 2").replace("\n",
    #                                                                                                               "")
    #     if bp_mfg == "": bp_mfg == "-"
    #     bp_Product = log.os_popen(
    #         f"cat /tmp/sost_tmp/sost_tmp | grep -A7 {bp_title} | grep -i 'Product' | cut -d ':' -f 2").replace("\n", "")
    #     if bp_Product == "": bp_Product == "-"

    #     bp_Serial = log.os_popen(f"cat /tmp/sost_tmp/sost_tmp | grep -A7 {bp_title} | grep -i 'Serial' | cut -d ':' -f 2").replace(
    #         "\n", "")
    #     if bp_Serial == "": bp_Serial == "-"

    #     bp_Part_Number = log.os_popen(
    #         f"cat /tmp/sost_tmp/sost_tmp | grep -A7 {bp_title} | grep -i 'Part Number' | cut -d ':' -f 2").replace("\n", "")
    #     if bp_Part_Number == "": bp_Part_Number == "-"

    #     bp_Extra = log.os_popen(f"cat /tmp/sost_tmp/sost_tmp | grep -A7 {bp_title} | grep -i 'Extra' | cut -d ':' -f 2").replace(
    #         "\n", "")
    #     if bp_Extra == "": bp_Extra == "-"

    #     print_save_text(flags=flags, folder_path=folder_path, type="backboard", count=count,
    #                     text=bp_name.ljust(30) + bp_mfg_date.ljust(30) + bp_mfg.ljust(30) + bp_Product.ljust(
    #                         30) + bp_Serial.ljust(30) + bp_Part_Number.ljust(30) + bp_Extra)
    # log.os_popen("cat /tmp/sost_tmp/sost_tmp")
    # log.os_popen("rm -rf /tmp/sost_tmp/sost_tmp")
    
    if flags == "1" : 
        if diff_information(count,folder_path,"backboard"):
            log._pr("BMC Backboard Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("BMC Backboard Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")

# Mega storcli collect raid info
def storinfo(flags, folder_path, count):

    if log.json_get('collect_array',"storinfo",web='no-log',filename='collect').strip() !='1':return 0
    if log.os_popen("lspci | grep -i sas | grep -v usb").strip() == "":return 0
    if not os.path.exists("/opt/MegaRAID/storcli/storcli64"):
        print_save_text(flags=flags, folder_path=folder_path, type="storinfo", count=count, text="Storcli64 not Found!")
        if flags == "1" :
            log._pr("OS Storcli64 Not Found!".ljust(40) + "\033[33m[Warn]\033[0m   \033[33m[Warn]\033[0m")
            return 0
    else:

        # controller num 
        controller_num = log.os_popen("/opt/MegaRAID/storcli/storcli64 /call show | grep -i controller | grep -vi time | cut -d '=' -f 2 | tr -d ' '",flags='no-log').strip().split()
        if controller_num == []:
            print_save_text(flags=flags, folder_path=folder_path, type="storinfo", count=count, text="Storcli64 Controller Not Found!")
            if flags == "1" :
                log._pr("OS Storcli64 Controller Not Found!".ljust(40) + "\033[33m[Warn]\033[0m   \033[33m[Warn]\033[0m")
                return 0
        
        command = '/opt/MegaRAID/storcli/storcli64'

        for ctrl in controller_num:
            print_save_text(flags=flags, folder_path=folder_path, type="storinfo", count=count, text="-"*40+f"\nController".ljust(15)+"Product Name".ljust(30)+'Serial Number'.ljust(20)+'BDF'.ljust(20)+'FW'.ljust(20)+'Physical Drives')
            raid_product_name = log.os_popen(f"{command} /c{ctrl} show | grep 'Product Name' | cut -d '=' -f 2",flags='no-log').strip()
            raid_serial_number = log.os_popen(f"{command} /c{ctrl} show | grep 'Serial Number' | cut -d '=' -f 2",flags='no-log').strip()
            raid_bdf = log.os_popen(f"{command} /c{ctrl} show | grep 'PCI Address' | cut -d '=' -f 2",flags='no-log').strip()
            raid_fw = log.os_popen(f"{command} /c{ctrl} show | grep 'FW Version' | cut -d '=' -f 2",flags='no-log').strip()
            raid_phy_num = log.os_popen(f"{command} /c{ctrl}/eall/sall show all| grep -i 'physical sector size' | wc -l",flags='no-log').strip()
            raid_phy_dev_list = log.os_popen(f"{command} /c{ctrl}/eall/sall show all | grep Drive | grep State | awk '{{print $2}}'",flags='no-log').strip().replace(":",",").split()
            print_save_text(flags=flags, folder_path=folder_path, type="storinfo", count=count, text=ctrl.ljust(14)+raid_product_name.ljust(30)+raid_serial_number.ljust(20)+raid_bdf.ljust(20)+raid_fw.ljust(20)+raid_phy_num)
            if raid_phy_dev_list == ['']:continue
            print_save_text(flags=flags, folder_path=folder_path, type="storinfo", count=count,text="-"*40+"\nController".ljust(16)+"PhySlot".ljust(15)+"SN".ljust(15)+"ModelNumber".ljust(25)+"FW".ljust(10)+"RawSize".ljust(15)+"DevSpeed".ljust(10)+"LinkSpeed".ljust(15)+"State".ljust(10)+"Type".ljust(10)+"Interface")
            for disk in raid_phy_dev_list:
                disk_sn = log.os_popen(f"{command} {disk} show all | grep 'SN = ' | cut -d '=' -f 2 | tr -d ' '").strip()
                disk_model_number = log.os_popen(f"{command} {disk} show all | grep 'Model Number' | cut -d '=' -f 2 | tr -d ' '").strip()
                disk_fw = log.os_popen(f"{command} {disk} show all | grep 'Firmware Revision' | cut -d '=' -f 2 | tr -d ' '").strip()
                disk_raw_size = log.os_popen(f"{command} {disk} show all | grep 'Raw size' | cut -d '=' -f 2 | cut -d '[' -f 1").strip()
                disk_DevSpeed = log.os_popen(f"{command} {disk} show all | grep 'Device Speed' | cut -d '=' -f 2 | tr -d ' '").strip()
                disk_linkSpeed = log.os_popen(f"{command} {disk} show all | grep 'Link Speed' | cut -d '=' -f 2 | tr -d ' '").strip()
                disk_state = log.os_popen(f"{command} {disk} show all | sed -n '14p' | awk '{{print $3}}'").strip()
                disk_Type = log.os_popen(f"{command} {disk} show all | sed -n '14p'|awk '{{print $8}}' ").strip()
                disk_Inter = log.os_popen(f"{command} {disk} show all | sed -n '14p' | awk '{{print $7}}' ").strip()

                print_save_text(flags=flags, folder_path=folder_path, type="storinfo", count=count,text=ctrl.ljust(15)+disk.ljust(15)+disk_sn.ljust(15)+disk_model_number.ljust(25)+disk_fw.ljust(10)+disk_raw_size.ljust(15)+disk_DevSpeed.ljust(10)+disk_linkSpeed.ljust(15)+disk_state.ljust(10)+disk_Type.ljust(10)+disk_Inter)

        # # raid lspci collect info
        # lspci_info = log.os_popen("lspci | grep -i sas | grep -v usb").strip()
        # # storcli64 collect info
        # stor_infoo = log.os_popen(
        #     "/opt/MegaRAID/storcli/storcli64 /call show all | head -n 211 | grep -v 'Date' | grep -v 'temperature' | grep -v 'BBU status' ",flags='no-log')
        # # check lspci info == 0 and stor_info == 0 exit
        # if len(lspci_info) == len(stor_infoo): log._error("Raid.info.Error.Exit!")
        # # storinfo
        # print_save_text(flags=flags, folder_path=folder_path, type="storinfo", count=count,
        #                 text="-" * 60 + "\n" + lspci_info + "\n" + "-" * 60 + "\n" + stor_infoo + "\n" + "=" * 60)
        if flags == "1" : log._pr(
            "OS Storcli64 Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")

# Get OS Network information
def os_net_info(flags, folder_path, count):
    if log.json_get('collect_array',"netinfo",web='no-log',filename='collect').strip() !='1':return 0
    echo_dev_info_sleep(flags,count)
    nic_arry = log.os_popen("ls /sys/class/net | sort |egrep -v 'lo|br|bond|usb|docker' 2>/dev/null").strip().split()
    print_save_text(flags=flags, folder_path=folder_path, type="netinfo", count=count,
                    text="[Order]".ljust(9) + "[Nic_Name]".ljust(20) + "[BDF]".ljust(15)+"[Nic_Lnk]".ljust(35) + "[Module]".ljust(
                        15) + "[DD_Version]".ljust(35) + "[FW_Version]")
    order = 0
    for nic_name in nic_arry:
        bdf = log.os_popen(f"ethtool -i {nic_name} | grep bus-info | awk -F': ' '{{print $2}}'").strip()
        if bdf == "":bdf="NA"
        if "usb" in bdf:continue
        link_sta = log.os_popen(f"lspci -vvvs {bdf.strip()} 2>/dev/null | grep -i lnksta: | cut -d : -f 2 | tr -d ' ' ").strip()
        if link_sta == "":link_sta="NA"
        module = log.os_popen(f"ethtool -i {nic_name} | grep ^driver | awk '{{print $2}}'").strip()
        if module == "":module="NA"
        dd_ver = log.os_popen(f"ethtool -i {nic_name} | grep ^version | awk '{{print $2}}'|sed 's/ /_/g'").strip()
        if dd_ver == "":dd_ver="NA"
        fw_ver = log.os_popen(
            f"ethtool -i {nic_name} | grep ^firmware-version | awk -F': ' '{{print $2}}'| sed 's/ /_/g'").strip()
        if fw_ver == "":fw_ver="NA"
        print_save_text(flags=flags, folder_path=folder_path, type="netinfo", count=count,
                        text="".ljust(3) + str(order).ljust(6) + nic_name.ljust(20) + bdf.ljust(15)+link_sta.ljust(35) + module.ljust(
                            15) + dd_ver.ljust(35) + fw_ver)
        order += 1
    
    if flags == "1" : 
        if diff_information(count,folder_path,"netinfo"):
            log._pr("OS net info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("OS net info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")


def ipmi_mcinfo(flags, folder_path, count):
    if log.json_get('collect_array',"mcinfo",web='no-log',filename='collect').strip() !='1':return 0
    echo_dev_info_sleep(flags,count)

    retry_get_ipmi_info('ipmitool mc info','BMC IPMI MC Info ')

    ipmi_mc_info = log.os_popen("ipmitool mc info")
    print_save_text(flags=flags, folder_path=folder_path, type="mcinfo", count=count,text=ipmi_mc_info)
    
    if flags == "1" : 
        if diff_information(count,folder_path,"mcinfo"):
            log._pr("BMC IPMI MC Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("BMC IPMI MC Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")

def chassis_status(flags, folder_path, count):
    if log.json_get('collect_array',"chassis",web='no-log',filename='collect').strip() !='1':return 0
    echo_dev_info_sleep(flags,count)
    chassis_status_info = log.os_popen("ipmitool chassis status | grep -vi 'last power event' ")
    print_save_text(flags=flags, folder_path=folder_path, type="chassis", count=count,text=chassis_status_info)
    
    if flags == "1" : 
        if diff_information(count,folder_path,"chassis"):
            log._pr("BMC Chassis Status Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
        else:
            log._pr("BMC Chassis Status Info ".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[FAIL]\033[0m")

def other_collect_info(flags, folder_path, count, cmd_name):
    result = log.os_popen(cmd_name)
    cmd_folder_name = cmd_name.replace("-", "").replace("/", "").replace("\'", "").strip().replace(" ", "_").replace(
        "'", "").replace(".", "_")
    if not os.path.exists(f"{folder_path}/system_info/{cmd_folder_name}"):
        os.mkdir(f"{folder_path}/system_info/{cmd_folder_name}")
    print_save_text(flags=flags, folder_path=folder_path, type=cmd_folder_name, count=count, text=result)
    if flags == "1" : log._pr(
        f" Other Collect info {cmd_folder_name}".ljust(40) + "\033[32m[Pass]\033[0m")

def bmc_survival_check(flags, path, count):
    # return bmc_survival_check_ibmc(flags, path, count)
    bmc_chip = log.json_get("BMC_Survival_Config","bmc_chip").strip()   
    if bmc_chip == "ASPEED-2600":
        return bmc_survival_check_2600(flags, path, count)
    elif bmc_chip == "Hisilicon-Hi1711":
        return bmc_survival_check_ibmc(flags, path, count)
    else:
        log.json_set("BMC_Survival_Config","switch","0")
        log._error(f"Sost currently does not support BMC login check for {bmc_chip} chips ! BMC_Survival_Config -> switch -> 0")
        
def bmc_survival_check_ibmc(flags, path, count):
    if log.json_get("BMC_Survival_Config", "switch").strip() != "1":
        return
    bmcip = log.os_popen(''' ipmitool lan print | grep -i 'ip address' | grep -vi source | cut -d ':' -f 2 | tr -d ' *' ''').strip()
    username = log.json_get("BMC_Survival_Config", "BMC_Username").strip()
    password = log.json_get("BMC_Survival_Config", "BMC_Password").strip()
    osip_arry = log.os_popen(r''' ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' ''').split()
    log._dp(f"iBMC BMC Survival Login osip arry : {str(osip_arry)}")
    if osip_arry == []:log._error("OS Not Found IP Address!")
    if flags == "1" :
        print('''
════════════════════════════════════════════════════════════════
|                     Services Status Check                    |
═══════════════════════════════════════════════[Collect]═[Check]''')
    # Determine whether to enable the check
    try:
        import time
        import requests
        import json
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        def get_ibmc_pcie_info(session,bmcip,flags,folder_path,count):
            ibmc_pcie_info_url = f"https://{bmcip}/UI/Rest/System/Boards/PCIeCard"
            pcieinfo_data = json.loads(session.get(ibmc_pcie_info_url,verify=False).text)
            # No Found PCIeinfo Exit Test
            # if str(pcieinfo_data).strip() == '[]':log._error("iBMC Web Not Found pcieinfo!")
            print_save_text(flags=flags, folder_path=folder_path, type="ibmcpcie", count=count,text=str(pcieinfo_data).strip())
            if flags == '1' and diff_information(count=count,path=folder_path,typee='ibmcpcie'):
                log._pr(f"iBMC Web Collect PCIe Info".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
            else:
                if count == '0':return
                log._pr(f"iBMC Web Collect PCIe Info".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[Fail]\033[0m")
            
        def get_ibmc_fan_info(session,bmcip,flags,folder_path,count):
            ibmc_fan_info_url = f'https://{bmcip}/UI/Rest/System/Thermal'
            fan_data = json.loads(session.get(ibmc_fan_info_url,verify=False).text)
            # 提取所有 SpeedRatio 信息
            speed_ratios = []
            for group in fan_data["Fans"]:
                if not group:
                    continue
                fan = group[0]
                speed_ratio = fan.get("SpeedRatio", 0)
                name = fan.get("Name", f"Unknown ({group.index})")
                speed_ratios.append((name, speed_ratio))
            # 格式化输出
            for name, ratio in speed_ratios:
                print_save_text(flags=flags, folder_path=folder_path, type="ibmcfan", count=count,text=f"{name}:{str(int(ratio))}".strip())
            
            if flags == '1' and diff_information(count=count,path=folder_path,typee='ibmcfan'):
                log._pr(f"iBMC Web Collect FAN Info".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
            else:
                if count == '0':return
                log._pr(f"iBMC Web Collect FAN Info".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[Fail]\033[0m")
        def get_ibmc_fw_info(session,bmcip,flags,folder_path,count):
            ibmc_fw_info_url = f"https://{bmcip}/UI/Rest/BMCSettings/UpdateService"
            fw_info = str(session.get(ibmc_fw_info_url,verify=False).text)
            text= "fw_info len : "+str(len(fw_info))+"\n"+str(fw_info)
            print_save_text(flags=flags, folder_path=folder_path, type="ibmcfw", count=count,text=str(text).strip())
            if flags == '1' and diff_information(count=count,path=folder_path,typee='ibmcfw'):
                log._pr(f"iBMC Web Collect FW Info".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
            else:
                if count == '0':return
                log._pr(f"iBMC Web Collect FW Info".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[Fail]\033[0m")

        def get_ibmc_psu_watts(session,bmcip,flags,folder_path,count):
            psu_watts_url = f"https://{bmcip}/UI/Rest/System/PowerSupply"
            psu_info = json.loads(session.get(psu_watts_url,verify=False).text)
            input_watts = [str(int(psu["InputWatts"])) for psu in psu_info["SupplyList"]]
            input_watts = str(input_watts).replace("[","").replace("]","")
            print_save_text(flags=flags, folder_path=folder_path, type="ibmcpsu", count=count,text=str(input_watts).strip())
            if flags == '1' and diff_information(count=count,path=folder_path,typee='ibmcpsu'):
                log._pr(f"iBMC Web Collect PSU Watts".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
            else:
                if count == '0':return
                log._pr(f"iBMC Web Collect PSU Watts".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[Fail]\033[0m")

        def get_ibmc_cpu_info(session,bmcip,flags,folder_path,count):
            cpu_info_url = f"https://{bmcip}/UI/Rest/System/Processor"
            cpu_info = json.loads(session.get(cpu_info_url,verify=False).text)
            print_save_text(flags=flags, folder_path=folder_path, type="ibmccpu", count=count,text=str(cpu_info).strip())
            if flags == '1' and diff_information(count=count,path=folder_path,typee='ibmccpu'):
                log._pr(f"iBMC Web Collect CPU Info".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
            else:
                if count == '0':return
                log._pr(f"iBMC Web Collect CPU Info".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[Fail]\033[0m")

        def get_ibmc_mem_info(session,bmcip,flags,folder_path,count):
            mem_info_url = f"https://{bmcip}/UI/Rest/System/Memory"
            mem_info = json.loads(session.get(mem_info_url,verify=False).text)
            text= "mem_info len : "+str(len(mem_info))+"\n"+str(mem_info)
            print_save_text(flags=flags, folder_path=folder_path, type="ibmcmem", count=count,text=str(text).strip())
            if flags == '1' and diff_information(count=count,path=folder_path,typee='ibmcmem'):
                log._pr(f"iBMC Web Collect MEM Info".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
            else:
                if count == '0':return
                log._pr(f"iBMC Web Collect MEM Info".ljust(40) + "\033[32m[Pass]\033[0m   \033[31m[Fail]\033[0m")

        def login_ibmc(username, password , bmcip):
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'}
                login_data = {"UserName": username, "Password": password, "Domain": "LocaliBMC", "Type": "Local"}
                login_url = f"https://{bmcip}/UI/Rest/Login"
                session = requests.session()
                response = session.post(login_url, data=login_data, headers=headers, verify=False)
                csrf = re.findall(r'"XCSRFToken"\s*:\s*"([^"]+)"', response.text)[0]
                if flags == '1':
                    log._pr(f"iBMC Simulate login Success".ljust(40) + "\033[32m[Pass]\033[0m   \033[32m[Pass]\033[0m")
                return session , csrf
            except Exception as e:
                log._pr(f"iBMC Simulate login Fail".ljust(40) + "\033[31m[Fail]\033[0m   \033[31m[Fail]\033[0m ")
                fail_info(error_type='ibmcloginFail',error_info=str(e),file1='ibmcLogin',file2='ibmcLogin')
                return True

        def session_delete(session,csrf):
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'}
                sessions_url = f"https://{bmcip}/UI/Rest/Sessions"
                sessions_text = session.get(sessions_url, headers=headers, verify=False).text
                parsed_data = json.loads(sessions_text)
                for osip in osip_arry:
                    session_ids = [member["SessionID"] for member in parsed_data["Members"] if member["IPAddress"] == osip]
                    for session_id in session_ids:
                        session_del_url = f'https://{bmcip}/UI/Rest/Sessions/{session_id.strip()}'
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
                            'x-csrf-token': csrf}
                        session.delete(url=session_del_url, headers=headers, verify=False).status_code
                        time.sleep(1)
            except Exception as e:
                log._error(f"iBMC删除会话失败! : {str(e)}")
                return True

        session,csrf = login_ibmc(username, password , bmcip)
        try:
            get_ibmc_psu_watts(session,bmcip,flags,path,count)
            get_ibmc_fw_info(session,bmcip,flags,path,count)
            get_ibmc_fan_info(session,bmcip,flags,path,count)
            get_ibmc_pcie_info(session,bmcip,flags,path,count)
            get_ibmc_cpu_info(session,bmcip,flags,path,count)
            get_ibmc_mem_info(session,bmcip,flags,path,count)
            session_delete(session, csrf)
        except Exception as e:
            session_delete(session, csrf)
            log._error(f"<sost> iBMC Information retrieval failed after login : {e}")
    except:
        return True
    
    return False

def bmc_survival_check_2600(flags, path, count):
    if log.json_get("BMC_Survival_Config", "switch").strip() != "1":
        return
    bmcip = log.os_popen(''' ipmitool lan print | grep -i 'ip address' | grep -vi source | cut -d ':' -f 2 | tr -d ' *' ''').strip()
    username = log.json_get("BMC_Survival_Config", "BMC_Username").strip()
    password = log.json_get("BMC_Survival_Config", "BMC_Password").strip()
    system_ip_arry = log.os_popen(r''' ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' ''').strip().split()

    if bmcip == "" or username == "" or password == "" or system_ip_arry == []:
        log._error("BMC_Survival_Config Error!")

    if flags == "1" :
        print('''
════════════════════════════════════════════════════════
|                   Services Status Check              |
════════════════════════════════════════════════════════''')

    bmc_ip = []
    if "," in bmcip:
        bmc_ip = bmcip.split(",")
    else:
        bmc_ip.append(bmcip)
    for bmcip in bmc_ip:
        # Determine whether the requirements for checking the viability are met
        try:
            import base64
            import requests
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            username_base64 = base64.b64encode(username.encode()).decode()
            password_base64 = base64.b64encode(password.encode()).decode()
            url = f"https://{bmcip}/api/session"
            data = {"username": username_base64, "password": password_base64}
            headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"}
            # -------------------------------------------------------------------------
            response = requests.post(url=url, headers=headers, data=data, verify=False)
            cookie = response.cookies
            re_cookie = r'(?<=<RequestsCookieJar\[<Cookie)(.+?)(?= for )'
            cookie = re.findall(re_cookie, str(cookie), re.S)[0].strip()
            re_CSRFToken = '(?<="CSRFToken": ")(.+?)(?=", "channel": )'
            csrf_token = re.findall(re_CSRFToken, response.text, re.S)[0]
            cookie = f"lang=zh-cn; {cookie.strip()}; refresh_disable=1; __Host-garc={csrf_token}; __Host-right_powerctl=1; __Host-TFAEnabled=; __Host-TFAStatus="

            headers = {
                "cookie": cookie,
                "x-csrftoken": csrf_token
            }

            url = f"https://{bmcip}/api/settings/service-sessions?service_id=1"
            response_1 = requests.get(url=url,headers=headers, verify=False).text
            session_ip = re.findall('''(?<="client_ip": ")(.+?)(?=", "user_id": )''',response_1,re.S)
            session_id = re.findall('''(?<="session_id": )(.+?)(?=, "session_type")''',response_1,re.S)
            url = f"https://{bmcip}/api/system_inventory/cpu_status"
            response = requests.get(url=url, headers=headers,verify=False).text
            log._dp(response)
            a = 0
            if len(session_ip) != len(session_id):log._error('bmc_survival_check() -> len(session_ip) != len(session_id) . Error ')
            for id in session_id:
                for system_ip in system_ip_arry:
                    if session_ip[a] == system_ip:
                        url = f"https://{bmcip}/api/settings/service-sessions/{id.strip()}"
                        headers = {
                            "cookie": cookie,
                            "x-csrftoken": csrf_token,
                        }
                        response = requests.delete(url=url, headers=headers, verify=False).text
                a+=1
            if flags == "1" :
                log._pr(f"BMC_ip : {bmcip}")
                log._pr(f"BMC Simulate login Success! ".ljust(40) + "\033[32m[Pass]\033[0m")
                
        except:
            if flags == "1" :
                log._pr(f"BMC_ip : {bmcip}")
                log._pr(f"BMC Simulate login Fail ! ".ljust(40) + "\033[31m[Fail]\033[0m")
                log._pr("BMC simulation login failed, please check if BMC is alive!  \033[33m[BMC模拟登录失败请检查BMC环境]\033[0m")
                try:
                    log.os_popen("lspci  | grep -i aspeed | grep -i vga | awk '{print $1}' | xargs lspci -xxxs")
                    bmc_vga_ver = log.os_popen("lspci  | grep -i aspeed | grep -i vga | awk '{print $1}' | xargs lspci -xxxs | grep -i 00: | grep -v 0000: | cut -d ' ' -f 10").strip()
                    if bmc_vga_ver == "41":
                        log._pr('-'*50)
                        log._pr("The current BMC chip is ASPEED-2500, and the BMC shared network port cannot be accessed under the system,")
                        log._pr("Please check if the configuration file contains the shared network port IP!")
                        log._pr("当前BMC芯片为:ASPEED-2500 , 系统下无法访问BMC共享网口, 请检查配置文件中是否包含共享网口IP!")
                except:
                    pass
                log._pr("-"*50)
                log._pr(f" BMC_IP       : {bmcip.strip()}")
                log._pr(f" BMC_UserName : {username.strip()}")
                log._pr(f" BMC_PassWord : {password.strip()}")
                log._pr("-"*50)
                return True
    return False

if __name__ == '__main__':
    print('', end='')



