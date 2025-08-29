#================================================
from lib.sost_public_lib import wait_time_ctrl_C,time,init_stability_path,change_json,clp,test_type_logo,os_env,end_test_logo,runTime,autologin,sel_bak_clear,check_stability_tools,get_bmc_info,update_sost,Multimodal_stability,Judging_autologin,aclost_init_env,bmc_tools_main,bmc_stability,Timed_operation_mode,startup_check,mulit_main,check_bmc_status,debug_mode,init_poweronoff_env,update_check
from lib.sost_logging import dong_log,json
from lib.sost_system_info_lib import test_config
import sys
log = dong_log()
log.debug_flags = str(log.json_get("sost","debug_flags"))
#================================================
def runstart(test_arry):
    log.json_set('Test_tmp','Running_flag','1')
    log.json_set('Test_tmp','test_status','NA')
    os_env()
    autologin()
    # 0 start_time 1 end_time 2 last_time 3 Power off -> Os Run Time  4 sost running timerunTime("1")
    runTime("0")
    clp()
    test_type = log.json_get("Test_tmp","test_type")
    test_test_folder = log.json_get("Test_tmp","test_folder_path")
    if test_type == "" or test_test_folder == "":
        log._error("sost_main.Exit.in 17 line")
    test_type_logo(test_type,"0")
    if log.json_get("Test_Config","simple_test_flags") != "simple":
        test_config("0","0",test_test_folder)
        test_config("2","0",test_test_folder)
        test_config("1","0",test_test_folder)
    end_test_logo()
    Judging_autologin()
    runTime("1")
    log.json_set('Test_tmp','Running_flag','3')
    wait_time_ctrl_C(int(log.json_get("Test_Config","end_wait_time")),flags='end')
    debug_mode()
    # Force Sync Data , solve Power Off Not Sync Data
    log.os_run("sync -f && sync",flags='no-log')
    log.os_run(log.json_get("Test_tmp","run_command"))
    time.sleep(int(log.json_get("Test_Config","end_wait_time")))
#================================================
bmclan = ""
update_check()
startup_check()

if str(log.json_get("Multimodal_stability","switch"))=="1":
    test_type,run_command,test_count = Multimodal_stability()
    if test_type == "AClost":
        aclost_init_env()
    log.json_set("Test_tmp","test_type",test_type)
    log.json_set("Test_Config","max_count",test_count)
else:
    u_chos = ''
    BMC_User = ''
    BMC_Pass = ''
    try:
        if 'json_test' in sys.argv[1]:
            strings ='{"'+sys.argv[1].replace(':','":"').replace(',','","')+'"}'
            data = json.loads(strings)
            chose = data["chose"]
            if chose == '13' or '14':
                try:bmclan = data['bmclan']
                except:bmclan = '1'
                try:BMC_User = data['bmcuser']
                except:BMC_User = 'admin'
                try:BMC_Pass = data['bmcpass']
                except:BMC_Pass = 'admin'
        elif sys.argv[1] == "reboot":
            chose = "1"
        elif sys.argv[1] == "powercycle":
            chose = "2"
        elif sys.argv[1] == "powerreset":
            chose = "3"
        elif sys.argv[1] == "aclost":
            chose = "4"
        else:
            log._pr("==============================================")
            log._pr("|    sost -s reboot      -> rebootTest       |")
            log._pr("|    sost -s aclost      -> AClostTest       |")
            log._pr("|    sost -s powercycle  -> PowerCycleTest   |")
            log._pr("|    sost -s powerreset  -> PowerResetTest   |")
            log._pr("==============================================")
            chose = "exit"
    except Exception as e :
        chose = ""
        pass
    if chose == "exit":log._error("User.Input.Error -> sost -s [value]")
    if chose == "":
        chose = log._in("Your choice : ")
    log._dmesg(f"User selected testing model : {chose}")
    #================================================
    #### systemctl reboot
    # The introduction of the Systemd system and service manager led to its emergence.
    # Systemd is the initialization system and service manager for many modern Linux distributions,
    # providing richer functionality and better dependency management than traditional init systems.
    # In a system managed by SystemD, SystemCTL is the core command used to manage system services, including restarting the system.
    #### init 6
    # init 6 -> process
    # reboot -> kernel
    #### poweroff -r
    # poweroff -r -> clear process / clear work
    # reboot -> kernel
    test_type,run_command= "",""
    if chose == "11":chose = Timed_operation_mode()
    
    if chose == "1":test_type = "reboot";run_command = "reboot"
    elif chose == "2":test_type = "powercycle";run_command = "ipmitool power cycle"
    elif chose == "3":test_type = "powerreset";run_command = "ipmitool power reset"
    elif chose == "4":
        test_type = "AClost"
        run_command = "sh -c `sync ; sleep 3 ; sh -c 'minicom &' ; sleep 5 ; echo a > /dev/ttyUSB0` &"
        aclost_init_env()
    elif chose == "5":test_type = "systemctl_reboot";run_command = "systemctl reboot"
    elif chose == "6":test_type = "init_6";run_command = "init 6"
    elif chose == "7":test_type = "poweroff_r";run_command = "poweroff --reboot"
    elif chose == "8":test_type = "shutdown_r_now";run_command = "shutdown -r now"
    elif chose == "9":
        bmc_tools_main(log.json_get("sost","Version"),log.json_get("sost","Release_Time"))
        exit()
    elif chose == "10":
        test_type = log._in("TestType   : ")
        if test_type == "":log._error("User.Input.Error!")
        run_command = log._in("RunCommand : ")
        if run_command == "":log._error("User.Input.Error!")
        log._pr(f"test_type = {test_type}\nRunCommand = {run_command}")
        if log._in("Are you sure ? [y / n] : ") == "n":
            log._error("User.Input.N -> exit()")
    elif chose == "12":
        mulit_main()
    elif chose == "13":
        test_type = "Bmc_Remote_Reset"
        check_bmc_status()
        bmc_information = get_bmc_info(bmclan,BMC_User,BMC_Pass)
        run_command = f"ipmitool -C 17 -I lanplus -H {bmc_information[0]} -U {bmc_information[1]} -P '{bmc_information[2]}' power reset"
    elif chose == "14":
        test_type = "Bmc_Remote_Cycle"
        check_bmc_status()
        bmc_information = get_bmc_info(bmclan,BMC_User,BMC_Pass)
        run_command = f"ipmitool -C 17 -I lanplus -H {bmc_information[0]} -U {bmc_information[1]} -P '{bmc_information[2]}' power cycle"
    elif chose == "15":
        test_type = 'Remote bmc reset warm'
        check_bmc_status()
        folder_path = init_stability_path('sost_bmcwarm')
        check_stability_tools()
        sel_bak_clear(folder_path)

        run_command = "bmc reset warm"
        change_json("0",test_type,folder_path,run_command)
        
        bmc_stability('warm',folder_path)
        exit()
    elif chose == "16":
        test_type = 'Remote bmc reset cold'
        check_bmc_status()

        folder_path = init_stability_path('sost_bmccold')
        check_stability_tools()
        sel_bak_clear(folder_path)

        run_command = "bmc reset cold"
        change_json("0",test_type,folder_path,run_command)

        bmc_stability('cold',folder_path)
        exit()
    elif chose == "17":
        test_type = 'Remote raw 0x06 0x02'
        check_bmc_status()

        folder_path = init_stability_path('sost_raw0602')
        check_stability_tools()
        sel_bak_clear(folder_path)

        run_command = "raw 0x06 0x02"
        change_json("0",test_type,folder_path,run_command)

        bmc_stability('raw',folder_path)
        exit()
    # ------------------------------------------------------------------------------------------
    elif chose == '18':
        test_type = "bmc_power_on_off"
        check_bmc_status()
        init_poweronoff_env(bmclan,BMC_User,BMC_Pass)
        run_command = "power_on_off"

    elif chose == '19':
        log._error('User.Input.Error')
    elif chose == "20":
        update_sost()
        exit()
    else:
        log._error("User.Input.Error")
folder_path = init_stability_path(test_type)
check_stability_tools()
sel_bak_clear(folder_path)
change_json("0",test_type,folder_path,run_command)
#RunStart
runstart(test_type)
