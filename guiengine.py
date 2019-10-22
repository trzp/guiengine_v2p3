#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''Copyright (C) 2018, Nudt, JingshengTang, All Rights Reserved
#Author: Jingsheng Tang
#Email: mrtang@nudt.edu.cn

# This gui program employs the vertical synchronization mode on the basis of using the directx
# graphic driver. It makes the program update the drawing synchornously with the monitor, thus
# to accurately contorl the stimulus graphics. It is similar to the sychtoolbox of Matlab. On
# this basis, the stimulus marker event is also set synchronously with the actual drawing.

# Since the vertical synchronization mode is used, the graphic user interface is fullscreen.

update: 2019/5/23
'''


import pygame
from pygame.locals import *

# 批量导入支持的模块，允许扩展
from modules import MY_MODULES

MODULES = {}
for script in MY_MODULES:
    # eg. from block import Block
    # eg. the Block is callable by MODULES['Block']
    exec('from %s import %s'%(script,MY_MODULES[script]),MODULES)

from multiprocessing import Queue,Event
import multiprocessing
import threading
import time,math
import os,platform
import numpy as np
from rz_global_clock import global_clock
from marker import Marker


SCREEN_SYNC = False
# 垂直同步设置，仅支持windows
OS = platform.system().lower()
if OS == 'windows':
    try:
        os.putenv('SDL_VIDEODRIVER','directx')
        os.environ['SDL_VIDEODRIVER'] = 'directx'
        SCREEN_SYNC = True
    except: raise KeyError('add an environment variable "SDL_VIDEODRIVER" with value of "directx" into the computer')

    import win32api,win32con
    SCRW = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    SCRH = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

elif OS == 'linux':
    pass
else:
    raise IOError('unrecognized system platform')

# 由于在windows下基于multiprocessing.process实现多进程类并不安全，因此将显式启动多进程函数
# 主进程与子进程采用queue和event通信，但是提供接口类，用来封装直接对queue和event的操作

layout = {'screen':{'size':(200,200),'color':(0,0,0),'type':'normal',
                        'Fps':60,'caption':'this is an example'},
             'cue':{'class':'sinBlock','parm':{'size':(100,100),'position':(100,100),
                    'frequency':13,'visible':True,'start':False}}}

def guiengine_proc(args):
    layout = args['layout']
    Q_c2g = args['Q_c2g']
    E_g2c = args['E_g2c']
    saddress = args['server_address']
    gui = GuiEngine(layout, Q_c2g, E_g2c, saddress)
    gui.StartRun()

class GuiIF():    #用于向guiengine发射信号
    def __init__(self,server_address = None,layout = layout):
        # Q_c2g:传递内容
        #     1. 单字符串：'_q_u_i_t_' -> 结束标志
        #     2. 列表：[stimulus setting, marker] -> 刺激设置，marker标志

        self.Q_c2g = Queue()
        self.E_g2c = Event()
        self.layout = layout
        self.args = {'layout':self.layout,'Q_c2g':self.Q_c2g,'E_g2c':self.E_g2c,'server_address':server_address}

    def quit(self):
        self.Q_c2g.put('_q_u_i_t_')

    def wait(self):
        self.E_g2c.wait()

    def update(self,stimulus,marker):
        self.Q_c2g.put([stimulus,marker])

class GuiEngine():
    stimuli = {}
    __release_ID_list = []

    def __init__(self,stims,Q_c2g,E_g2c,server_address):
        """
        stims:  dict to define a stimulus.
                eg. stims = {'cue':{'class':'Block','parm':{'size':(100,40),'position':(0,0)}}}
        Q_c2g: multiprocessing.Queue, used for accepting stimulus control command from core process
        kwargs: server_address = ?, the target server's address to accept marker
        
        property for describe screen
        size: (width,height)
        type: fullscreen/normal
        frameless: True/False
        color: (R,G,B)
        caption: string
        Fps: int, strongly suggest you set Fps as the same with system's Fps
        """

        self.Q_c2g = Q_c2g
        self.E_g2c = E_g2c
        self.marker_on = False
        self.marker_event = {}
        self.stp = False
        self.lock = threading.Lock()

        pygame.init()
        #初始化screen
        # 当且仅当window环境变量设置成功且fullscreen时，SCREEN_SYNC=True
        if stims['screen']['type'].lower() == 'fullscreen':
            self.screen = pygame.display.set_mode((0,0),FULLSCREEN | DOUBLEBUF | HWSURFACE,32)
        else:
            # 将窗口置中
            if OS == 'windows':
                w,h = stims['screen']['size']
                x = int((SCRW - w)/2.)
                y = int((SCRH - 50 - h)/2.) - 50  # 扣除任务栏高度
                os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i'%(x,y)

            self.screen = pygame.display.set_mode(stims['screen']['size'], NOFRAME | DOUBLEBUF, 32)
            SCREEN_SYNC = False

        self.screen_color = stims['screen']['color']
        self.screen.fill(self.screen_color)
        pygame.display.set_caption(stims['screen']['caption'])
        self.Fps = stims['screen']['Fps']
        del stims['screen']

        self.ask_4_update_gui = False       #线程接收到刷新请求后，通知主进程刷新
        self.update_in_this_frame = False   #主进程在一帧真实的刷新帧中确定能够进行刷新
        self.__update_per_frame_list = []   #接受帧刷新对象

        if server_address is None:
            class Marker():
                def __init__(self,sa):
                    pass
                def send_marker(self,marker):
                    raise Exception('marker_sender was not initilized because server_address parameter was not given')

        self.marker_sender = Marker(server_address)

        #注册刺激，生成实例
        for ID in stims:
            element = stims[ID]
            clas = element['class']
            if clas in MODULES:
                self.stimuli[ID] = MODULES[clas](self.screen,**element['parm'])

        backthread = threading.Thread(target = self.backthreadfun, args = (), daemon = True)
        backthread.start()

    def backthreadfun(self):  #接收刷新请求字典
        # arg = self.Q_c2g.get()
        # arg可能的形式：
        #     1. 单字符串：'_q_u_i_t_' -> 结束标志
        #     2. 列表：[stimulus setting, marker] -> 刺激设置，marker标志
        #     3. marker:  eg. {'mkr1':{'value':[0]}}

        while True:
            arg = self.Q_c2g.get()
            if arg == '_q_u_i_t_':
                self.stp = True     #用于终止主程序
                break

            stimulus_arg,self.marker_event = arg  #marker is a dict
            
            self.lock.acquire()
            [self.stimuli[id].reset(**stimulus_arg[id]) for id in stimulus_arg] #更新刺激实例的参数
            self.ask_4_update_gui = True  #请求刷新
            self.lock.release()
        print('[guiengine] sub thread ended')

    def StartRun(self):
        print('[guiengine] process started')
        self.E_g2c.set()
        clock = pygame.time.Clock()
        # END = 0
        while True:
            self.screen.fill(self.screen_color)

            if self.ask_4_update_gui:   #子线程请求刷新
                self.update_in_this_frame = True #将在这一帧刷新
                self.ask_4_update_gui = False

            #.items()方法将stimuli字典转换为列表，元素为元祖，k[0]对应ID, k[1]为具体的刺激对象实例
            # 意思是按照layer属性排序
            stis = sorted(self.stimuli.items(),key=lambda k:k[1].layer)
            [s[1].show() for s in stis] #按照图层书序顺序绘图，layer越大，越顶层
            pygame.display.flip() #该帧刷新完毕

            if not SCREEN_SYNC:  clock.tick(self.Fps)

            # 有刷新请求，且在该帧完成了刷新
            if self.update_in_this_frame:
                _clk = global_clock()
                if len(self.marker_event)>0:        #确实接受到了marker
                    for ky in self.marker_event:    # 将时间戳记录下来
                        self.marker_event[ky]['timestamp'] = _clk
                    self.marker_sender.send_marker(self.marker_event)
                self.update_in_this_frame = False

            pygame.event.get()
            if self.stp:    break  #只能通过主控结束

        pygame.quit()
        [self.stimuli[id].release() for id in self.stimuli] #更新刺激实例的参数

        print('[guiengine] process exit')

if __name__ == '__main__':
    gui = GuiIF() # 建立与GUI交互的接口
    _ = multiprocessing.Process(target = guiengine_proc,args = (gui.args,)) # 新建进程启动GUI
    _.start()
    gui.wait()    # 等待GUI启动
    time.sleep(1)
    gui.update({'cue':{'start':True}},{})  # 更新GUI且发送marker
    time.sleep(1)
    gui.update({'cue': {'start': False}},{}) # 更新GUI且发送marker
    time.sleep(1)
    gui.quit()
