from os import popen
from json import dumps
from time import sleep
from requests import post
from sys import exit


def check_user_exists():
    inputdata = raw_input('Enter your email: ')
    email = dumps({'email': inputdata}, ensure_ascii='False')
    urlcheck = "http://localhost.monitorbeta.com/rest/v1/checkemail"
    headers = {'content-type': 'application/json'}
    r = post(urlcheck, data=email, headers=headers)
    response = r.text
    if(response == "emailcheck_working"):
        check_auth_file()
    else:
        print ("You are not registered")
        exit()


def check_auth_file():
    global auth_code
    try:
        with open('/opt/linuxmonitor/serverauth.txt', 'r') as auth_file:
            auth_code = auth_file.read()
            auth = dumps({'auth': auth_code}, ensure_ascii='False')
            urlcheck = "http://localhost.monitorbeta.com/rest/v1/checkauth"
            headers = {'content-type': 'application/json'}
            r = post(urlcheck, data=auth, headers=headers)
            response = r.text
            if (response == "auth_result_working"):
                send_monitor_data()
            else:
                print ("Authentification code is not correct")
                choice = raw_input(
                    'Do you want to configure your server auth code [Y/N]: ')
                if (choice == "y") or (choice == "Y"):
                    configure_auth_file()
                elif (choice == "n") or (choice == "N"):
                    print ("Missing Authentification Code error will stay")
                    exit(0)
                else:
                    print ("Invalid select")
                    exit(0)
    except IOError as e:
        print ("Missing authentification file. Error: ", e)
        choice = raw_input(
            'Do you want to create and configure your server auth code [Y/N]: ')
        if (choice == "y") or (choice == "Y"):
            create_auth_file()
        elif (choice == "n") or (choice == "N"):
            print ("Missing Authentification Code error will stay")
            exit(0)
        else:
            print ("Invalid select")
            exit(0)


def configure_auth_file():
    try:
        with open('/opt/linuxmonitor/serverauth.txt', 'r+') as auth_file:
            auth_file.truncate()
            your_auth = raw_input(
                "Enter your server's authentification code: ")
            auth_file.write(your_auth)
            print (
                "-------------------------------------------------------------------")
            print (
                "#                  Your new auth code is saved.                   #")
            print (
                "-------------------------------------------------------------------")
            print ("Script Restart in 3 seconds...")
            auth_file.close()
            sleep(3)
            check_auth_file()
    except IOError as e:
        print ("Missing authentification file. Error: ", e)
        exit()


def create_auth_file():
    try:
        f = open("/opt/linuxmonitor/serverauth.txt", "w+")
        print ("-------------------------------------------------------------------")
        print ("#                   Your auth file is created.                    #")
        print ("-------------------------------------------------------------------")
        print ("Configuration starts in 3 seconds...")
        f.close()
        sleep(3)
        configure_auth_file()
    except IOError as e:
        print ("Error: ", e)
        print ("Remember to run this script as root (sudo python main.py): ")
        exit()


def send_monitor_data():
    os_name = popen("lsb_release -si").readline().strip()
    os_version = popen("lsb_release -sr").readline().strip()

    hostname = popen("hostname").readline().strip()
    internal_ip = popen("hostname -I").readline().strip()
    external_ip = popen(
        "wget -qO- http://ipecho.net/plain ; echo").readline().strip()

    cpu_model = popen(
        "lscpu | grep 'Model name:' | awk '{$1=\"\";$2=\"\";print}'").readline().strip()
    cpu_architecture = popen(
        "lscpu | grep 'Architecture:' | awk '{$1=\"\";print}'").readline().strip()
    cpu_cores = int(popen(
        "lscpu | grep 'Core(s) per socket:' | awk '{$1=\"\";$2=\"\";$3=\"\";print}'").readline().strip())
    cpu_threads = int(popen(
        "lscpu | grep 'Thread(s) per core:' | awk '{$1=\"\";$2=\"\";$3=\"\";print}'").readline().strip())
    cpu_percentage = round(float(popen(
        "awk -v a=\"$(awk '/cpu /{print $2+$4,$2+$4+$5}' /proc/stat; sleep 1)\" '/cpu /{split(a,b,\" \"); print 100*($2+$4-b[1])/($2+$4+$5-b[2])}'  /proc/stat").readline().strip()), 2)

    ram_total = round(
        (float(popen("free -m | grep Mem | awk '{print $2}'").readline().strip()) / 1024), 2)
    ram_used = round(
        (float(popen("free -m | grep Mem | awk '{print $3}'").readline().strip()) / 1024), 2)
    ram_free = round(
        (float(popen("free -m | grep Mem | awk '{print $4}'").readline().strip()) / 1024), 2)
    ram_shared = round(
        (float(popen("free -m | grep Mem | awk '{print $5}'").readline().strip()) / 1024), 2)
    ram_buff = round(
        (float(popen("free -m | grep Mem | awk '{print $6}'").readline().strip()) / 1024), 2)
    ram_available = round(
        (float(popen("free -m | grep Mem | awk '{print $7}'").readline().strip()) / 1024), 2)

    swap_total = round((float(
        popen("free -m | grep Swap | awk '{print $2}'").readline().strip()) / 1024), 2)
    swap_used = round((float(
        popen("free -m | grep Swap | awk '{print $3}'").readline().strip()) / 1024), 2)
    swap_free = round((float(
        popen("free -m | grep Swap | awk '{print $4}'").readline().strip()) / 1024), 2)

    total_hdd = round((float(popen(
        "df -P | awk '/^\/dev\/sd[a-z]/ { sum+=$2 } END { print sum }'").readline().strip()) / pow(1024, 2)), 2)
    used_hdd = round((float(popen(
        "df -P | awk '/^\/dev\/sd[a-z]/ { sum2+=$3 } END { print sum2 }'").readline().strip()) / pow(1024, 2)), 2)
    available_hdd = round((float(popen(
        "df -P | awk '/^\/dev\/sd[a-z]/ { sum3+=$4 } END { print sum3 }'").readline().strip()) / pow(1024, 2)), 2)

    pid_running = int(popen("ps -ef | wc -l").readline().strip())

    uptime = round(
        (float(popen("awk '{print $1}' /proc/uptime").readline()) / 3600), 2)

##################################################JSON SEND DATA###############################################
    windows_usage = dumps({
        'auth_code': auth_code,

        'os_name': os_name,  # string
        'os_version': os_version,  # string

        'cpu_model': cpu_model,  # CPU Model
        'cpu_architecture': cpu_architecture,  # CPU Archi..
        'cpu_cores': cpu_cores,  # Number of cpus
        'cpu_threads': cpu_threads,  # Number of threads
        'cpu_percentage': cpu_percentage,  # CPU Perc
        'pid_running': pid_running,  # Number of active PIDs

        'hostname': hostname,  # string
        'internal_ip': internal_ip,  # string
        'external_ip': external_ip,  # string

        'ram_total': ram_total,  # GB
        'ram_used': ram_used,  # GB
        'ram_free': ram_free,  # GB
        'ram_shared': ram_shared,  # GB
        'ram_available': ram_available,  # GB
        'ram_buff': ram_buff,  # GB

        'swap_total': swap_total,  # GB
        'swap_used': swap_used,  # GB
        'swap_free': swap_free,  # GB

        'total_hdd': total_hdd,  # All SDx partitions total in GB
        'used_hdd': used_hdd,  # All SDx partitions usage in GB
        'available_hdd': available_hdd,  # Free space in GB

        'uptime': uptime,  # Uptime in H:M format
    }, ensure_ascii='False')

    # Print value just for testing
    print(windows_usage)

    # Post data to server
    url = "http://localhost.monitorbeta.com/rest/v1/endpoint"
    headers = {'content-type': 'application/json'}
    r = post(url, data=windows_usage, headers=headers)

    # Print response just for testing
    print(r.text)

    sleep(5)

    # Recursive
    send_monitor_data()


def main():
    check_user_exists()


if __name__ == "__main__":
    main()

