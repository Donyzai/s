import argparse
import os
import sys
import json
import time

def json_load(key, value):
    if value == 'Version' or 'Release_Time':
        json_filename = '/opt/sost/config/sost_version.json'
    else:
        json_filename = '/opt/sost/config/sost.json'
    config = open(json_filename, "r")
    config = json.load(config)
    data = config[key][value]
    return data

def json_set(class_name, key, new_value):
    json_filename = '/opt/sost/config/sost.json'
    if class_name == 'debug':
        json_filename = '/opt/sost/config/debug.json'
    with open(json_filename, 'r') as file:
        data = json.load(file)
    data[class_name][key] = new_value
    with open(json_filename, 'w') as file:
        json.dump(data, file, indent=4)
        file.flush()

def debug_info():
    try:
        if sys.argv[1] == "debug":
            try:
                if sys.argv[2] == "help":
                    print('-'*40)
                    print('sost debug 0x00 -> debug flags = 0')
                    print('sost debug 0x01 -> debug flags = 1')
                    print('sost debug 0x02 -> debug flags = 2')
                    print('sost debug 0x03 -> debug flags = 3')
                    print('-' * 40)

                elif sys.argv[2] == "0x00":
                    print("<sost> Debug flags setting : 0")
                    json_set("debug","debug_flags","0")
                    exit()
                elif sys.argv[2] == "0x01":
                    print("<sost> Debug flags setting : 1")
                    json_set("debug","debug_flags","1")
                    exit()
                elif sys.argv[2] == "0x02":
                    print("<sost> Debug flags setting : 2")
                    json_set("debug", "debug_flags", "2")
                    exit()
                elif sys.argv[2] == "0x03":
                    print("<sost> Debug flags setting : 3")
                    json_set("debug", "debug_flags", "3")
                    exit()
                else:
                    return 0
            except:
                return 0

        if sys.argv[1] == "update":
            try:
                print("<sost> Update sost tool !")
                os.system("cd /opt/sost && python3 -c 'from lib.sost_public_lib import update_sost;update_sost()'")
            except:
                return 0
        if sys.argv[1] == "dony":
            print('dony')
    except:
        return 0

def parser_test():
    # Create argument parser with basic configuration
    parser = argparse.ArgumentParser(
        prog="sost",
        epilog=">> Thanks for using sost ! Author: Fanxiaodong <<",
        add_help=True,
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Register visible parameters
    # >> help=argparse.SUPPRESS Hide parameters from help documentation
    parser.add_argument("sost [args]", nargs='?', help="Command to execute")
    parser.add_argument("-a", "--autologin", action="store_true", help="Enable auto-login for sost")
    parser.add_argument("-b", "--bmclog_check", action="store_true", help="Check BMC log errors")
    parser.add_argument("-c", "--config", action="store_true", help="Modify sost configuration.")
    # parser.add_argument("-c", "--config", nargs='*',
    #                    help="Modify sost configuration.\n"
    #                         "Usage:\n"
    #                         "  sost -c open              # Directly open configuration file\n"
    #                         "  sost -c get <OBJECT>      # Get configuration (e.g., 'sost -c get 2')\n"
    #                         "  sost -c set <OBJECT> <KEY> <VALUE>  # Set configuration")
    parser.add_argument("-d", "--dmesg_check", action="store_true", help="Check dmesg errors")
    parser.add_argument("-e", "--exittest", action="store_true", help="Run exit test")
    parser.add_argument("-f", "--fix", action="store_true", help="Repair sost environment")
    parser.add_argument("-k", "--killall", action="store_true", help="Kill all sost processes")
    parser.add_argument("-m", "--testmode", action="store_true", help="Enable test mode")
    parser.add_argument("-o", "--output", action="store_true", help="Generate stability test report")
    parser.add_argument("-s", "--start", action="store_true", help="Start sost tool execution")
    parser.add_argument("-u", "--uninstall", action="store_true", help="Uninstall sost tools")
    parser.add_argument("-v", "--version", action="store_true", help="Show sost version")
    parser.add_argument("-w", "--webconsole", action="store_true",help="Launch sost web console")
    parser.add_argument("-z", "--continuee", action="store_true", help="Continue test execution")
    parser.add_argument("-i", "--info", action="store_true", help="Query server specific information")
    parser.add_argument("-sensor", "--sensor", action="store_true", help="Collect IPMI sensor data")

    # Hidden parameters for advanced users or debugging
    parser.add_argument("-D", "--debug", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(f"-i1", f"--in1",action="store",help=argparse.SUPPRESS)
    parser.add_argument(f"-i2", f"--in2",action="store",help=argparse.SUPPRESS)
    parser.add_argument(f"-i3", f"--in3",action="store",help=argparse.SUPPRESS)

    args = parser.parse_args()

    if args.debug:
        print("<sost> Debug mode enabled - detailed logs will be output")
        print('===========================================================')
        print("Entered debug mode, displaying all input parameters:")
        print('===========================================================')
        for i in range(1,11):
            param_value = getattr(args, f'in{i}', 'Not provided')
            print(f"in{i} value: {param_value if param_value is not None else 'Not provided'}")

    def config_help_d():
        print('-----------------------------------------------------')
        print("sost -c get -in1 [Config_Object] -in2 [Config_Key]")
        print("sost -c set -in1 [Config_Object] -in2 [Config_Key] -in3 [New_Value]")
        print("sost -c open  Open sost.json configuration file")
        print('-----------------------------------------------------')

    if args.config:
        os.system("vim /opt/sost/config/sost.json")
        # try:sys.argv[3]
        # except:os.system("vim /opt/sost/config/sost.json")

        # try:
        #     if sys.argv[2] == "open":
        #         os.system("vim /opt/sost/config/sost.json")
        #         exit()
        #     # parms1 = get / set 
        #     parms1 = args.in1
        #     # parms2 = config object
        #     parms2 = args.in2
        #     # parms3 = config key
        #     parms3 = args.in3
        #     # parms4 = config new_value
        #     parms4 = args.in4
        #     # command 
        #     # sost --config -i1 get -i2 Test_Config -i3 Result_path
        #     print('-'*70)
        #     print(f"<sost> parms1 Configuration operation type : {parms1}")
        #     print(f"<sost> parms2 Configuration object         : {parms2}")
        #     print(f"<sost> parms3 Configuration key            : {parms3}")
        #     print(f"<sost> parms4 New configuration value      : {parms4}")
        #     print('-'*70)
        #     if parms1 == 'get':
        #         print("sost -c get")
        #         if parms2 == None and parms3 == None:
        #             print("<sost> parms2 and parms3 are required for 'get' operation")
        #         elif parms2 != None and parms3 == None:
        #             print("<sost> parms3 is required for 'get' operation")
        #         else:
        #             print(json_load(parms2, parms3))
        #     elif parms1 == 'set':
        #         print("sost -c set")
        #         if parms2 == None or parms3 == None or parms4 == None:
        #             print("<sost> parms2, parms3, and parms4 are required for 'set' operation")
        #         else:
        #             json_set(parms2, parms3, parms4)
        #             print(f"<sost> Set {parms2} {parms3} to {parms4} Success!")
        #     elif parms1 == "open":
        #         print("sost -c open")
        #         os.system("vim /opt/sost/config/sost.json")
        #     else:
        #         config_help_d()
        # except:
        #     config_help_d()

    if args.bmclog_check:
        os.system('''cd /opt/sost && python3 -c "from lib.sost_system_info_lib import bmclog_check;bmclog_check('','')"''')

    if args.version:
        print(f'sost ver : {str(json_load("sost", "Version"))} ReleaseTime : {str(json_load("sost", "Release_Time"))}')

    if args.autologin:
        def help_d():
            print("=======================[Autologin]==========================")
            print(" 1. sost -a enable         enable System Autologin")
            print(" 2. sost -e disable        disable System Autologin")
            print("===========================================================")
        try:
            argv2_value = sys.argv[2]
            if argv2_value == "enable":
                os.system("cd /opt/sost && python3 -c 'from lib.sost_public_lib import autologin;autologin()'")
                print("< sost > Enable  Autologin!")
            elif argv2_value == "disable":
                os.system("sed -i 's/root::/root:x:/' /etc/passwd")
                print("< sost > Disable Autologin!")
        except:
            help_d()

    if args.exittest:

        def help_d():
            print("=======================[ExitTest]==========================")
            print(" 1. sost -e all         All Fail Not Exit!")
            print(" 2. sost -e default     default Settings")
            print("===========================================================")
        try:
            argv2_value = sys.argv[2]
            if argv2_value == "all":
                print("<sost> Fail exit -> All Fail Not exit!")
                json_set("Test_Config","fail_exit_flags","0")
            elif argv2_value == "default":
                print("<sost> Fail exit -> Default restored")
                json_set("Test_Config","fail_exit_flags","1")
            else:
                help_d()
        except:
            help_d()

    if args.testmode:
        def help_d():
            print("=======================[TestMode]==========================")
            print(" 1. sost -m bmc         Only collect information about BMC ")
            print(" 2. sost -m os          Only collect information about OS  ")
            print(" 3. sost -m simple      Only conduct stability testing")
            print(" 4. sost -m default     default Settings")
            print("===========================================================")
        try:
            argv2_value = sys.argv[2]
            if argv2_value == "bmc":
                json_set("Test_Config","simple_test_flags","bmc")
                print("<sost> Set Bmc Mode Success!")
            elif argv2_value == "os":
                json_set("Test_Config","simple_test_flags","os")
                print("<sost> Set OS Mode Success!")
            elif argv2_value == "simple":
                json_set("Test_Config","simple_test_flags","simple")
                print("<sost> Set Simple Mode Success!")
            elif argv2_value == "default":
                json_set("Test_Config","simple_test_flags","")
                print("<sost> Set Default Mode Success!")
            else:
                help_d()
                print("<sost> sost -m {value} -> value Input Err!")
        except:
            help_d()
            print("<sost> sost -m {value} -> value Input Err!")

    if args.output:
        try:
            if input("<sost> Do you want to collect information (你想要收集日志吗)? [y/n] : ").strip() == "n":exit()
            print("<sost> CollectingInfo......Waiting...... 正在收集请耐心等待......")
            folder_name = 'os_info_'+str(time.strftime("%Y%m%d_%H%M%S", time.localtime()))
            os.system(f"mkdir -p {folder_name}")
            os.system(f"dmesg > /root/{folder_name}/dmesg.log 2>/dev/null")
            os.system(f"lspci > /root/{folder_name}/lspci.log 2>/dev/null")
            os.system(f"lspci -vvv > /root/{folder_name}/lspci_vvv.log 2>/dev/null")
            os.system(f"lspci -tv > /root/{folder_name}/lspci_tv.log 2>/dev/null")
            os.system(f"hostnamectl > /root/{folder_name}/hostnamectl.log 2>/dev/null")
            os.system(f"nkvers > /root/{folder_name}/nkvers.log 2>/dev/null")
            os.system(f"ip a > /root/{folder_name}/ip_a.log 2>/dev/null")
            os.system(f"cat /proc/version > /root/{folder_name}/proc_ver.log 2>/dev/null")
            os.system(f"dmidecode -t bios > /root/{folder_name}/dmi_bios.log 2>/dev/null")
            os.system(f"ipmitool mc info > /root/{folder_name}/ipmi_mc_info.log 2>/dev/null")
            os.system(f"free -g > /root/{folder_name}/free_g.log 2>/dev/null")
            os.system(f"cat /etc/os-release > /root/{folder_name}/{folder_name}.log 2>/dev/null")
            os.system(f"uname -a >> /root/{folder_name}/{folder_name}.log 2>/dev/null")
            os.system(f''' cd /opt/sost/ && python3 -c 'from lib.sost_system_info_lib import test_config;test_config("1","0","/root/{folder_name}/")' ''')
            os.system(f"mv /root/{folder_name}/testconfig.txt /root/{folder_name}/dev_info.log 2>/dev/null")
            os.system(f"md5sum /root/{folder_name}/* > /root/{folder_name}/md5sum.log")
            os.system(f"tar -cvf /root/{folder_name}.tar /root/{folder_name} >/dev/null 2>&1 ")
            os.system("clear")
            print("==================================")
            print("<sost> Collect Success!")
            print("==================================")
            print(f"<sost> ServerBakupInfoPath : /root/{folder_name}")
            print(f"<sost> Md5sumCheck         : /root/{folder_name}/md5sum.log")
            print(f"<sost> TarFile             : /root/{folder_name}.tar")
            print(f"<sost> TarFileMd5Sum       : "+os.popen(f"md5sum /root/{folder_name}.tar | awk '{{print $1}}'").read().strip())
            print("==================================")
        except Exception as e:
            print(f"<sost> Collect Fail ! fail info : {str(e)}")

    # Query server specific information
    if args.info:
        def help_d():
            print('='*80)
            print("[+] SOST query hardware information help document | sost查询硬件信息帮助文档")
            print('='*80)
            print('\n|--[Value]-|-----------[Help Information]---------------|-------[帮助信息]------|')
            print("| pcieinfo |  Query server PCIE device information      | 查询服务器PCIE设备信息|")
            print("| pcieslot |  Query server PCIE interface information   | 查询服务器PCIE接口信息|")
            print("| osip     |  Query server system IP information        | 查询服务器系统IP信息\t|")
            print("| mem      |  Query server memory information           | 查询服务器内存信息\t|")
            print("| psu      |  Query server power information            | 查询服务器电源信息\t|")
            print("| cpu      |  Query server CPU information              | 查询服务器CPU信息\t|")
            print("| disk     |  Query server hard disk information        | 查询服务器硬盘信息\t|")
            print("| disk1    |  Query server hard disk information (natt) | 查询服务器硬盘详细信息|")
            print("| fw       |  Query server firmware version information | 查询服务器固件版本信息|")
            print("| bp       |  Query server Backplane information        | 查询服务器物理背板信息|")
            print("| bmcip    |  Query server BMCIP information            | 查询服务器BMCIP信息\t|")
            print("| bmchip   |  Query server BMC chip information         | 查询服务器BMC芯片信息\t|")
            print("| raid     |  Query server RAID information             | 查询服务器RAID卡信息\t|")
            print('|----------|--------------------------------------------|-----------------------|')
            print("| test     |  Query SOST Test info                      | 查询当前测试信息\t|")
            print("| uuid     |  Query server UUID information             | 查询服务器UUID信息\t|")
            print("| hwmac    |  Query server MAC Address information      | 查询服务器MAC地址信息\t|")
            print('|----------|--------------------------------------------|-----------------------|')
            print('='*80)
            print("Command : sost -i [Value] ")
            print('='*80)
        try:
            if sys.argv[2] == "pcieinfo":os.system('''cd /opt/sost/ && python3 -c "from lib.sost_system_info_lib import pcieinfo;pcieinfo('0','',' ')" ''')
            elif sys.argv[2] == "test":
                print('='*40+'\n'+os.popen('''cat /opt/sost/config/sost.json | grep -A 5 BMC_Survival_Config | grep -v BMC_Survival_Config | tr -d ' "{},' ''').read().replace(":","  \t:  ").strip()+'\n'+'='*40)
                print(os.popen('''cat /opt/sost/config/sost.json | grep -A 6 Multimodal_stability | grep -v Multimodal_stability | tr -d ' "{},' ''').read().replace(":","       \t:  ").strip()+'\n'+'='*40)
                print(os.popen('''cat /opt/sost/config/sost.json | grep -A7 Test_tmp | grep -v Test_tmp | tr -d ' "{},' ''').read().replace(":","       \t:  ").strip()+'\n'+'='*40)
            elif sys.argv[2] == "pcieslot":os.system('''cd /opt/sost/ && python3 -c "from lib.sost_system_info_lib import pcieslot;pcieslot('0','',' ')" ''')
            elif sys.argv[2] == "osip":os.system('''cd /opt/sost/ && python3 -c "from lib.sost_system_info_lib import osip;osip('0','',' ')" ''')
            elif sys.argv[2] == "mem":os.system('''cd /opt/sost/ && python3 -c "from lib.sost_system_info_lib import meminfo;meminfo('0','',' ')" ''')
            elif sys.argv[2] == "psu":os.system('''cd /opt/sost/ && python3 -c "from lib.sost_system_info_lib import psuinfo;psuinfo('0','',' ')" ''')
            elif sys.argv[2] == "cpu":os.system('''cd /opt/sost/ && python3 -c "from lib.sost_system_info_lib import cpu_info;cpu_info('0','',' ')" ''')
            elif sys.argv[2] == "disk":os.system('''cd /opt/sost/ && python3 -c "from lib.sost_system_info_lib import os_disk_info;os_disk_info('0','',' ')" ''')
            elif sys.argv[2] == "disk1":os.system('''cd /opt/sost/ && python3 -c "from lib.sost_system_info_lib import os_disk_info_1;os_disk_info_1('0','',' ')" ''')
            elif sys.argv[2] == "net":os.system('''cd /opt/sost/ && python3 -c "from lib.sost_system_info_lib import os_net_info;os_net_info('0','',' ')" ''')
            elif sys.argv[2] == "fw":os.system('''cd /opt/sost/ && python3 -c "from lib.sost_system_info_lib import fwinfo;fwinfo('0','',' ')" ''')
            elif sys.argv[2] == "bmcip":os.system('''cd /opt/sost/ && python3 -c "from lib.sost_system_info_lib import bmcip;bmcip('0','',' ')" ''')
            elif sys.argv[2] == "bp":os.system('''cd /opt/sost/ && python3 -c "from lib.sost_system_info_lib import backboard_info;backboard_info('0','',' ')" ''')
            elif sys.argv[2] == "uuid":print(os.popen("ipmitool mc guid | grep -vi ipmi | grep -i guid | cut -d ':' -f 2 | tr -d ' -'").read().strip())
            elif sys.argv[2] == "hwmac":print(os.popen(''' ipmitool lan print | awk -F': ' '/MAC Address[ ]*:/ {print $2}' ''').read().strip())
            elif sys.argv[2] == "raid":os.system('''cd /opt/sost/ && python3 -c "from lib.sost_system_info_lib import storinfo;storinfo('0','','')" ''')
            elif sys.argv[2] == "sha256":
                try:
                    import hmac;import base64
                    strings = os.popen(''' cat /opt/sost/config/sost_version.json | tr -d '",'| grep -i Release_time | awk '{{print $2,$3}}' ''').read().strip()
                    hmac_digest = hmac.new(key=base64.b64decode("c29zdGZhbnhpYW9kb25n").decode('utf-8').encode('utf-8'),msg=strings.encode('utf-8'),digestmod='sha256')
                    print(str(hmac_digest.hexdigest()))
                except:
                    print("0000000000000000000000000000000000000000000000000000000000000000")
                    
            elif sys.argv[2] == "bmchip":
                print('='*60)
                bmc_chip = os.popen("cd /opt/sost && python3 -c 'from lib.sost_public_lib import bmc_Chip;print(str(bmc_Chip()[0]))'").read().strip()
                print(f"The current BMC chip is : {bmc_chip}")
                print('='*60)
            else:
                if sys.argv[2] == "-h" or sys.argv[2] == '--help' or sys.argv[2] == "" or sys.argv[2] == "help":
                    help_d()
        except:
            help_d()

    # Start test execution function
    if args.sensor:
        os.system("cd /opt/sost && python3 -c 'from lib.sost_public_lib import def_Handling_sensors;def_Handling_sensors()'")

    # Continue test execution function
    if args.dmesg_check:
        os.system('''cd /opt/sost && python3 -c "from lib.sost_system_info_lib import dmesg_check;dmesg_check('')"''')

    # Start test execution function
    if args.killall:
        os.system("ps -aux | grep -i swc | grep -v grep | awk '{print $2}' | xargs kill -9")
        os.system("ps -aux | grep -i auto_test | grep -v grep | awk '{print $2}' | xargs kill -9")
        json_set("Test_tmp","Running_flag","6")
        os.system("yes | sost -f bash")
        os.system("rm -rf /root/.config/autostart/*")
        print("<sost> All processes of sost have been cleaned up and bash-profile has been reset!")
        os.system("ps -aux | grep -i sost | grep -v grep | awk '{print $2}' | xargs kill -9")

    # Start test execution function
    if args.fix:
        def help_d():
            print("=========================================================================")
            print("|                     Sost Fix File Help Documents                      |")
            print("=========================================================================")
            print("|  sost -f bash      -> fix bash_profile   修复bash_profile文件\t\t|")
            print("|  sost -f auto      -> fix autotest       清理GUI_autostart文件\t|")
            print("|  sost -f config    -> fix sost.json      重建sost.json文件\t\t|")
            print("|  sost -f ssh       -> fix RemoteSSH      修复SSH无法远程登录问题\t|")
            print("|  sost -f net       -> Rebuild NetPort    nmcli重建网口名称\t\t|")
            print("=========================================================================")
        try:
            if sys.argv[2] == "auto":
                os.system("rm -rf /root/.config/autostart/*")
                time.sleep(1)
                print("<sost> Clear /root/.config/autostart/* Successful!")
            if sys.argv[2] == "help":
                help_d()
            elif sys.argv[2] == "net":
                netport_list = os.popen(''' nmcli -t -f NAME connection show | grep -viE "lo|vi|do" ''').read().strip().split("\n")
                print(netport_list)
                if input("<sost> Sost performs/net rebuild! All existing network connections will be deleted, Do you want to continue? [y / n ] : ").lower() != "y": exit()
                for net_name in netport_list:
                    os.system(f"nmcli connection delete '{net_name}' >/dev/null 2>&1")
                    os.system(f'nmcli connection add con-name {net_name} type ethernet ifname {net_name} autoconnect yes')
                    print(f"<sost> Rebuild {net_name} Success!")
                    time.sleep(1)
                print("<sost> Rebuild NetPort Success!")

            if sys.argv[2] == "bash":
                file_text = f'''# .bash_profile
# Get the aliases and functions
if [ -f ~/.bashrc ]; then
        . ~/.bashrc
fi

# User specific environment and startup programs

PATH=$PATH:$HOME/bin

export PATH
'''
                if input("<sost> Sost performs/root/.bash_profile! File reset, Do you want to continue? [y / n ] : ").lower() == "y":
                    with open("/root/.bash_profile","w") as f:
                        f.write(file_text)
                        f.flush()
            if sys.argv[2] == 'config':
                if input("<sost> Do you want to reset the sost.json file [y / n ] : ").lower() == "y":
                    os.system("yes | cp -rf /opt/sost/config/.sost.json.bak /opt/sost/config/sost.json")
                    print("<sost> Reset sost.json file successfully !")
            if sys.argv[2] == "ssh":
                print("<sost> Fix root Remote login success!")
                os.system("sed -i 's/root::/root:x:/' /etc/passwd")
        except:
            help_d()

    # Start test execution function
    if args.webconsole:
        try:
            if sys.argv[2] == "help":
                print("================================================|")
                print("|        Sost WebConsole Help Documents         |")
                print("================================================|")
                print("|  sost -w start      -> Start SostWebConsole   |")
                print("|  sost -w stop       -> Stop  SostWebConsole   |")
                print("|  sost -w restart    -> ReStart SostWebConsole |")
                print("|  sost -w status     -> SostWebConsole Status  |")
                print("=================================================")
            if sys.argv[2] == "start":
                result = os.popen("systemctl status swc-manager.service | grep -i Active:").read().strip()
                if "running" in result:
                    print("<sost> \033[33mThe service is running!\033[0m")
                    print("<sost> \033[33m"+result+"\033[0m")
                else:
                    os.system('systemctl start swc-manager.service')
                    print("<sost> \033[32mService has been activated!\033[0m")
                    print("<sost> \033[32m"+result+"\033[0m")
            elif sys.argv[2] == "stop":
                result = os.popen("systemctl status swc-manager.service | grep -i Active:").read().strip()
                if "running" not in result:
                    print("<sost> \033[33mService has been deactivated!\033[0m")
                    print("<sost> \033[33m"+result+"\033[0m")
                else:
                    os.system("systemctl stop swc-manager.service")
                    print("<sost> \033[32mService to be closed!\033[0m")
                    print("<sost> "+os.popen("systemctl status swc-manager.service | grep -i Active:").read().strip())
              
            elif sys.argv[2] == "status":
                print('='*60)
                print("<sost> swc-manager.service Status  : " + os.popen('systemctl status swc-manager.service | head -n 3 | tail -n 1 | cut -c 1-40').read().strip())
                print("<sost> Flask web Server Status     : " + os.popen('curl -o /dev/null -s -w "%{http_code}\n" http://127.0.0.1:13250').read().strip())
                print("<sost> firewall Status             : " + os.popen("systemctl status firewalld.service  | grep -i active | awk '{print $2}'").read().strip())
                print("<sost> Tmp_Folder_status           : " + os.popen("du /tmp/sost_tmp -h").read().strip())
                print("<sost> netstat LISTEN              : " + os.popen('netstat -anlt | grep -i 13250 | grep -i LISTEN').read().strip().replace("  "," "))
                print("<sost> Process                     : " + os.popen("ps -uax | grep -i sost_web_console | grep -v grep").read().strip())
                print('='*60)
            elif sys.argv[2] == "restart":
                os.system("systemctl restart swc-manager.service")
                print("<sost> \033[32mThe service has been restarted\033[0m")
                print("<sost> "+os.popen("systemctl status swc-manager.service | grep -i Active:").read().strip())
            else:
                print("================================================|")
                print("|        Sost WebConsole Help Documents         |")
                print("================================================|")
                print("|  sost -w start      -> Start SostWebConsole   |")
                print("|  sost -w stop       -> Stop  SostWebConsole   |")
                print("|  sost -w restart    -> ReStart SostWebConsole |")
                print("|  sost -w status     -> SostWebConsole Status  |")
                print("=================================================")
        except:
            print("================================================|")
            print("|        Sost WebConsole Help Documents         |")
            print("================================================|")
            print("|  sost -w start      -> Start SostWebConsole   |")
            print("|  sost -w stop       -> Stop  SostWebConsole   |")
            print("|  sost -w restart    -> ReStart SostWebConsole |")
            print("|  sost -w status     -> SostWebConsole Status  |")
            print("=================================================")

    # Continue test execution function
    if args.continuee:
        if "multi-user.target" in os.popen("systemctl get-default").read():
            if "sost -z" not in os.popen("cat /root/.bash_profile").read():
                with open('/root/.bash_profile','a') as f:
                    f.write('sost -z')
        else:
            def autostart(tmp):
                os.system("yes | sost -f bash >/dev/null ")
                if not os.path.exists("/root/.config/autostart/sost.desktop"):
                    if not os.path.exists("/root/.config/autostart"): os.mkdir("/root/.config/autostart")
                    os.system("rm -rf /root/.config/autostart/*")
                    os.system("touch /root/.config/autostart/sost.desktop")
                    os.system("echo '[Desktop Entry]' >> /root/.config/autostart/sost.desktop")
                    os.system("echo 'Type=Application' >> /root/.config/autostart/sost.desktop")
                    os.system(f"echo '{tmp}' >> /root/.config/autostart/sost.desktop")
                    os.system("echo 'Name=Sost_AutoStart' >> /root/.config/autostart/sost.desktop")
                    os.system("echo 'Icon=system-run' >> /root/.config/autostart/sost.desktop")
                    os.system("echo '' >> /root/.config/autostart/sost.desktop")
            if str(os.popen("cat /etc/os-release | grep -i kylin | wc -l").read()) != "0":
                tmp = 'Exec=mate-terminal --window --maximize -x bash -c "sost -z;exec bash;"'
                autostart(tmp)
            elif str(os.popen("cat /etc/os-release | grep -i rhel | wc -l").read()) != "0":
                tmp = 'Exec=gnome-terminal -- bash -c "sost -z; exec bash;"'
                autostart(tmp)
            else:
                with open('/root/.bash_profile','a') as f:
                    f.write('sost -z')
        
        # Check if multimodal stability test is enabled
        if 'sost_mulit_result' in os.popen("sost -i test | grep -i test_folder_path | cut -d ':' -f 2 | tr -d ' '").read().strip():
            json_set('Multimodal_stability','switch','1')

        # Start the auto_test.py script
        os.system("cd /opt/sost && python3 auto_test.py")

    # sost uninstall function
    if args.uninstall:
        if input("<sost> Do you want to uninstall sost? (y/n) ").lower() == "y":
            print("<sost> Waiting 10s before uninstalling... Ctrl + C kill uninstall Process!")
            time.sleep(10)
            os.system('systemctl stop swc-manager.service >/dev/null 2>&1')
            os.system("rm -rf /usr/bin/sost")
            os.system("rm -rf /usr/local/bin/sost")
            if input("<sost> Do you want to keep the old tool information? (y/n) ").lower() == "y":
                os.system("mv /opt/sost /tmp/sost_uninstall_tmp_folder")
            else:
                os.system("rm -rf /opt/sost")
            print("<sost> Uninstalling sost Success! Luck to you!")

    # sost help display
    if len(sys.argv) == 1: parser.print_help()

    if args.start:
        try:
            os.system(f"sh -c 'cd /opt/sost/ && python3 -B sost_main.py {sys.argv[2]}'")
        except:
            os.system(f"sh -c 'cd /opt/sost/ && python3 -B sost_main.py'")

if __name__ == '__main__':
    debug_info()
    parser_test()
