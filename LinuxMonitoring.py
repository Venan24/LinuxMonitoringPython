from os import popen
from json import dumps
from time import sleep
from sys import exit
import httplib

def send_monitor_data():
    windows_usage = dumps({
        'auth_code': auth_code,
        'os_name': popen("lsb_release -si").readline().strip(),
        'os_version': popen("lsb_release -sr").readline().strip(),

        'cpu_model' : popen("lscpu | grep 'Model name:' | awk '{$1=\"\";$2=\"\";print}'").readline().strip(),
        'cpu_architecture' : popen("lscpu | grep 'Architecture:' | awk '{$1=\"\";print}'").readline().strip(),
        'cpu_cores' : int(popen("lscpu | grep 'Core(s) per socket:' | awk '{$1=\"\";$2=\"\";$3=\"\";print}'").readline().strip()),
        'cpu_threads' : int(popen("lscpu | grep 'Thread(s) per core:' | awk '{$1=\"\";$2=\"\";$3=\"\";print}'").readline().strip()),
        'cpu_percentage' : round(float(popen("awk -v a=\"$(awk '/cpu /{print $2+$4,$2+$4+$5}' /proc/stat; sleep 1)\" '/cpu /{split(a,b,\" \"); print 100*($2+$4-b[1])/($2+$4+$5-b[2])}'  /proc/stat").readline().strip()),2),
        'pid_running': int(popen("ps -ef | wc -l").readline().strip()),

        'hostname': popen("hostname").readline().strip(),
        'internal_ip': popen("hostname -I").readline().strip(),
        'external_ip': popen("wget -qO- http://ipecho.net/plain ; echo").readline().strip(),

        'ram_total': round((float(popen("free -m | grep Mem | awk '{print $2}'").readline().strip())/1024),2),
        'ram_used': round((float(popen("free -m | grep Mem | awk '{print $3}'").readline().strip())/1024),2),
        'ram_free': round((float(popen("free -m | grep Mem | awk '{print $4}'").readline().strip())/1024),2),
        'ram_shared': round((float(popen("free -m | grep Mem | awk '{print $5}'").readline().strip()) / 1024), 2),
        'ram_available': round((float(popen("free -m | grep Mem | awk '{print $7}'").readline().strip()) / 1024), 2),
        'ram_buff': round((float(popen("free -m | grep Mem | awk '{print $6}'").readline().strip()) / 1024), 2),

        'swap_total': round((float(popen("free -m | grep Swap | awk '{print $2}'").readline().strip())/1024),2),
        'swap_used': round((float(popen("free -m | grep Swap | awk '{print $3}'").readline().strip()) / 1024), 2),
        'swap_free': round((float(popen("free -m | grep Swap | awk '{print $4}'").readline().strip()) / 1024), 2),

        'total_hdd': round((float(popen("df -P | awk '/^\/dev\// { sum+=$2 } END { print sum }'").readline().strip())/pow(1024,2)),2),
        'used_hdd': round((float(popen("df -P | awk '/^\/dev\// { sum2+=$3 } END { print sum2 }'").readline().strip())/pow(1024,2)),2),
        'available_hdd': round((float(popen("df -P | awk '/^\/dev\// { sum3+=$4 } END { print sum3 }'").readline().strip())/pow(1024,2)),2),

        'uptime': round((float(popen("awk '{print $1}' /proc/uptime").readline())/3600),2)
    }, ensure_ascii='False')

    #Post Request
    hdr = {"content-type": "application/json"}
    conn = httplib.HTTPConnection('127.0.0.1:80')
    conn.request('POST', '/rest/v1/endpoint', body=windows_usage, headers=hdr)
    response = conn.getresponse()
    print(response.read())

    sleep(5)

def main():
    while True:
      send_monitor_data()

if __name__ == "__main__":
    try:
      main()
    except KeyboardInterrupt:
      print ("   ### Monitoring scrypt has been stopped by user ###");
      pass