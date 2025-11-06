from lib.sost_public_lib import test_type_logo,dong_log,runTime,end_test_logo,wait_time_ctrl_C,max_count_logo,Judging_autologin,time,autologin,defalt_path,result_html,swc_EndTest,return_wait_time,debug_mode
from lib.sost_system_info_lib import test_config,check_running_time
# init logging
log = dong_log()
log.debug_flags = str(log.json_get("debug","debug_flags",filename="debug"))
log.os_run("mkdir -p /tmp/sost_tmp")

# check tty
if log.json_get("debug","noSendCommand",filename="debug")!="1":
    if "pts" in log.os_popen("tty"):
        log._exitt("The program cannot be interrupted in PTS!")

#check stability status
if str(log.os_popen("cat /etc/os-release | grep -i ubuntu | wc -l").strip())=="0":
    if log.os_popen("ps aux | grep -i auto_test | grep -v grep | grep -v sd | wc -l").strip()!="1":
        log._error("sost is running!")
else:
    log._dp("OS is Ubuntu, so ignore stability test!")

if log.json_get("Test_tmp","test_type") == "":log._error("No stability testing was conducted!")
# Init logging
autologin()
Judging_autologin()
#judge max count
max_count_flags = max_count_logo()
if max_count_flags != None:
    if max_count_flags[0]:
        if max_count_flags[1]=="default":
            log.json_set("Test_Config","max_count","0")
            defalt_path()
            result_html()
            exit()
        else:
            exit()
last_count = log.json_get("Test_tmp", "test_count")
next_count = str(int(last_count)+1)
path = log.json_get("Test_tmp","test_folder_path")
#write last_time
try:runTime("2")
except:log._exitt("Unable to Continue Test!") 
#User.ctrl + c exit()----------------------------------------------------
wait_time = return_wait_time()
# show logo
test_type_logo(log.json_get("Test_tmp","test_type"),last_count)
swc_EndTest()
#User.ctrl + c exit()
log.json_set('Test_tmp','Running_flag','2')
wait_time_ctrl_C(wait_time,flags='start')
#set now count
log.json_set("Test_tmp","test_count",next_count)
# write start_time
runTime("0")
# save count to count
log.os_popen(f"echo {next_count} > {path}/count.txt")
# show Now Test logo
#------------------------------------------------------------------------
runTime("5","start")
test_config("1",next_count,path)
runTime("5","end")
#0 start_time 1 end_time 2 last_time 3 Power off -> Os Run Time  4 sost running timerunTime("1")
runTime("3")
runTime("4")
runTime("1")
check_running_time(next_count)
end_test_logo()
log.json_set('Test_tmp','Running_flag','3')
wait_time_ctrl_C(int(log.json_get("Test_Config","end_wait_time")),flags='end')
debug_mode()
swc_EndTest()
# Force Sync Data , solve Power Off Not Sync DatarunTime
log.os_run("sync -f && sync",flags='no-log')
log.os_run(log.json_get("Test_tmp","run_command").strip())
time.sleep(int(log.json_get("Test_Config","end_wait_time")))
