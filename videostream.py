#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2018, Nudt, JingshengTang, All Rights Reserved
# Author: Jingsheng Tang
# Email: mrtang@nudt.edu.cn

import pygame
from pygame_anchors import *
import os
from copy import deepcopy

from mjpeg.client import MJPEGClient
import cv2
import numpy as np
import threading


class MjpegStream(object):

    def __init__(self, root, **argw):
        self.size = (640,480)
        self.position = (0, 0)
        self.anchor = 'center'
        self.url = ''
        
        self.borderon = False
        self.borderwidth = 1
        self.bordercolor = (0, 0, 0, 0)

        self.textcolor = (0, 255, 255, 0)
        self.textfont = 'arial'
        self.textanchor = 'center'
        self.textsize = 10
        self.textbold = False
        self.text = ''
        
        self.layer = 0
        self.visible = False     #刺激可见
        self.start = False          #刺激开始

        self.blitp = (0,0)
        self.txtsur = None
        self.txtblitp = (0,0)
        
        self.parmkeys = ['size', 'position', 'anchor', 'url','borderon', 'borderwidth', 'bordercolor',
                 'textcolor', 'textfont', 'textanchor', 'textsize', 'textbold',
                'text', 'layer', 'visible', 'start']
        
        #
        self._update = True
        pygame.font.init()
        self.root = root
        self.reset(**argw)
        
        self.sur = pygame.Surface(self.size)
        self.sur.fill((0,255,0))

        if not os.path.isfile(self.textfont):
            self.textfont = pygame.font.match_font(self.textfont)
        self.font_object = pygame.font.Font(self.textfont, self.textsize)
        self.font_object.set_bold(self.textbold)
        
        # 初始化mjpeg客户端
        self.mjpeg_client = MJPEGClient(self.url)
        bufs = self.mjpeg_client.request_buffers(65536, 50)
        for b in bufs:
            self.mjpeg_client.enqueue_buffer(b)
        self.mjpeg_client.start()
        
        # 更新stream
        self._lock = threading.Lock()
        th = threading.Thread(target = self._update_stream,args = (),daemon = True)
        th.start()

    def release(self):
        self.mjpeg_client.stop()
        self._update = False
    
    def _update_stream(self):
        while self._update:
            buf = self.mjpeg_client.dequeue_buffer()

            if self.start:
                im = cv2.imdecode(np.array(buf.data),cv2.IMREAD_COLOR)[:,:,::-1] #BGR通道反转
                w,h,_ = im.shape
                sur = pygame.image.fromstring(im.flatten().tostring(np.uint8),(w,h),'RGB')

                self._lock.acquire()
                self.sur = pygame.transform.scale(sur,self.size)
                if self.txtsur is not None:
                    self.sur.blit(self.txtsur,self.txtblitp)
                self._lock.release()

            self.mjpeg_client.enqueue_buffer(buf)

    def update_parm(self, **argw):
        for item in argw:
            exec('self.%s = argw[item]' % (item))

    def reset(self, **argw):
        self.update_parm(**argw)
        self.blitp = self.blitpborder = blit_pos1(self.size, self.position, self.anchor)

        if self.text != '':
            self.txtsur = self.font_object.render(self.text, 1, self.textcolor)
            p0 = getcorner(self.sur.get_size(), self.textanchor)
            self.txtblitp = blit_pos(self.txtsur, p0, self.textanchor)
        else:
            self.txtsur = None

    def show(self):
        if self.visible:
            self.root.blit(self.sur, self.blitp)
            if self.borderon:
                pygame.draw.rect(self.root, self.bordercolor, pygame.Rect(
                    self.blitpborder, self.size), self.borderwidth)