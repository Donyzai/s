from sost_logging import dong_log

log = dong_log()
# no-log -> not save cmd.log
# ''     -> save cmd.log
cmd_log_flags = 'no-log'

import os
from datetime import datetime
import json
import time
import subprocess

# subprocess IPMI Run Command timeout
ipmi_timeout = 5

def ipmi_run(command):
    try:
        result = subprocess.run(command , shell=True , timeout=5,text=True,capture_output=True)
        result = result.stdout.strip()
    except Exception as e:
        result = ''
    return result

def simple_json_get(obj,key):
    aNUM = '12'
    if obj == "Multimodal_stability":aNUM = '2'
    print(f''' cat /opt/sost/config/sost.json  | grep -{aNUM} {obj} | grep -i {key}| tr -d ' ,"' | cut -d ':' -f 2 ''')
    return log.os_popen(f''' cat /opt/sost/config/sost.json  | grep -{aNUM} {obj} | grep -i {key}| tr -d ' ,"' | cut -d ':' -f 2 ''',flags=cmd_log_flags).replace('"',"").replace(",","").strip()

def bmc_ver():
    os.system("touch /tmp/sost_tmp/swc_bmc_ver.log")
    if os.popen("ps aux | grep -i 's/0x//g' | grep -i '3p' | grep -v 'ps aux' | wc -l").read().strip() == "0":
        os.system(''' timeout 1 echo "$(ipmitool mc info 2>/dev/null | grep 'Firmware Revision' | awk '{ print $4 }').$(ipmitool mc info 2>/dev/null | grep -A4 'Aux Firmware Rev Info' | grep -vi 'Firmware' | head -n 4 | awk '{ print $1 }' | sed 's/0x//g' | paste -sd.)" > /tmp/sost_tmp/swc_bmc_ver.log & ''')
    return os.popen("cat /tmp/sost_tmp/swc_bmc_ver.log | head -n 1 | tr -d '\n'").read().strip()

def cpld_ver():
    cpld_version = ""
    if os.popen(''' cat /opt/sost/config/sost.json  | grep -i bmc_chip | cut -d ':' -f 2 | tr -d '", ' ''').read().strip() !="ASPEED-2600":
        return "NA"
    try:
        # 32
        device_id = os.popen(''' result=$(timeout 0.5 ipmitool mc info 2>/dev/null | grep -i "device id" | awk '{if (NF >= 4) print $4}');echo "${result:-N/A}" ''').read().strip()
        if device_id == "32":
            raw_str = os.popen(''' output=$(timeout 1 ipmitool raw 0x0e 0x6f 2>/dev/null) && echo "$output" || echo "N/A" ''').read().strip()
            for i in range(8):
                hex_value = raw_str.split()[i]
                raw = int(hex_value, 16)
                cpld_version = cpld_version + "".join(chr(raw))
    except:
        cpld_version = "NA"
    
    return str(cpld_version)

def cpu_usage():
    """获取当前 CPU 使用率（百分比，0-100）"""
    with open('/proc/stat', 'r') as f:
        # 第一次读取（总 CPU 时间）
        line = f.readline()  # 第一行是 "cpu ..."
        cpu_data = list(map(int, line.split()[1:]))  # 提取数值部分
    
    # 计算第一次采样的总时间和空闲时间
    total1 = sum(cpu_data)
    idle1 = cpu_data[3] + cpu_data[4]  # idle + iowait
    
    # 短暂休眠（减少误差）
    time.sleep(0.1)
    
    # 第二次读取
    with open('/proc/stat', 'r') as f:
        line = f.readline()  # 再次读取第一行
        cpu_data = list(map(int, line.split()[1:]))
    
    # 计算第二次采样的总时间和空闲时间
    total2 = sum(cpu_data)
    idle2 = cpu_data[3] + cpu_data[4]
    
    # 计算 CPU 使用率
    total_diff = total2 - total1
    idle_diff = idle2 - idle1
    cpu_usage = 100 * (total_diff - idle_diff) / total_diff
    
    return round(cpu_usage, 2)

def get_value(text):
    return os.popen(f''' cat /opt/sost/config/sost.json  | grep -i '{text}' | cut -d ':' -f 2 | tr -d ' ,"' ''').read().strip()

def fail_info():
    result = log.json_get("Test_tmp","test_status",web=cmd_log_flags)
    path_folder = log.json_get("Test_tmp","test_folder_path",web=cmd_log_flags)
    if result == 'FAILc':
        failc_info = os.popen(f"cat {path_folder}/failc.txt").read().strip()
        data = '==============================\nSummaryInfo \n==============================\n'+ log.os_popen(f"cat {path_folder}/failc_result/summary.log 2>/dev/null",flags=cmd_log_flags).strip()+ '\n==============================\n'+str(failc_info)
        return str(data).replace('(','').replace(')','').replace('{','').replace('}','').strip()
    elif result == 'FAIL':
        fail_info = os.popen(f"cat {path_folder}/fail.txt").read()
        if fail_info.strip()=='':
            fail_info = os.popen(f"cat /opt/sost/log/sost_interactive.log").read()
        return fail_info
    else:
        return ""

def hw_mac():
    mac_file_path = '/tmp/sost_tmp/mac'
    # 判断文件夹是否存在，判断文件是否存在
    if not os.path.exists('mac_file_path'):
        os.system(f'mkdir -p /tmp/sost_tmp && touch {mac_file_path}')

    # 采集BMC mac地址
    mac = ipmi_run(''' ipmitool lan print | awk -F': ' '/MAC Address[ ]*:/ {print $2}' ''' )
    if mac != '' and mac != '00:00:00:00:00:00':
        with open(mac_file_path,'w') as f:
            f.write(mac)
        return mac
    else:
        log._sd("swc未采集到bmc_mac地址信息!读取旧信息替代!")
        return open(mac_file_path,'r').read().strip()

def return_get_data():

    """获取系统测试数据和状态信息"""
    # 初始化基础数据
    base_data = {
        'Test-status': 'NA',
        'Test-type': 'NA',
        'Test-count': 'NA',
        'Test-result': 'NA',
        'Test-Start-Time':get_value('startT_time'),
        'Test-End-Time':get_value('endT_time'),
        'zLast_Time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'fail_info': fail_info(),
        'bmc_chip': get_value('bmc_chip'),

        "start_wait_time": get_value('start_wait_time'),
        "aclost_wait_time": get_value('aclost_wait_time'),
        
        'BMC_LAN_1': '0.0.0.0',
        "OS":str(os.popen("cat /etc/os-release  | grep -i PRETTY_NAME | cut -d '=' -f 2 ").read().replace('(',"").replace(')',"").replace('"',"").strip())+'   '+str(os.popen("uname -r").read().strip()),
        
        "fail_exit_flags":str(os.popen(''' cat /opt/sost/config/sost.json  | grep -i fail_exit_flags | grep -iv blacklist | cut -d ':' -f 2 | tr -d ' ",' ''').read().strip()) or 'NA',       
        "fail_exit_blacklist":str(os.popen(''' cat /opt/sost/config/sost.json  | grep -i fail_exit_blacklist | cut -d ':' -f 2 | tr -d ' ",' ''').read().strip()) or 'NA',
        'BMC_ver':bmc_ver(),
        'Bios_ver': os.popen("dmidecode -t bios | grep -i version | grep -v '#' | awk '{print $2}' 2>/dev/null").read().strip(),
        'sostVer': os.popen("cat /opt/sost/config/sost_version.json | grep -i version | cut -b 21-25 2>/dev/null",).read().strip().replace('"', "").replace(",", ""),
        'hw_mac':hw_mac()
    }

    count = simple_json_get("Test_tmp","test_count") or "NA"
    typee = simple_json_get("Test_tmp","test_type") or "NA"
    pressure_check = get_running_test_type()
    
    if pressure_check !="NA":
        base_data.update({
            'Test-status': 'running',
            'Test-type': pressure_check,
            'Test-count': "NA",
            'Test-result': "Pass"
    })
    
    base_data.update({
        'Test-type': process_test_type(typee),
        'Test-count': count,
        'Test-result': simple_json_get('Test_tmp','test_status')
    })

    runningFlag = simple_json_get("Test_tmp","Running_flag")

    if runningFlag == '0' or runningFlag == '5':
        base_data.update({
            'Test-status': 'No-Test',
            'Test-type': 'NA',
            'Test-count': 'NA',
            'Test-result': 'NA'
        })

    # value	role	swc_status
    # 0	No-Test	No-Test
    # 1	Running-Test	Running
    # 2	Collecting information	Collecting
    # 3	Rebooting	Rebooting
    # 4	TestEnding	Ending
    # 5	Clear TestTmpInfo -> swcClearInfoButton	No-Test / NA
    # 6	sostErrStop	sostErrStop
    # 7	sostWaitingForTest	sostWaitingForTest
    # 8	natt TestStart	DiskTestRunning
    # 9	natt TestEnd	DiskTestEnding

    elif runningFlag == '1':
        base_data.update({'Test-status': 'Running'})
    elif runningFlag == '2':
        base_data.update({'Test-status': 'Collecting'})
    elif runningFlag == '3':
        base_data.update({'Test-status': 'Rebooting'})
    elif runningFlag == '4':
        base_data.update({'Test-status': 'Ending'})
    elif runningFlag == '6':
        base_data.update({
            'Test-status': 'sostErrStop',
            'Test-result': 'FAIL'
            })
    elif runningFlag == '7':
        base_data.update({
            'Test-status': 'sostWaitingForTest',
            'Test-type': simple_json_get("Test_tmp","test_type"),
            'Test-count': '0',
            'Test-result': 'Pass'
            })
    elif runningFlag == '8':
        base_data.update({
            'Test-status': 'DiskTestRunning',
            'Test-type': 'DiskTest',
            'Test-count': '0',
            'Test-result': 'Pass'
            })
    elif runningFlag == '9':
        base_data.update({
            'Test-status': 'DiskTestEnding',
            'Test-type': 'DiskTest',
            'Test-count': 'NA',
            'Test-result': 'Pass'
            })
    else:
        base_data.update({'Test-status': 'NA'})

    base_data.update({
        'SYS_IP': get_system_ip(),
        'BMC_LAN_1': get_bmc_ip(),
    })

    if os.popen('ps -aux  | grep -i xmx_shell | grep -vi grep').read().strip()!='':
        base_data.update({
            'Test-status': 'Running',
            'Test-type': 'xmx_shell',
            'Test-count': 'xmx_shell',
            'Test-result': 'xmx_shell'
        })

    if os.popen('ps -aux  | grep -i lds_shell | grep -vi grep | grep -vi refresh').read().strip()!='':
        base_data.update({
            'Test-status': 'Running',
            'Test-type': 'lds_shell',
            'Test-count': 'lds_shell',
            'Test-result': 'lds_shell'
        })

    return base_data

# 辅助函数
def is_process_running(process_name):
    """检查进程是否在运行"""
    cmd = f"ps -aux | grep -iE '{process_name}' | grep -v grep | grep -vi gsd-housekee | wc -l"
    result = os.popen(cmd).read().strip()
    # if process_name == 'ping':
    #     print(f"process name {process_name} , result : {result}")
    return result != "0"

def process_test_type(test_type):
    """处理测试类型"""
    if simple_json_get("Multimodal_stability","switch") !="0":
        test_type += "-M"
    fail_exit_flags = simple_json_get("Test_Config", "fail_exit_flags").strip()
    if fail_exit_flags == "0":
        return test_type + "-E"
    return test_type

def get_running_test_type():
    """获取正在运行的测试类型"""
    test_processes = {
        'iperf': 'iperf',
        'netperf': 'netperf',
        'stress': 'stress',
        'linpack': 'xhpl',
        'stream': 'stream',
        'ltpstress': 'ltp',
        'natt': 'natt',
        'amdsst': 'amdsst',
        'ptu': 'ptu',
        'ptat': 'ptat',
        'cpu2006': 'cpu2006',
        'cpu2017': 'cpu2017',
        'specpower': 'specpower',
        "unixbench":'unixbench',
        'sost-sensor': 'sost.*sensor',
        "ping":"ping"
    }
    for test_type, pattern in test_processes.items():
        if is_process_running(pattern) :
            return test_type
    return "NA"

def get_system_ip():
    
    osip_file_path = '/tmp/sost_tmp/osip'
    if not os.path.exists(osip_file_path):os.system(f"touch {osip_file_path}")
    ip = os.popen('''nmcli connection show 2>/dev/null | grep -vE "lo|--|NAME" | head -n 1 | awk '{print $1}' | xargs ifconfig | grep -i inet | awk '{print $2}' | grep -v : | grep -v 127.0.0.1''').read().strip()
    if ip != '' and ip != '0.0.0.0':
        with open(osip_file_path,'w') as f:f.write(ip)
        return ip
    else:
        log._sd("未获取到OSIP,使用旧文件代替")
        return open(osip_file_path,'r').read().strip()

def get_bmc_ip():
    # bmcip存放位置
    bmc_ip_file = '/tmp/sost_tmp/bmcip'
    if not os.path.exists(bmc_ip_file):
        os.system("touch /tmp/sost_tmp/bmcip")
    # 
    ip = ipmi_run(f"ipmitool lan print 2>/dev/null | grep -i 'ip address' | grep -vi source | cut -d ':' -f 2 | tr -d ' ' ")
    if ip=='':
        ip = ipmi_run(f"ipmitool lan print 8 2>/dev/null | grep -i 'ip address' | grep -vi source | cut -d ':' -f 2 | tr -d ' ' ")
        if ip == '':
            log._sd("未检测到bmcip地址!使用旧IP进行代替!")
            return open(bmc_ip_file,'r').read().strip()
    with open(bmc_ip_file,'w') as f:f.write(ip)
    return ip

if __name__ == '__main__':
    log._sd("Sost has enabled the server information collection service.(swc_cinfo.py)")
    while True:
        data = json.dumps(return_get_data(),indent=4)
        with open('/opt/sost/config/server_info.json','w') as f:
            f.write(data)
            f.flush()
        os.sync()
        time.sleep(1)
