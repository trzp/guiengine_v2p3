#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2018, Nudt, JingshengTang, All Rights Reserved
# Author: Jingsheng Tang
# Email: mrtang@nudt.edu.cn

import pygame
from pygame_anchors import *
import os


class Imagebox(object):
    image = ''
    size = (0, 0)
    position = (0, 0)
    anchor = 'lefttop'
    text = ''
    textcolor = (0, 255, 255)
    textfont = 'arial'
    textsize = 10
    textanchor = 'lefttop'
    borderon = False
    borderwidth = 1
    bordercolor = (255, 255, 255)
    textbold = False
    layer = 0
    visible = False

    parmkeys = ['image', 'size', 'position', 'anchor', 'text', 'textcolor', 'textfont', 'textsize',
                'textanchor', 'borderon', 'borderwidth', 'bordercolor', 'layer', 'visible', 'textbold',
                ]
    sur = None
    blitp = (0, 0)

    def __init__(self, root, **argw):
        pygame.font.init()
        self.root = root
        if not os.path.isfile(self.textfont):
            self.textfont = pygame.font.match_font(self.textfont)
        self.font_object = pygame.font.Font(self.textfont, self.textsize)
        self.font_object.set_bold(self.textbold)
        self.reset(**argw)

    def update_parm(self, **argw):
        for item in argw:
            exec('self.%s = argw[item]' % (item))

    def reset(self, **argw):
        self.update_parm(**argw)
        if self.size == (0, 0):  # 默认使用image的size
            self.sur = pygame.image.load(self.image).convert()
            self.size = self.sur.get_size()
        else:
            self.sur = pygame.transform.scale(
                pygame.image.load(self.image).convert(), self.size)

        if self.text != '':
            txt = self.font_object.render(self.text, 1, self.textcolor)
            p0 = getcorner(self.sur.get_size(), self.textanchor)
            p = blit_pos(txt, p0, self.textanchor)
            self.sur.blit(txt, p)

        self.blitp = blit_pos1(self.size, self.position, self.anchor)
        # return self.sur,self.blitp

    def show(self):
        if self.visible:
            if self.sur != None:
                self.root.blit(self.sur, self.blitp)
            if self.borderon:
                pygame.draw.rect(self.root, self.bordercolor, pygame.Rect(
                    self.blitp, self.size), self.borderwidth)
