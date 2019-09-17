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

from guiengine import GuiEngine
from multiprocessing import Queue 
from multiprocessing import Event
import multiprocessing
import time

layout = {'screen':{'size':(200,200),'color':(0,0,0),'type':'fullscreen',
                        'Fps':60,'caption':'this is an example'},
             'cue':{'class':'sinBlock','parm':{'size':(100,100),'position':(100,100),
                    'frequency':13,'visible':True}}}

def example1():
    Q_c2g = Queue()
    E_g2p = Event()
    Q_g2s = Queue()
    
    gui = GuiEngine(layout,Q_c2g,E_g2p,Q_g2s)
    gui.StartRun()

def proc(layout,Q_c2g,E_g2p,Q_g2s):
    gui = GuiEngine(layout,Q_c2g,E_g2p,Q_g2s)
    gui.StartRun()

def example2():
    Q_c2g = Queue()
    E_g2p = Event()
    Q_g2s = Queue()
    process = multiprocessing.Process(target=proc,args=(layout,Q_c2g,E_g2p,Q_g2s))
    process.start()

    # while True:
        # if E_g2p.is_set():break
        # Q_c2g.put([{'cue':{'start':True}},{''}])
        # time.sleep(5)
        # Q_c2g.put([{'cue':{'start':False}},{''}])
        # time.sleep(1)
        

    print 'main process exit'


if __name__ == '__main__':
    example2()
