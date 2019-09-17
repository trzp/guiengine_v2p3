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

from guiengine import *

def main():
    layout = {'screen': {'size': (200, 200), 'color': (0, 0, 0), 'type': 'normal',
                         'Fps': 60, 'caption': 'this is an example'},
              'cue': {'class': 'sinBlock', 'parm': {'size': (100, 100), 'position': (100, 100),
                                                    'frequency': 8.3, 'visible': True,'start':False}}}
    gui_ctrl = guiCtrl(layout)
    gui_monitor = guiMonitor(gui_ctrl.args)
    sub_gui_pro = multiprocessing.Process(target=guiengine_proc,args=(gui_ctrl.args,))
    sub_gui_pro.start()

    time.sleep(3)
    while True:
        if gui_monitor.is_gui_quit():   break
        gui_ctrl.update({'cue':{'start':True}},{''})
        print('start')
        time.sleep(3)
        gui_ctrl.update({'cue': {'start': False}},{''})
        print('stop')
        time.sleep(1)
    input()
    gui_ctrl.update({'cue':{'start':True}},{''})
    print('main process quit')

if __name__ == '__main__':
    main()
