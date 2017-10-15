#!/usr/bin/env python
#-*- coding:utf-8 -*-

from json import dump, load
from re import sub, findall
from urllib import request, parse
import ssl
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.resources import resource_find
frot=resource_find("DroidSansFallback.ttf")
from kivy.uix.label import Label
from kivy.uix.popup  import Popup
baidu = 'http://www.soso.com'
info_file = 'cmcc_info.json'
def printa(str):
    Popup(title='cmccedu', content=Label(text=str,font_name=frot),size_hint=(None, None), size=(200, 300)).open()

def get_info(username,password,sslv3=False):
    baidu = 'http://www.baidu.com'
    save = {
        'username': username,
        'password': password
    }
    with open('save', 'w') as f:
        dump(save, f)
    if sslv3:
        https_sslv3_handler = request.HTTPSHandler(context=ssl.SSLContext(ssl.PROTOCOL_SSLv3))
        opener = request.build_opener(https_sslv3_handler)
        request.install_opener(opener)
    requesto = request.urlopen(baidu)
    url = requesto.geturl()                   # get redirect url
    if url == baidu:
        domain = ''
        login_info = {}
        printa (u'已经连网，不用再登录了:-)')
    else:
        print ('正在获取登录信息...')
        domain, args_url = url.split('?')
        wlanacssid = 'CMCC-EDU' # for CMCC-EDU, ssid is always CMCC-EDU
        args = args_url.split('&')
        for arg in args:
            if arg.split('=')[0] == 'wlanuserip':
                wlanuserip = arg.split('=')[1]
            elif arg.split('=')[0] == 'wlanacname':
                wlanacname = arg.split('=')[1]
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
        info = {'domain':domain, 'logout_info':logout_info}
        with open(info_file, 'w') as f:
            dump(info, f)

    return domain, login_info

def login(domain, info):
    if domain:
        print ('正在登录...')
        params = parse.urlencode(info).encode('ascii')
        login_url = domain.replace('input', 'login')
        requesto = request.Request(url=login_url, data=params, unverifiable=True)
        response = request.urlopen(requesto)
        encoding = response.headers['content-type'].split('charset=')[-1]
        content = response.read().decode(encoding)
        if '登录成功' in content:
            time_remains = findall('套餐剩余.*', content)
            if time_remains:
                printa ('登录成功'+'\n'+sub('<[^<]+?>', '', time_remains[0]))

        else:
            printa ('登录失败！')

def logout(domain, info):
    logout_url = domain.replace('input', 'logout')
    params = parse.urlencode(info).encode('ascii')
    requesto = request.Request(url=logout_url, data=params, unverifiable=True)
    try:
        response = request.urlopen(requesto,timeout=5)
        if response.code == 200:
            printa('成功下线！')
    except:
        printa('下线错误！')

class LoginScreen(GridLayout):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        try:
            with open('save', 'r') as f:
                d = load(f)
                username= d['username']
                password= d['password']
        except:
             username=''
             password=''
        self.cols = 2
        self.row_force_default=True
        self.row_default_height=40
        self.add_widget(Label(text=u'用户名',font_name=frot))
        self.username = TextInput(multiline=False,text=username)
        self.add_widget(self.username)
        self.add_widget(Label(text=u'密码',font_name=frot))
        self.password = TextInput(password=True, multiline=False,text=password)
        self.add_widget(self.password)
        denglu = Button(text=u'登陆',font_name=frot)
        xiaxian = Button(text=u'下线',font_name=frot)
        denglu.bind(on_release=self.denglu)
        xiaxian.bind(on_release=self.xiaxian)
        self.add_widget(denglu)
        self.add_widget(xiaxian)
    def denglu(self,obj):
        domain, login_info = get_info(self.username.text,self.password.text)
        login(domain, login_info)
    def xiaxian(self,obj):
        with open(info_file, 'r') as f:
            d = load(f)
        domain = d['domain']
        logout_info = d['logout_info']
        logout(domain, logout_info)



class cmccedu(App):
    def build(self):
        return LoginScreen()

if __name__ == '__main__':
    cmccedu().run()

