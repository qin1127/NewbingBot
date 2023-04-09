#    New Bing QQBot


                                       基于go-cqhttp的newbingQQ聊天机器人
                                       
####使用教程
*需要魔法上网
##### 一. python源码
*你需要Python环境来运行，并且需要安装websocket-client、requests、flask库


1.获取newbing的ticket
  \* 你需要能访问newbing
  
           (1)   将newbing.js的内容添加到收藏夹，
           (2)   在bing聊天页点击书签，将弹出ticket
2.填写qq号和ticket

            在newbingbot.py第一行和第二行填上你的QQ号和ticket
3.登录go-cqhttp

            直接运行newbingbot.py，会弹出二维码，扫码登录.
*此步骤出现问题可以看go-cqhttp的文档

*请不要更改config.yml

##### 二. 可执行文件

             将QQ和ticket写到list.txt里面即可，其他相同
             直接运行newbingbot.exe

