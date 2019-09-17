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

update: 2019/5/23
'''


import pygame
from pygame.locals import *
from block import Block
from sinblock import sinBlock
from mblock import mBlock
from imagebox import Imagebox
import threading
import time,math
import os,platform
import numpy as np

from get_global_clock_rz import get_global_clock as sysclock   # a cross platform clock

_VSYNC_ = False

# 垂直同步设置，仅支持windows
# 垂直同步允许获取显示器的刷新信号，因此可以做到精确刷新帧画面
# windows系统且全屏，垂直同步有效

if platform.system() == 'Windows':
    try:
        os.putenv('SDL_VIDEODRIVER','directx')
        os.environ['SDL_VIDEODRIVER'] = 'directx'
        _VSYNC_ = True
    except: raise KeyError,'add an environment variable "SDL_VIDEODRIVER" with value of "directx" into the computer'
elif platform.system() == 'Linux':
    _VSYNC_ = False
else:
    raise IOError,'unrecognized system platform'


class brGui(threading.Thread):

    def __init__(self,layout,gmess,**kwargs):
        """
        layout:  dict to define stimulus layout. must contain layout for screen
            eg, layout = {'screen':{'size':(200,200),'color':(0,0,0),'type':'fullscreen',
                            'Fps':60,'caption':'this is an example'},
                         'cue':{'class':'sinBlock','parm':{'size':(100,100),'position':(100,100),
                                'frequency':13,'visible':True,'start':True}}}

        gmess: type of stimMessage which is an object to transmit json string for controlling
            the GUI's updating

        kwargs: eg. trigger_mess = xx, if an object with type of stimMessage with the name of trigger_mess,
            this object will send out trigger event at the precision time when the required stimulus is rendered.
        """
        
        super(brGui,self).__init__()
        pygame.init()
        self.gmess = gmess

        self.stimuli = {}
        self.__release_ID_list = []

        if kwargs.has_key('trigger_mess'):
            self.trigger_mess = kwargs['trigger_mess']
            self._trigger_enable_ = True
        else:
            self._trigger_enable_ = False

        self.stp = False
        self.lock = threading.Lock()

        #初始化screen
        if layout['screen']['type'].lower() == 'fullscreen':
            self.screen = pygame.display.set_mode((0,0),FULLSCREEN | DOUBLEBUF | HWSURFACE,32)
        else:
            if layout['screen'].has_key('frameless'):
                self.screen = pygame.display.set_mode(layout['screen']['size'],NOFRAME | DOUBLEBUF,32)
            else:
                self.screen = pygame.display.set_mode(layout['screen']['size'],DOUBLEBUF,32)
            _VSYNC_ = False  #非全屏情况下无法开启垂直同步

        self.screen_color = layout['screen']['color']
        self.screen.fill(self.screen_color)
        pygame.display.set_caption(layout['screen']['caption'])
        self.Fps = layout['screen']['Fps']
        del layout['screen']

        self.ask_update_gui = False       #线程接收到刷新请求后，通知主进程刷新
        self.update_in_this_frame = False   #主进程在一帧真实的刷新帧中确定能够进行刷新
        self.__update_per_frame_list = []   #接受帧刷新对象

        #注册刺激，生成实例
        for ID in layout:
            element = layout[ID]
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

    def write_log(self,m):
        print '[brGUI][%.4f]%s'%(sysclock(),m)

    def run(self):  #接收刷新请求字典
        while True:
            if self._trigger_enable_:
                stimulus_arg,self.trigger_event = self.gmess.get()
            else:
                stimulus_arg = self.gmess.get()

            if stimulus_arg.has_key('_q_u_i_t_'):
                self.stp = True
                time.sleep(0.1)
                break

            self.lock.acquire()
            [self.stimuli[id].reset(**stimulus_arg[id]) for id in stimulus_arg.keys()] #更新刺激实例的参数
            self.ask_update_gui = True  #请求刷新
            self.lock.release()

    def start_run(self):
        self.write_log('process started')
        clock = pygame.time.Clock()
        Go = True
        while Go:
            self.screen.fill(self.screen_color)
            #需要帧刷新的对象进行相应更新
            [sti.update_per_frame() for sti in self.__update_per_frame_list]

            if self.ask_update_gui:   #子线程请求刷新
                self.update_in_this_frame = True #将在这一帧刷新
                self.ask_update_gui = False

            #.items()方法将stimuli字典转换为列表，元素为元祖，k[0]对应ID, k[1]为具体的刺激对象实例
            # 意思是按照layer属性排序
            stis = sorted(self.stimuli.items(),key=lambda k:k[1].layer)
            [s[1].show() for s in stis] #按照规定的layer顺序绘图，layer越大，越顶层
            pygame.display.flip() #该帧刷新完毕

            if not _VSYNC_: clock.tick(self.Fps)

            if self._trigger_enable_:
                #这一帧有刷新请求，并刚刚完成了刷新 ，发射带时间戳的trigger event
                if self.update_in_this_frame:   #更新trigger，记录下此时的clock,因此，trigger的记录是伴随着真实的显示器刷新的
                    self.trigger_event['timestamp'] = sysclock()
                    self.trigger_mess.put(self.trigger_event)
                    self.update_in_this_frame = False

            evs = pygame.event.get()
            for e in evs:
                if e.type == QUIT:
                    Go = False
                elif e.type == KEYDOWN:
                    if e.key == K_ESCAPE:
                        Go = False

            if self.stp: Go = False

        pygame.quit()
        for ID in self.__release_ID_list:   del self.stimuli[ID]
        self.write_log('process ended')


if __name__ == '__main__':
    import multiprocessing
    layout = {'screen': {'size': (200, 200), 'color': (0, 0, 0), 'type': 'normal',
                         'Fps': 60, 'caption': 'this is an example'},
              'cue': {'class': 'Block', 'parm': {'size': (100, 100), 'forecolor':(255,255,255),'position': (100, 100),'visible': True,'text':'demo','textsize':40}}}

    gui = brGui(layout,multiprocessing.Queue())
    gui.start_run()
