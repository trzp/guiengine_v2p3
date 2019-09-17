![bciros](bciros_logo.png)

Copyright (C) 2018, Nudt, JingshengTang, All Rights Reserved

Author: Jingsheng Tang

Email: mrtang@nudt.edu.cn

## [BCIROS](http://weibo.com/ihubo),[GuiEngine](http://weibo.com/ihubo),[Phase](http://weibo.com/ihubo)

## GuiEngine是什么?
一个简洁的图形刺激引擎

## GuiEngine的特性
* 为了确保图形刺激的精确性，我们使用了opengl硬件加速技术，并且运用了垂直同步(Vertical Hold)方法，使每一帧图形都能被精确渲染
* 通过GUI来发射信号标记能够在图形渲染的精确时刻记录下事件，有助于获得更可靠的信号处理结果
* 跨平台，目前已在windows和linux系统经过测试

## GuiEngine运行环境
* python3，pygame，[rz_global_clock](https://github.com/trzp/sysclock)

## GuiEngine编程
我们建议将为GUI开辟一个独立进程，以提高效率。为此我们提供了一个进程函数和一个交互接口，即：
```javascript
def guiengine_proc(args):
    ...

class GuiIF():    #用于向guiengine发射信号
    def __init__(self,server_address = None,layout = layout):
        ...
        self.args = ...

    def quit(self):
        ...

    def wait(self):
        ...

    def update(self,stimulus,marker):
        ...
```
典型的使用方法是：
```javascript
if __name__ == '__main__':
    # 布局
    layout = {'screen':{'size':(200,200),'color':(0,0,0),'type':'normal',
                        'Fps':60,'caption':'this is an example'},
             'cue':{'class':'sinBlock','parm':{'size':(100,100),'position':(100,100),
                    'frequency':13,'visible':True,'start':False}}}
    
    # 远程服务器的地址，用来接收marker。该例程不使用。
    saddr = None
    
    # 建立与GUI交互的接口
    gui = GuiIF(saddr,layout) 
    
    # 为guiengine_proc开辟一个独立的进程，其参数是gui.args
    _ = multiprocessing.Process(target = guiengine_proc,args = (gui.args,)) # 新建进程启动GUI
    _.start()
    
    gui.wait()      # 等待GUI启动（一般初始化过程需要1-2秒)
    time.sleep(1)
    gui.update({'cue':{'start':True}},{})  # 更新GUI且发送marker（此处发送的marker为None）
    time.sleep(1)
    gui.update({'cue': {'start': False}}, {}) # 更新GUI且发送marker
    time.sleep(1)
    gui.quit()      # 关闭GUI
```

## GuiIF编程说明
用户通过GuiIF类进行初始化以及与GUI进程的交互。因此，仅需要了解GuiIF的使用
### 初始化参数：server_address
为远端服务器地址（ip,port），该服务器用来通过udp socket接收GUI进程发送的marker消息。如果该参数为None,则GUI不发送marker消息，**注意，此时如果在GuiIF.update()中尝试传入非空的marker字典，将引发异常。因为初始化不发送marker,那么在update时就应当填入空的字典{}**
    
### 初始化参数：layout
* 布局，字典类型
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
    * color: (R,G,B)
    * caption: string
    * Fps: int, strongly suggest you set Fps as the same with system's Fps
    * 补充说明：Fps应当设置为与系统一致，确保在系统垂直同步开启失败时能够保持正确同步。另外，当且仅当type为fullscreen时，硬件加速和垂直同步才可开启。因此，在正式实验时，应当使用fullscreen模式。

* 对其他刺激的描述：如例子中key'刺激1'为对该刺激唯一的标识，其item为一个字典，来具体描述其内容，包含class和parm两个key。class对应了刺激图形类型，parm用来描述这个刺激图形的参数。
* 目前支持的刺激图形有：
    *  Block: 用以标识方块，文本等
    *  sinBlock: 用以表示灰度以正弦波规律变化的方块
    *  mBlock： 用以标识灰度以随机编码调制变化的方块
    *  ImageBox：用以加载图像的纹理

### GuiIF方法：wait()
由于GUI程序启动需要完成初始化等工作，一般需要2-3秒。在正式开始实验之前应当使用wait()来等待GUI完成启动。

### GuiIF方法：quit()
关闭GUI

### GuiIF方法：update(stims,marker)
该方法用来修改GUI布局元素的行为以及发送marker,**该marker和stims是对应的，GUI进程当且仅当完成该stims的渲染时刻记录下marker的时间戳**

* stims:字典
* 示例
```javascript
{'cue':{'visible':True,'forecolor':(255,0,0)}} # cue可见且颜色设置为红色
```

* marker:字典
* 示例
```javascript
{'cue_mkr':{'value':[1]}}
```
* 机制：当GUI接受到update请求后立即按照stims的内容准备好相关内容，在GUI主循环刷新信号到来后立即将其渲染到屏幕，此时记录下全局时间戳，将该时间戳记录到marker中，将为其添加timestamp键值，即 {'cue_mkr':{'value':[1],'timestamp':[xxx]}}。事实上，内部使用了Marker类，意味着该时间戳将自动与远程服务器的时钟对准（无需用户关心该细节）。且为了减少网络通信的开销，marker会有短暂的缓存机制，确保marker通过socket向远端发送的时间间隔不低于0.1秒。**这里需要在信号处理部分稍加注意**
