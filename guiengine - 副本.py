#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''Copyright (C) 2018, Nudt, JingshengTang, All Rights Reserved
#Author: Jingsheng Tang
#Email: mrtang@nudt.edu.cn

# This gui program employs the vertical synchronization mode on the basis of using the directx
# graphic driver. It makes the program update the drawing synchornously with the monitor, thus
# to accurately contorl the stimulus graphics. It is similar to the sychtoolbox of Matlab. On
# this basis, the stimulus trigger event is also set synchronously with the actual drawing.

# Since the vertical synchronization mode is used, the graphic user interface is fullscreen.
'''

import pygame
from pygame.locals import *
from block import Block
from sinblock import sinBlock
from mblock import mBlock
from imagebox import Imagebox
from multiprocessing import Queue,Event
import multiprocessing
import threading
import time,math
import os,platform
import numpy as np

from get_global_clock_rz import get_global_clock as sysclock

if platform.system() == 'Windows':
    try:
        os.putenv('SDL_VIDEODRIVER','directx')
        os.environ['SDL_VIDEODRIVER'] = 'directx'
    except: raise KeyError,'add an environment variable "SDL_VIDEODRIVER" with value of "directx" into the computer'
elif platform.system() == 'Linux':
    pass
else:
    raise IOError,'unrecognized system platform'
    
OS = platform.system().lower()

class GuiEngine(threading.Thread):
    stimuli = {}
    __release_ID_list = []

    def __init__(self,stims,Q_c2g,E_g2p,Q_g2s):
        """
        stims:  dict to define a stimulus.
                eg. stims = {'cue':{'class':'Block','parm':{'size':(100,40),'position':(0,0)}}}
        Q_c2g: multiprocessing.Queue, used for accepting stimulus control command from core process
        E_g2p: multiprocessing.Event, used for sending user termination event to the phase process
        Q_g2s: multiprocessing.Queue, used for sending accurate trigger to sigpro process
        
        property for describe screen
        size: (width,height)
        type: fullscreen/normal
        frameless: True/False
        color: (R,G,B)
        caption: string
        Fps: int, strongly suggest you set Fps as the same with system's Fps
        """
        super(GuiEngine,self).__init__()
        pygame.init()
        self.Q_c2g = Q_c2g
        self.E_g2p = E_g2p
        self.Q_g2s = Q_g2s
        self.trigger_on = False
        self.trigger_event = {}
        self.stp = False
        self.lock = threading.Lock()

        #初始化screen
        if stims['screen']['type'].lower() == 'fullscreen':
            self.screen = pygame.display.set_mode((0,0),FULLSCREEN | DOUBLEBUF | HWSURFACE,32)
            self.vsync = True
            print self.vsync,'vsync'
        else:
            if stims['screen'].has_key('frameless'):
                self.screen = pygame.display.set_mode(stims['screen']['size'],NOFRAME | DOUBLEBUF,32)
            else:
                self.screen = pygame.display.set_mode(stims['screen']['size'],DOUBLEBUF,32)
            self.vsync = False

        if OS != 'windows': self.vsync = False

        self.screen_color = stims['screen']['color']
        self.screen.fill(self.screen_color)
        pygame.display.set_caption(stims['screen']['caption'])
        self.Fps = stims['screen']['Fps']
        del stims['screen']

        self.ask_4_update_gui = False       #线程接收到刷新请求后，通知主进程刷新
        self.update_in_this_frame = False   #主进程在一帧真实的刷新帧中确定能够进行刷新
        self.__update_per_frame_list = []   #接受帧刷新对象

        #注册刺激，生成实例
        for ID in stims:
            element = stims[ID]
            if element['class'] == 'Block': self.stimuli[ID] = Block(self.screen,**element['parm'])
            elif element['class'] == 'Imagebox':self.stimuli[ID] = Imagebox(self.screen,**element['parm'])
            elif element['class'] == 'sinBlock':
                self.stimuli[ID] = sinBlock(self.screen,**element['parm'])
                self.__update_per_frame_list.append(self.stimuli[ID])   #帧刷新对象的列表
            elif element['class'] == 'mBlock':
                self.stimuli[ID] = mBlock(self.screen,**element['parm'])
                self.__update_per_frame_list.append(self.stimuli[ID])
            else:   pass

        self.setDaemon(True)                #子线程隧主线程退出
        self.start()

    def run(self):  #接收刷新请求字典
        # arg = self.Q_c2g.get()
        # arg可能的形式：
        #     1. 单字符串：'_q_u_i_t_' -> 结束标志
        #     2. 列表：[stimulus setting, trigger] -> 刺激设置，trigger标志

        while True:
            arg = self.Q_c2g.get()
            if arg == '_q_u_i_t_':
                self.stp = True     #用于终止主程序
                time.sleep(0.1)
                break

            stimulus_arg,self.trigger_event = arg  #trigger is a dict
            
            self.lock.acquire()
            [self.stimuli[id].reset(**stimulus_arg[id]) for id in stimulus_arg.keys()] #更新刺激实例的参数
            self.ask_4_update_gui = True  #请求刷新
            self.lock.release()
        print '>>> guiengine sub thread ended'
    

    def StartRun(self):
        print '>>> gui engine started'
        clock = pygame.time.Clock()
        END = 0
        while True:
            self.screen.fill(self.screen_color)
            #需要帧刷新的对象进行相应更新
            [sti.update_per_frame() for sti in self.__update_per_frame_list]

            if self.ask_4_update_gui:   #子线程请求刷新
                self.update_in_this_frame = True #将在这一帧刷新
                self.ask_4_update_gui = False

            #.items()方法将stimuli字典转换为列表，元素为元祖，k[0]对应ID, k[1]为具体的刺激对象实例
            # 意思是按照layer属性排序
            stis = sorted(self.stimuli.items(),key=lambda k:k[1].layer)
            [s[1].show() for s in stis] #按照图层书序顺序绘图，layer越大，越顶层
            pygame.display.flip() #该帧刷新完毕

            if not self.vsync:  clock.tick(self.Fps)

            #这一帧有刷新请求，并刚刚完成了刷新 ，这里通过queue发射带时间戳的trigger
            if self.update_in_this_frame:   #更新trigger，记录下此时的clock,因此，trigger的记录是伴随着真实的显示器刷新的
                self.Q_g2s.put([sysclock(),self.trigger_event])
                self.update_in_this_frame = False

            evs = pygame.event.get()
            for e in evs:
                if e.type == QUIT:
                    END=1
                elif e.type == KEYDOWN:
                    if e.key == K_ESCAPE: END=1
            if END:break
            if self.stp:    break

        pygame.quit()
        if END: self.E_g2p.set()  #通知phase进程，用户结束
        for ID in self.__release_ID_list:   del self.stimuli[ID]
        self.Q_c2g.put('_q_u_i_t_')

        print '>>> gui engine exit'