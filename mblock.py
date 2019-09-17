#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2018, Nudt, JingshengTang, All Rights Reserved
# Author: Jingsheng Tang
# Email: mrtang@nudt.edu.cn

import pygame
from pygame_anchors import *
import os
from copy import deepcopy


class mBlock(object):
    '''
    used for generate m-sequence stimulus. i.e. vary at each frame accodring to the sequence.
    all the stimulus type with behavior control at each frame should regesit with a key of "perframe"
    '''
    size = (5, 5)
    position = (0, 0)
    anchor = 'center'
    forecolor1 = (255, 255, 255, 255)
    forecolor0 = (255, 0, 0, 255)

    borderon = False
    borderwidth = 1
    bordercolor = (0, 0, 0, 0)

    textcolor = (0, 255, 255, 0)
    textfont = 'arial'
    textanchor = 'center'
    textsize = 10
    textbold = False
    text = ''

    m_sequence = None
    repetition = 1
    layer = 0
    visible = False     #刺激可见
    start = False          #刺激开始


    _sequence = []
    parmkeys = ['size', 'position', 'anchor', 'borderon', 'borderwidth', 'bordercolor',
                'forecolor1', 'textcolor', 'textfont', 'textanchor', 'textsize', 'textbold',
                'text', 'layer', 'visible', 'm_sequence', 'repetition', 'start','forecolor0']
    sur = None
    blitp = (0,0)

    def __init__(self, root, **argw):
        pygame.font.init()
        self.root = root
        self.reset(**argw)

        if not os.path.isfile(self.textfont):
            self.textfont = pygame.font.match_font(self.textfont)
        self.font_object = pygame.font.Font(self.textfont, self.textsize)
        self.font_object.set_bold(self.textbold)

    def update_parm(self, **argw):
        for item in argw:
            exec('self.%s = argw[item]' % (item))

    def update_per_frame(self):  #每一帧被调用一次
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

    def reset(self, **argw):
        self.update_parm(**argw)
        self.blitp = self.blitpborder = blit_pos1(self.size, self.position, self.anchor)
        self.sur = pygame.Surface(self.size)
        self.sur.fill(self.forecolor0)

        if argw.has_key('start'):
            if argw['start']:
                self._sequence = deepcopy(self.m_sequence)
                if self.repetition > 0:
                    self._sequence *= self.repetition

        if self.text != '':
            txt = self.font_object.render(self.text, 1, self.textcolor)
            p0 = getcorner(self.sur.get_size(), self.textanchor)
            p = blit_pos(txt, p0, self.textanchor)
            self.sur.blit(txt, p)

    def show(self):
        if self.visible:
            if self.sur != None:
                if self.__draw: self.sur.fill(self.forecolor1)
                else:           self.sur.fill(self.forecolor0)
                self.root.blit(self.sur, self.blitp)
            if self.borderon:
                pygame.draw.rect(self.root, self.bordercolor, pygame.Rect(
                    self.blitpborder, self.size), self.borderwidth)