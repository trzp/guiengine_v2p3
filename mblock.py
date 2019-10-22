#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2018, Nudt, JingshengTang, All Rights Reserved
# Author: Jingsheng Tang
# Email: mrtang@nudt.edu.cn

import pygame
from pygame_anchors import *
import os
from copy import copy


class mBlock(object):
    '''
    used for generate m-sequence stimulus. i.e. vary at each frame accodring to the sequence.
    all the stimulus type with behavior control at each frame should regesit with a key of "perframe"
    '''
    
    def __init__(self, root, **argw):
        self.size = (5, 5)
        self.position = (0, 0)
        self.anchor = 'center'
        self.forecolor1 = (255, 255, 255)
        self.forecolor0 = (255, 0, 0)

        self.borderon = False
        self.borderwidth = 1
        self.bordercolor = (0, 0, 0, 0)

        self.textcolor = (0, 255, 255, 0)
        self.textfont = 'arial'
        self.textanchor = 'center'
        self.textsize = 10
        self.textbold = False
        self.text = ''

        self.m_sequence = None
        self.repetition = 1
        self.layer = 0
        self.visible = False  # 刺激可见
        self.start = False  # 刺激开始

        self._sequence = []
        self.parmkeys = ['size', 'position', 'anchor', 'borderon', 'borderwidth', 'bordercolor',
                    'forecolor1', 'textcolor', 'textfont', 'textanchor', 'textsize', 'textbold',
                    'text', 'layer', 'visible', 'm_sequence', 'repetition', 'start', 'forecolor0']
        self.sur = None
        self.txtsur = None
        self.blitp = (0, 0)
        self.txtblitp = (0,0)
        
        pygame.font.init()
        self.root = root
        self.reset(**argw)

        if not os.path.isfile(self.textfont):
            self.textfont = pygame.font.match_font(self.textfont)
        self.font_object = pygame.font.Font(self.textfont, self.textsize)
        self.font_object.set_bold(self.textbold)

    def release(self):
        pass

    def update_parm(self, **argw):
        for item in argw:
            exec('self.%s = argw[item]' % (item))

    def show(self):  #每一帧被调用一次
        if self.visible:
            if self.start:
                if len(self._sequence) == 0:    #没有了就画forecolor0颜色
                    self.sur.fill(self.forecolor0)
                    self.start = False
                else:
                    m = self._sequence.pop(0)       #从前开始
                    if self.repetition == 0:        #无限循环
                        self._sequence.append(m)    #将取出来的序列添加到最后
                    self.sur.fill(self.forecolor1) if m else self.sur.fill(self.forecolor0)
            else:
                self.sur.fill(self.forecolor0)

            if self.sur != None:
                if self.txtsur is not None:
                    self.sur.blit(self.txtsur,self.txtblitp)

                self.root.blit(self.sur,self.blitpborder)

            if self.borderon:
                pygame.draw.rect(self.root, self.bordercolor, pygame.Rect(
                    self.blitpborder, self.size), self.borderwidth)


    def reset(self, **argw):
        self.update_parm(**argw)
        self.blitp = self.blitpborder = blit_pos1(self.size, self.position, self.anchor)
        self.sur = pygame.Surface(self.size)
        self.sur.fill(self.forecolor0)

        if 'start' in argw:
            if argw['start']:
                self._sequence = copy(self.m_sequence)
                if self.repetition > 0:
                    self._sequence *= self.repetition

        if self.text != '':
            self.txtsur = self.font_object.render(self.text, 1, self.textcolor)
            p0 = getcorner(self.sur.get_size(), self.textanchor)
            self.txtblitp = blit_pos(self.txtsur, p0, self.textanchor)
        else:
            self.txtsur = None