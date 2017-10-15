# coding: UTF-8
from __future__ import unicode_literals
import urllib, urllib2, sys, json, re
mishi='example1mdhcispr'
testurl = 'http://www.speedtest.net'
# change this to file you want to save login info
info_file = 'cmcc_info.json'
import sys,os
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

class prpcrypt():
    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC
    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        return b2a_hex(self.ciphertext)
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text.rstrip(b'\0')
def jiami():
    pc = prpcrypt(mishi)
    print " -------生成密码程序----------"
    username = raw_input(u"请输入用户名：".encode('gbk'))
    u = pc.encrypt(username)
    password = raw_input(u"请输入密码：".encode('gbk'))
    p = pc.encrypt(password)
    r=os.popen('wmic csproduct get UUID')
    info=r.readlines()
    b = pc.encrypt(username+info[2].strip()+password)
    f = open('naprd','wb')
    f.write(u+b'\n'+p+b'\n'+b)
    f.close()
    print ' 已生成本机唯一密匙，文件被拿走也没用'
def jiemi():
    pc = prpcrypt(mishi)
    try:
        f = open('naprd','rb')
        u=f.readline()
        p=f.readline()
        b=f.readline()
        f.close()
    except:
        raise
    username=pc.decrypt(u.strip()).decode()
    password=pc.decrypt(p.strip()).decode()
    r=os.popen('wmic csproduct get UUID')
    info=r.readlines()
    bn = pc.encrypt(username+info[2].strip()+password)
    if bn==b.strip():
        return [username,password]
    else:
        raise ValueError("invavid id")
def get_info(site=testurl):
    request = urllib2.urlopen(site)
    url = request.url                   # get redirect url
    if url == site:
        domain = ''
        login_info = {}
        print ' 已经连网，不用再登录了:-)'
    else:
        print ' 正在获取登录信息...'
        domain, args_url = url.split('?')
        wlanacssid = 'CMCC-EDU' # for CMCC-EDU, ssid is always CMCC-EDU
        args = args_url.split('&')
        for arg in args:
            if arg.split('=')[0] == 'wlanuserip':
                wlanuserip = arg.split('=')[1]
            elif arg.split('=')[0] == 'wlanacname':
                wlanacname = arg.split('=')[1]
            elif arg.split('=')[0] == 'wlanacip':
                wlanacip = arg.split('=')[1]
            # elif arg.split('=')[0] == 'wlanacssid':
            #     wlanacssid = arg.split('=')[1]

        login_info = {
            'staticusername':username,
            'staticpassword':password,
            'wlanacname':wlanacname,
            'wlanuserip':wlanuserip,
            'loginmode':'static',
            'wlanacssid':wlanacssid
        }
        logout_info = {
            'username':username,
            'wlanacname':wlanacname,
            'wlanuserip':wlanuserip,
            'wlanacssid':wlanacssid
        }
        pc = prpcrypt(mishi)
        logout_info=pc.encrypt(str(logout_info))
        info = {'domain':domain, 'logout_info':logout_info}
        with open(info_file, 'w') as f:
            json.dump(info, f)
    return domain, login_info
def login(domain, info):
    if domain:
        print ' 正在登录...'
        params = urllib.urlencode(info)
        login_url = domain.replace('raw_input', 'login')
    # uncheck certificate,this is unsafe, as soon as CMCC-EDU 
    # certificate be valid again, you should set verify=True for
    # security
        request = urllib2.Request(url=login_url, data=params, unverifiable=True)
        response = urllib2.urlopen(request)
        encoding = response.headers['content-type'].split('charset=')[-1]
        content = response.read().decode(encoding)
        if '登录成功' in content:
            print ' 登录成功！'
            time_remains = re.findall('套餐剩余.*', content)
            if time_remains:
                print ' '+re.sub('<[^<]+?>', '', time_remains[0])
        else:
            print ' 登录失败！'
def logout(domain, info):
    logout_url = domain.replace('raw_input', 'logout')
    params = urllib.urlencode(info)
    request = urllib2.Request(url=logout_url, data=params, unverifiable=True)
    response = urllib2.urlopen(request)
    if response.code == 200:
        print ' 成功下线！'
def main(argv=''):
    if len(argv)==2:
        if argv[1]=='jiami':
            jiami()
            exit()
    try:
        [username,password]=jiemi()
    except IOError:
        print ' 读写错误，是否生成密码文件'
        jiami()
        raw_input(u"按任意键登陆".encode('gbk'))
        main()
        exit()
    except ValueError:
        print ' 新机器请重新生成密码'
        jiami()
        raw_input(u"按任意键登陆".encode('gbk'))
        main()
        exit()
    except:
        print ' 未知错误'
        exit()
    if len(sys.argv) == 2:
        if sys.argv[1] == 'logout':
            with open(info_file, 'r') as f:
                d = json.load(f)
            pc = prpcrypt(mishi)
            domain = d['domain']
            logout_info = d['logout_info']
            logout_info=json.dumps(pc.decrypt(logout_info).decode())
            logout(domain, logout_info)
            raw_input(u"按任意键关闭".encode('gbk'))
            exit()
    domain, login_info = get_info()
    login(domain, login_info)
    raw_input(u"按任意键关闭".encode('gbk'))
if __name__ == '__main__':
    main(sys.argv)
