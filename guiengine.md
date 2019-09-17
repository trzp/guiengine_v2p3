![bciros](bciros_logo.png)

Copyright (C) 2018, Nudt, JingshengTang, All Rights Reserved

Author: Jingsheng Tang

Email: mrtang@nudt.edu.cn

## [BCIROS](http://weibo.com/ihubo),[GuiEngine](http://weibo.com/ihubo),[Phase](http://weibo.com/ihubo)

## GuiEngine是什么?
一个简洁的图形刺激引擎

## GuiEngine的特性
* 为了确保图形刺激的精确性，我们使用了opengl硬件加速技术，并且运用了垂直同步(Vertical Hold)方法，使每一帧图形都能被精确渲染
* EEG刺激实验的信号标签由GuiEngine来发射，确保标签记录的时刻是被请求的图形刺激真正被渲染时。
* 跨平台，目前已在windows和linux系统经过测试

## GuiEngine的下载与安装
* 请确保您的电脑安装有[python](https://www.python.org/)和[pygame](https://www.pygame.org/)包
* [下载](https://github.com/trzp/guiengine)所有文件，修改setup.py中python_path，比如'c:\Python27'或者'/usr/lib/python2.7'，并运行setup.py即完成安装

    ```python
    if __name__ == '__main__':
        install_package('guiengine_trzp',python_path)
    ```
    
## 依赖库：[get_global_clock_rz](https://github.com/trzp/sysclock)

## GuiEngine编程
* 导入类并使用：
    ```python
    from guiengine import GuiEngine
    
    guieng = GuiEngine(stims,Q_c2g,E_g2p,Q_g2s)
    guieng.StartRun()
    ```
* 类的方法：
    * \__init__(self,stims,Q_c2g,E_g2p,Q_g2s):实例化引擎
    * StartRun()：启动引擎

## GuiEngine.\__init__参数说明
### 参数：stims:
* python字典(未来我们将支持xml超文本标记语言描述的文件或者字符串，敬请期待)，用来描述图形界面的布局。
* 示例：
```python
sti = {'screen':{'size':(600,500),'color':(0,0,0)},
        'cue':{'class':'Block','parm':{'size':(100,40),'position':(600/2,30),
        'anchor':'center','visible':True,'forecolor':(0,0,0),'text':'tangjign',
        'textsize':25,'textcolor':(0,0,255),'textanchor':'center'}}}
```
    * 说明：该字典的形式为{'screen':{描述screen的属性}，'刺激1':{对刺激1的描述}，'刺激2':{对刺激2的描述}，}
    * 至少应当包含对screen的描述，screen的属性有：
        * size: (width,height)
        * type: fullscreen/normal
        * frameless: True/False
        * color: (R,G,B)
        * caption: string
        * Fps: int, strongly suggest you set Fps as the same with system's Fps
        * 补充说明：Fps应当设置为与系统一致，确保在系统垂直同步开启失败时能够保持正确同步。另外，当且仅当type为fullscreen时，硬件加速和垂直同步才可开启。因此，在在线使用时，应当使用fullscreen模式。
    
    * 对其他刺激的描述：如例子中key'刺激1'为对该刺激唯一的标识，其item为一个字典，来具体描述其内容，包含class和parm两个key。class对应了刺激图形类型，parm用来描述这个刺激图形的参数。
        * 目前支持的刺激图形有：
            *  Block: 用以标识方块，文本等
            *  sinBlock: 用以表示灰度以正弦波规律变化的方块
            *  mBlock： 用以标识灰度以随机编码调制变化的方块
            *  ImageBox：用以加载图像的纹理
    
### 参数：Q_c2g,E_g2p,Q_g2s，用于工作进程/线程与guiengine的交互
* 一旦GuiEngine启动(StartRun)，线程将被阻塞。因此我们需要通过另一个线程或者进程（此处称其为工作线程/进程）通过Q_c2g,E_g2p,Q_g2s与之交互。
* Q_c2g: 这是一个能够实现线程/进程之间传递列表的类，当工作进程和GuiEngine进程具有亲缘关系时，您可以直接使用multiprocessing.Queue；
    * 当您需要通过远程或者另一个与GuiEngine进程没有亲缘关系的工作进程来与GuiEngine交互时，您可以使用命名管道或者socket来实现这个类。
    * 您需要实现这个类的一个方法：
        * [stims_update,trigger]=x.get():返回一个列表，列表内包含两个字典。该函数为阻塞型函数，切不可为非阻塞型。
        * 显然，命名管道和socket只能传递字符串，因此您需要做一定的工作将字符串解析为列表和字典。一个技巧是使用xml超文本标记字符串或者json文件作为中间内容，在请求端使用对应工具将dict转换为xml/json文件，在响应端使用对应工具将字符串解析为字典。Python的第三方库无所不能！
    * Q_c2g传递的内容：[stims_update,trigger]
        * stims_upate: {'ID':{parms}}，ID对应此前初始化时的唯一标识，否则该内容将被忽略。parms为字典：描述该对象的属性。示例：
        * trigger:{'trigger_name1':value1，'trigger_name2':value2}, 即描述trigger对应的值
        ```python
        q.put([{'Flsh1':{'forecolor':(255,0,0),'text':'hello'}},{'stimulus_code':1}])
        ```
    * 补充说明：当您通过Q\_c2g传递 \_\_quit__ 字符串时，将终止GuiEngine进程
* E_g2p: 这是一个能够实现线程/进程之间传递事件的类，当工作进程和GuiEngine进程具有亲缘关系时，您可以直接使用multiprocessing.Event；
    * 同理您可以通过其他方法实现这个类
    * 您需要实现这个类的几个方法：
        * x.set(): 向外发送一个事件
        * 接受端需要实现非阻塞函数x.isSet()来判断x.set()是否被调用，即是否发射了事件
    * 工作进程通过E_g2p查询.isSet()来得知GuiEngine是否触发了用户退出事件，GuiEngine运行中可通过Esc键退出程序
* Q_g2s: 和Q\_c2g类似。但用来向工作线程发射带时间戳的trigger。

## example1
这是一个静态示例，这个界面仅仅显示一个text,它将不会有任何动态效果
```python
from guiengine import GuiEngine
from multiprocessing import Queue 
from multiprocessing import Event
import multiprocessing
import time

layout = {'screen':{'size':(200,200),'color':(0,0,0),'type':'normal',
                        'Fps':60,'caption':'this is an example'},
             'cue':{'class':'Block','parm':{'size':(100,100),'position':(100,100),
                    'forecolor':(128,128,128),'text':'hello world','visible':True}}}

def exmaple1():
    Q_c2g = Queue()
    E_g2p = Event()
    Q_g2s = Queue()
    
    gui = GuiEngine(layout,Q_c2g,E_g2p,Q_g2s)
    gui.StartRun()


if __name__ == '__main__':
    example1()
```

## example2
这个一个动态示例，我们将guimachine放在一个子进程里面运行，主进程通过Q\_c2g与之交互

```python
from guiengine import GuiEngine
from multiprocessing import Queue 
from multiprocessing import Event
import multiprocessing
import time

layout = {'screen':{'size':(200,200),'color':(0,0,0),'type':'normal',
                        'Fps':60,'caption':'this is an example'},
             'cue':{'class':'Block','parm':{'size':(100,100),'position':(100,100),
                    'forecolor':(128,128,128),'text':'hello world','visible':True}}}

def proc(layout,Q_c2g,E_g2p,Q_g2s):
    gui = GuiEngine(layout,Q_c2g,E_g2p,Q_g2s)
    gui.StartRun()

def example2():
    Q_c2g = Queue()
    E_g2p = Event()
    Q_g2s = Queue()
    process = multiprocessing.Process(target=proc,args=(layout,Q_c2g,E_g2p,Q_g2s))
    process.start()

    while True:
        if E_g2p.is_set():break
        Q_c2g.put([{'cue':{'forecolor':(200,200,0)}},{'code':0}])
        time.sleep(0.5)
        Q_c2g.put([{'cue':{'forecolor':(100,100,0)}},{'code':0}])
        time.sleep(0.5)

    print 'main process exit'


if __name__ == '__main__':
    example2()

```

Edit by Jingsheng Tang

give thanks to MaHua
















Edit By [MaHua](http://mahua.jser.me)