QQ = "3361823093"                                   # 你的QQ号,只用来判断群聊里是不是@了你
ticket = "1rbl1E09wF3BwAR-3ZNT7pTyHZe_Ji1e02xk0s4GznxUBTFTJAQJQP4-iF1VrBB7yF1nq9HnjLgcobqU7lsA3J0NZIXb4HHa7_-uevcSdwIk2TFhDXhMw2iYLs5UXs39R01Sq_uUBh39M5T0nA4wj5cf5Qo1Rn1Gt0ToUFiSVjHQbaH9htWbqd1xK6DnGHtPN3-Y_4SfQnN4rQGTYmRbRjw"
                                                    # 填你的bingbot的一个cookies，获取方法见github
                                                    #这个是我的ticket，过期了请自行获取

#一个小白写的bingbot，可用于QQ群聊和私聊
#哈哈，代码写的很烂，请见谅
#编写使用环境：python3.10.9
#使用的库：websocket-client、requests、flask

'''

使用前要填上你的qq和ticket
ticket获取方法见github
没有做登录逻辑 PS：太菜了 ，所以如果你的ticket过期了，你需要重新获取ticket  注意！ticket大概半个月过期一次


'''


from subprocess import run
import threading
from flask import Flask, request
import logging
import re
import websocket
import requests
import json
import time

# 储存所有私聊用户（对象.user）的字典
users = {}
# 储存所有群聊用户（对象.user）的字典
userGroupList = {}#二维字典，第一维是群号，第二维是QQ号
# 用于指令的函数，可以自己添加
def ctrl():
    command = input("")
    if command == "/exit":
        exit(0)
    elif command == "/list":
        print(users)

threadCommand = threading.Thread(target=ctrl)
threadCommand.start()


class user:
    def __init__(self, uid):
        # 初始化对话前置内容
        self.pre_temp = ',"previousMessages":[{"text":"重新开始总是很棒。问我任何问题!","author":"bot","adaptiveCards":[],"suggestedResponses":[{"text":"一年有多少小时?","contentOrigin":"DeepLeo","messageType":"Suggestion","messageId":"e8a3f640-6c88-044c-e8b6-ada9cad50bec","offense":"Unknown"},{"text":"如何制作蛋糕?","contentOrigin":"DeepLeo","messageType":"Suggestion","messageId":"a26c9cde-3203-50aa-739a-f628419070db","offense":"Unknown"},{"text":"给我看鼓舞人心的名言","contentOrigin":"DeepLeo","messageType":"Suggestion","messageId":"fb4f23da-9796-6ab9-7f65-b4afc99a3476","offense":"Unknown"}],"messageId":"de58df9f-c171-60fc-5542-bcf168fa34ba","messageType":"Chat"}]'
        self.massage1 = "{\"type\":6}"
        self.newRes = None  # 保存的会话内容
        self.uid = uid  # QQ号，用于区分用户
        self.invocationId_temp = 3  # 对话轮数，第一轮对话对应 invocationId_temp = 3
        self.start_temp = "true"  # 是否是一轮对话的开始
        self.beatStop = 0  # 心跳线程的开关

    # 将message发送到对应QQ

    def printqq(self, message):
        pra = {}
        pra['message'] = message
        pra["user_id"] = str(self.uid)
        a = requests.get('http://127.0.0.1:5700/send_private_msg', params=pra)
        print(a.json())

    """

    # 打开后会把message和uid打印到控制台的函数，用来测试
    def printqq(self, message):
        pra = {}
        pra['message'] = message
        pra["user_id"] = str(self.uid)
        # a = requests.get('http://127.0.0.1:5700/send_private_msg', params=pra)
        print(message, "将发给：", self.uid)
    """

    # bing对话请求
    def bing(self, question):
        #lenth是收到回复的次数，第三次有可能是搜索提示
        global lenth
        lenth = 0

        # 心跳包
        massage1 = "{\"type\":6}"

        # 心跳函数
        def beat(ws):
            while True:
                time.sleep(10)
                if self.beatStop == 1:
                    return 0
                try:
                    ws.send(self.massage1)
                except:
                    return 0

        def on_open(ws):
            # 开起心跳线程
            self.beatStop = 0
            self.threadBeat.start()

            massage = "{\"protocol\":\"json\",\"version\":1}"  # websocket握手内容
            # 主提问信息
            massage3 = '{"arguments":[{"source":"cib","optionsSets":["nlu_direct_response_filter","deepleo","disable_emoji_spoken_text","responsible_ai_policy_235","enablemm","h3imaginative","rai253","cpcttl7d","localtime","dv3sugg"],"allowedMessageTypes":["Chat","InternalSearchQuery","InternalSearchResult","Disengaged","InternalLoaderMessage","RenderCardRequest","AdsQuery","SemanticSerp","GenerateContentQuery","SearchQuery"],"sliceIds":["checkauth","precibcf","sydperfinput","228h3adss0","h3adss0","301rai253","301rai253","cache0307","ssoverlap50","ssplon","sssreduce","sswebtop2","308disbings0","224local","224local"],"traceId":"6409f21480fd4fcebc15aa822f486710","isStartOfSession":start_temp,"message":{"locale":"zh-CN","market":"zh-CN","region":"US","location":"lat:47.639557;long:-122.128159;re=1000m;","locationHints":[{"Center":{"Latitude":45.74020676284351,"Longitude":126.67019362635415},"RegionType":2,"SourceType":11},{"country":"United States","state":"Ohio","city":"Glenmont","zipcode":"44628","timezoneoffset":-5,"dma":510,"countryConfidence":8,"cityConfidence":5,"Center":{"Latitude":40.5321,"Longitude":-82.1282},"RegionType":2,"SourceType":1}],"timestamp":"2023-03-09T22:50:00+08:00","author":"user","inputMethod":"Keyboard","text":"question_temp","messageType":"Chat"},"conversationSignature":"conversationSignature_temp","participant":{"id":"id_temp"},"conversationId":"conversationId_temp"pre_temp}],"invocationId":"invocationId_temp","target":"chat","type":4}'
            massage3 = massage3.replace("conversationId_temp", self.newRes['conversationId'])
            massage3 = massage3.replace("conversationSignature_temp", self.newRes['conversationSignature'])
            massage3 = massage3.replace("id_temp", self.newRes['clientId'])
            massage3 = massage3.replace("pre_temp", self.pre_temp)
            self.pre_temp = ""  # 清除，下一次不再发送初始化的部分
            massage3 = massage3.replace("question_temp", question)
            massage3 = massage3.replace("invocationId_temp", str(self.invocationId_temp))
            self.invocationId_temp += 1  # 对话轮数自加一
            massage3 = massage3.replace("start_temp", self.start_temp)
            self.start_temp = "false"  # 不再是开始的内容

            rs = ""  # 向bing发送的消息必须加上才能被识别
            massage3 = massage3 + rs
            ws.send(massage)  # 发送握手信息
            time.sleep(0.5)
            ws.send(massage1)
            ws.send(massage3)  # 发送主提问信息

        def on_message(ws, message):
            global lenth
            # 心跳检测2
            lenth = lenth + 1
            if lenth >= 15:
                ws.send(massage1)  # 发送心跳2
                lenth = 4

            # message = re.sub(r"\\n", "", message)
            # message = re.sub(r"\\uD(...)", "", message)
            b = re.findall('(.+?)', message)[0]
            #print(b)



            # 获取bing搜索信息
            if lenth == 3:
                try:
                    b = b.replace("\\", "")
                    json1 = json.loads(b)
                except:
                    return
                try:
                    search = json1["arguments"][0]["messages"][0]["spokenText"]
                    self.printqq(search)
                except:
                    pass
            try:
                type = message[8]

            except:
                type = "0"
            if type == "6":
                # beat
                ws.send(self.massage1)
            #type = 2 是最终回复，具体回复内容的结构要自己去抓包看看，或者可以把message打印出来看看
            if type == "2":
                try:
                    json1 = json.loads(b)
                except:
                    self.printqq("System: error,code = 1,json fail")
                    return
                #ip限制检查，请求过于频繁会被限制，不过每个IP可以请求很多，一般不会被限制，
                #每次限制大概10个小时，是限制IP，换账号也不行
                try:
                    messageBan = json1["item"]["result"]["message"]

                    if messageBan == "Request is throttled.":
                        self.printqq("System: Ip limited,please try hours later.")
                    elif messageBan == "The last user message is being processed. Please wait for a response before submitting further messages.":
                        self.printqq("System: The last user message is being processed. Please wait for a response before submitting further messages.")
                except:
                    pass
                try:
                    ansList = json1["item"]["messages"]

                except:
                    print("error,code = 0", json1, end="")
                    return 0
                ans = ""
                for i in ansList:
                    #print(i)
                    try:
                        ansTure = i["sourceAttributions"]
                    except:
                        continue

                    ans = i["text"]
                    ans = re.sub("\[\^.*\^]", "", ans)
                #print(ans)

                self.printqq(ans)

                ws.close()

        def on_error(ws, error):
            print("error", end="")
            self.printqq("ERROR: " + str(error))

        def on_close(ws):
            self.beatStop = 1  # 关闭心跳线程

            print("### closed ###")

        # new新建对话
        """
        这里是新建对话的部分，这个请求的返回值中有conversationId，conversationSignature，clientId，这三个值是后面请求的必要参数，集合在newRes中，存储在self.newRes中
        这个请求需要魔法  :-(
        """
        if self.newRes == None:
            url = "https://www.bing.com/turing/conversation/create"

            cookies = {
                "_U": ticket
            }
            try:
                newRes = requests.get(url, cookies=cookies, timeout=30).json()  # 获取新建对话的信息，保存在newRes中
            except:
                self.printqq("Connect fail")  # 超时提示
                return
            self.printqq("System: A New Conversation.")  # 开始时有新建对话提示
            print("A New Conversation!")
            self.newRes = newRes  # 保存新建对话的信息

        # 创建 websocket 连接
        ws = websocket.WebSocketApp("wss://sydney.bing.com/sydney/ChatHub",
                                    on_open=on_open, on_message=on_message,
                                     on_close=on_close, on_error=on_error)
        # 创建心跳线程
        self.threadBeat = threading.Thread(target=beat, args=(ws,))
        # 运行 websocket 连接

        print("bing start!")
        ws.run_forever()

class userGroup(user):
    def __init__(self, uid,gid):
        super().__init__(uid)
        self.gid = gid
    #重写printqq，使其可以在群聊加上at
    def printqq(self, message):
        message = r"[CQ:at,qq=" + str(self.uid) + r"] " + str(message)
        pra = {}
        pra['message'] = message
        pra["group_id"] = str(self.gid)
        a = requests.get('http://127.0.0.1:5700/send_group_msg', params=pra)
        print(a.json())

#对接收的消息进行处理，分为私聊和群聊
def userJudge(uid, message,gid):
    if gid == 0:#gid = 0 为私聊
        useTemp = users.get(uid, "no")
        if useTemp == "no":
            users[uid] = user(uid)
            print("A New User!", uid)
        #指令
        if message[0] == "/":
            if message == "/clear":
                try:
                    users[uid].ini()
                    users[uid].printqq("clear")
                except:
                    users[uid].printqq("目前没有记录")
            elif message[0:6] == "/help":
                pass
        else:
            users[uid].bing(message)
    else:  #其他，gid不为0，为群聊，这里的gid是群号
        try:
            #这个是CQ码，用来判断是否被at
            at = re.findall("\[CQ:at,qq=(.+?)]", message)[0]
        except:
            at = "no"

        if str(at) == QQ:
            message = re.sub("\[CQ:at,qq=(.+?)] ", "", message)

            useTempGroup = userGroupList.get(gid, {}).get(uid, "no")
            if useTempGroup == "no":
                userGroupList[gid] = dict()
                userGroupList[gid][uid] = userGroup(uid,gid)
                print("A New Group User!", uid)
            #指令
            if message[0] == "/":
                if message == "/clear":
                    try:
                        userGroupList[gid][uid].ini()
                        userGroupList[gid][uid].printqq("clear")
                    except:
                        userGroupList[gid][uid].printqq("目前没有记录")
                elif message[0:6] == "/help":
                    pass
            else:
                userGroupList[gid][uid].bing(message)


def listen():
    app = Flask(__name__)
    log = logging.getLogger('werkzeug')
    log.disabled = True
    '''监听端口，获取QQ信息'''

    @app.route('/', methods=["post"])
    def post_data():
        global bingOrGpt
        '下面的request.get_json().get......是用来获取关键字的值用的，关键字参考上面代码段的数据格式'
        if request.get_json().get('message_type') == 'private':  # 如果是私聊信息
            uid = request.get_json().get('sender').get('user_id')  # 获取信息发送者的 QQ号码
            message = request.get_json().get('raw_message')  # 获取原始信息
            print(message + "  from:" + str(uid))
            userJudge(uid, message, 0)

        if request.get_json().get('message_type') == 'group':  # 如果是群聊信息
            gid = request.get_json().get('group_id')  # 获取群号
            uid = request.get_json().get('sender').get('user_id')  # 获取信息发送者的 QQ号码
            message = request.get_json().get('raw_message')  # 获取原始信息
            print(message + "   from_group:" + str(gid) + "  QQ:" + str(uid))
            userJudge(uid, message, gid)

        return 'OK'

    app.run(debug=False, host='127.0.0.1', port=5701)  # 此处的 host和 port对应yml文件的设置


"""测试时使用，可以模拟qq传入
if __name__ == "__main__":
    while True:
        uid = input("uid: ")
        while True:
            question = input("you: ")
            if question == "quit":
                break
            useTemp = users.get(uid, "no")

            if useTemp == "no":
                users[uid] = user(uid)
                users[uid].bing(question)
            else:
                useTemp.bing(question)
"""

if __name__ == '__main__':
    thr = threading.Thread(target=listen)
    thr.start()
    run("go-cqhttp.exe -faststart")











#真的有人会看到吗，花了这么长时间，好像没有任何意义  :-X

#如果你也对这个感兴趣或安装出现问题，或者有什么好的想法，可以加我qq  919836565(备注“bingbot”)，我会尽力帮助你 :-)


