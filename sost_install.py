# Filename : sost_install.py
# Release time : 2024-09-18
# Version:1.0.1
# by:Dong

import os
import time

def sost_print(text):
    print(f'<sost> {str(text).strip()}')

def wait_symbol(timeout):
    for i in reversed(range(0,int(timeout))):
        print(" [-.-] ", end="", flush=True)
        time.sleep(1)
    print("\n")

def alive():
    sost_print('Before installation begins, please check the network configuration. ')
    sost_print('If you need to debug the network, use Ctrl+C to close the installation script!')
    sost_print('安装开始前请检查网络配置,如果需要调试网络，ctrl + c 关闭安装脚本!')
    sost_print('Time out waiting for 5 s（超时等待5秒）')
    wait_symbol(5)
    ping_flags = 0
    while True:
        if '0% packet loss' in os.popen('ping -c 1 ttyinfo.com').read().strip():
            sost_print('Installation mode : Online mode')
            install_mode = 'Online'
            break
        else:
            ping_flags += 1
            sost_print(f'Retry {ping_flags} times(重试中!)')
            time.sleep(1)

        if ping_flags == 5:
            print('\n')
            sost_print('Installation mode : Offline mode')
            install_mode = 'Offline'
            break
    return install_mode

def linux_os():
    distro = None
    version = None
    # 检查 /etc/os-release
    if os.path.exists('/etc/os-release'):
        with open('/etc/os-release', 'r') as f:
            for line in f:
                if line.startswith('ID='):
                    distro_id = line.split('=')[1].strip('"\n')
                    if distro_id == 'ubuntu':
                        distro = 'Ubuntu'
                    elif distro_id == 'rhel' or 'redhat' in distro_id.lower():
                        distro = 'RHEL'
                    elif distro_id == 'centos' or 'centos' in distro_id.lower():
                        distro = 'CentOS'
                    elif distro_id == 'kylin':
                        distro = 'Kylin'
                    elif distro_id == "openEuler":
                        distro = 'openEuler'
                if line.startswith('VERSION_ID='):
                    version = line.split('=')[1].strip('"\n')
                if distro and version:
                    break

    # 如果 /etc/os-release 没有提供足够的信息，则检查其他文件
    if not distro or not version:
        if os.path.exists('/etc/redhat-release'):
            with open('/etc/redhat-release', 'r') as f:
                content = f.read().strip()
                if 'CentOS' in content:
                    distro = 'CentOS'
                    # 尝试从内容中提取版本号
                    for part in content.split():
                        if part.startswith('release') or part.startswith('CentOS'):
                            version = part.split()[-1]
                elif 'Red Hat' in content:
                    distro = 'RHEL'
                    # 尝试从内容中提取版本号
                    for part in content.split():
                        if part.startswith('release') or part.startswith('Red Hat'):
                            version = part.split()[-1]
        elif os.path.exists('/etc/centos-release'):
            distro = 'CentOS'
            with open('/etc/centos-release', 'r') as f:
                content = f.read().strip()
                # 尝试从内容中提取版本号
                for part in content.split():
                    if part.startswith('CentOS'):
                        version = part.split()[-1]
        elif os.path.exists('/etc/kylin-release'):
            distro = 'Kylin'
    if not version:
        version = 'Unknown'

    return distro, version

def rhel_yum_replace(ver):
    #version

    if '10.0' in ver:
        os.system("mv /etc/yum.repos.d/redhat.repo /etc/yum.repos.d/redhat.repo.bak")
        with open("/etc/yum.repos.d/aliyun_yum.repo","a") as f:
            f.write("[ali_baseos]\n")
            f.write("name=ali_baseos\n")
            f.write("baseurl=https://mirrors.aliyun.com/centos-stream/10-stream/BaseOS/x86_64/os/\n")
            f.write("gpgcheck=0\n")
            f.write("\n")
            f.write("[ali_appstream]\n")
            f.write("name=ali_appstream\n")
            f.write("baseurl=https://mirrors.aliyun.com/centos-stream/10-stream/AppStream/x86_64/os/\n")
            f.write("gpgcheck=0\n")
            f.flush()
        f.close()
    
    elif "9." in ver:
        # bakcup
        os.system("mv /etc/yum.repos.d/redhat.repo /etc/yum.repos.d/redhat.repo.bak")
        with open("/etc/yum.repos.d/aliyun_yum.repo","a") as f:
            f.write("[ali_baseos]\n")
            f.write("name=ali_baseos\n")
            f.write("baseurl=https://mirrors.aliyun.com/centos-stream/9-stream/BaseOS/x86_64/os/\n")
            f.write("gpgcheck=0\n")
            f.write("\n")
            f.write("[ali_appstream]\n")
            f.write("name=ali_appstream\n")
            f.write("baseurl=https://mirrors.aliyun.com/centos-stream/9-stream/AppStream/x86_64/os/\n")
            f.write("gpgcheck=0\n")
            f.flush()
        f.close()
    elif "8." in ver:
        # bakcup
        os.system("mv /etc/yum.repos.d/redhat.repo /etc/yum.repos.d/redhat.repo.bak")
        os.system("curl -o /etc/yum.repos.d/redhat.repo http://mirrors.aliyun.com/repo/Centos-8.repo")
    elif "7." in ver:
        os.system("mv /etc/yum.repos.d/redhat.repo /etc/yum.repos.d/redhat.repo.bak")
        os.system("curl -o /etc/yum.repos.d/redhat.repo http://mirrors.aliyun.com/repo/Centos-7.repo")
    print("rhel_yum_replace Success!")

def install_tools(install_type):
    tools_arr = ["nvme-cli","ipmitool","smartmontools","python3-pip","minicom","python3-flask","net-tools","network-manager","fio","libaio*","nvme-cli","numactl","sysstat"]
    if install_type == "ubuntu":
        os.system("apt list --installed > /tmp/apt_installed_list.txt 2>/dev/null")
        f = open("/tmp/apt_installed_list.txt","r").read()
        for tool in tools_arr:
            if tool.strip() in f:
                continue
            os.system(f"apt-get install {tool.strip()} -y")
        os.system("apt-get install numactl* -y")
    else:
        os.system("yum list installed > /tmp/yum_installed_list.txt 2>/dev/null")
        f = open("/tmp/yum_installed_list.txt","r").read()
        for tool in tools_arr:
            if tool.strip() in f:
                continue
            os.system(f"yum install {tool.strip()} -y")
        os.system("yum install numactl* -y")
    # init python3 pip
    os.system("pip3 list > /tmp/pip3_installed_list.txt 2>/dev/null")
    f = open("/tmp/pip3_installed_list.txt","r").read()
    os.system("python3 -m ensurepip --default-pip")
    #os.system("pip3 install --upgrade nltk -i https://pypi.tuna.tsinghua.edu.cn/simple --force")
    pip_install_array = ["wheel","pyinstaller","Flask","requests","tqdm","nltk"]
    for pip_package in pip_install_array:
        if pip_package.strip() in f:
            continue
        os.system(f'pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple {pip_package} --force')
    
def install_sost():

    print(os.getcwd())

    # Create Sost Stablity OLD Folder
    os.system("mkdir -p /root/sost_old_folder")

    # Backup Last Sost Install Folder
    backup_folder_name = f'/opt/bak_sost_{str(time.strftime("%Y%m%d%H%M"))}'
    if os.path.exists("/opt/sost"):
        os.system("rm -rf /opt/bak_sost_*")
        os.system(f"mv /opt/sost {backup_folder_name}")

    # now_path = /tmp/sost-v1.0.8-Release
    now_path = os.path.dirname(os.getcwd()+"/sost_install.py")

    # cp Release File To sost Folder
    os.system("mkdir -p /opt/sost")
    os.system(f"cp -rf {now_path}/* /opt/sost")
    os.system(f"chmod 777 -R /opt/sost/*")

    # backup histroy File To Release Folder
    os.system(f"cp -rf {backup_folder_name}/history /opt/sost/history 2>/dev/null")

    #Clear Install File
    os.system("rm -rf /opt/sost/sost_install.py")
    os.system("rm -rf /opt/sost/packages")
    os.system("rm -rf /opt/sost/__pycache__")
    os.system("rm -rf /opt/sost/.vscode")

    # Judge sost.py in sost/bin
    if os.path.exists('/opt/sost/bin/sost.py'):
        print("sost.py in /opt/sost/bin!")
    
    return now_path

def init():
    __file__ = os.getcwd()+"/sost_install.py"
    sost_folder_path = os.path.dirname(__file__)
    sost_folder_name = os.path.basename(os.path.dirname(__file__))
    sost_os_path = os.path.dirname(sost_folder_path)
    for file_name in os.listdir(sost_os_path):
        if "sost" in file_name and "Release.tar" in file_name:
            os.system(f"rm -rf {sost_os_path}/{file_name}")
        if "sost" in file_name and "Release" in file_name:
            if file_name == sost_folder_name:
                continue
            else:
               os.system(f"rm -rf {sost_os_path}/{file_name}")
    # kill sost web_console service
    os.system("ps -aux | grep -i sost_web_console | grep -v grep | awk '{print $2}' | xargs kill -9")
    print("初始化安装环境成功!")
    print("Init Install env Pass!")

def build_sost():
    # Delete Old sost Command
    os.system('rm -rf /usr/bin/sost')
    os.system('rm -rf /usr/local/bin/sost')
    #Check pyinstaller Tools
    if os.popen("whereis pyinstaller | cut -d ':' -f 2").read().strip() != "":
        #Check bin Folder
        if not os.path.exists("/opt/sost/bin"):
            print("Not Found /opt/sost/bin Folder")
            exit()
        # build sost.py
        os.system('cd /opt/sost/bin && pyinstaller -F --onefile sost.py && mv dist/sost . && rm -rf sost.spec && rm -rf build/ && rm -rf dist/ && yes | mv /opt/sost/bin/sost /usr/local/bin/sost')
        
        #check build sost command
        if os.path.exists("/usr/local/bin/sost"):
            print("sost build command success!")
        else:
            print("sost build command Fail!")
            os.system("cd /opt/sost && touch /usr/local/bin/sost && chmod 777 /usr/local/bin/sost && echo 'python3 /opt/sost/bin/sost.py $1 $2 $3 $4 $5 $6' >> /usr/local/bin/sost && cd && sync && sost -h")
    else:
        print("Pyinstaller安装失败，现在进行手动安装。")
        os.system("cd /opt/sost && touch /usr/local/bin/sost && chmod 777 /usr/local/bin/sost && echo 'python3 /opt/sost/bin/sost.py $1 $2 $3 $4 $5 $6' >> /usr/local/bin/sost && cd && sync && sost -h")

def swc_manager():
    os.system("systemctl stop swc-manager.service 2>/dev/null")
    os.system("rm -rf /etc/systemd/system/swc-manager.service 2>/dev/null")
    os.system("touch /etc/systemd/system/swc-manager.service 2>/dev/null")
    with open("/etc/systemd/system/swc-manager.service","w") as f:
        f.write("[Unit]"+"\n")
        f.write("Description=swc-manager"+"\n")
        f.write("After=multi-user.target,graphical.target"+"\n")
        f.write(""+"\n")
        f.write("[Service]"+"\n")
        f.write("Type=simple"+"\n")
        f.write("ExecStart=python3 /opt/sost/swc_web.py > /dev/null"+"\n")
        f.write("Restart=on-failure"+"\n")
        f.write(""+"\n")
        f.write("[Install]"+"\n")
        f.write("WantedBy=multi-user.target"+"\n")
        f.write(""+"\n")
        f.flush()
    os.system("chmod 777 /etc/systemd/system/swc-manager.service 2>/dev/null")
    os.system("systemctl daemon-reload 2>/dev/null")
    os.system("systemctl restart swc-manager.service 2>/dev/null")
    os.system("systemctl enable swc-manager.service 2>/dev/null")
    print("<sost> service is installed!")

def ubuntu_apt_replace():
    os.system("sudo cp /etc/apt/sources.list /etc/apt/sources.list.backup")
    os.system('''sudo bash -c "cat << EOF > /etc/apt/sources.list
deb http://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs) main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs)-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs)-backports main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs)-security main restricted universe multiverse
EOF"''')
    os.system('apt update')
    os.system('dpkg-divert --rename --add /usr/lib/$(py3versions -d)/EXTERNALLY-MANAGED ubuntu pip3')

def openEuler_yum_replace():
    
    repo_info = os.popen('cat /etc/yum.repos.d/openEuler.repo').read()
    if 'huaweicloud' in repo_info:
        return 0
    if 'aliyun' in repo_info:
        return 0

    os.system('rm -rf /etc/yum.repos.d/local.repo')
    # cp backupFile to openEuler.repo
    os.system('cp -rf /etc/yum.repos.d/openEuler.repo.bak /etc/yum.repos.d/openEuler.repo 2>/dev/null')
    os.system('cp -rf /etc/yum.repos.d/openEuler.repo-bak /etc/yum.repos.d/openEuler.repo 2>/dev/null')
    os.system('cp -rf /etc/yum.repos.d/bak.openEuler.repo /etc/yum.repos.d/openEuler.repo 2>/dev/null')
    os.system('cp -rf /etc/yum.repos.d/openEuler.repobak /etc/yum.repos.d/openEuler.repo 2>/dev/null')

    os.system('cp -rf /etc/yum.repos.d/openEuler.repo /etc/yum.repos.d/openEuler.repo.bak 2>/dev/null')
    os.system(''' sed -i 's|http://repo.openeuler.org/|http://repo.huaweicloud.com/openeuler/|g' /etc/yum.repos.d/openEuler.repo ''')
    os.system("yum clean all")
    os.system("yum makecache")

if __name__ == '__main__':
    print('''
        ==========================================================
        |         ████████                    ██                 |
        |        ██░░░░░░                    ░██                 |
        |       ░██         ██████   ██████ ██████               |
        |       ░█████████ ██░░░░██ ██░░░░ ░░░██░                |
        |       ░░░░░░░░██░██   ░██░░█████   ░██                 |
        |              ░██░██   ░██ ░░░░░██  ░██                 |
        |        ████████ ░░██████  ██████   ░░██                |
        |       ░░░░░░░░   ░░░░░░  ░░░░░░     ░░                 |
        ==========================================================
        |    sost install success!       Author: Fan Xiaodong    |
        ==========================================================''')
    init()
    install_mode = alive()
    system_os = linux_os()
    
    if install_mode == 'Online':
        install_type = ""
        # RHEL Change yum.repo
        if system_os[0] == "RHEL":
            rhel_yum_replace(system_os[1])
            install_type = "yum"
        elif system_os[0] == "Ubuntu":
            ubuntu_apt_replace()
            install_type = "ubuntu"
        elif system_os[0] == "openEuler":
            openEuler_yum_replace()
        install_tools(install_type)
    elif install_mode == 'Offline':
        os.system("chmod 777 /opt/sost/bin/sost.py && echo 'python3 /opt/sost/bin/sost.py' >> /usr/local/bin/sost && chmod 777 /usr/local/bin/sost")
        sost_print('Install Tool : fio / iostst(sysstat) / numactl / libaio!')
        sost_print('无法识别网络可用！更改为离线安装!请手动安装 fio  iostst(sysstat)  numactl  libaio 四个工具!才能够正常使用!')
        sost_print('Install sost into the server')
        sost_print('正在安装sost工具至服务器中....')
        sost_print('Please manually install the following tools(手动安装以下工具!)')
        print('[!] yum install fio      -y')
        print('[!] yum install sysstat  -y')
        print('[!] yum install numactl  -y')
        print('[!] yum install libaio   -y')
        print('[!] yum install smartmontools -y')
    else:
        sost_print('Install mode Error!')
    
    now_path = install_sost()

    os.system('mkdir -p /tmp/sost_tmp 2>/dev/null')
    if install_mode == 'Online':
        if system_os[0] == 'Ubuntu':
            os.system(f"touch /usr/local/bin/sost && chmod 777 /usr/local/bin/sost && echo 'python3 /opt/sost/bin/sost.py $1 $2 $3 $4' > /usr/local/bin/sost && sost -h")
        else:
            build_sost()
    else:
        os.system(f"touch /usr/local/bin/sost && chmod 777 /usr/local/bin/sost && echo 'python3 /opt/sost/bin/sost.py $1 $2 $3 $4' > /usr/local/bin/sost && sost -h 2>/dev/null")
    swc_manager()
    if os.popen(" whereis sost 2>/dev/null | cut -d ':' -f 2 | tr -d ' ' ") == "":
        os.system("touch /usr/local/bin/sost 2>/dev/null && chmod 777 /usr/local/bin/sost 2>/dev/null && echo 'python3 /opt/sost/bin/sost.py $1 $2 $3 $4' > /usr/local/bin/sost && sost -h 2>/dev/null")
    else:
        if os.popen("file /usr/local/bin/sost 2>/dev/null | grep -i text | wc -l").read().strip() == "0":
            os.system("rm -rf /opt/sost/bin 2>/dev/null")
    os.system("rm -rf /tmp/run.sh 2>/dev/null")

    now_path = os.path.dirname(os.getcwd()+"/sost_install.py")
    os.system(f'rm -rf {now_path} 2>/dev/null')
    os.system(f'rm -rf {now_path}.tar 2>/dev/null')
    
    print('''
==========================================================
|         ████████                    ██                 |
|        ██░░░░░░                    ░██                 |
|       ░██         ██████   ██████ ██████               |
|       ░█████████ ██░░░░██ ██░░░░ ░░░██░                |
|       ░░░░░░░░██░██   ░██░░█████   ░██                 |
|              ░██░██   ░██ ░░░░░██  ░██                 |
|        ████████ ░░██████  ██████   ░░██                |
|       ░░░░░░░░   ░░░░░░  ░░░░░░     ░░                 |
==========================================================
|    sost install Success!        Author: Fan Xiaodong   |  
==========================================================''')