# Filename : dong_public_lib.py
# Release time : 2024.07.12
# Version:1.0
# by:FanXiaodong
# ══════════════════════════════════
import threading
# from .sost_logging import *
from .sost_logging import dong_log
from .sost_system_info_lib import test_config
import time
import os
import hashlib
from datetime import datetime, timedelta

log = dong_log()
log.debug_flags = str(log.json_get("debug","debug_flags",web='no-log',filename="debug"))

def testsha256():
    sha256_str = log.json_get("Test_tmp","test_type").strip() + log.json_get("Test_tmp","startT_time").strip()
    # uuid encode = test_type + start_time
    log.json_set("Test_tmp","test_sha256",str(hashlib.sha256(sha256_str.encode(encoding='UTF-8')).hexdigest()))

def update_show(update_flag,tips):
    clp()
    print(f'''
══════════════════════════════════════════════════════
||                                     ██           ||
||                                    ░██           ||
||           ██████  ██████   ██████ ██████         ||
||          ██░░░░  ██░░░░██ ██░░░░ ░░░██░          ||
||         ░░█████ ░██   ░██░░█████   ░██           ||
||          ░░░░░██░██   ░██ ░░░░░██  ░██           ||
||          ██████ ░░██████  ██████   ░░██          ||
||         ░░░░░░   ░░░░░░  ░░░░░░     ░░           ||
══════════════════════════════════════════════════════
>> {tips}''')

    if update_flag == '1':
        update_sost(noexit_flag='1')
    elif update_flag == '2':
        update_sost(update_flag='1')
    elif update_flag == '3':
        update_sost(noexit_flag='1')
    elif update_flag == '4':
        update_sost(update_flag='1')
    else:
        return

def update_check():

    sost_server_ip = log.json_get("sost","update_Web_server_ip",filename='version').strip()

    try:
        if os.system(f'ping {sost_server_ip} -c 1 -i 0.5 -W 0.5 >/dev/null 2>&1') != 0:
            return False
    except:
        return False

    update_flag = log.os_popen(f"curl -X GET http://{sost_server_ip}/sost/update_flag.txt 2>/dev/null").replace("\n","").strip()
    remote_sha256 = log.os_popen(f"curl -X GET http://{sost_server_ip}/sost/new_version_sha256.txt 2>/dev/null").replace("\n","").strip()
    local_sha256 = log.os_popen('sost -i sha256').replace("\n","").strip()

    log._dp(f"update_flag    : {update_flag}")
    log._dp(f"remote_sha256  : {remote_sha256}")
    log._dp(f"local_sha256   : {local_sha256}")
    
    if update_flag == '' or remote_sha256 == '' or local_sha256 == '':
        log._dp("SOST update_server_ip Error!")
        return 0
        
    if remote_sha256 == local_sha256:
        log._dp("The sha256 remote value is consistent with the local value, so no update is needed")
        return 0
    
    if update_flag == '0':
        log._dp("SOST is the latest version")
        return 0
    elif update_flag == '1':
        log._dp("SOST is recommended to update")
        tips = 'Your SOST is not the latest version. It is recommended to update it'
    elif update_flag == '2':    
        log._dp("SOST must be updated")
        tips = 'Your SOST is not the latest version and must be updated'
    elif update_flag == '3':
        log._dp("SOST is recommended to downgrade")
        tips = 'Your SOST is not the latest version. It is recommended to downgrade'
    elif update_flag == '4':
        log._dp("SOST must be downgraded")
        tips = 'Your SOST is not the latest version and must be downgraded'
    else:
        return 0
    update_show(update_flag,tips)

def init_poweronoff_env(bmclan='',BMC_User='',BMC_Pass=''):
    bmc_information = get_bmc_info(bmclan,BMC_User,BMC_Pass)
    sost_poweronoff_serverIP = log.json_get('power_on_off','server_ip').strip()
    sost_poweronoff_serverPort = log.json_get('power_on_off','server_port').strip()
    log.os_run('rm -rf /usr/bin/power_on_off')
    log.os_run('rm -rf /usr/local/bin/power_on_off')
    log.os_run('touch /usr/local/bin/power_on_off && chmod 777 /usr/local/bin/power_on_off')
    log.os_run(f"echo 'curl -G http://{sost_poweronoff_serverIP}:{sost_poweronoff_serverPort}/power_on?bmc_ip={bmc_information[0]}' > /usr/local/bin/power_on_off")
    log.os_run("echo 'ipmitool power off' >> /usr/local/bin/power_on_off")
    if log.os_popen("whereis power_on_off | cut -d ':' -f 2 | tr -d ' '").strip() == '':
        log._error("Please Check /usr/local/bin/power_on_off file!")
    return

def debug_mode():
    if log.json_get("debug","noSendComand",filename='debug').strip() == '1': 
        defalt_path()
        log._error("DebugMode Enabled noSendComand = 1")

def return_wait_time():
    
    if log.json_get("Test_tmp","test_type") == "AClost":
        # if aclost_wait_time not set -> return start_wait_time
        if log.json_get("Test_Config","aclost_wait_time").strip() == "":
            try:wait_time = int(log.json_get("Test_Config","start_wait_time"))
            except:wait_time = 25
        else:
            try:wait_time = int(log.json_get("Test_Config","aclost_wait_time"))
            except:wait_time = 60
    else:
        wait_time = int(log.json_get("Test_Config","start_wait_time"))

    return wait_time

def check_bmc_status():
    log._pr("BMC Status Checking Status......")
    if log.os_popen("ipmitool mc info 2>/dev/null| grep -i Product | wc -l").strip() == "0":
        log._error("Bmc Status [x]")

def swc_EndTest():
    if "1" in log.os_popen("cat /opt/sost/config/sost.json | grep -i 'swc_flags' | cut -d ':' -f 2"):
        clp()
        count = str(int(log.json_get("Test_tmp","test_count")) - 1)
        if count == -1:count = 0
        test_type_logo(log.json_get("Test_tmp","test_type"),count)
        print("\033[33m [ >> WebConsole_Stop_Test_flags << ] \033[0m")
        print("\033[33m <swc-flags> WebMesole remotely sends a test interrupt flag, and the current test is paused. \033[0m")
        print("\033[33m <swc-flags> WebConsole远程发送测试中断flag，当前测试暂停。\033[0m")
        log.json_set("Test_tmp","swc_flags","0")
        defalt_path()
        result_html()
        exit()

def mulit_main():
    clp()
    print('''
===============================================================================
|     ████     ████          ██ ██   ██   ██████████                   ██     |
|    ░██░██   ██░██         ░██░░   ░██  ░░░░░██░░░                   ░██     |
|    ░██░░██ ██ ░██ ██   ██ ░██ ██ ██████    ░██      █████   ██████ ██████   |
|    ░██ ░░███  ░██░██  ░██ ░██░██░░░██░     ░██     ██░░░██ ██░░░░ ░░░██░    |
|    ░██  ░░█   ░██░██  ░██ ░██░██  ░██      ░██    ░███████░░█████   ░██     |
|    ░██   ░    ░██░██  ░██ ░██░██  ░██      ░██    ░██░░░░  ░░░░░██  ░██     |
|    ░██        ░██░░██████ ███░██  ░░██     ░██    ░░██████ ██████   ░░██    |
|    ░░         ░░  ░░░░░░ ░░░ ░░    ░░      ░░      ░░░░░░ ░░░░░░     ░░     |
===============================================================================''')
    if log._in("Do you want Open Mulit Mode ? [y / n] : ").lower() != "y":log._error("User.Input.Exit")
    print()
    log._pr("="*40)
    log._pr("If you don't want to conduct the test, ")
    log._pr("you can enter the key directly without entering the number of turns!")
    log._pr("如果你不想进行某项测试，可以不输入圈数直接回车!")
    log._pr("="*40)
    if aclost_init_env(flags=False):
        log._pr("ACLost Test \t\t\t \033[42m √ \033[0m")
        aclost_flags=True
    else:
        log._pr("ACLost Test \t\t\t \033[41m x \033[0m")
        aclost_flags=False
    log._pr("="*40)
    reboot_count = log._in("Input reboot count : ").strip()
    if reboot_count == "":
        reboot_count="no-test"
        log.json_set("Multimodal_stability","count_reboot","")
    else:
        try:
            int(reboot_count)
            log.json_set("Multimodal_stability","count_reboot",str(reboot_count))
        except:
            log._error(f"User.Input.Error! reboot_count : {str(reboot_count)}")
    powercycle_count  = log._in("Input powercycle count : ").strip()
    if powercycle_count == "":
        powercycle_count="no-test"
        log.json_set("Multimodal_stability","count_powercycle","")
    else:
        try:
            int(powercycle_count)
            log.json_set("Multimodal_stability","count_powercycle",str(powercycle_count))
        except:
            log._error(f"User.Input.Error! count_powercycle : {str(powercycle_count)}")

    powerreset_count  = log._in("Input powerreset count : ").strip()
    if powerreset_count == "":
        powerreset_count="no-test"
        log.json_set("Multimodal_stability","count_powerreset","")
    else:
        try:
            int(powerreset_count)
            log.json_set("Multimodal_stability","count_powerreset",str(powerreset_count))
        except:
            log._error(f"User.Input.Error! powerreset_count : {str(powerreset_count)}")

    aclost_count  = log._in("Input ACLost count : ").strip()
    if aclost_count == "":
        aclost_count="no-test"
        log.json_set("Multimodal_stability","count_aclost","")
    else:
        try:
            if aclost_flags:
                int(aclost_count)
                log.json_set("Multimodal_stability","count_aclost",str(aclost_count))
            else:
                log._pr("ACLost Config Error!Unable to set up testing!")
                log.json_set("Multimodal_stability","count_aclost","")
                aclost_count = "no-test"
        except:
            log._error(f"User.Input.Error! count_aclost : {str(aclost_count)}")

    if reboot_count == "no-test" and powercycle_count == "no-test" and powerreset_count == "no-test" and aclost_count == "no-test":log._error("User.Input.Error")
    print("================Config================")
    log._pr(f"reboot     count     : {reboot_count}")
    log._pr(f"PowerCycle count     : {powercycle_count}")
    log._pr(f"PowerReset count     : {powerreset_count}")
    log._pr(f"ACLost     count     : {aclost_count}")
    print("================Config================")
    if log._in("Are you ok ? [y / n] : ") !="y":log._error("User.Input.Exit!")
    log.json_set("Multimodal_stability","switch","1")
    path = log.json_get("Test_Config", "Result_path")
    log.os_popen(f"mv {path}/sost_mulit_result {path}/sost_old_folder/sost_mulit_result_{now_time()} 2>/dev/null")
    log.os_popen(f"mkdir -p {path}/sost_mulit_result")
    now_timee = now_time()
    log.os_run(f"echo '{now_timee}' > {path}/sost_mulit_result/sost_start_time.txt")
    log.json_set("Test_tmp","startT_time",now_timee)
    log.json_set("Test_tmp","endT_time","")
    log.os_run(f" cat /opt/sost/config/sost.json  | grep -A6 Multimodal_stability > {path}/sost_mulit_result/test_plan.txt")
    print(os.popen('ps -aux | grep -i "sost -s"').read().strip())
    os.system("ps -aux | grep -iE 'sost -s|sost.py -s|sost.py' | grep -v grep | awk '{print $2}' | xargs kill -9 && sost -s ")

# sost startup check
def startup_check():
    #backup cmd.log and clear cmd.log
    log._dmesg("The main program of Sost has started running.")
    if log.json_get("debug","debug_flags",filename="debug").strip()=="0":
        log.os_run('rm -rf /tmp/sost_tmp/old_cmd.log')
        log.os_run('mv /opt/sost/log/cmd.log /tmp/sost_tmp/old_cmd.log')
        log._dmesg('Sost Clear cmd.log Success!')
        
    logo(log.json_get("sost","Release_Time",filename='version'),log.json_get("sost","Version",filename='version'))
    log.json_set("Test_tmp","swc_flags","0")
    log.os_run("mkdir -p /tmp/sost_tmp")

    test_mode = log.json_get("Test_Config","simple_test_flags").strip()
    if test_mode !="":
        log._pr(f"Now Test Mode 【 {test_mode} 】")
        log._pr(f"Restore default values Command : sost -m default ")
        u_in = log._in(" Continue ? [y / n]: ").strip().lower()
        if u_in =='n' or u_in == "no" or u_in == "q":
            log._error("User.Input.Exit!")

def result_html(return_path=False):
    if log.json_get("Test_Config","result_html") == "0":return 
    try:
        folder_path = log.json_get("Test_tmp","test_folder_path").strip()
        # File paths
        test_config_content = log.os_popen(f"cat {folder_path}/testconfig.txt 2>/dev/null").strip()
        total_rounds = log.os_popen(f"cat {folder_path}/count.txt 2>/dev/null").strip()
        test_status = 'Pass'
        status_class = 'pass'
        # Determine test status
        fail_info = ""
        if log.os_popen(f"ls {folder_path} 2>/dev/null | grep -i 'fail' | grep -i continue | wc -l").strip() != '0':
            test_status = 'Failc'
            status_class = 'fail-c'
            fail_info = log.os_popen(f''' cd {folder_path} && ls | grep -i fail | grep -v html | xargs -I {{}} sh -c 'echo "{'='*60}\nFile: {folder_path}/{{}}\n{'='*60}" && cat {{}}' ''').strip()
        if log.os_popen(f"ls {folder_path} 2>/dev/null | grep 'fail.txt' | grep -vi continue | wc -l").strip() != '0':
            test_status = 'Fail'
            status_class = 'fail'
            fail_info = log.os_popen(f"cat {folder_path}/fail.txt ").strip()
        # Fetch additional system information
        test_typpe = log.json_get('Test_tmp', 'test_type')
        serverip = log.os_popen('''ip -4 addr | grep inet | grep -v 127.0.0.1 | awk '{print $2}' ''').strip()
        os_info = log.os_popen('''cat /etc/os-release | grep -i PRETTY_NAME | cut -d '=' -f 2''').strip().replace('"', '')
        bmcip = log.os_popen('''cat /opt/sost/config/server_info.json | grep -iE 'bmc_lan_' | cut -d ':' -f 2 | tr -d ' ",' ''').strip().replace("\n",",")
        start_time = datetime.strptime(log.os_popen(f"cat {folder_path}/sost_start_time.txt 2>/dev/null").strip(), "%Y-%m-%d-%H-%M-%S").strftime("%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(str(now_time()), "%Y-%m-%d-%H-%M-%S").strftime("%Y-%m-%d %H:%M:%S")
        sost_ver = log.json_get("sost","Version",filename='version').strip()
        bmc_ver  = log.os_popen(''' cat /opt/sost/config/server_info.json  | grep -i bmc_ver | cut -d ':' -f 2 | tr -d ' ,"' ''').strip() 
        bios_ver = log.os_popen(''' cat /opt/sost/config/server_info.json  | grep -i bios_ver | cut -d ':' -f 2 | tr -d ' ,"' ''').strip() 
        cpld_ver = log.os_popen("cat /tmp/sost_tmp/fwtmp 2>/dev/null| grep -i cpld.ver | cut -d ':' -f 2").strip() 
        log.os_popen("rm -rf /tmp/sost_tmp/fwtmp 2>/dev/null")
        # Generate HTML content
        html_content = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>sost-稳定性测试结果-{test_status.strip()}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    line-height: 1.6;
                    background-color: #f4f4f9;
                    color: #333;
                }}

                header {{
                    text-align: center;
                    padding: 20px;
                    background-color: #003366;
                    color: white;
                }}

                h1 {{
                    margin: 0;
                }}

                section {{
                    margin: 20px auto;
                    width: 90%;
                    max-width: 800px;
                    background: white;
                    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                    border-radius: 10px;
                    padding: 20px;
                }}
                .test-summary {{
                    margin: 20px auto;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                    border: 1px solid #ddd;
                    background-color: white;
                }}
                .test-summary h2 {{
                    margin-bottom: 15px;
                    font-size: 24px;
                    color: #333;
                }}
                .summary-content {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    padding: 10px 20px;
                    background-color: #f9f9f9;
                    border-radius: 8px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                    margin-top: 15px;
                }}
                .summary-item {{
                    flex: 1;
                    text-align: center;
                }}
                .summary-label {{
                    display: block;
                    font-weight: bold;
                    margin-bottom: 5px;
                    color: #555;
                }}
                .summary-value {{
                    font-size: 18px;
                    font-weight: bold;
                }}
                .pass .summary-value {{
                    color: #4CAF50;
                }}
                .fail .summary-value {{
                    color: red;
                }}
                .fail-c .summary-value {{
                    color: #dbb400;
                }}
                pre {{
                    background: #f8f8f8;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    overflow-x: auto;
                }}
                footer {{
                    text-align: center;
                    padding: 10px;
                    background: #003366;
                    color: white;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <header>
                <h1>sost稳定性测试结果-{test_status.strip()} | TTY测试部</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </header>

            <section id="summary-section" class="test-summary {status_class}">
                <h2>测试总结</h2>
                <div class="summary-content">
                    <div class="summary-item">
                        <span class="summary-label">测试结果</span>
                        <span class="summary-value">{test_status}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">测试圈数</span>
                        <span class="">{total_rounds}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">测试类型</span>
                        <span class="">{test_typpe}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">BMC版本</span>
                        <span class="">{bmc_ver}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">BIOS版本</span>
                        <span class="">{bios_ver}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">CPLD版本</span>
                        <span class="">{cpld_ver}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">系统IP</span>
                        <span class="">{serverip}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">BMCIP</span>
                        <span class="">{bmcip}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">系统</span>
                        <span class="">{os_info}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">开始测试时间</span>
                        <span class="">{start_time}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">结束测试时间</span>
                        <span class="">{end_time}</span>
                    </div>

                    <div class="summary-item">
                        <span class="summary-label">sost版本信息</span>
                        <span class="">{sost_ver}</span>
                    </div>
                </div>
            </section>

            <section>
                <h2>报错信息汇总打印</h2>
                <pre>{fail_info}</pre>
            </section>

            <section>
                <h2>开始测试配置信息</h2>
                <pre>{test_config_content}</pre>
            </section>

            <footer>
                <p>Generated by Sost | TTY测试部</p>
            </footer>
        </body>
        </html>
        """
        output_html = os.path.join(folder_path, f'sost-Result-{test_status}-{total_rounds}.html')
        # Write to output HTML file
        log.os_run(f'rm -rf {folder_path}/sost-Result-*')
        with open(output_html, 'w') as f:
            f.write(html_content)
        log.os_run(f'firefox {output_html} &')
        log._pr(f"Stability test report(稳定性测试报告生成成功) : {output_html}")
    except:
        log._pr(f"Stability test result generation failed! (稳定性测试结果生成失败)")
        log._error("result_html() -> Error!")
    
    if return_path:
        return output_html

# natt start_end_time
def start_end_time(time):
    runtime = timedelta(seconds=int(time))
    now = datetime.now()
    end_time = now + runtime
    log._pr("=" * 60)
    log._pr(f"WaitTime      : {str(time)}s")
    log._pr(f'NowTime       : {now.strftime("%Y-%m-%d %H:%M:%S")}')
    log._pr(f'StartTime     : {end_time.strftime("%Y-%m-%d %H:%M:%S")}')
    log._pr("=" * 60)

#-*-------------------------------------------------------------------------------
#AClost iniy
def aclost_init_env(flags=True):
    if log.os_popen("ls /dev/ | grep ttyUSB | wc -l").strip() == "0":
        if flags:
            log._error("No /dev/ttyUSB0 found! -> Please check the software and hardware environment!")
        else:
            return False
    else:
        log.os_popen("ipmitool chassis policy always-on 2>/dev/null")
        log._pr("AClost is already set chassis policy always-on!")
        minicon_config()
    return True
#logo
def bmc_stability_logo(bmc_ip):
    clp()
    bmc_chip_type = bmc_Chip()[0]
    stability_type = log.json_get("Test_tmp","test_type")
    stability_count = log.json_get("Test_tmp","test_count")
    print(f'''
════════════════════════════════════════════
||   ██                            ██     ||
||  ░██                           ░██     ||
||   ██      ██████████   ██████ ██████   ||
||  ░██████ ░░██░░██░░██ ██░░░░ ░░░██░    ||
||  ░██░░░██ ░██ ░██ ░██░░█████   ░██     ||
||  ░██  ░██ ░██ ░██ ░██ ░░░░░██  ░██     ||
||  ░██████  ███ ░██ ░██ ██████   ░░██    ||
||  ░░░░░   ░░░  ░░  ░░ ░░░░░░     ░░     ||
════════════════════════════════════════════
[+]  bmc IP   : {bmc_ip}
[+]  bmc_Chip : {bmc_chip_type}
[+]  Type     : {stability_type.ljust(30)}
[+]  Count    : {stability_count.ljust(30)}
[+]  Result   : Pass
════════════════════════════════════════════''')

#count_down(seconds=10,text="IPMI Log Collecting!")
def count_down(seconds=0,text=''):
    remain_time = timedelta(seconds=seconds)
    while remain_time.total_seconds() > 0:
        time.sleep(1)
        remain_time -= timedelta(seconds=1)
        print("\r< sost > {} {}s Waitings => {} s".format(text,seconds,remain_time), end="", flush=True)

# 对BMC进行存活性检查
def bmc_alive(bmc_ip,bmc_user,bmc_pass):
    max_try_time = 1800
    while True:
        if log.os_popen(f"ping -c 1 {bmc_ip} | grep -i ttl").strip() != "":
            log._dp("Bmc IP Ping is Alive!")
            if log.os_popen(f"ipmitool -C 17 -I lanplus -U {bmc_user} -P '{bmc_pass}' -H {bmc_ip} mc info 2>/dev/null").strip() != "":
                return True
            else:
                log._dp("Bmc IPMI is UnAlive!")
        else:
            log._dp("Bmc IP Ping is UnAlive!")
        max_try_time+=10
        count_down(10,"Wait for 10 seconds to retrieve BMC status again")

# Bmc Remote 稳定性测试
def bmc_stability(type='',folder_path=''):
    # type 1 -> warm
    #      2 -> cold
    #      3 -> raw
    bmc_ip,bmc_user,bmc_pass = get_bmc_info()
    log.os_run("sost -m bmc")
    # debug print ---------------------
    # Set Bmc Test Mode!
    # one Cycles Time : 240 + 25 = 265s -> 4m25s
    while True:
        bmc_stability_logo(bmc_ip)
        swc_EndTest()
        count = log.json_get("Test_tmp","test_count")
        wait_time_ctrl_C(log.json_get("Test_Config","start_wait_time"),flags='start')
        runTime("0")
        print("\n")
        # check bmc state
        if bmc_alive(bmc_ip,bmc_user,bmc_pass):
            log._pr("Bmc is Alive!")
        # Collect SystemInformation
        test_config("1",count,folder_path)
        log.json_set("Test_tmp","test_count",str(int(count)+1))
        time.sleep(3)
        if type == "1":
            log.os_popen(f"ipmitool -C 17 -I lanplus -U {bmc_user} -P '{bmc_pass}' -H {bmc_ip} bmc reset warm")
        elif type == "2":
            log.os_popen(f"ipmitool -C 17 -I lanplus -U {bmc_user} -P '{bmc_pass}' -H {bmc_ip} bmc reset cold")
        else:
            log.os_popen(f"ipmitool -C 17 -I lanplus -U {bmc_user} -P '{bmc_pass}' -H {bmc_ip} raw 0x06 0x02")
        #save count -> folder_path>count.txt
        log.os_popen(f"echo {str(int(count)+1)} > {folder_path}/count.txt")
        #waiting for
        if count!="0":runTime("3")
        runTime("4")
        runTime("1")
        count_down(240,'Waiting BMC Restart! Not Close Sost!')

# BMC quickly Create Audit Log
def bmc_Create_audit_log(bmc_ip,bmc_user,bmc_pass):
    try:
        import requests
        from tqdm import tqdm
        from requests.packages import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except:
        log._error("Python.requests.lib -> Dependency library not installed! Unable to test!")
    test_num = log._in("Input the number of generated items Enter-> 500 (输入生成数量,回车默认值500) : ").strip()
    if test_num.strip() == "":test_num = "500"
    test_num = int(test_num)
    clp()
    log._pr("\n"+'='*120+"\n"+'The log generation process has been initiated, please wait for the progress bar to end.\n'+"="*120+"\n")

    def ami_requests_post(test_num):
        for i in tqdm(range(test_num)):
            headers = {
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            }
            data = {
                "username": "YWRtaW4=",
                "password": "MQ=="
            }
            try:
                requests.post(url=f"https://{bmc_ip}/api/session",headers=headers,data=data,verify=False)
            except Exception as e:
                log._pr(f"Article {str(i)}: Fail Generation,errorInfo : {e}")

        log._pr("\n"+'='*120+"\n"+'Log generation successful, please log in to BMC to view the audit log list. GoodBye! \n'+"="*120+"\n")

    def e2000s_clear_sel(test_num):
        for i in tqdm(range(test_num)):
            log.os_run(f"ipmitool -C 17 -I lanplus -U {bmc_user} -P '{bmc_pass}' -H {bmc_ip} sel clear")
        log._pr("\n"+'='*120+"\n"+'Log generation successful, please log in to BMC to view the audit log list. GoodBye! \n'+"="*120+"\n")
   
    try:
        bmc_chip_type = bmc_Chip()[0]
        if bmc_chip_type == "Phy-E2000S":
            e2000s_clear_sel(test_num)
        else:
            ami_requests_post(test_num)
    except:
        ami_requests_post(test_num)
    return


# BMC quickly Create Sel Log
def bmc_Create_sel_log(bmc_ip,bmc_user,bmc_pass):
    try:
        if 'Phy-E2000S' in bmc_Chip()[0]:
            log._error("Phy-E2000S Not Create Sel Log!")
    except:
        log._error("bmc_Create_sel_log() -> bmc_Chip()[0] Error")
    clp()
    bmc_pass = str(bmc_pass).replace(r"`",r"\`").replace(r"'",r"\`")
    # Debug Area ---------------------------------------------
    try:
        from tqdm import tqdm
        log._tips("\n"+"="*120+"\nFrist backup sel log -> /tmp/sost_tmp/sost_tmp\n"+"="*120)
        log.os_run(f"ipmitool -C 17 -I lanplus -U {bmc_user.strip()} -P {bmc_pass.strip()} -H {bmc_ip.strip()} sel save /tmp/sost_tmp/sost_tmp")
        log._tips("Success!\n")

        log._tips("\n"+"="*120+"\nFrist Clear sel log\n"+"="*120)
        log.os_run(f"ipmitool -C 17 -I lanplus -U {bmc_user.strip()} -P {bmc_pass.strip()} -H {bmc_ip.strip()} sel clear")
        log._tips("Success!\n")

        clear_sel_num = log.os_popen(f"sh -c 'ipmitool -C 17 -I lanplus -U {bmc_user.strip()} -P {bmc_pass.strip()} -H {bmc_ip.strip()} sel elist | wc -l'").strip().replace("\n","")
        time.sleep(3)
        if clear_sel_num == "0":
            log._error("Bmc sel log num : 0")
        elif clear_sel_num == "1":
            log._tips(f"Bmc sel log num : {str(clear_sel_num)}")
        else:
            return
        
        user_input = log._in("Input the number of generated items Enter-> 4000 [Max 10000]: ").strip()
        if user_input == "":user_input = "4000"
        # Validate user input is a number and within range (1-10000)
        if user_input.isdigit():
            if int(user_input) > 10000:
                log._error("User.Input.Error! Max 10000")
        else:
            log._error("User.Input.Error! Not a number!")

        log._tips("Now start collecting the first log information!")
        try:
            log.os_run(f"ipmitool -C 17 -I lanplus -U {bmc_user.strip()} -P {bmc_pass.strip()} -H {bmc_ip.strip()} sel save /tmp/sost_tmp/sost_sel_log_bak")
            log._tips("Success!")
        except:
            log.error_exit("collecting the first log Error!")

        try:
            log._tips("Start generating log files now!")
            for i in tqdm(range(int(user_input))):
                log.os_run("cat /tmp/sost_tmp/sost_sel_log_bak >> /tmp/sost_tmp/sost_sel_log")
            log.os_run("rm -rf /tmp/sost_tmp/sost_sel_log_bak ")
            log._tips("Successfully generated log file!")
        except:
            log._error("Failed to generate log file!")
        try:
            log._tips("Now start writing log files to BMC SEL, please be patient and wait for the process to complete!")
            log.os_run(f"ipmitool -C 17 -I lanplus -U {bmc_user.strip()} -P {bmc_pass.strip()} -H {bmc_ip.strip()} sel add /tmp/sost_tmp/sost_sel_log")
            log._tips("Successfully generated log file!")
        except:
            log._error("Failed to generate log file!")
        log.os_run("rm -rf /tmp/sost_tmp/sost_sel_log")

    except:
        pass

    return

# BMC Tools Main

def bmc_tools_main(release_time, version):
    clp()
    bmc_chip = bmc_Chip()[0]
    print(f'''
══════════════════════════════════════════════════
||   ██████████                    ██           ||
||  ░░░░░██░░░                    ░██           ||
||      ░██      ██████   ██████  ░██  ██████   ||
||      ░██     ██░░░░██ ██░░░░██ ░██ ██░░░░    ||
||      ░██    ░██   ░██░██   ░██ ░██░░█████    ||
||      ░██    ░██   ░██░██   ░██ ░██ ░░░░░██   ||
||      ░██    ░░██████ ░░██████  ███ ██████    ||
||      ░░      ░░░░░░   ░░░░░░  ░░░ ░░░░░░     ||
||══════════════════════════════════════════════||
||  1 . BMC sensor / sdr Collect to Log         ||
||  2 . Quick generation of BMC sel logs        ||
||  3 . Quick generation of BMC audit logs      || 
||══════════════════════════════════════════════||''')
    chose = log._in("You Chose : ")
    # chose = "2"
    if chose == '1':
        clp()
        def_Handling_sensors()
    elif chose == "2":
        bmc_information = get_bmc_info()
        bmc_Create_sel_log(bmc_information[0],bmc_information[1],bmc_information[2])
    elif chose == "3":
        bmc_information = get_bmc_info()
        bmc_Create_audit_log(bmc_information[0],bmc_information[1],bmc_information[2])
    elif chose == "q" or chose == "exit":
        exit()
    else:
        bmc_tools_main(release_time.ljust(11),version)

# BMC chip inspection
def bmc_Chip(flags=""):

    # simple json get
    def simple_json_get(obj,key,flags=""):
        return log.os_popen(f"cat /opt/sost/config/sost.json  | grep -A5 {obj} | grep -i {key} | cut -d ':' -f 2",flags=flags).replace('"',"").replace(",","").strip()

    # Hi1711
    if log.os_popen("lspci | grep -i hi171x | grep -i vga | wc -l",flags).strip() != "0":
        if simple_json_get("BMC_Survival_Config","bmc_chip",flags) != "Hisilicon-Hi1711":
            log.json_set("BMC_Survival_Config","bmc_chip","Hisilicon-Hi1711",flags)
        return "Hisilicon-Hi1711",True

    #Phy-E2000S
    if log.os_popen('lspci | grep -i aspeed | grep -i vga | wc -l',flags).strip() != "1":
        if log.os_popen("lspci | grep -i 'Display controller: Phytium Technology Co' | wc -l").strip() == '1':
            if simple_json_get("BMC_Survival_Config","bmc_chip",flags) != "Phy-E2000S":
                log.json_set("BMC_Survival_Config","bmc_chip","Phy-E2000S",flags)
            return 'Phy-E2000S',True
        return 'Fail',False

    # ASPEED 2500 or ASPEED 2600
    if log.os_popen("lspci  | grep -i aspeed | grep -i vga | wc -l",flags).strip()!="0":
        log.os_popen("lspci  | grep -i aspeed | grep -i vga | awk '{print $1}' | xargs lspci -xxxs",flags)
        bmc_vga_ver = log.os_popen("lspci  | grep -i aspeed | grep -i vga | awk '{print $1}' | xargs lspci -xxxs | grep -i 00: | grep -v 0000: | cut -d ' ' -f 10",flags).strip()
        if bmc_vga_ver == '52':
            if simple_json_get("BMC_Survival_Config","bmc_chip",flags) != "ASPEED-2600":
                log.json_set("BMC_Survival_Config","bmc_chip","ASPEED-2600",flags)
            return "ASPEED-2600" , True
        elif bmc_vga_ver == "41":
            if simple_json_get("BMC_Survival_Config","bmc_chip",flags) != "ASPEED-2500":
                log.json_set("BMC_Survival_Config","bmc_chip","ASPEED-2500",flags)
            return "ASPEED-2500" , True
        else:
            if simple_json_get("BMC_Survival_Config","bmc_chip",flags) != "ASPEED-Other":
                log.json_set("BMC_Survival_Config","bmc_chip","ASPEED-Other",flags)
            return 'ASPEED-Other' , False

    return "GetNull",False

# ipmitool sel backup and frist clear sel
# save path : debug folder
def sel_bak_clear(path):
    if log.json_get("Test_Config","simple_test_flags") == "simple":return 
    # backup bmc sel log ->
    try:
        if 'Phy-E2000S' in bmc_Chip()[0].strip():
            log._pr("Bmc Chip : Phy-E2000S -> Not clear Sel log!")
            return
    except:
        log._error("sost_public_lib -> sel_bak_clear() -> bmc_Chip()[0]")
        return
    log.os_popen("ipmitool sel clear")
    time.sleep(1)

#BMC Sensors Check
def def_Handling_sensors():
    def Handling_sensors(file_path, result_folder, sensors_type, filter_type, flags):
        clp()
        log._pr("Now Start Handling sensors!")
        if not os.path.exists(file_path):
            log._error("Not Found File!")
        if not os.path.exists(result_folder):
            os.mkdir(result_folder)
        if "sdr" in sensors_type:
            sensor_command = 'ipmitool sdr'
        else:
            sensor_command = 'ipmitool sensor list'
        sensor_title_arry = log.os_popen(fr"{sensor_command} 2>/dev/null | cut -d '|' -f 1 ").split('\n')
        for sensor_title in sensor_title_arry:
            sensor_log_filename = sensor_title.replace(' ','')
            if filter_type != "":
                if filter_type.lower() not in sensor_title.lower():continue
            log.os_run(f"echo '{sensor_title}' >> {result_folder}/sensor_data/{sensor_log_filename}.log")
            log.os_run(f"cat {file_path} | grep -w '{sensor_title}' | cut -d '|' -f 2 >> {result_folder}/sensor_data/{sensor_log_filename}.log")
        log.os_run(f"paste -d ',' {result_folder}/sensor_data/*.log > {result_folder}/sost_sensors_list.csv")
        log.os_run(f"rm -rf {result_folder}/sensor_data")
        log._pr(f"Result File Path : {result_folder}/sost_sensors_list.csv")

    def countdown(execution_time, flags, path):
        start_time = time.time()
        log._pr("Running Times : " + str(execution_time))
        if flags == "0":
            log.os_run(f"touch {path}/sost_ipmi_sensor.txt")
            command = f"date >> {path}/sost_ipmi_sensor.txt && ipmitool sensor list 2>/dev/null >> {path}/sost_ipmi_sensor.txt"
        else:
            log.os_run(f"touch {path}/sost_ipmi_sdr.txt")
            command = f"date >> {path}/sost_ipmi_sdr.txt && ipmitool sdr list 2>/dev/null >> {path}/sost_ipmi_sdr.txt"
        clp()
        print('''\033[32m
    ════════════════════════════════════════════════════════
    |               ██████    ████████   ██████            |
    |              ░█░░░░██  ██░░░░░░   ██░░░░██           |
    |              ░█   ░██ ░██        ██    ░░            |
    |              ░██████  ░█████████░██                  |
    |              ░█░░░░ ██░░░░░░░░██░██                  |
    |              ░█    ░██       ░██░░██    ██           |
    |              ░███████  ████████  ░░██████            |
    |              ░░░░░░░  ░░░░░░░░    ░░░░░░             |
    ════════════════════════════════════════════════════════
    |           IPMI sensor collection enabled!            |
    ════════════════════════════════════════════════════════\033[0m''')
        runtime = timedelta(seconds=int(execution_time))
        now = datetime.now()
        log._pr(f'StartTime   : {now.strftime("%Y-%m-%d %H:%M:%S")}')
        log._pr(f'EndTime     : {(now + runtime).strftime("%Y-%m-%d %H:%M:%S")}')
        log._pr("The program is running, please be patient and wait for it to end...... Ctrl + C Exit!")
        while True:
            try:
                tmp = log.os_run(command)
                if tmp == "Failed":break
                current_time = time.time()
                if current_time - start_time >= execution_time:
                    break  # 跳出循环
            except:
                break

    def user_runTime():
        running_time = log._in("Running Time Enter->3600s (s): ").strip()
        if running_time.strip() == '':
            return 3600
        try:
            float(running_time)
        except:
            log._error("User.Input.Error()")
        return int(running_time)

    def handling_sensor_sdr_num():
        print("-" * 40)
        log._pr("Start comparing the number of sensors and SDR sensors")
        print("-" * 40)
        sensor_num = int(log.os_popen("ipmitool sensor 2>/dev/null | wc -l").strip())
        sdr_num = int(log.os_popen("ipmitool sdr 2>/dev/null | wc -l").strip())
        # flags : 0 -> sensor
        # flags : 1 -> sdr
        flags = "0"
        if int(sensor_num) == int(sdr_num):
            log._pr("The number of sensors is consistent!")
            log._pr(f"Number of  sensor : {sensor_num}")
            log._pr(f"Number of     sdr : {sdr_num}")
            flags = "0"
        elif int(sensor_num) > int(sdr_num):
            log._pr("The number of sensors is greater than the number of SDR sensors!")
            log._pr(f"Number of  sensor : {sensor_num}")
            log._pr(f"Number of     sdr : {sdr_num}")
            flags = "0"
        elif int(sensor_num) < int(sdr_num):
            log._pr("The number of SDR sensors is greater than the number of sensor sensors!")
            log._pr(f"Number of  sensor : {sensor_num}")
            log._pr(f"Number of     sdr : {sdr_num}")
            flags = "1"
        else:
            log._error("Error check sensor_num and sdr_num !")
        print("-" * 60)
        return flags

    print('''
════════════════════════════════════════════════════════════════════════════
|    ████████                    ██         ██████    ████████   ██████    |
|   ██░░░░░░                    ░██        ░█░░░░██  ██░░░░░░   ██░░░░██   |
|  ░██         ██████   ██████ ██████      ░█   ░██ ░██        ██    ░░    |
|  ░█████████ ██░░░░██ ██░░░░ ░░░██░       ░██████  ░█████████░██          |
|  ░░░░░░░░██░██   ░██░░█████   ░██        ░█░░░░ ██░░░░░░░░██░██          |
|         ░██░██   ░██ ░░░░░██  ░██        ░█    ░██       ░██░░██    ██   |
|   ████████ ░░██████  ██████  ░░██  █████░███████  ████████  ░░██████     |
|   ░░░░░░░░   ░░░░░░  ░░░░░░    ░░  ░░░░░ ░░░░░░░  ░░░░░░░░    ░░░░░░     |
════════════════════════════════════════════════════════════════════════════
|           Auther:Xiaodong Fan                 sost-bsc.ver : v1.0        |
════════════════════════════════════════════════════════════════════════════
|  0.sensor             |  1. sdr              |  2. Auto                  |   
════════════════════════════════════════════════════════════════════════════
''')
    log.np_title = "sostBMC_Sensor"
    result_path = log.json_get("Test_Config", "Result_path")
    path = f"{result_path}/sostbmc_sensor"
    if not os.path.exists(path=f"{result_path}/sostbmc_sensor"):
        log.os_run(f"mkdir -p {result_path}/sostbmc_sensor/sensor_data")
    else:
        if not os.path.exists(path=f"{result_path}/sost_old_folder"):
            log.os_run(f"mkdir -p {result_path}/sost_old_folder")
        now_time = str(time.strftime("_%Y_%m_%d_%H_%M_%S", time.localtime()))
        log.os_run(f"mv {result_path}/sostbmc_sensor {result_path}/sost_old_folder/sostbmc_sensor_{str(now_time)}")
        log.os_run(f"mkdir -p {result_path}/sostbmc_sensor/sensor_data")
    user_input = log._in("Enter the mode you want to select 0/1/2  Ether -> 0: ")
    log.os_run("clear")
    flags = "0"
    if user_input == "0":
        flags = "0"
    elif user_input == "1":
        flags = "1"
    elif user_input == "2":
        flags = handling_sensor_sdr_num()
    elif user_input == "":
        flags = "0"
    else:
        log._error("User.Input.Exit() -> user_input")

    running_times = user_runTime()

    print('''
═════════════════════════════════════════════════════════════════════════════
|   ██████    ████████   ██████          ████ ██  ██   ██                   |
|  ░█░░░░██  ██░░░░░░   ██░░░░██        ░██░ ░░  ░██  ░██                   |
|  ░█   ░██ ░██        ██    ░░        ██████ ██ ░██ ██████  █████  ██████  |
|  ░██████  ░█████████░██        █████░░░██░ ░██ ░██░░░██░  ██░░░██░░██░░█  | 
|  ░█░░░░ ██░░░░░░░░██░██       ░░░░░   ░██  ░██ ░██  ░██  ░███████ ░██ ░   |
|  ░█    ░██       ░██░░██    ██        ░██  ░██ ░██  ░██  ░██░░░░  ░██     |
|  ░███████  ████████  ░░██████         ░██  ░██ ███  ░░██ ░░██████░███     | 
|  ░░░░░░░  ░░░░░░░░    ░░░░░░          ░░   ░░ ░░░    ░░   ░░░░░░ ░░░      |
═════════════════════════════════════════════════════════════════════════════
|           Auther:Xiaodong Fan                 sost-bsc.ver : v1.0         |
═════════════════════════════════════════════════════════════════════════════
|  0. ALL Sensors   1. TEMP     2. FAN      3. WATTS     4. User.Input      |
═════════════════════════════════════════════════════════════════════════════
''')
    user_input_tmp = log._in("Select the type of sensor you want to filter 0/1/2/3/4  Enter -> 0 : ")
    
    if user_input_tmp.strip()!="":
        try:float(user_input_tmp)
        except:log._error("User.Input.Error()")
    filter_type = ""
    if user_input_tmp == "0":
        filter_type = ""
    elif user_input_tmp == "1":
        filter_type = "TEMP"
    elif user_input_tmp == "2":
        filter_type = "FAN"
    elif user_input_tmp == "3":
        filter_type = "WATTS"
    elif user_input_tmp == "4":
        filter_type = log._in("Filter Type : ")
    elif user_input_tmp.strip() == "":
        filter_type = ""
    else:
        log._error("User.Input.Error() -> user_input_tmp")

    if flags == "0":
        countdown(running_times, flags, path)
        Handling_sensors(file_path=f"{path}/sost_ipmi_sensor.txt", result_folder=path, sensors_type="sensor",
                         filter_type=filter_type, flags="")
    else:
        countdown(running_times, flags, path)
        Handling_sensors(file_path=f"{path}/sost_ipmi_sdr.txt", result_folder=path, sensors_type="sdr",
                         filter_type=filter_type, flags="")
    exit()

def Judging_autologin():
    if "kylin" in log.os_popen("cat /etc/os-release |grep 'PRETTY_NAME'").lower().strip():
        # False or True
        autostart_ = os.path.exists("/root/.config/autostart/sost.desktop")
        # 0 or !0
        bashprofile = int(log.os_popen("cat /root/.bash_profile | grep -i 'sost -z' | wc -l"))
        if autostart_:
            log._pr("GUI autostart sost.desktop is already !")
        if bashprofile != 0 :
            log._pr("Text autotest is already !")
        if autostart_ and bashprofile != 0:
            log._pr("GUI and Text Two models conflict!")
            kylin_mod = log.os_popen("systemctl get-default")
            if "graphical.target" in kylin_mod:
                log._pr("Kylin model is GUI! -> clear .bash_profile")
                log.os_run("yes | sost -f bash")
            else:
                log._pr("Kylin model is Text -> clear autostart folder")
                log.os_run("rm -rf /root/.config/autostart/*")
        else:
            log._pr("The self startup file is normal!")

def minicon_config():
    tmp = log.os_popen("cat /etc/minirc.dfl 2>/dev/null")
    if "/dev/ttyUSB0" in tmp and "pu rtscts" in tmp:
        log._pr("Minicom Config is already configured!")
        return 0
    
    if log.os_popen(f"cat /etc/os-release | grep -i ubuntu | wc -l").strip() == "0":
        filename = "/etc/minirc.dfl"
    else:
        filename = "/etc/minicom/minirc.dfl"
    
    if not os.path.exists(filename):
        log._pr(f"Minicom Config File Not Found! Create {filename} File!")
        log.os_run(f"touch {filename}")

    with open(filename,"w") as f:
        f.write('# Machine-generated file - use "minicom -s" to change parameters.'+"\n")
        f.write("pu port             /dev/ttyUSB0"+"\n")
        f.write("pu rtscts           No"+"\n")
        f.flush()
    log._pr("Minicom Config set Success!")

def Multimodal_stability():
    switch_status = log.json_get("Multimodal_stability","switch")
    if switch_status != "1":return 0
    # -------------------------------------------------------------------------------------------
    count_aclost = log.json_get("Multimodal_stability", "count_aclost")
    if count_aclost != "" and count_aclost != "0":
        return "AClost", "sh -c `sync ; sleep 3 ; sh -c 'minicom &' ; sleep 5 ; echo a > /dev/ttyUSB0` &" ,count_aclost
    # -------------------------------------------------------------------------------------------
    count_reboot = log.json_get("Multimodal_stability", "count_reboot")
    if count_reboot != "" and count_reboot != "0":
        return "reboot", "reboot" ,count_reboot
    # -------------------------------------------------------------------------------------------
    count_powercycle = log.json_get("Multimodal_stability", "count_powercycle")
    if count_powercycle != "" and count_powercycle != "0":
        return "powercycle", "ipmitool power cycle" ,count_powercycle
    # -------------------------------------------------------------------------------------------
    count_powerreset = log.json_get("Multimodal_stability", "count_powerreset")
    if count_powerreset != "" and count_powerreset != "0":
        return "powerreset", "ipmitool power reset" ,count_powerreset
    # -------------------------------------------------------------------------------------------
    if count_reboot == "0" or count_reboot == "" and count_powercycle == "0" or count_powercycle == "" and count_powerreset == "0" or count_powerreset == "" and count_aclost =="0" or count_aclost == "":
        clp()
        log._pr("MulitMode Test : End")
        log.json_set("Multimodal_stability","switch","0")
        log.json_set("Multimodal_stability","count_reboot","")
        log.json_set("Multimodal_stability","count_powercycle","")
        log.json_set("Multimodal_stability","count_powerreset","")
        log.json_set("Multimodal_stability","count_aclost","")

        log.json_set("Test_tmp","test_type","")
        log.json_set("Test_tmp","test_count","")
        log.json_set("Test_tmp","test_folder_path","")
        log.json_set("Test_tmp","run_command","")

        log.json_set("Test_Config","max_count","")
        log.os_run("yes | sost -f bash")
        log.os_run("rm -rf /root/.config/autostart/*")
        log._pr("multi.stability.test completed, reset config file, deleted!")
        log.os_run("ps -aux | grep -i sost | grep -v grep | grep -v sost_web_console | awk '{print $2}' |xargs kill -9")
    # -------------------------------------------------------------------------------------------

def updating_sost(update_ver,server_ip):

    log._pr("\033[32mStop swc-manager.service Success!\033[0m")
    log.os_run('sost -w stop >/dev/null')

    log.os_run(f'rm -rf /tmp/sost-v{update_ver}-Release*')

    if log.os_popen(f'''wget http://{server_ip}/sost/sost-v{update_ver}-Release.tar -O /tmp/sost-v{update_ver}-Release.tar 2>/dev/null && echo 'success' || echo 'fail' ''').strip() == 'fail':
        log.os_run(f'rm -rf /tmp/sost-v{update_ver}-Release*')
        log._error(f"Failed to download the latest sost file! Please Check : http://{server_ip}/sost/sost-v{update_ver}-Release.tar")

    log._pr(f"\033[32mGet New sost release version to /tmp/sost-v{update_ver}-Release.tar success!\033[0m")

    # md5sum 
    log._pr("\033[34mDownload sost md5sum : " + log.os_popen(f"md5sum /tmp/sost-v{update_ver}-Release.tar | awk '{{print $1}}'").strip()+'\033[0m')

    # untar sostReleaseTar File
    log._pr(f"\033[32mUntar /tmp/sost-v{update_ver}-Release.tar\033[0m")
    log.os_run(f"tar -xvf /tmp/sost-v{update_ver}-Release.tar -C /tmp")
    
    # check untar File Folder
    if not os.path.exists(f'/tmp/sost-v{update_ver}-Release'):
        log._error("Untar File Error!")

    # Delete Tar File
    log._pr(f"\033[32mDelete /tmp/sost-v{update_ver}-Release.tar\033[0m")
    log.os_run(f"rm -rf /tmp/sost-v{update_ver}-Release.tar")

    # Runing Install File
    log._pr(f"\033[32mRuning Install File /tmp/sost-v{update_ver}-Release/sost_install.py\033[0m")

    # Runing Install File and kill sost_main.py
    os.system(f" echo 'cd /tmp/sost-v{update_ver}-Release/ && python3 sost_install.py' > /tmp/run.sh ")
    os.system("cd /tmp && sh /tmp/run.sh &")
    os.system(f"ps aux | grep -i sost_main | grep -iv grep | awk '{{print $2}}' | xargs kill -9")
    
def return_alive_server_ip():
    server_ip = log.json_get("sost", "update_Web_server_ip",filename='version').strip().split(',')
    for ip in server_ip:
        result = log.os_popen(f"ping -c 1 {ip} | tail -n 2 | head -n 2")
        if "100% packet loss" not in result:
            return ip

def update_sost(update_flag='',noexit_flag=''):
    if update_flag != '1':
        if log._in("Do you want to Update ? [ y / n] ").lower() == 'n':
            if noexit_flag == '':
                log._error("User.Input.Not.Update")
            else:
                return
    # sost Release server ip 
    server_ip = str(return_alive_server_ip()).strip()
    # 1.0.8
    now_ver = log.json_get('sost','Version').strip() 
    # 1.0.8
    update_ver = log.os_popen(f"curl -s http://{server_ip}/sost/new_version.txt").strip() 
    # StartUpdateing Sost
    updating_sost(update_ver,server_ip)

def get_bmc_info(u_chos='',BMC_User='',BMC_Pass=''):
    clp()
    log._tips("<------ BMC status check ----->")
    Dedicated_lan_num = log.json_get("Test_Config","Dedicated_lan_num")
    Share_lan_num = log.json_get("Test_Config","Share_lan_num")

    Dedicated_ip = log.os_popen(f"ipmitool lan print {Dedicated_lan_num} 2>/dev/null  | grep -vi source | grep -i 'ip address' | awk '{{print $4}}' 2>/dev/null").strip()
    share_ip = log.os_popen(f"ipmitool lan print {Share_lan_num} 2>/dev/null  | grep -vi source | grep -i 'ip address' | awk '{{print $4}}'").strip()
    if Dedicated_ip.strip() == "0.0.0.0" and share_ip.strip() == "0.0.0.0" or Dedicated_ip == "" and share_ip == "":
        print('''\033[31m
════════════════════════════════════════════════════════════════════════════════════
||                            ████████     ██     ██ ██                           ||
||                            ░██░░░░░     ████   ░██░██                          ||
||                            ░██         ██░░██  ░██░██                          ||    
||                            ░███████   ██  ░░██ ░██░██                          ||
||                            ░██░░░░   ██████████░██░██                          ||
||                            ░██      ░██░░░░░░██░██░██                          ||
||                            ░██      ░██     ░██░██░████████                    ||
||                             ░░       ░░      ░░ ░░ ░░░░░░░░                    ||
════════════════════════════════════════════════════════════════════════════════════
||                          Oh.My.God Stability Fail Please                       ||
════════════════════════════════════════════════════════════════════════════════════\033[0m''')
        log._tips("[-] Bmc Status check Error!")
        log._tips("BMC状态丢失,请等待一段时间后重新开始进行稳定性测试。")
        log._error("BMC status lost, please wait for a period of time before resuming stability testing.")
        log._error("Dedicated_ip and share_ip is Null!")
        return
    log._tips("[+] Bmc Status check Success!")

    #Collect dedicated ip info
    Dedicated_arry = []
    Dedicated_arry.append(Dedicated_ip)
    Dedicated_subnet_mask = log.os_popen(f"ipmitool lan print {Dedicated_lan_num} 2>/dev/null  | grep -vi source | grep -i 'subnet mask' | awk '{{print $4}}' ").strip()
    if Dedicated_subnet_mask == "":Dedicated_subnet_mask = "xxx.xxx.xxx.xxx"
    Dedicated_gatway_ip   = log.os_popen(f"ipmitool lan print {Dedicated_lan_num} 2>/dev/null  | grep -vi source | grep -i 'Default Gateway IP' | awk '{{print $5}}' ").strip()
    if Dedicated_gatway_ip == "":Dedicated_gatway_ip = "xxx.xxx.xxx.xxx"
    Dedicatede_mac   = log.os_popen(f"ipmitool lan print {Dedicated_lan_num} 2>/dev/null  | grep -vi source | grep -i 'MAC Address' | awk '{{print $4}}' ").strip()
    if Dedicatede_mac == "":share_mac = "xx:xx:xx:xx:xx:xx"
    #Collect shared ip info
    Share_arry = []
    Share_arry.append(share_ip)
    share_subnet_mask = log.os_popen(f"ipmitool lan print {Share_lan_num} 2>/dev/null | grep -vi source | grep -i 'subnet mask' | awk '{{print $4}}' ").strip()
    if share_subnet_mask == "":share_subnet_mask = "xxx.xxx.xxx.xxx"
    share_gatway_ip   = log.os_popen(f"ipmitool lan print {Share_lan_num} 2>/dev/null  | grep -vi source | grep -i 'Default Gateway IP' | awk '{{print $5}}' ").strip()
    if share_gatway_ip == "":share_gatway_ip = "xxx.xxx.xxx.xxx"
    share_mac   = log.os_popen(f"ipmitool lan print {Share_lan_num} 2>/dev/null  | grep -vi source | grep -i 'MAC Address' | awk '{{print $4}}' ").strip()
    if share_mac == "":share_mac = "xx:xx:xx:xx:xx:xx"

    Dedicated_alive="NA"
    share_alive = "NA"

    log._tips("Checking whether bmcip can ping, Waiting.......")

    if " 0% packet loss" in log.os_popen(f"ping -c 1 {Dedicated_ip.strip()} 2>/dev/null"):
        Dedicated_alive = "\033[42m √ \033[0m"
    else:
        Dedicated_alive = "\033[41m x \033[0m"
    
    if " 0% packet loss" in log.os_popen(f"ping -c 1 {share_ip.strip()} 2>/dev/null"):
        share_alive = "\033[42m √ \033[0m"
    else:
        share_alive = "\033[41m x \033[0m"

    print(fr'''════════════════════════════════════════════════════════════════════════
|     ___   __  __    ___             ___    _  _      ___    ___      |
|    | _ ) |  \/  |  / __|           |_ _|  | \| |    | __|  / _ \     |
|    | _ \ | |\/| | | (__     ___     | |   | .` |    | _|  | (_) |    |
|    |___/ |_|__|_|  \___|   |___|   |___|  |_|\_|   _|_|_   \___/     |
|  _|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_| """ |_|"""""|    |
|  "`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'    |
════════════════════════════════════════════════════════════════════════
|     Start configuring BMC now! Automatically obtain information!     |
════════════════════════════════════════════════════════════════════════''')
    print(f"|    1 . Dedicated ip : {Dedicated_ip.ljust(20)}  Status : [{Dedicated_alive}]           |")
    print(f"|    2 . Shared    ip : {share_ip.ljust(20)}  Status : [{share_alive}]           |")
    print('════════════════════════════════════════════════════════════════════════')

    if u_chos =='':
        u_chos = log._in("Chose Your Test lan  [ 1 / 2 ] Enter -> 1 ").strip()
        if u_chos=='':
            u_chos = '1'

    if u_chos != "1" and u_chos !="2":log._error("User.Input.Err")
    
    if BMC_User == '' and BMC_Pass =='':
        try:
            if 'Phy-E2000S' in bmc_Chip()[0]:
                BMC_User = log._in("Bmc_Username Enter -> root : ").strip()
                if BMC_User == "q" or BMC_User == "exit":log._error("User.Input.Exit()")
                if BMC_User == "":
                    BMC_User = "root"
                BMC_Pass = log._in("Bmc_Password Enter -> 0penBmc  : ").strip()
                if BMC_Pass == "q" or BMC_Pass == "exit":log._error("User.Input.Exit()")
                if BMC_Pass == "":
                    BMC_Pass = "0penBmc"
            elif 'Hisilicon' in bmc_Chip()[0]:
                BMC_User = log._in("Bmc_Username Enter -> Administrator : ").strip()
                if BMC_User == "q" or BMC_User == "exit":log._error("User.Input.Exit()")
                if BMC_User == "":
                    BMC_User = "Administrator"
                BMC_Pass = log._in("Bmc_Password Enter -> ttytty`12  : ").strip()
                if BMC_Pass == "q" or BMC_Pass == "exit":log._error("User.Input.Exit()")
                if BMC_Pass == "":
                    BMC_Pass = "ttytty`12"
            else:
                #---------------------------------------------------------------
                BMC_User = log._in("Bmc_Username Enter -> admin : ").strip()
                if BMC_User == "q" or BMC_User == "exit":log._error("User.Input.Exit()")
                # BMC_User = ""
                if BMC_User == "":
                    BMC_User = "admin"
                #---------------------------------------------------------------
                BMC_Pass = log._in("Bmc_Password Enter -> admin  : ").strip()
                if BMC_Pass == "q" or BMC_Pass == "exit":log._error("User.Input.Exit()")
                # BMC_Pass = ""
                if BMC_Pass == "":
                    BMC_Pass = "admin"
                #---------------------------------------------------------------
        except:
            #---------------------------------------------------------------
                BMC_User = log._in("Bmc_Username Enter -> admin : ").strip()
                if BMC_User == "q" or BMC_User == "exit":log._error("User.Input.Exit()")
                # BMC_User = ""
                if BMC_User == "":
                    BMC_User = "admin"
                #---------------------------------------------------------------
                BMC_Pass = log._in("Bmc_Password Enter -> admin  : ").strip()
                if BMC_Pass == "q" or BMC_Pass == "exit":log._error("User.Input.Exit()")
                # BMC_Pass = ""
                if BMC_Pass == "":
                    BMC_Pass = "admin"
                #---------------------------------------------------------------

    if u_chos == "1":
        Dedicated_arry.append(BMC_User)
        Dedicated_arry.append(BMC_Pass)
        return Dedicated_arry
    elif u_chos == "2":
        Share_arry.append(BMC_User)
        Share_arry.append(BMC_Pass)
        return Share_arry
    else:
        log._error("User.Input.Err")

def defalt_path(show_flags=True):
    log.json_set('Test_tmp','Running_flag','4')
    # Set EndTime To sost.json File
    log.json_set("Test_tmp","endT_time",now_time())
    # SSH Config Set Default and restart sshd
    log.os_run("sed -i 's/PermitEmptyPasswords yes/#PermitEmptyPasswords no/g' /etc/ssh/sshd_config")
    log.os_run("systemctl restart sshd")
    # Set multi mode Close
    log.json_set("Multimodal_stability","switch","0")
    # Set start/end wait time
    log.json_set("Test_tmp","StartWaitTimeCountdown","00")
    log.json_set("Test_tmp","EndWaitTimeCountdown","00")
    
    log.json_set("Test_Config","simple_test_flags","")

    # Set bash_profile Default
    log.os_run("yes | sost -f bash")

    # Get Now Test Status
    test_status = log.json_get("Test_tmp","test_status")
    # sost tips
    print('')
    log._pr("!!!SOST process is closing......Waiting!!!")

    test_status = log.json_get('Test_tmp','test_status').strip()
    if show_flags:
        if test_status == 'Pass':
            print('''\033[32m
    ════════════════════════════════════════════════════════
    ||         ███████                                    ||
    ||        ░██░░░░██                                   || 
    ||        ░██   ░██  ██████    ██████  ██████         ||
    ||        ░███████  ░░░░░░██  ██░░░░  ██░░░░          ||
    ||        ░██░░░░    ███████ ░░█████ ░░█████          ||
    ||        ░██       ██░░░░██  ░░░░░██ ░░░░░██         ||
    ||        ░██      ░░████████ ██████  ██████          ||
    ||        ░░        ░░░░░░░░ ░░░░░░  ░░░░░░           ||
    ════════════════════════════════════════════════════════\033[0m''')
        elif test_status == 'FAIL':
            from .sost_system_info_lib import fail_logo
            fail_logo(save_config=False)
            
        elif test_status == 'FAILc':
            from .sost_system_info_lib import failc_logo
            failc_logo(save_config=False)
        else:
            pass

        log._pr("===============================================================")
        log._pr("Test type        : " + log.json_get("Test_tmp","test_type"))
        log._pr("Test Count       : " + log.json_get("Test_tmp","test_count"))
        log._pr("Test Folder      : " + log.json_get("Test_tmp","test_folder_path"))
        log._pr("Test Status      : " + test_status)
        log._pr("Test Start Time  : " + log.json_get("Test_tmp","startT_time"))
        log._pr("Test End   Time  : " + log.json_get("Test_tmp","endT_time"))
        log._pr("===============================================================")

    # clear autoTest Config File
    log.os_run("rm -rf /root/.config/autostart/*")
    log.os_run("yes | sost -f bash")
    # Set Default swc config
    log.json_set("Test_tmp","swc_flags","0")
    log.json_set("Test_Config","max_count","")
    # Restore key information from/etc/passwd
    # Autologin root password flags set null
    log.os_run("sed -i 's/root::/root:x:/' /etc/passwd")
    # history
    count = log.json_get('Test_tmp','test_count').strip()
    if count != "0":
        test_type = log.json_get('Test_tmp','test_type')
        result_folder = log.json_get('Test_tmp','test_folder_path')
        test_result = log.json_get("Test_tmp","test_status")
        start_time = log.os_popen(f"cat {result_folder}/sost_start_time.txt").strip()
        bios_ver = log.os_popen(f"cat {result_folder}/system_info/fwinfo/fwinfo_0.txt | grep -i bios.ver | cut -d ':' -f 2 && cat {result_folder}/system_info/fwinfo/fwinfo_0.txt  | grep -i Bios-ReleaseTime | cut -d ':' -f 2 ").strip().replace("\n","")
        bmcc_ver = log.os_popen(f"cat {result_folder}/system_info/fwinfo/fwinfo_0.txt  | grep -i bmc.ver | cut -d ':' -f 2").strip()
        json_data = f'{{"time": "{start_time}", "type": "{test_type}", "count": {count}, "result": "{test_result}" , "bios.ver" : "{bios_ver}" , "bmc.ver" : "{bmcc_ver}"}}'
        log.os_run(f' touch /opt/sost/history && echo "{json_data}" >> /opt/sost/history')


def wait_time(runtime,flags):
    for i in reversed(range(int(runtime))):
        time.sleep(1)
        if len(str(i))==1:i=str('0'+str(i))
        print("\r< sost > Please Wait Times `Ctrl + c` exit() : {}s".format(str(i).strip()), end="", flush=True)
        if flags=='start':
            log.json_set('Test_tmp','StartWaitTimeCountdown',str(int(i)))
        elif flags=='end':
            log.json_set('Test_tmp','EndWaitTimeCountdown',str(int(i)))
        else:
            return
    print("", end="")

def wait_time_ctrl_C(wait,flags):
    try:
        wait_time(int(wait),flags)
    except:
        log._dmesg("user close sost test")
        defalt_path()
        result_html()
        exit()

#wait time and q exit()
def auto_test_wait_time(prompt,timeout):
    print(prompt,end="")
    result = [None]
    def input_thread():
        try:result[0] = input()
        except EOFError:result[0] = None
    thread = threading.Thread(target=input_thread)
    thread.start()
    thread.join(timeout)
    if not thread.is_alive():
        result[0] = "q"
    else:
        result[0] = "None"
    if result[0] == "q":exit()

# return Time
def now_time(): 
    return str(time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))

def check_stability_tools():
    tools = ["nvme","ipmitool","numactl"]
    no_install_arry = []
    for tool_name in tools:
        if log.os_popen(f"whereis {tool_name} | awk '{{print $2}}'").strip() == "":
            no_install_arry.append(tools)
    if len(no_install_arry) > 0:
        log._pr("Please install : "+str(no_install_arry[::]))
        log._error("Sost Tools Check Fail!")

    if not os.path.exists("/opt/MegaRAID/storcli"):
        log._warning("Storcli64 Not install!")

    log._pr("Sost Stability Tools check Success!")

def config_autologging():

    # Create gett@tty1.service
    if not os.path.exists('/etc/systemd/system/getty@tty1.service'):
        log.os_run("cp -rf /lib/systemd/system/getty@.service /etc/systemd/system/getty@tty1.service")
        log.os_run("chmod 777 /etc/systemd/system/getty@tty1.service")
        log.os_run("sed -i 's/noclear/autologin root --noclear/' /etc/systemd/system/getty@tty1.service")
        log.os_run("rm -rf /etc/systemd/system/getty.target.wants/getty@tty1.service")
        log.os_run("ln -s /etc/systemd/system/getty@tty1.service /etc/systemd/system/getty.target.wants/getty@tty1.service")
    # Sed root password flag -> NULL
    if log.os_popen("cat /etc/passwd | grep -i 'root::0:0' | wc -l").strip() == "0":
        log.os_run("sed -i '1s/x//' /etc/passwd")
    # 
    if not os.path.exists("/etc/systemd/system/getty@tty1.service.d/override.conf"):
        log.os_run("mkdir /etc/systemd/system/getty@tty1.service.d")
        log.os_run("touch /etc/systemd/system/getty@tty1.service.d/override.conf")
        log.os_run("chmod 777 /etc/systemd/system/getty@tty1.service.d/override.conf")
        log.os_run("echo '[Service]' >> /etc/systemd/system/getty@tty1.service.d/override.conf")
        log.os_run("echo '' >> /etc/systemd/system/getty@tty1.service.d/override.conf")
        log.os_run("echo 'ExecStart=' >> /etc/systemd/system/getty@tty1.service.d/override.conf")
        log.os_run("echo '' >> /etc/systemd/system/getty@tty1.service.d/override.conf")
        log.os_run("echo 'ExecStart=-/sbin/agetty --noissue --autologin root %I $TERM' >> /etc/systemd/system/getty@tty1.service.d/override.conf")
        log.os_run("echo '' >> /etc/systemd/system/getty@tty1.service.d/override.conf")
        log.os_run("echo 'Type=idle' >> /etc/systemd/system/getty@tty1.service.d/override.conf")
        log.os_run("echo '' >> /etc/systemd/system/getty@tty1.service.d/override.conf")
    
# Kylin Auto Login Set
def kylin_autologin():
    # Auto Create File Folder
    log.os_run("mkdir -p /usr/share/lightdm/lightdm.conf.d/")
    log.os_run("mkdir -p /etc/lightdm/")

    file_1 = "/usr/share/lightdm/lightdm.conf.d/60-kylin.conf"
    file_2 = "/etc/lightdm/lightdm.conf"
    file_3 = "/root/.profile"
    #touch aleardy file not clear text
    log.os_run(f"touch {file_1}")
    log.os_run(f"touch {file_2}")
    log.os_run(f"touch {file_3}")

    with open(file_1,"w") as f:
        f.write("[SeatDefaults]\n")
        f.write("user-session=mate\n")
        f.write("allow-guest=false\n")
        f.write("greeter-show-manual-login=true")
    if "autologin-guest=false" not in log.os_popen(f"cat {file_2} | tail -n 4"):
        log.os_run(f"echo [Seat:*] >> {file_2}")
        log.os_run(f"echo autologin-guest=false >> {file_2}")
        log.os_run(f"echo autologin-user=root >> {file_2}")
        log.os_run(f"echo autologin-user-timeout=0 >> {file_2}")
    with open(file_3,"w") as f:
        f.write('''if [ "$BASH" ]; then
  if [ -f ~/.bashrc ]; then
    . ~/.bashrc
  fi
fi 
mesg n 2> /dev/null || true''')
        f.flush()

# kylin GUI Auto Run env
def kylin_Gui_Run():
    config_autologging()
    if "multi-user.target" in log.os_popen("systemctl get-default").strip():
        log.os_run("yes | sost -f bash")
        with open('/root/.bash_profile','a') as f:
            f.write('sost -z')
    else:
        log.os_run("yes | sost -f bash")
        if not os.path.exists("/root/.config/autostart"):os.mkdir("/root/.config/autostart")
        log.os_run("rm -rf /root/.config/autostart/*")
        log.os_run("touch /root/.config/autostart/sost.desktop")
        log.os_run("echo '[Desktop Entry]' >> /root/.config/autostart/sost.desktop")
        log.os_run("echo 'Type=Application' >> /root/.config/autostart/sost.desktop")
        tmp = 'Exec=mate-terminal --window --maximize -x bash -c "sost -z;exec bash;"'
        log.os_run(f"echo '{tmp}' >> /root/.config/autostart/sost.desktop")
        log.os_run("echo 'Name=Sost_AutoStart' >> /root/.config/autostart/sost.desktop")
        log.os_run("echo 'Icon=system-run' >> /root/.config/autostart/sost.desktop")

def RHEL_Gui_Run():
    config_autologging()

    if '10.0' in log.os_popen("cat /etc/os-release | grep -w VERSION= | tr -d ' '"):
        log.os_run('systemctl set-default multi-user.target')
        log._dp("RHEL 10.0 Only Text Mode Running Test!")

    if "multi-user.target" in log.os_popen("systemctl get-default").strip():
        log._dp("RHEL Currently mode : text , Set Autologing Success!")
    else:
        log._dp("RHEL Currently mode :  GUI , Set Autologing Success!")
        log.os_run("yes | sost -f bash")
        if not os.path.exists("/root/.config/autostart"):os.mkdir("/root/.config/autostart")
        log.os_run("rm -rf /root/.config/autostart/*")
        log.os_run("touch /root/.config/autostart/sost.desktop")
        log.os_run("echo '[Desktop Entry]' >> /root/.config/autostart/sost.desktop")
        log.os_run("echo 'Type=Application' >> /root/.config/autostart/sost.desktop")
        tmp = 'Exec=gnome-terminal -- bash -c "sost -z; exec bash;"'
        log.os_run(f"echo '{tmp}' >> /root/.config/autostart/sost.desktop")
        log.os_run("echo 'Name=Sost_AutoStart' >> /root/.config/autostart/sost.desktop")
        log.os_run("echo 'Icon=system-run' >> /root/.config/autostart/sost.desktop")
        log.os_run("echo '' >> /root/.config/autostart/sost.desktop")
        if "AutomaticLogin" not in log.os_popen("cat /etc/gdm/custom.conf"):
            log.os_run("echo '[daemon]' >> /etc/gdm/custom.conf")
            log.os_run("echo 'AutomaticLoginEnable=true' >> /etc/gdm/custom.conf")
            log.os_run("echo 'AutomaticLogin=root' >> /etc/gdm/custom.conf")

#check os and set autologin
def autologin():
    os_ver = log.os_popen("cat /etc/os-release |grep 'PRETTY_NAME'")
    if "Kylin" in os_ver:
        kylin_autologin()
        kylin_Gui_Run()
    elif "openEuler" in os_ver:
        # GUI -> Text
        log.os_popen("systemctl set-default multi-user.target")
        config_autologging()
    elif "Ubuntu" in os_ver:
        # GUI -> Text
        log.os_popen("systemctl set-default multi-user.target")
        config_autologging()
    elif "BigCloud" in os_ver:
        # GUI -> Text
        log.os_popen("systemctl set-default multi-user.target")
        config_autologging()
    elif "CentOS" in os_ver:
        # GUI -> Text
        log.os_popen("systemctl set-default multi-user.target")
        config_autologging()
    elif "Red Hat" in os_ver:
        RHEL_Gui_Run()
    else:
        # GUI -> Text
        log.os_popen("systemctl set-default multi-user.target")
        config_autologging()
        log._pr("AuthLogingSys : Not Fount SYS_Ver Please check /etc/os-release")
    
    if log.os_popen("cat /etc/ssh/sshd_config | grep -i '#PermitEmptyPasswords'").strip() != "":
        log.os_run("sed -i 's/#PermitEmptyPasswords no/PermitEmptyPasswords yes/g' /etc/ssh/sshd_config")
        log.os_run("systemctl restart sshd")

# check .bash_profile
def os_env():
    # clear old sost log
    log.os_popen("rm -rf /opt/sost/log/*")
    # clear bash_profile sost -z
    if "sost" in log.os_popen("cat /root/.bash_profile | grep -i sost").strip():
        log.os_run("yes | sost -f bash")

    with open('/root/.bash_profile','a') as f:
            f.write('sost -z')

def end_test_logo():
    print('''════════════════════════════════════════
|               End Test               |
════════════════════════════════════════''')
    path = log.json_get("Test_tmp","test_folder_path").strip()
    if "failc.txt" in log.os_popen(f"ls -al {path}").strip():
        log.json_set("Test_tmp","test_status","FAILc")
        test_status = "FAILc"
    elif log.os_popen(f"ls -al {path} | grep -v failc.txt | grep -i fail.txt | wc -l").strip() !="0":
        log.json_set("Test_tmp","test_status","Fail")
        test_status = "Fail"
    else:
        log.json_set("Test_tmp","test_status","Pass")
        test_status = "Pass"
    count = log.json_get("Test_tmp", "test_count")
    type = log.json_get("Test_tmp","test_type")
    log._pr(f"Test_Type         : {type.strip()}")
    log._pr(f"Test_Count        : {count.strip()}")
    log._pr(f"Test_Status       : {test_status.strip()}")
    print()
    log._pr("Waiting for restart........")

# save time
def runTime(flags):
    count = log.json_get("Test_tmp", "test_count")
    if flags == "0":
        start_time_file_path = str(log.json_get("Test_tmp", "test_folder_path")) + "/debug/start_time.txt"
        with open(start_time_file_path,"w") as f:
            f.write(str(int(time.time())))
            f.flush()
            os.fsync(f.fileno())
    # save end_time
    elif flags == "1":
        end_time_file_path = str(log.json_get("Test_tmp", "test_folder_path")) + "/debug/end_time.txt"
        with open(end_time_file_path,"w") as f:
            f.write(str(int(time.time())))
            f.flush()
            os.fsync(f.fileno())
    # save last time
    elif flags == "2":
        last_time_file_path = str(log.json_get("Test_tmp", "test_folder_path")) + "/debug/last_time.txt"
        end_time_file_path = str(log.json_get("Test_tmp", "test_folder_path")) + "/debug/end_time.txt"
        now_timem = time.time()
        end_time = log.os_popen(f"cat {end_time_file_path}")
        result = str(int(now_timem) - int(end_time))
        if end_time == "" or now_timem == "": log._error("end.time.now.time.Error.Exit!")
        with open(last_time_file_path,"w") as f:
            f.write(str(result))
            f.flush()
            os.fsync(f.fileno())
    # Power off -> Os Run Time
    elif flags == "3":
        running_time_file_path = str(log.json_get("Test_tmp", "test_folder_path")) + "/running_time.txt"
        start_time_file_path = str(log.json_get("Test_tmp", "test_folder_path")) + "/debug/start_time.txt"
        end_time_file_path = str(log.json_get("Test_tmp", "test_folder_path")) + "/debug/end_time.txt"
        restart_time = str(int(log.os_popen(f"cat {start_time_file_path}")) - int(log.os_popen(f"cat {end_time_file_path}")))
        last_running_time = log.json_get("Test_tmp","running_time_now")
        log._dp(f"Last running time : {last_running_time} s")
        log._dp(f"Now running time  : {restart_time} s")
        log.json_set("Test_tmp","running_time_last",str(last_running_time))
        log.json_set("Test_tmp","running_time_now",str(restart_time))
        with open(running_time_file_path, "a") as f:
            if str(count)=="0":
                restart_time="FirstRun!"
            f.write("=" * 40 + "\n" + f"< sost > Last restart time : {restart_time} s\n< sost >  Nowcount\t\t : {count} times\n< sost >  NowTime \t\t : {now_time()}\n< sost >  TestType\t\t : {log.json_get('Test_tmp','test_type')}\n" + "=" * 40 + "\n")
            f.flush()
            os.fsync(f.fileno())
        
        log._dp(f"Last restart time : {restart_time} s")
    # sost running time
    elif flags == "4":
        start_time_file_path = str(log.json_get("Test_tmp", "test_folder_path")) + "/debug/start_time.txt"
        start_time = open(start_time_file_path, "r").read()
        sost_running_time = int(time.time()) - int(start_time)
        save_file = str(log.json_get("Test_tmp", "test_folder_path")) + "/debug/sost_running_time.log"
        with open(save_file, "a") as f:
            f.write("=" * 40 + "\n")
            f.write(f"< sost > sost Running time : {str(sost_running_time)} s\n< sost > sost NowCount     : {str(count)} times\n< sost > NowTime \t\t : {now_time()}\n"+f"sost Running time : {str(sost_running_time)} s"+"\n")
            f.write("=" * 40 + "\n")
            os.fsync(f.fileno())
    else:
        log._error("runTime.Exit.flags")

# echo dmesg error | fail | unknown | info
def dmesg_show():
    print('=' * 60)
    print("Show dmesg error and fail detailed information Please look dmesg_log")
    print(log.os_popen("dmesg | grep -iE 'fail|error'"))
    print('=' * 60)

# clear terminal print
def clp(): 
    if log.json_get("debug","debug_flags",filename="debug") == "0":
        os.system("clear")
    return

# Config_json
def change_json(count, test_type, path, run_command):
    # if Test Config no Null Init Config.json
    if log.json_get("Test_tmp", "test_type") != "" or log.json_get("Test_tmp", "test_count") != "" or log.json_get("Test_tmp", "test_folder_path") != "":
        log.json_set("Test_tmp","test_type","")
        log.json_set("Test_tmp","test_count","")
        log.json_set("Test_tmp","test_folder_path","")
        log.json_set("Test_tmp","run_command","")
    
    if str(str(count).strip()) == "0":
        log.json_set('Test_tmp','test_type',test_type)
        log.json_set('Test_tmp','test_count',"0")
        log.json_set('Test_tmp','test_folder_path',path)
        log.json_set('Test_tmp','run_command',run_command)    
    else:
        log.json_set('Test_tmp','test_count',str(int(log.json_get("Test_tmp", "test_count")) + 1))

# User.input.TestTYpe.Init.Folder
def init_stability_path(test_type):
    # INIT Test type Folder
    path = log.json_get("Test_Config", "Result_path")
    # result folder path
    if log.json_get("Multimodal_stability","switch").strip()=="1":
        result_folder_path = f"{path}/sost_mulit_result/{test_type}"
    else:
        result_folder_path = f"{path}/{test_type}"
    if not os.path.exists(result_folder_path):
        # create new folder
        log.os_run(f'mkdir -p {result_folder_path}')
    else:
        #result backup to sost_old_folder folder
        result_folder_bak = f"{path}/sost_old_folder"
        if not os.path.exists(result_folder_bak):os.makedirs(result_folder_bak)
        # backup Old stability log
        count = log.os_popen(f"cat {result_folder_path}/count.txt").strip()
        start_time = log.os_popen(f"cat {result_folder_path}/sost_start_time.txt").strip()
        result = "Pass"
        if "fail" in log.os_popen(f"ls {result_folder_path}"):
            result = "Fail"
        log.os_run(f"mv {result_folder_path} {result_folder_bak}/{test_type}_{count}_{result}_{start_time}")
        # create new folder
        log.os_run(f'mkdir -p {result_folder_path}')
    
    # create debug system_folder
    log.os_run(f"mkdir -p {result_folder_path}/system_info && mkdir -p {result_folder_path}/debug",flags='no-log')

    touch_file_arry = ['count.txt','sost_start_time.txt','debug/start_time.txt','debug/last_time.txt','debug/end_time.txt']
    for filename in touch_file_arry:
        log.os_run(f"touch {result_folder_path}/{filename}",flags='no-log')
        if filename == 'count.txt':
            log.os_run(f"echo 0 > {result_folder_path}/count.txt",flags='no-log')
        elif filename == 'sost_start_time.txt':
            now_timeee = now_time()
            log.os_run(f"echo '{now_timeee}' > {result_folder_path}/sost_start_time.txt",flags='no-log')
            log.json_set("Test_tmp","startT_time",now_timeee)
            log.json_set("Test_tmp","endT_time","")
        else:
            continue
    #backup sost.json to result folder
    log.os_run(f"cp -rf /opt/sost/config/sost.json {result_folder_path}/debug/",flags='no-log')
    #save systeminfo -> ps -aux 
    log.os_run(f"ps -aux >> {result_folder_path}/debug/sost_ps_aux.log",flags='no-log')
    #save systeminfo -> cat /proc/meminfo
    log.os_run(f"cat /proc/meminfo >> {result_folder_path}/debug/sost_meminfo.log",flags='no-log')
    #save systeminfo -> /proc/cmdline
    log.os_run(f"cat /proc/cmdline >> {result_folder_path}/debug/sost_cmdline.log",flags='no-log')
    #save systeminfo -> devices
    log.os_run(f"ls /dev >> {result_folder_path}/debug/sost_devices.log",flags='no-log')
    #save systeminfo -> ssh_users
    log.os_run(f"netstat -anlt  | grep -i :22 >> {result_folder_path}/debug/sost_ssh_user.log",flags='no-log')

    # Init Json File
    log.json_set("Test_tmp", "test_status","NA")

    # Return result_Folder_path
    return result_folder_path

def max_count_logo():

    max_count = log.json_get("Test_Config","max_count")
    now_count = log.json_get("Test_tmp","test_count")
    if not max_count == "":
        try:
            if int(now_count)+1 >= int(max_count):
                if log.json_get("Multimodal_stability","switch") != "1":
                    print(f'''
════════════════════════════════════════════════════════════════════════════════
||                                                                            ||    
||       ████████                    ██         ████████               ██     ||
||     ██░░░░░░                    ░ ██        ░██░░░░░               ░██     ||
||     ░██         ██████   ██████ ██████      ░██        ███████      ██     ||
||     ░█████████ ██░░░░██ ██░░░░ ░░░██░  █████░███████ ░░██░░░██  ██████     ||
||     ░░░░░░░░██░██   ░██░░█████   ░██  ░░░░░ ░██░░░░   ░██  ░██ ██░░░██     ||
||            ░██░██   ░██ ░░░░░██  ░██        ░██       ░██  ░██░██  ░██     ||
||     ████████ ░░██████  ██████   ░░██        ░████████ ███  ░██░░██████     ||
||     ░░░░░░░░   ░░░░░░  ░░░░░░     ░░        ░░░░░░░░ ░░░   ░░  ░░░░░░      ||
||                                                                            ||           
════════════════════════════════════════════════════════════════════════════════
||     The maximum number of tests set by the user has been reached! exit!    ||
════════════════════════════════════════════════════════════════════════════════
||       \tMax_Count : {max_count.ljust(4)}              Now_Count : {now_count.ljust(4)}\t\t      ||          
════════════════════════════════════════════════════════════════════════════════''')
                    return True,"default"
                else:
                    print('''
══════════════════════════════════════════════════════════════════════════════════════════
|     ████     ████          ██ ██   ██         ████     ████               ██           |
|    ░██░██   ██░██         ░██░░   ░██        ░██░██   ██░██              ░██           |
|    ░██░░██ ██ ░██ ██   ██ ░██ ██ ██████      ░██░░██ ██ ░██  ██████      ░██  █████    |
|    ░██ ░░███  ░██░██  ░██ ░██░██░░░██░  █████░██ ░░███  ░██ ██░░░░██  ██████ ██░░░██   |
|    ░██  ░░█   ░██░██  ░██ ░██░██  ░██  ░░░░░ ░██  ░░█   ░██░██   ░██ ██░░░██░███████   |
|    ░██   ░    ░██░██  ░██ ░██░██  ░██        ░██   ░    ░██░██   ░██░██  ░██░██░░░░    |
|    ░██        ░██░░██████ ███░██  ░░██       ░██        ░██░░██████ ░░██████░░██████   |
|    ░░         ░░  ░░░░░░ ░░░ ░░    ░░        ░░         ░░  ░░░░░░   ░░░░░░  ░░░░░░    |
══════════════════════════════════════════════════════════════════════════════════════════''')
                    log._pr("The current test has been completed and we will proceed to the next test!")
                    log._pr("正在进行下一个模型测试,请勿关闭此窗口!耐心等待系统重启!")
                    now_type = log.json_get("Test_tmp","test_type")
                    if now_type == "AClost":
                        log._pr("=" * 60 + "\nSost has enabled the multi model stability testing function, current testing type: aclost")
                        log._pr("Sost已开启多模型稳定性测试功能,已完成测试模型：aclost\n"+"=" * 60)
                        log.json_set("Multimodal_stability","count_aclost","0")
                        os.system("sost -s")
                        return True,'mulit'
                    elif now_type == "reboot":
                        log._pr("=" * 60 + "\nSost has enabled the multi model stability testing function, current testing type: reboot")
                        log._pr("Sost已开启多模型稳定性测试功能,已完成测试模型：reboot\n"+"=" * 60)
                        log.json_set("Multimodal_stability","count_reboot","0")
                        os.system("sost -s")
                        return True,'mulit'
                    elif now_type == "powercycle":
                        log._pr("=" * 60 + "\nSost has enabled the multi model stability testing function, current testing type: powercycle")
                        log._pr("Sost已开启多模型稳定性测试功能,已完成测试模型：powercycle\n"+"=" * 60)
                        log.json_set("Multimodal_stability","count_powercycle","0")
                        os.system("sost -s")
                        return True,'mulit'
                    elif now_type == "powerreset":
                        log._pr("=" * 60 + "\nSost has enabled the multi model stability testing function, current testing type: powerreset")
                        log._pr("Sost已开启多模型稳定性测试功能,已完成测试模型：powerreset\n"+"=" * 60)
                        log.json_set("Multimodal_stability","count_powerreset","0")
                        os.system("sost -s")
                        return True,'mulit'
                    else:
                        log._error("max_count_logo.now_type.Err!")
        except:
            log._dp("Max_Count read Err!")
            return False,"mulit"

def test_type_logo(test_type, count):
    version = log.json_get("sost","Version",filename='version')
    test_status = log.json_get("Test_tmp","test_status").strip()
    if test_status == "FAILc":
        test_status = "\033[33mFAILc\033[0m".ljust(23)
    elif test_status == "FAIL":
        test_status = "\033[31mFAIL\033[0m".ljust(23)
    elif test_status == "Pass":
        test_status = "\033[32mPass\033[0m".ljust(23)
    else:
        test_status = "NA".ljust(14)
    if str(count)=="0":test_status="NA".ljust(14)
    print(f'''══════════════════════════════════════════════════════
||                                     ██           ||
||                                    ░██           ||
||           ██████  ██████   ██████ ██████         ||
||          ██░░░░  ██░░░░██ ██░░░░ ░░░██░          ||
||         ░░█████ ░██   ░██░░█████   ░██           ||
||          ░░░░░██░██   ░██ ░░░░░██  ░██           ||
||          ██████ ░░██████  ██████   ░░██          ||
||         ░░░░░░   ░░░░░░  ░░░░░░     ░░           ||
══════════════════════════════════════════════════════
|| sost.ver : {version.ljust(10)}   || State : {str(test_status)}|| 
||--------------------------------------------------||
|| Type : {str(test_type).ljust(16)} || Count : {str(count).ljust(5)}         ||
══════════════════════════════════════════════════════''')
def Timed_operation_mode():
    clp()
    # ----------------------------------------------------------------------------------------------
    print(f'''═══════════════════════════════════════════════════════════════════════════════════════
||                                                                                   ||
||     ████████                    ██         ███████                                ||
||    ██░░░░░░                    ░██        ░██░░░░██                     █████     ||  
||   ░██         ██████   ██████ ██████      ░██    ░██  ██████  ███████  ██░░░██    ||
||   ░█████████ ██░░░░██ ██░░░░ ░░░██░  █████░██    ░██ ██░░░░██░░██░░░██░██  ░██    ||
||   ░░░░░░░░██░██   ░██░░█████   ░██  ░░░░░ ░██    ░██░██   ░██ ░██  ░██░░██████    ||
||          ░██░██   ░██ ░░░░░██  ░██        ░██    ██ ░██   ░██ ░██  ░██ ░░░░░██    ||
||    ████████ ░░██████  ██████   ░░██       ░███████  ░░██████  ███  ░██  █████     ||
||   ░░░░░░░░   ░░░░░░  ░░░░░░     ░░        ░░░░░░░    ░░░░░░  ░░░   ░░  ░░░░░      ||
||                                                              Auther:Xiaodong Fan  ||
||═══════════════════════════════════════════════════════════════════════════════════||
||    1 . reboot         |    5 . systemctl reboot    |                              ||
||    2 . power cycle    |    6 . init 6              |                              ||
||    3 . power reset    |    7 . poweroff -r         |                              ||
||    4 . AClost         |    8 . shutdown -r         |                              ||
||═══════════════════════════════════════════════════════════════════════════════════||''')
    test_chose = log._in("You Chose : ")
    clp()
    # ----------------------------------------------------------------------------------------------
    print(f'''═══════════════════════════════════════════════════════════════════════════════════════
||                                                                                   ||
||     ████████                    ██         ███████                                ||
||    ██░░░░░░                    ░██        ░██░░░░██                     █████     ||  
||   ░██         ██████   ██████ ██████      ░██    ░██  ██████  ███████  ██░░░██    ||
||   ░█████████ ██░░░░██ ██░░░░ ░░░██░  █████░██    ░██ ██░░░░██░░██░░░██░██  ░██    ||
||   ░░░░░░░░██░██   ░██░░█████   ░██  ░░░░░ ░██    ░██░██   ░██ ░██  ░██░░██████    ||
||          ░██░██   ░██ ░░░░░██  ░██        ░██    ██ ░██   ░██ ░██  ░██ ░░░░░██    ||
||    ████████ ░░██████  ██████   ░░██       ░███████  ░░██████  ███  ░██  █████     ||
||   ░░░░░░░░   ░░░░░░  ░░░░░░     ░░        ░░░░░░░    ░░░░░░  ░░░   ░░  ░░░░░      ||
||                                                              Auther:Xiaodong Fan  ||
||═══════════════════════════════════════════════════════════════════════════════════||
||               1 . WaitTime                |             2 . Process               ||
||═══════════════════════════════════════════════════════════════════════════════════||''')
    chose = log._in("You Chose -> Enter 1 : ")
    if chose == "":chose == '1'
    if chose != '1' and chose != '2':log._error("User.Input.Error -> Timed_operation_mode() -> chose")
    clp()
    # ----------------------------------------------------------------------------------------------

    print(f'''═══════════════════════════════════════════════════════════════════════════════════════
||                                                                                   ||
||     ████████                    ██         ███████                                ||
||    ██░░░░░░                    ░██        ░██░░░░██                     █████     ||  
||   ░██         ██████   ██████ ██████      ░██    ░██  ██████  ███████  ██░░░██    ||
||   ░█████████ ██░░░░██ ██░░░░ ░░░██░  █████░██    ░██ ██░░░░██░░██░░░██░██  ░██    ||
||   ░░░░░░░░██░██   ░██░░█████   ░██  ░░░░░ ░██    ░██░██   ░██ ░██  ░██░░██████    ||
||          ░██░██   ░██ ░░░░░██  ░██        ░██    ██ ░██   ░██ ░██  ░██ ░░░░░██    ||
||    ████████ ░░██████  ██████   ░░██       ░███████  ░░██████  ███  ░██  █████     ||
||   ░░░░░░░░   ░░░░░░  ░░░░░░     ░░        ░░░░░░░    ░░░░░░  ░░░   ░░  ░░░░░      ||
||                                                              Auther:Xiaodong Fan  ||
||═══════════════════════════════════════════════════════════════════════════════════||''')
    if chose == '1':
        waitTime = log._in("Enter the time you want to wait -> Enter 3600s : ").strip()
        log._pr(f"Please wait patiently for {str(waitTime)} seconds before the SOST starts to run automatically.")
        try:float(waitTime)
        except:log._error("User.Input.Error()")
        start_end_time(waitTime)
        wait_time_ctrl_C(waitTime,flags='start')
        clp()
    elif chose == '2':
        clp()
        print(f'''═══════════════════════════════════════════════════════════════════════════════════════
||                                                                                   ||
||     ████████                    ██         ███████                                ||
||    ██░░░░░░                    ░██        ░██░░░░██                     █████     ||  
||   ░██         ██████   ██████ ██████      ░██    ░██  ██████  ███████  ██░░░██    ||
||   ░█████████ ██░░░░██ ██░░░░ ░░░██░  █████░██    ░██ ██░░░░██░░██░░░██░██  ░██    ||
||   ░░░░░░░░██░██   ░██░░█████   ░██  ░░░░░ ░██    ░██░██   ░██ ░██  ░██░░██████    ||
||          ░██░██   ░██ ░░░░░██  ░██        ░██    ██ ░██   ░██ ░██  ░██ ░░░░░██    ||
||    ████████ ░░██████  ██████   ░░██       ░███████  ░░██████  ███  ░██  █████     ||
||   ░░░░░░░░   ░░░░░░  ░░░░░░     ░░        ░░░░░░░    ░░░░░░  ░░░   ░░  ░░░░░      ||
||                                                              Auther:Xiaodong Fan  ||
||═══════════════════════════════════════════════════════════════════════════════════||
||                   1. PID                |          2. ProcessName                 ||
||═══════════════════════════════════════════════════════════════════════════════════||''')
        chose = log._in('chose Enter -> 1 : ')
        
        def pid_process(pid_num):
            try:float(pid_num)
            except:log._error("User.Input.Error() -> Timed_operation_mode() -> pid_num")
            if log.os_popen(f'ps -p {pid_num.strip()} | wc -l').strip() == '1':
                log._error(f"PID Not Found : \n{log.os_popen(f'ps -p {pid_num}')}")
            log._pr('='*30)
            log._pr(f"PidInfo : \n{log.os_popen(f'ps -p {pid_num}')}")
            log._pr('='*30)
            log._pr("Wait 5 seconds to start monitoring the end of the process!")
            wait_time_ctrl_C('5',flags='')
            log._pr('')
            clp()
            print(f'''═══════════════════════════════════════════════════════════════════════════════════════
||                                                                                   ||
||     ████████                    ██         ███████                                ||
||    ██░░░░░░                    ░██        ░██░░░░██                     █████     ||  
||   ░██         ██████   ██████ ██████      ░██    ░██  ██████  ███████  ██░░░██    ||
||   ░█████████ ██░░░░██ ██░░░░ ░░░██░  █████░██    ░██ ██░░░░██░░██░░░██░██  ░██    ||
||   ░░░░░░░░██░██   ░██░░█████   ░██  ░░░░░ ░██    ░██░██   ░██ ░██  ░██░░██████    ||
||          ░██░██   ░██ ░░░░░██  ░██        ░██    ██ ░██   ░██ ░██  ░██ ░░░░░██    ||
||    ████████ ░░██████  ██████   ░░██       ░███████  ░░██████  ███  ░██  █████     ||
||   ░░░░░░░░   ░░░░░░  ░░░░░░     ░░        ░░░░░░░    ░░░░░░  ░░░   ░░  ░░░░░      ||
||                                                              Auther:Xiaodong Fan  ||
||═══════════════════════════════════════════════════════════════════════════════════||
||            PID process monitoring is turned on do not turn off SOST!              ||
||═══════════════════════════════════════════════════════════════════════════════════||
< sost > Wait for the process to end ......
< sost > Starttime : {str(time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))}
< sost > Waiting . . . . . . . . . [-.-]''')
            while True:
                time.sleep(2)
                if log.os_popen(f'ps -p {pid_num.strip()} | wc -l',flags='no-log').strip() == '1':
                    break

        if chose == "":chose == '1'
        if chose != '1' and chose != '2':log._error("User.Input.Error -> Timed_operation_mode() -> chose")
        if chose == '1':
            pid_num = log._in("pid_num : ").strip()
            pid_process(pid_num)
        elif chose == '2':
            process_name = log._in('Process Name : ')
            log._pr('='*60)
            log._pr(f'''\n\n{log.os_popen(f"ps -aux | grep -i '{process_name}' | grep -v grep")}''')
            log._pr('='*60)
            pid_num = log._in("pid_num : ").strip()
            pid_process(pid_num)
    else:
        log._error("User.Input.Exit() -> ")
    
    return test_chose

def print_firework():
    import random
    import time
    import os
    num_patterns = 5
    num_explosions = 1
    max_star_count = 5
    speed = 0.5
    """
    绘制五颜六色的烟花爆炸效果

    :param num_patterns: 启动时的烟花形状数量（默认5次）
    :param num_explosions: 每次爆炸的层数（默认1层）
    :param max_star_count: 每层烟花最多的星星数量（默认12颗星星）
    :param speed: 每层爆炸的延时（默认0.1秒）
    """

    # 定义颜色的 ANSI 转义序列（直接放在函数内部）
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    RESET = "\033[0m"  # 重置颜色

    # 颜色列表
    colors = [RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN]

    # 预设的烟花启动形状（即最上面的 *）
    firework_patterns = [
        "        *        ",
        "      *   *      ",
        "    *       *    ",
        "  *           *  ",
        " *             * ",
        "  *           *  ",
        "    *       *    ",
        "      *   *      ",
        "        *        "
    ]

    # 打印烟花前的效果
    os.system('cls' if os.name == 'nt' else 'clear')  # 清屏
    print("< sost > Fireworks show ")
    # 给最上面的 * 加上颜色
    for _ in range(num_patterns):  # 控制烟花的起始形状爆炸次数
        color = random.choice(colors)  # 随机选择一种颜色
        print(color + random.choice(firework_patterns) + RESET)  # 打印带颜色的烟花形状
        time.sleep(0.1)  # 等待一段时间，再显示下一帧

    # 烟花爆炸效果：模拟星星从中心向外扩散
    for i in range(1, num_explosions + 1):  # 控制爆炸层数
        for _ in range(random.randint(5, max_star_count)):  # 每层随机生成一定数量的星星
            color = random.choice(colors)  # 随机选择一种颜色
            offset_x = random.randint(-i, i)  # 随机水平偏移量
            offset_y = random.randint(-i, i)  # 随机垂直偏移量
            # 输出带颜色的星号，模拟烟花从中心扩散
            print(color + " " * (7 + offset_x) + "*" + " " * (7 - offset_y) + RESET)
        time.sleep(speed)  # 控制烟花爆炸速度
    print('\033[0m')
    print("\033[42m< sost > Happy new year 2025. I wish you good health and all the best !\033[0m")
    print("< sost > After 3 seconds, start SOST !")
    time.sleep(3)

# print logo
def logo(release_time, version):
    # 烟花
    #try:print_firework()
    #except:pass
    clp()
    bmc_chip = bmc_Chip()[0]
    version = version.ljust(7)
    if "d" in version.lower() or "debug" in version.lower():
        version = "\033[31m"+version.ljust(7)+"\033[0m"
    else:
        version = "\033[32m"+version.ljust(7)+"\033[0m"
    # 原始代码部分，保持不变
    print(f'''════════════════════════════════════════════════════════════════════════════
|                                             ░██                          |
|                    ██████  ██████   ██████ ██████                        |
|                   ██░░░░  ██░░░░██ ██░░░░ ░░░██░                         |
|                  ░░█████ ░██   ░██░░█████   ░██                          |
|                   ░░░░░██░██   ░██ ░░░░░██  ░██                          |
|                   ██████ ░░██████  ██████   ░░██                         |
|                  ░░░░░░   ░░░░░░  ░░░░░░     ░░     Auther:Xiaodong Fan  |
|═══════════════════════════════════════════════════════════════════════════''')
    print(f"|    ReTime:{release_time.ljust(11)}     Ver.{version} "+f"BMC_Chip:\033[33m{bmc_chip.ljust(18)}\033[0m|")
    print('''|══════════════════════════════════════════════════════════════════════════|
|   1 . reboot         |    5 . systemctl reboot   |   9. Test Tools       |
|   2 . power cycle    |    6 . init 6             |  10. other  Test      |
|   3 . power reset    |    7 . poweroff -r        |  11. Timed operation  |
|   4 . AClost         |    8 . shutdown -r        |  12. Mulit Test       |
|══════════════════════════════════════════════════════════════════════════|
|  13 . BMC Remote Power reset     |  17 . BMC Remote raw 0x06 0x02        |
|  14 . BMC Remote Power cycle     |  18 . BMC Power On/Off                | 
|  15 . BMC Remote bmc reset warm  |  19 . NA                              |
|  16 . BMC Remote bmc reset cold  |  20 . update sost  (OTA)              |
════════════════════════════════════════════════════════════════════════════''')

def smtp_send_result(text):
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import smtplib
    global server_stmp
    smtp_server = log.json_get("smtp","smtp_server")
    smtp_port = int(log.json_get("smtp","smtp_port"))
    sender_email = log.json_get("smtp","sender_email")
    receiver_email = log.json_get("smtp","receiver_email")
    password = log.json_get("smtp","pop3_password")
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = 'Sost Stability Fail Tips!'
    msg.attach(MIMEText(text, 'plain'))
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

