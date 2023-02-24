# Author inokoe , 2023/2/21
# The first version, without sufficient validation！
import hashlib
import hmac
import json
import random
import re
import time

import requests
from my_fake_useragent import UserAgent

from srun_base64 import *
from srun_xencode import *

# User info
username = ''
password = ''

# Browser User Agent
ua = UserAgent(family='chrome')

# Http Protocol
http_prefix = "http://"

# domain URL pool
domain_suffix = {"domain": "gw.xju.edu.cn",
                 "user_info": "gw.xju.edu.cn/cgi-bin/rad_user_info",
                 "get_challenge": "gw.xju.edu.cn/cgi-bin/get_challenge",
                 "login": "gw.xju.edu.cn/cgi-bin/srun_portal"}

# Browser Header
headers = {
    'user_agent': ua.random(),
    'referer': domain_suffix['domain']
}

# Key parameter
callback = str(int(time.time() * 100 * 100 + random.randint(1, 9999)))
time_stamp = str(int(time.time() * 100))

# Login parameters , base64 info
# This is a fixed encoding for generating the accession key parameters
info = ''

# ip
ip = ''

# token
token = ''

# chksum
chksum = ''

# enc
enc = 'srun_bx1'

# MD5
md5 = ''


def url_maker(suffix):
    return http_prefix + suffix


def check_server_status():
    response = requests.get(url_maker(domain_suffix['domain']), timeout=5, headers=headers)
    if response.status_code == 200:
        print("Server found.")
        return True
    else:
        print("Could not find the protal server")
        return False


def catch_user_info():
    my_params = {'callback': "jQuery" + callback, '_': time_stamp}
    response = requests.get(url_maker(domain_suffix['user_info']), timeout=5, headers=headers, params=my_params)
    response.encoding = 'utf8'
    return response


def info_catch(x):
    x = x.replace('jQuery', '')
    x = x.replace(callback, '')
    x = x.replace('(', '')
    x = x.replace(')', '')
    return x


def challenge():
    my_params = {'callback': "jQuery" + callback, '_': time_stamp, 'username': username, 'ip': ip, '_': time_stamp}
    response = requests.get(url_maker(domain_suffix['get_challenge']), timeout=5, headers=headers, params=my_params)
    if response.status_code != 200:
        return False
    text = info_catch(response.text)
    text = json.loads(text)
    if text['error'] == 'ok':
        global token
        token = text['challenge']
        return True
    return False


def user_data_collect(y):
    x = {}
    # Show username or not.
    # x['user_name'] = y['user_name']
    trans_time = time.localtime(y['add_time'])
    trans_time = time.strftime("%Y-%m-%d %H:%M:%S", trans_time)
    x['Last login time'] = trans_time
    x['ISP'] = y['billing_name']
    x['Online Ip'] = y['online_ip']
    x['Usage'] = str(y['sum_bytes'])[0:2] + 'GB'
    x = json.dumps(x, sort_keys=True, indent=4, separators=(',', ':'),
                   ensure_ascii=False)
    return x


def md5_calculation():
    global password, token
    return hmac.new(token.encode(),
                    password.encode(), hashlib.md5).hexdigest()


def sha1_calculation():
    global token, password, username, info
    chksum = token + username + token + md5.replace('{MD5}',
                                                    '') + token + '4' + token + ip + token + '200' + token + '1' + token + info
    # print(chksum)
    return hashlib.sha1(chksum.encode()).hexdigest()


def get_info():
    global username, password, ip, enc
    info_temp = {
        "username": username,
        "password": password,
        "ip": ip,
        "acid": '1',
        "enc_ver": enc
    }
    i = re.sub("'", '"', str(info_temp))
    i = re.sub(" ", '', i)
    return i


def login():
    global username, password, chksum, info, ip
    info = "{SRBX1}" + get_base64(get_xencode(get_info(), token))
    chksum = sha1_calculation()
    # print("chksum", chksum)
    my_params = {'callback': "jQuery" + callback, '_': time_stamp, 'action': 'login', 'username': username,
                 'password': md5, 'os': 'Windows 10', 'name': 'Windows', 'double_stack': '1', 'chksum': chksum,
                 'ac_id': '4', 'ip': ip, 'n': '200', 'type': '1', 'info': info}
    # print(my_params)
    response = requests.get(url_maker(domain_suffix['login']), timeout=5, headers=headers, params=my_params)
    if response.status_code == 200:
        response = info_catch(response.text)
        response = json.loads(response)
        if response['error'] == 'ok':
            print('Login Success')
            time.sleep(2)
            show_user_info(catch_user_info().text)
        else:
            print('Login Failed Cause - ', response['error'])


def show_user_info(y):
    # print(y)
    x = info_catch(y)
    x = json.loads(x)
    print(user_data_collect(x))


def show_all_details():
    print("MD5", md5)
    print('login')
    print('ip', ip)
    print(info)
    print("token", token)


if __name__ == '__main__':
    print("running .....")
    if username == '' or password == '':
        print('No user info set!')
        exit(0)
    if check_server_status():
        res = catch_user_info()
        if res.status_code != 200:
            print("The server has been found, but its response is not normal.")
        else:
            res_text = info_catch(res.text)
            # print(res.text)
            res_text = json.loads(res_text)
            ip = res_text['online_ip']
            print("Check server status.")
            if res_text['error'] == 'ok':
                print('You have already logged in.')
                print(user_data_collect(res_text))
            else:
                print("Verification is required before login.")
                if challenge():
                    md5 = '{MD5}' + md5_calculation()
                    login()

    print('... (_ Exit _)...')
    time.sleep(3)
