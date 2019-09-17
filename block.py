#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2018, Nudt, JingshengTang, All Rights Reserved
# Author: Jingsheng Tang
# Email: mrtang@nudt.edu.cn

import pygame
from pygame_anchors import *
import os


class Block(object):
    size = (5, 5)
    position = (0, 0)
    anchor = 'center'
    forecolor = (255, 255, 255, 255)

    borderon = False
    borderwidth = 2
    bordercolor = (0, 0, 0, 0)

    textcolor = (0, 255, 255, 0)
    textfont = 'arial'
    textanchor = 'center'
    textsize = 10
    textbold = False
    text = ''

    layer = 0
    visible = False

    parmkeys = ['size', 'position', 'anchor', 'borderon', 'borderwidth', 'bordercolor',
                'forecolor', 'textcolor', 'textfont', 'textanchor', 'textsize', 'textbold',
                'text', 'layer', 'visible']
    sur = None
    blitp = (0, 0)

    def __init__(self, root, **argw):
        pygame.font.init()
        self.root = root
        self.transparent = False


        if not os.path.isfile(self.textfont):
            self.textfont = pygame.font.match_font(self.textfont)
        self.font_object = pygame.font.Font(self.textfont, self.textsize)
        self.font_object.set_bold(self.textbold)

        self.reset(**argw)  # 重设参数
        if not os.path.isfile(self.textfont):
            self.textfont = pygame.font.match_font(self.textfont)
        self.font_object = pygame.font.Font(self.textfont, self.textsize)
        self.font_object.set_bold(self.textbold)

    def update_parm(self, **argw):  # 接收新的参数
        for item in argw:
            exec('self.%s = argw[item]' % (item))

    def reset(self, **argw):
        self.update_parm(**argw)
        self.blitp = self.blitpborder = blit_pos1(
            self.size, self.position, self.anchor)
        self.sur = pygame.Surface(self.size)
        self.sur.fill(self.forecolor)

        if self.text != '':
            txt = self.font_object.render(self.text, 1, self.textcolor)
            p0 = getcorner(self.sur.get_size(), self.textanchor)
            p = blit_pos(txt, p0, self.textanchor)
            self.sur.blit(txt, p)

        if len(self.forecolor)>3 and self.forecolor[3] == 0:
            self.transparent = True
        else:
            self.transparent = False
  # return self.sur,self.blitp

    def show(self):  # 显示到screen
        if self.visible:
            if not self.transparent and self.sur is not None:
                self.root.blit(self.sur, self.blitp)
            if self.borderon:
                pygame.draw.rect(self.root, self.bordercolor, pygame.Rect(
                    self.blitpborder, self.size), self.borderwidth)
