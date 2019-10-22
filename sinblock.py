#!/usr/bin/env python
#-*- coding:utf-8 -*-

#Copyright (C) 2018, Nudt, JingshengTang, All Rights Reserved
#Author: Jingsheng Tang
#Email: mrtang@nudt.edu.cn

import pygame
from pygame_anchors import *
import os
import time
import math
from rz_clock import clock


class sinBlock(object):
    '''
    used for generate sin type stimulus. i.e. the gray vary at each frame accodring to the sequence.
    '''

    def __init__(self, root, **argw):
        self.size = (5,5)
        self.position = (0,0)
        self.anchor = 'center'
        self.forecolor0 = (0,0,0)
        self.forecolor1 = (255,255,255)

        self.bordercolor = (0,0,0,0)
        self.borderon = False
        self.borderwidth = 1

        self.textcolor = (0,255,255,0)
        self.textfont = 'arial'
        self.textanchor = 'center'
        self.textsize = 10
        self.textbold = False
        self.text = ''

        self.frequency = 10
        self.init_phase = 0
        self.duration = float('inf')
        self.start = False
        self.__fcolor = None

        self.layer = 0
        self.visible = False

        self.coef = np.array([0,0,0])
        self.parmkeys = ['size','position','anchor',
                    'forecolor0','forecolor1','textcolor','textfont','textanchor','textsize','textbold',
                    'text','layer','visible','frequency','init_phase','duration','start',
                    'borderon', 'borderwidth', 'bordercolor',]
        self.sur = None
        self.blitp = (0,0)
        self.clk = clock()

        self.txtsur = None
        self.txtblitp = (0,0)

        pygame.font.init()
        self.root = root

        self.reset(**argw)
        if not os.path.isfile(self.textfont): self.textfont = pygame.font.match_font(self.textfont)
        self.font_object = pygame.font.Font(self.textfont,self.textsize)
        self.font_object.set_bold(self.textbold)

    def release(self):
        pass

    def update_parm(self,**argw):
        for item in argw:   exec('self.%s = argw[item]'%(item))
        
    def show(self):
        if self.visible:
            if self.start:
                tt = clock()
                if tt - self.clk > self.duration:
                    self.start = False
                    self.sur.fill(self.forecolor0)
                t = tt-self.clk
                f = (math.sin(2*math.pi*self.frequency*t + self.init_phase - 0.5*math.pi)+1)*0.5   #0-1
                self.__fcolor = self.coef * f + self.forecolor0
                self.sur.fill(self.__fcolor)
            else:
                # self.sur.fill(self.forecolor0)
                pass

            if self.txtsur is not None:
                self.sur.blit(self.txtsur,self.txtblitp)

            self.root.blit(self.sur,self.blitp)
            if self.borderon:
                pygame.draw.rect(self.root, self.bordercolor, pygame.Rect(
                    self.blitpborder, self.size), self.borderwidth)

    def reset(self,**argw): #接受主控的控制
        self.update_parm(**argw)
        self.blitp = self.blitpborder = blit_pos1(self.size,self.position,self.anchor)
        self.coef = np.array(self.forecolor1)-np.array(self.forecolor0)
        self.sur = pygame.Surface(self.size)
        self.sur.fill(self.forecolor0)

        if 'start' in argw:
            if argw['start']:
                self.clk = clock()

        if self.text != '':
            self.txtsur = self.font_object.render(self.text, 1, self.textcolor)
            p0 = getcorner(self.sur.get_size(), self.textanchor)
            self.txtblitp = blit_pos(self.txtsur, p0, self.textanchor)
        else:
            self.txtsur = None

