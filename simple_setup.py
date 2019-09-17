#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/15 9:01
# @Version : 1.0
# @File    : setup.py
# @Author  : Jingsheng Tang
# @Version : 1.0
# @Contact : mrtang@nudt.edu.cn   mrtang_cs@163.com
# @License : (C) All Rights Reserved

# 本脚本用于生成.pth文件，可将该文件放置在python path/lib/site-packages目录下，实现永久添加系统目录

if __name__ == '__main__':
    import os
    rootdir = os.path.dirname(os.path.abspath(__file__))
    package_name = os.path.split(rootdir)[-1]
    with open(os.path.join(rootdir,package_name + '.pth'),'w') as f:
        f.write(rootdir)



