from lib.sost_logging import dong_log

log = dong_log()
# no-log -> not save cmd.log
# ''     -> save cmd.log
cmd_log_flags = 'no-log'
log.debug_flags = str(log.json_get("debug", "debug_flags",web='no-log',filename="debug"))

import os
import subprocess
import logging
import time

try:
    from flask import Flask, render_template, jsonify, send_file, request
    
except:
    log.error_exit("Flask module not installed successfully, unable to open web_comsole")
from datetime import datetime

app = Flask(__name__)
app.logger.setLevel(logging.ERROR)

# 关闭请求日志
@app.after_request
def after_request(response):
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    return response

def failinfo():
        result = log.json_get("Test_tmp","test_status",web=cmd_log_flags)
        path_folder = log.json_get("Test_tmp","test_folder_path",web=cmd_log_flags)
        if result == 'FAILc':
            failc_info = os.popen(f"cat {path_folder}/failc.txt").read().strip()
            data = '==============================\nSummaryInfo \n==============================\n'+ log.os_popen(f"cat {path_folder}/failc_result/summary.log 2>/dev/null",flags=cmd_log_flags).strip()+ '\n==============================\n'+str(failc_info)
            return str(data).replace('(','').replace(')','').replace('{','').replace('}','').strip().replace('\n','<br>')
        elif result == 'FAIL':
            fail_info = os.popen(f"cat {path_folder}/fail.txt").read()
            if fail_info.strip()=='':
                fail_info = os.popen(f"cat /opt/sost/log/sost_interactive.log").read()
            return fail_info.replace('\n','<br>')
        else:
            return ''
        
@app.route('/slog', methods=['GET'])
def slog():

    # Type
    # alarm -> /opt/sost/log/alarm.log
    # debug -> /opt/sost/log/debug.log
    # interactive -> /opt/sost/log/sost_interactive.log
    # json -> /opt/sost/log/json.log
    # popen -> /opt/sost/log/popen.log
    # run -> /opt/sost/log/run.log

    slog_type = request.args.get('type')
    
    if slog_type not in ['alarm', 'debug', 'interactive', 'fail' ,'json', 'popen', 'run','showconfig']:
        return "Invalid type parameter", 400
    
    if slog_type == 'alarm':
        alarm_log = log.os_popen("cat /opt/sost/log/alarm.log",flags=cmd_log_flags).replace('\n','<br>').replace(" ", "&nbsp&nbsp")
        if alarm_log != '':return alarm_log
    elif slog_type == 'debug':
        debug_log = log.os_popen("cat /opt/sost/log/debug.log",flags=cmd_log_flags).replace('\n','<br>').replace(" ", "&nbsp&nbsp")
        if debug_log != '':return debug_log
    elif slog_type == 'interactive':
        interactive_log = log.os_popen("cat /opt/sost/log/sost_interactive.log",flags=cmd_log_flags).replace('\n','<br>').replace(" ", "&nbsp&nbsp")
        if interactive_log != '':return interactive_log
    elif slog_type == 'fail':
        faillog = failinfo()
        if faillog != '':return faillog
    elif slog_type == 'json':
        json_log = log.os_popen("cat /opt/sost/log/json.log",flags=cmd_log_flags).replace('\n','<br>').replace(" ", "&nbsp&nbsp")
        if json_log != '':return json_log
    elif slog_type == 'popen':
        popen_log = log.os_popen("cat /opt/sost/log/popen.log",flags=cmd_log_flags).replace('\n','<br>').replace(" ", "&nbsp&nbsp")
        if popen_log != '':return popen_log
    elif slog_type == 'run':
        run_log = log.os_popen("cat /opt/sost/log/run.log",flags=cmd_log_flags).replace('\n','<br>').replace(" ", "&nbsp&nbsp")
        if run_log != '':return run_log

    return "No log information" , 200

@app.route('/getrunningTime')
def get_running_time():
    runTime = log.os_popen(f"cat {log.json_get('Test_tmp','test_folder_path',web=cmd_log_flags)}/running_time.txt",flags=cmd_log_flags).strip()
    return runTime.replace('\n','<br>')

@app.route('/clearinfo')
def clear_info():
    log.json_set('Test_tmp','Running_flag','0')
    return 'success',200

#@app.route('/sjson_set', methods=['POST'])
@app.route('/sjson', methods=['GET'])
def sjson():
    # bmcsel_check -> /opt/sost/config/bmcsel_check.json
    # collect_array -> /opt/sost/config/collect_array.json
    # debug -> /opt/sost/config/debug.json
    # dmesg_check -> /opt/sost/config/dmesg_check.json
    # server_info -> /opt/sost/config/server_info.json
    # sost -> /opt/sost/config/sost.json
    # sost_version -> /opt/sost/config/sost_version.json
    # swc -> /opt/sost/config/swc.json

    # HTTP Post JSON Example:
    # data = request.get_json()
    # obj = data.get('obj')
    # key = data.get('key')
    # new_value = data.get('new_value')
    # filename = data.get('filename')

    # HTTP GET Example:
    typee = request.args.get('type')
    obj = request.args.get('obj')
    key = request.args.get('key')
    new_value = request.args.get('new_value')
    filename = request.args.get('filename')

    if filename not in ['bmcsel_check', 'collect_array', 'debug', 'dmesg_check', 'server_info', 'sost', 'sost_version', 'swc',"showconfig"]:
        return jsonify({"error": "Invalid filename parameter"}), 400
    
    if not obj or not key or filename is None:
        if filename != 'showconfig':
            return jsonify({"error": "Missing required parameters"}), 400
    
    if filename == 'showconfig':
        # fail_exit_flags
        fail_exit_flags = log.json_get("Test_Config","fail_exit_flags",web=cmd_log_flags)
        # fail_exit_blacklist
        fail_exit_blacklist = log.json_get("Test_Config","fail_exit_blacklist",web=cmd_log_flags)
        # start_wait_time
        start_wait_time = log.json_get("Test_Config","start_wait_time",web=cmd_log_flags)
        # aclost_wait_time
        aclost_wait_time = log.json_get("Test_Config","aclost_wait_time",web=cmd_log_flags)
        data = '{"fail_exit_flags": "'+str(fail_exit_flags)+'", "fail_exit_blacklist": "'+str(fail_exit_blacklist)+'", "start_wait_time": "'+str(start_wait_time)+'", "aclost_wait_time": "'+str(aclost_wait_time)+'"}'
        return data

    if filename == 'bmcsel_check':
        if typee == 'get':
            value = log.json_get(obj, key, filename='bmcsel_check')
            return jsonify({key: value}), 200
        else:
            log.json_set(obj, key, new_value, filename='bmcsel_check')
            return 'success',200
    elif filename == 'collect_array':
        log.json_set(obj, key, new_value, filename='collect_array')
        return 'success',200
    elif filename == 'debug':
        log.json_set(obj, key, new_value, filename='debug')
        return 'success',200
    elif filename == 'dmesg_check':
        log.json_set(obj, key, new_value, filename='dmesg_check')
        return 'success',200
    elif filename == 'server_info':
        log.json_set(obj, key, new_value, filename='server_info')
        return 'success',200
    elif filename == 'sost':
        if typee == 'get':
            value = log.json_get(obj, key, filename='sost')
            return jsonify({key: value}), 200
        elif typee == 'set':
            log.json_set(obj, key, new_value, filename='sost')
            return 'success',200
    elif filename == 'sost_version':
        log.json_set(obj, key, new_value, filename='version')
        return 'success',200
    elif filename == 'swc':
        log.json_set(obj, key, new_value, filename='swc')
        return 'success',200
    else:
        return jsonify({"error": "File not found"}), 404

    return "File not found", 404

@app.route('/run', methods=['GET'])
def run_stability():

    data = request.args.get('type')
    testOrder = request.args.get('testOrder')
    bmclan = request.args.get('bmclan')
    bmcuser = request.args.get('bmcuser')
    bmcpass = request.args.get('bmcpass')
    run_wait_time = request.args.get('run_wait_time')

    print(data,testOrder,bmclan,bmcuser,bmcpass,run_wait_time)


    if data == 'other' and testOrder == None:
        return jsonify({"error": "Missing required parameter 'testOrder'"}), 400
    if data == 'other' and bmclan == None:
        return jsonify({"error": "Missing required parameter 'bmclan'"}), 400    
    if data == 'other' and bmcuser == None:
        return jsonify({"error": "Missing required parameter 'bmcuser'"}), 400
    if data == 'other' and bmcpass == None:
        return jsonify({"error": "Missing required parameter 'bmcpass'"}), 400

    if not data:
        return jsonify({"error": "Missing required parameter 'type'"}), 400
    try:
        process_count = int(subprocess.check_output(
            "pgrep -f -c 'sost(-[zs]|\\.py)( -[zs]|\\.py -[zs])?( -a)?( reboot| powercycle| powerreset| aclost)?'", 
            shell=True
        ).strip())
    except (subprocess.CalledProcessError, ValueError):
        process_count = 0
    
    if process_count > 0:
        return jsonify({"error": "SOST is already running a stability test!"}), 400
    if run_wait_time != None or run_wait_time != '':
        if data == 'reboot':
            testOrder = '1'
            typee = 'reboot'
        elif data == 'powercycle':
            testOrder = '2'
            typee = 'powercycle'
        elif data == 'powerreset':
            testOrder = '3'
            typee = 'powerreset'
        elif data == 'aclost':
            testOrder = '4'
            typee = 'aclost'
        else:
            testOrder = ''
            typee = ''
        addc = f"json_test:dongzai,chose:{testOrder},run_wait_time:{run_wait_time}"
    else:
        addc = ''
        typee = ''

    commands = {
        'reboot': f'sost -s {addc} &',
        'powercycle': f'sost -s {addc} &',
        'powerreset': f'sost -s {addc} &',
        'aclost': f'sost -s {addc} &',
        'continue'  : 'sost -z &',
        'stop'      : 'sost -k &',
        'other': f'''  sost -s json_test:dongzai,chose:{testOrder},bmclan:{bmclan},bmcuser:{bmcuser},bmcpass:{bmcpass},run_wait_time:{run_wait_time} & '''
    }
    if data not in commands:
        return jsonify({"error": "Invalid command parameter"}), 400
    try:
        run_command = commands[data]
        subprocess.Popen(run_command, shell=True, executable='/bin/bash')
        return jsonify({"message": f"{data.capitalize()} command executed successfully."}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to execute command: {str(e)}"}), 400

def now_time():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d -> %H:%M:%S")
    return formatted_time

@app.route('/')
def home():
    """首页，显示10个按钮"""
    return render_template('index.html')

@app.route('/stability')
def stability_status():
    return log.os_popen("sost -i test",flags=cmd_log_flags).strip().replace('\n','<br>')

def compress_and_return_file(source_dir,file_type=''):

    lan1 = log.os_popen("cat /tmp/sost_tmp/swc_ipmi_lan1.txt | tr -d ' *\n'",flags=cmd_log_flags).strip()
    lan2 = log.os_popen("cat /tmp/sost_tmp/swc_ipmi_lan8.txt | tr -d ' *\n'",flags=cmd_log_flags).strip()

    typee = log.json_get("Test_tmp", "test_type", web=cmd_log_flags)
    countt = log.json_get("Test_tmp", "test_count", web=cmd_log_flags)

    if lan1 !='':
        bmcip = lan1
    elif lan2 !='':
        bmcip = lan2
    else:
        bmcip = 'NA'

    now_time = datetime.now().strftime('%Y%m%d%H%M')
    if file_type == '':
        tmp_dir = f"/tmp/sost_tmp/sost_{bmcip}_{typee}_{countt}_{now_time}"
        log.os_popen(f"cp -rf {source_dir} {tmp_dir}", flags=cmd_log_flags)
        log.os_popen(f"tar -cvf {tmp_dir}.tar {tmp_dir}", flags=cmd_log_flags)
        log.os_popen(f"rm -rf {tmp_dir}", flags=cmd_log_flags)
    elif file_type == 'slog':
        tmp_dir = f"/tmp/sost_tmp/sost_{bmcip}_slog_{now_time}"
        log.os_popen(f"mkdir -p {tmp_dir}", flags=cmd_log_flags)
        log.os_popen(f"cp -rf /opt/sost/log/* {tmp_dir}/", flags=cmd_log_flags)
        log.os_popen(f"tar -cvf {tmp_dir}.tar {tmp_dir}", flags=cmd_log_flags)
        log.os_popen(f"rm -rf {tmp_dir}", flags=cmd_log_flags)
    elif file_type == 'sfolder':
        tmp_dir = f"/tmp/sost_tmp/sost_{bmcip}_sfolder_{now_time}"
        log.os_popen(f"mkdir -p {tmp_dir}", flags=cmd_log_flags)
        log.os_popen(f"cp -rf /opt/sost {tmp_dir}/", flags=cmd_log_flags)
        log.os_popen(f"tar -cvf {tmp_dir}.tar {tmp_dir}", flags=cmd_log_flags)
        log.os_popen(f"rm -rf {tmp_dir}", flags=cmd_log_flags)
    elif file_type == 'scache':
        tmp_dir = f"/tmp/sost_tmp/sost_{bmcip}_scache_{now_time}"
        log.os_popen(f"mkdir -p {tmp_dir}", flags=cmd_log_flags)
        log.os_popen(f"cp -rf /tmp/sost_tmp/* {tmp_dir}/", flags=cmd_log_flags)
        log.os_popen(f"tar -cvf {tmp_dir}.tar {tmp_dir}", flags=cmd_log_flags)
        log.os_popen(f"rm -rf {tmp_dir}", flags=cmd_log_flags)
    else:
        return None
    
    return f"{tmp_dir}.tar"

@app.route('/stability_download_log', methods=['GET'])
def stability_download_log():

    file_type = request.args.get('file_type','')

    if file_type not in ['', 'slog', 'sfolder']:
        return "Invalid file_type parameter", 400

    path = log.json_get("Test_tmp", "test_folder_path", web=cmd_log_flags)

    if not path:
        return "路径未找到", 404
    
    compressed_file_path = compress_and_return_file(path,file_type=file_type)
    try:
        return send_file(compressed_file_path, as_attachment=True)
    finally:
        os.remove(compressed_file_path)

@app.route('/history')
def return_history():
    # 读取原始数据
    raw_data = log.os_popen("cat /opt/sost/history").replace("\n", "<br>")

    # 创建表格结构并添加样式和大标题
    formatted_data = """
    <style>
        /* 页面背景与基本布局 */
        body {
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 40px;
            background: linear-gradient(135deg, #cce7ff, #80bfff); /* 渐变背景 */
            color: #333;
        }
        h1 {
            text-align: center;
            color: #1a73e8; /* 强烈的蓝色标题 */
            font-size: 55px;
            margin-bottom: 40px;
            font-weight: bold;
            text-shadow: 3px 3px 20px rgba(0, 0, 0, 0.15); /* 添加文字阴影 */
        }

        /* 表格样式 */
        table {
            width: 95%;
            margin: 0 auto;
            border-collapse: collapse;
            background: #fff;
            border-radius: 16px; /* 圆角 */
            box-shadow: 0 6px 30px rgba(0, 0, 0, 0.1);
        }

        th, td {
            padding: 18px 25px;
            text-align: center;
            border: 1px solid #ddd;
            font-size: 16px;
            transition: background-color 0.3s, transform 0.2s ease;
        }

        th {
            background-color: #1a73e8; /* 深蓝色表头 */
            color: white;
            font-size: 20px;
            font-weight: 600;
            border-radius: 16px 16px 0 0; /* 圆角表头 */
        }

        td {
            background-color: rgba(255, 255, 255, 0.9);
            color: #333;
            border-radius: 8px;
        }

        tr:nth-child(even) td {
            background-color: #f9f9f9; /* 偶数行更柔和 */
        }

        tr:hover {
            background-color: #e1f5fe; /* 悬浮行背景色 */
            transform: translateY(-5px); /* 行悬浮效果 */
        }

        tr {
            transition: background-color 0.3s ease-in-out, transform 0.2s;
        }

        /* 响应式设计 */
        @media screen and (max-width: 768px) {
            h1 {
                font-size: 40px;
            }
            table {
                width: 100%;
                font-size: 14px;
            }
            th, td {
                padding: 12px;
            }
        }
    </style>
    <title>SOST稳定性历史数据</title>
    <h1>SOST稳定性历史数据</h1>
    <table>
        <tr>
            <th>Time</th>
            <th>Type</th>
            <th>Count</th>
            <th>BIOS Version</th>
            <th>BMC Version</th>
            <th>Result</th>
        </tr>"""

    # 按行拆分数据
    entries = raw_data.split("<br>")

    for entry in entries:
        if entry.strip():  # 如果行不为空
            # 解析每一行的内容，格式为 {key: value}
            entry_data = entry.strip('{}').split(',')
            time, type_, count, bios_ver, bmc_ver, result = "", "", "", "", "", ""

            # 提取具体字段
            for field in entry_data:
                key, value = field.split(':')
                if key.strip() == "time":
                    time = value.strip()
                elif key.strip() == "type":
                    type_ = value.strip()
                elif key.strip() == "count":
                    count = value.strip()
                elif key.strip() == "bios.ver":
                    bios_ver = value.strip()
                elif key.strip() == "bmc.ver":
                    bmc_ver = value.strip()
                elif key.strip() == "result":
                    result = value.strip()  # 确保去除多余空格
            # 直接将数据填入表格的一行，不做背景色的判断
            formatted_data += f'<tr><td>{time}</td><td>{type_}</td><td>{count}</td><td>{bios_ver}</td><td>{bmc_ver}</td><td>{result}</td></tr>'
    # 结束表格
    formatted_data += "</table>"
    return formatted_data

@app.route('/get_data')
def return_get_data():

    if log.os_popen("ps aux | grep -i swc_cinfo | grep -v grep | wc -l",flags=cmd_log_flags).strip()!='0':
        return log.os_popen("cat /opt/sost/config/server_info.json",flags=cmd_log_flags)
    else:
        os.system("nohup python3 /opt/sost/lib/swc_cinfo.py &")
        time.sleep(3)
        return log.os_popen("cat /opt/sost/config/server_info.json",flags=cmd_log_flags)

@app.route('/swc_flags')
def return_swc_flags():
    os.system(''' sed -i 's/"swc_flags": "0"/"swc_flags": "1"/g' /opt/sost/config/sost.json ''')
    result = os.popen("cat /opt/sost/config/sost.json | grep -i 'swc_flags'").read().strip()
    return "Success!"+result

@app.route("/sost_tmp")
def return_sost_tmp():
    result = os.popen("cat /tmp/sost_tmp/swc_cache").read().replace('\n', '<br>').replace(" ", "&nbsp&nbsp")
    return result

@app.route('/execute_command', methods=['POST'])
def execute_command():
    data = request.get_json()
    command = data.get('command')
    try:
        # 使用subprocess模块执行命令
        output = log.os_popen(command)
    except subprocess.CalledProcessError as e:
        output = f"Command '{command}' returned non-zero exit status {e.returncode}.\n{e.stderr}"
    except Exception as e:
        output = f"An error occurred: {str(e)}"

    return jsonify({'output': output})

if __name__ == '__main__':

    log.os_popen("systemctl stop firewalld.service",flags=cmd_log_flags)
    log.os_popen("iptables -F",flags=cmd_log_flags)
    log.os_popen("mkdir -p /tmp/sost_tmp",flags=cmd_log_flags)
    log.os_popen("touch /tmp/sost_tmp/swc_ipmi_lan1.txt",flags=cmd_log_flags)
    log.os_popen("touch /tmp/sost_tmp/swc_ipmi_lan8.txt",flags=cmd_log_flags)
    log.os_popen("touch /tmp/sost_tmp/swc_ipmi_Board_Product.txt",flags=cmd_log_flags)
    log.os_popen("touch /tmp/sost_tmp/swc_cache",flags=cmd_log_flags)

    lan_1_result = log.os_popen("ipmitool lan print 1 | grep -i 'ip address' | grep -vi source | awk '{print $4}'",
                                flags=cmd_log_flags)
    if lan_1_result.strip() != "":log.os_popen(f"echo '{lan_1_result}' > /tmp/sost_tmp/swc_ipmi_lan1.txt &", flags=cmd_log_flags)

    lan_8_result = log.os_popen("ipmitool lan print 8 | grep -i 'ip address' | grep -vi source | awk '{print $4}'",flags=cmd_log_flags)
    if lan_8_result.strip() != "":log.os_popen(f"echo '{lan_8_result}' > /tmp/sost_tmp/swc_ipmi_lan8.txt &", flags=cmd_log_flags)

    log.os_popen("ipmitool fru print 0 | grep -i 'Board Product' | awk '{print $4}' > /tmp/sost_tmp/swc_ipmi_Board_Product.txt &",flags=cmd_log_flags)
    log._pr(f"swc_web is Running! Running-Time -> {str(datetime.now().strftime('%Y%m%d %H:%M:%S'))} (swc_web.py)")
    if log.os_popen("ps aux | grep -i swc_cinfo | grep -v grep | wc -l",flags=cmd_log_flags).strip()=="0":
        log._pr("swc_web -> swc_cinfo Running! (swc_web.py)")
    else:
        log._pr("swc_web -> swc_cinfo is aleady Running! (swc_web.py)")
        os.system("nohup python3 /opt/sost/lib/swc_cinfo.py &")
    os.system("rm -rf nohup.out")
    app_ip = log.os_popen(''' cat /opt/sost/config/swc.json  | grep -i swc_ip | cut -d ':' -f 2 | tr -d '",' ''',flags=cmd_log_flags).strip()
    app_port = log.os_popen(''' cat /opt/sost/config/swc.json  | grep -i swc_port | cut -d ':' -f 2 | tr -d '",' ''',flags=cmd_log_flags).strip()
    app.run(host=app_ip, port=int(app_port))
