import json
import os
try:
    from ws4py.client.threadedclient import WebSocketClient
except:
    os.system('')
    os.system('pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ws4py')
    print('正在安装依赖...')

import platform
from tkinter import *
from tkinter import messagebox

connected = False
channel_ = '公共聊天室'
my_trip = ''
var_text = None
my_text = None

client_name = '[PIG Chat](https://github.com/MuRongPIG/CrossStreet-Python)'
client_key = 'HXjURea2vReYejA'
def var_append(var, data):
    # var.set(var.get() + '\n' + data)
    my_text.insert(INSERT, '\n' + data)
    my_text.see(END)


class Settings:
    def __init__(self):
        self.save_filename = 'chat.json'
        self.username = 'undefined'
        self.password = ''
        self.channel = channel_
        self.load()

    def load(self):
        if not os.path.exists(self.save_filename):
            self.new()
        with open(self.save_filename, 'r') as f:
            js = json.loads(f.read())
            self.username = js['username']
            self.password = js['password']
            self.channel = js['channel']

    def save(self):
        with open(self.save_filename, 'w') as f:
            js = json.dumps({
                'username': self.username,
                'password': self.password,
                'channel': self.channel
            })
            f.write(js)

    def new(self):
        with open(self.save_filename, 'w') as f:
            js = json.dumps({
                'username': self.username,
                'password': self.password,
                'channel': self.channel
            })
            f.write(js)


def parse_cmds(data):
    global my_trip
    m_settings = Settings()
    if 'cmd' not in data:
        return ''
    cmd = data['cmd']
    if cmd == 'onlineAdd':
        if data['nick'] == m_settings.username:
            my_trip = data['trip']
            if my_trip == 'null':
                my_trip = ''
        return "%s 加入聊天室" % data['nick']
    if cmd == 'chat':
        if 'nick' in data and 'trip' in data:
            return "%s %s\n%s" % (data['trip'], data['nick'], data['text'])
        return "%s %s\n%s" % (m_settings.username, my_trip, data['text'])
    if cmd == 'onlineSet':
        users = ''
        for u in data['nicks']:
            users = users + u + ','
        users = users[:-1]
        return '欢迎来到十字街！请保证您已经阅读并同意了服务协议。\n如果您所在的聊天室没有在线的用户，' \
               '可以尝试加入聊天室 ?公共聊天室\n在线的用户: ' + users
    if cmd == 'info':
        return "信息：" + data['text']
    if cmd == 'warn':
        return "警告：" + data['text']
    if cmd == 'onlineRemove':
        return '%s 离开了聊天室' % data['nick']
    return '(%s)' % json.dumps(data)


class MyClient(WebSocketClient):
    def opened(self):
        global connected
        settings = Settings()
        channel = settings.channel
        if channel == '':
            channel = channel_
        # print(self.channel)
        if len(settings.password) > 0 :
            user = settings.username
            pswd = settings.password
            req = json.dumps({"cmd": "join", "channel": channel, "nick": user, "password": pswd, })
        else:
            user = settings.username
            pswd = ''
            req = json.dumps({"cmd": "join", "channel": channel, "nick": user,})
        self.send(req)
        connected = True

    def closed(self, code, reason=None):
        global connected
        print("Closed down:", code, reason)
        connected = False

    def send_text(self, text):
        data = json.dumps({'cmd': 'chat', "text": text})
        print('<-', data)
        self.send(data)

    def received_message(self, resp):
        global var_text
        print('->', resp)
        try:
            resp = json.loads(str(resp))
        except Exception as e:
            print(resp, e)
            return
        data = resp
        result = parse_cmds(data) + '\n'
        # print(result)
        var_append(var_text, result)


class ChatClientSetup:
    def __init__(self, root=None):
        self.root = root
        if self.root is None:
            self.root = Tk()
        top = self.root
        self.top = self.root
        if platform.system() == 'Windows':
            top.attributes("-toolwindow", 1)
            top.attributes("-topmost", 1)
        top.resizable(width=False, height=False)
        top.title("登录-新版十字街 By @MuRongPIG")
        # top.overrideredirect(True)
        # self.root.iconify()

        self.setup_user = StringVar()
        self.setup_password = StringVar()
        self.setup_channel = StringVar()
        self.setup_channel.set(channel_)

        self.settings = Settings()

        frame = Frame(top)

        self.setup_user.set(str(self.settings.username))
        self.setup_password.set(str(self.settings.password))
        self.setup_channel.set(str(self.settings.channel))

        Label(frame, text='用户名').grid(row=1, column=1)
        Entry(frame, textvariable=self.setup_user).grid(row=1, column=2)
        Label(frame, text='密码').grid(row=2, column=1)
        Entry(frame, textvariable=self.setup_password).grid(row=2, column=2)
        Label(frame, text='房间(默认%s)' % channel_).grid(row=3, column=1)
        Entry(frame, textvariable=self.setup_channel).grid(row=3, column=2)

        frame.pack(side=TOP)
        Button(top, text='登录', command=self.setup_confirm).pack(side=BOTTOM, fill=X, expand=1)

        top.mainloop()

    def setup_confirm(self):
        self.settings.username = self.setup_user.get()
        self.settings.password = self.setup_password.get()
        self.settings.channel = self.setup_channel.get()
        self.settings.save()
        self.top.destroy()

    def loop(self):
        self.root.mainloop()


class ChatClient:
    def __init__(self, root=None):
        self.api = 'wss://ws.crosst.chat:35197/'
        self.settings = Settings()

        self.username = self.settings.username
        self.channel = self.settings.channel
        self.password = self.settings.password

        self.root = root
        if self.root is None:
            self.root = Tk()
        self.title = '聊天室 - %s' % self.username
        self.root.title(self.title)

        self.var_send = StringVar()
        self.entry = Entry(self.root, textvariable=self.var_send)
        self.entry.grid(columnspan=5, row=1, sticky=W + E)
        self.entry.bind('<Return>', self.send_message)
        global var_text
        var_text = StringVar()

        self.scroll = Scrollbar()
        global my_text
        my_text = Text(self.root)
        self.scroll.config(command=my_text.yview)
        my_text.config(yscrollcommand=self.scroll.set)
        my_text.grid(column=1, row=0)
        self.scroll.grid(column=0, row=0, sticky=N + S)

        self.button = Button(self.root, text="SEND", command=self.send_message)
        self.button.grid(column=5, row=1)

        self.ws = None
        self.init_ws()

    def init_ws(self):
        self.ws = MyClient(self.api)
        self.ws.connect()

    def send_message(self, event=None):
        message = self.var_send.get()
        self.ws.send_text(message)
        self.var_send.set("")

    def loop(self):
        self.root.mainloop()


if __name__ == '__main__':
    _settings = Settings()
    _setup = ChatClientSetup()
    _setup.loop()
    client = ChatClient()
    client.loop()
