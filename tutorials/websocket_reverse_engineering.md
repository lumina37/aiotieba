# 使用python+aiohttp还原某度某吧私信的websocket+protobuf+RSA/AES加密流程

本人是一名大三学生，因为某吧吧务管理有自动发送私信的需求，我就利用课余时间逆向研究了某吧app的私信功能。刚准备研究的时候，我在github和吾爱破解都搜了一下，没找到相关内容，这篇文章算是补个漏吧

先给个Unlicense开源仓库地址[https://github.com/Starry-OvO/Tieba-Manager](https://github.com/Starry-OvO/Tieba-Manager)还望各位能赏个star

jadx反编译应该算是很常规的逆向手段了，而且说实话我没写过java也不太了解java，只能靠C++的开发经验来推测代码的用途，我这篇文章的参考价值可能更多地在python实现上

如下图，用网页端打开某吧私信页的时候可以明显看到一个status_code=101的websocket建立请求，并且发送和接收私信都是在这个websocket上实现，我就大胆猜测app的私信功能也是基于websocket实现的

![010-网页端websocket](https://user-images.githubusercontent.com/48282276/173098204-1ef8eea7-0fcd-400e-af3b-643cad84174a.png)

打开模拟器和wireshark开始抓包。然后打开私信界面

![020-app私聊界面](https://user-images.githubusercontent.com/48282276/173099765-1202f4c5-aaa3-4e62-8679-de7f3e3c4d8b.png)

wireshark抓到了websocket建立请求，追踪这个请求的TCP流

![030-wireshark追踪流](https://user-images.githubusercontent.com/48282276/173099798-bb64192e-c985-483e-b1bd-f491f9e5bf3e.png)

如下图所示，可以发现该请求的Host和网页端的一致，都是im.tieba.baidu.com:8000

![040-抓包ws建立请求](https://user-images.githubusercontent.com/48282276/173100150-7c37faae-9d71-4a31-a5e6-57da1d342ed4.png)

观察一下client发给server的第一个websocket包，如下图所示。可以看到很多明文的字符串，但也夹杂着一些不能ascii解码的内容，出于直觉我猜测这是protobuf的编码效果

![050-分析ws第1帧](https://user-images.githubusercontent.com/48282276/173100175-49c92f59-5607-46b4-a62b-921eac4f2258.png)

再看后续双方通信的websocket包，完全不包含明文，我推测这是某种加密的效果

![051-分析ws第2帧](https://user-images.githubusercontent.com/48282276/173100762-65408ae5-33cd-4b24-ba69-81db47802484.png)

![052-分析ws第3帧](https://user-images.githubusercontent.com/48282276/173100764-d9e595c1-4b9b-4e25-95b7-ac52274d7d82.png)

jadx反编译某吧极速版app

![060-jadx打开极速版](https://user-images.githubusercontent.com/48282276/173100770-b79497e5-85b6-49c9-8163-06ab47d8a12e.png)

搜索字符串im.tieba.baidu.com并跳转到下图位置

![070-jadx搜索imtieba](https://user-images.githubusercontent.com/48282276/173100777-55b1a706-11f1-4ff6-9faa-b999e7049e98.png)

搜索一下该变量被调用的位置，如下图红框所示。蓝框标出的是伏笔，和后续的RSA加密有关

![080-jadx跟踪url](https://user-images.githubusercontent.com/48282276/173100786-77041e37-7ed7-49bf-b551-424d2651a4ef.png)

跟踪这个链接，我们可以找到Socket的初始化方法

![090-找到socket初始化函数](https://user-images.githubusercontent.com/48282276/173102292-0862b5ed-6144-4dc3-9b77-a7e42b9cb1fe.png)

注意到上图红框里的MessageManager，因为它有个类方法sendMessage（如下图），再综合其他一系列特征，比如创建并行化任务队列的相关方法，我判断出这应该是负责收发包的类

![100-注意到MessageManager](https://user-images.githubusercontent.com/48282276/173102311-ba988981-8ff4-4901-965b-967e18fb8848.png)

分析一下上图红框里的函数e

![120-sendMessage进入发包函数](https://user-images.githubusercontent.com/48282276/173102318-a1270ddd-1917-4c36-b91b-7635681f444c.png)

通过上图所示的分析，再结合类成员变量（如mData、mCmd等）的内容，我判断出Message应该是一个保存请求参数的类，而MessageTask保存了任务类别相关的信息

![130-分析发包函数](https://user-images.githubusercontent.com/48282276/173102327-a79011e5-28b6-4951-b099-df618c98ac04.png)

mCmd是初始化Message的一个关键参数，需要特别注意它的用途，如下图所示

![140-注意cmd的作用](https://user-images.githubusercontent.com/48282276/173102336-97e0093a-a42a-49d5-92e1-3bf07edd44c7.png)

根据下图分析，我推测Message的类成员变量mData保存了请求相关的数据

![150-注意mData的作用](https://user-images.githubusercontent.com/48282276/173102347-e82a3cad-ece5-4da1-af7b-250c11bd7f8e.png)

下面跟踪一下setData方法

![160-跟踪setData](https://user-images.githubusercontent.com/48282276/173107272-87835be6-feff-44b5-b7a5-228dc3374789.png)

找到了一个纯虚成员函数encode

![180-准备跟踪encode](https://user-images.githubusercontent.com/48282276/173107285-c34c9577-8030-42d3-be03-c2f0b69ff2b7.png)

因为这个方法的具体实现在Message的子类中，我们只能回到initSocket来找找其他线索

会动态调试的也可以考虑在这个initSocket方法附近下断点

![190-回到initSocket](https://user-images.githubusercontent.com/48282276/173109464-9a4b3e5a-b663-412b-80a6-fee455a6f822.png)

上图所示的ResponseOnlineMessage是被注册到MessageManager的第一个MessageTask对应的Message子类，我判断它应该是被用于接收client发给server的第一个websocket包的返回数据

如下图所示，点开这个Message我们找到了protobuf流程的特征

![210-发现protobuf](https://user-images.githubusercontent.com/48282276/173109473-804f43c6-7949-41d0-85d3-76d0524bfa3d.png)

如下图所示，通过UpdateClientInfoResIdl提供的线索，我们可以进一步找到同一级文件夹下UpdateClientInfoReqIdl的protobuf字段定义

根据名称和字段定义我判断Req是请求proto，而Res是响应proto

![220-找到UpdateClientInfoReqIdl字段定义](https://user-images.githubusercontent.com/48282276/173109479-e7c74a44-045a-4ee0-be1b-743034a397ce.png)

其中UpdateClientInfoReqIdl.DataReq的proto定义如下图所示

![230-找到UpdateClientInfoReqIdl字段定义](https://user-images.githubusercontent.com/48282276/173109483-5b3819cb-b3e9-4c95-8e97-6c3d4278594f.png)

下一步就是查找protobuf字段被装填的位置，这可以通过查找Builder被调用的位置来实现，如下图所示

![250-寻找protobuf数据装填位置](https://user-images.githubusercontent.com/48282276/173109508-117dbb22-0a8c-45a3-ad30-33e780a85b40.png)

我们找到了UpdateClientInfoMessage的类方法encode，它正是对上文提到的Message类的纯虚方法encode的具体实现

如下图所示，看来这个encode系列方法所实现的功能就是装填protobuf字段

![260-明确装填方式并寻找上级调用](https://user-images.githubusercontent.com/48282276/173109526-0720f401-db63-44b2-8922-4959a92cc023.png)

同时找到该encode方法被调用的位置getData，再找getData方法的上级调用，如下图所示

![270-寻找上级调用](https://user-images.githubusercontent.com/48282276/173109531-62621958-1b44-4617-ad41-eaa42909da23.png)

找到了函数encodeInBackground，以及熟悉的老朋友mData

该函数通过java反射来调用protobuf-Builder的toByteArray方法，将proto容器转换为bytes

![280-找到encodeInBackground](https://user-images.githubusercontent.com/48282276/173109538-145a2a02-91e6-4ece-8e37-5d020c9aea0f.png)

再找encodeInBackground方法的上层调用，找到方法a

![290-找到打包方法](https://user-images.githubusercontent.com/48282276/173165063-5bc3c43b-4063-4dfe-bbf0-1bac54accccb.png)

这个a方法非常重要，简单分析如下

![300-分析打包方法-改](https://user-images.githubusercontent.com/48282276/173165064-6bb33fa6-11da-4b7f-905a-37f5f542ebed.png)

深入函数e，发现一个函数g.f

![310-e函数分析](https://user-images.githubusercontent.com/48282276/173165065-3ce33912-8d7a-4a7d-9031-acb9f12018a3.png)

点进去发现这是一个gzip压缩的方法

![320-e函数分析gzip](https://user-images.githubusercontent.com/48282276/173165067-cdfe3fd0-4531-43f2-9636-27a0c964cb97.png)

接着分析a函数里的u.a函数，发现这是一个简单的AES加密方法

![330-u a函数分析AES](https://user-images.githubusercontent.com/48282276/173165068-bf951058-20c7-499b-97db-e6fdd2b779fd.png)

既然是AES加密我们就得找密钥

如下图所示，类成员变量Yn就是AES密钥，该密钥通过函数g里的函数调用u.be(eo)生成

![340-AES密钥](https://user-images.githubusercontent.com/48282276/173165070-64c0c7fa-d5a1-4027-aa84-07f15d01afe1.png)

为了搞清楚生成的时机，还得看看函数g在何处被调用，如下图所示

![350-寻找g函数被调用的位置](https://user-images.githubusercontent.com/48282276/173165071-5cbff80b-9312-4469-be96-a47e2fc39d2a.png)

发现函数g只在Socket初始化的时候被调用了一次

因为函数g的入参和AES加密无关，这个getPublicKey我们后面再看

![360-找到g函数被调用的位置](https://user-images.githubusercontent.com/48282276/173165089-5c757732-789a-4074-a98b-ed96b14ce83d.png)

下面分析一下生成AES密钥的函数u.be的入参eo

![370-分析eo](https://user-images.githubusercontent.com/48282276/173165093-7421e705-8639-41c5-bb7c-1ea5f780bd44.png)

点进函数eo发现这是个返回36字节长的随机bytes的函数

而且他这个子串分割写得好像有点问题，子串长度与int i无关，而是一个固定值36

![380-eo随机生成36bytes](https://user-images.githubusercontent.com/48282276/173165096-1c90f95f-d0a7-4c15-a0ef-8699f3b6bf96.png)

然后就用sha1生成一个AES密钥，salt是bytes数组ahI

![390-生成AES密钥](https://user-images.githubusercontent.com/48282276/173165097-8b9d27ed-bf70-43d3-a000-4d1bb116e3ee.png)

现在我们就完全知道函数a中的函数e和函数u.a的用途了，解析如下

![400-阐释上层函数-改](https://user-images.githubusercontent.com/48282276/173165103-8e1cfdc8-2932-4105-9bb1-5e74d7dac7e4.png)

然后是对a.a函数的分析，如下图

![400-分析a a函数-改](https://user-images.githubusercontent.com/48282276/173165110-8b087267-71af-4d21-9888-70654aef3e61.png)

为了验证上述猜测，我们保存一下websocket的首个请求

![420-保存字节流](https://user-images.githubusercontent.com/48282276/173165122-525f0a4d-34d1-406e-9819-2a7b71c7d2b5.png)

看头部的9字节，第1个字节为0x08，意味着数据未经过AES加密和gzip压缩；后4个字节转换到十进制就是熟悉的cmd=1001

![430-分析9字节头部](https://user-images.githubusercontent.com/48282276/173165124-45411fe0-ae91-49f9-89b6-d1ee497fc0b9.png)

用hexediter删去头部9字节后保存，再用protoc反解剩余内容，发现确实是protobuf

![440-分析protobuf](https://user-images.githubusercontent.com/48282276/173165127-3f58e4e6-0ab5-4cb8-a80c-a06dd3ba4496.png)

熟悉某吧客户端爬虫的能很轻松地看出来，这些protobuf字段基本都是固定的客户端标识，比较常规，除了一个secretKey需要额外分析

先看secretKey字段的赋值位置

![450-寻找secretKey的生成方式](https://user-images.githubusercontent.com/48282276/173165137-8cf2e791-6a81-45e3-8899-9af2c34c2fe4.png)

然后搜索类属性secretKey被赋值的位置

![460-寻找secretKey的生成方式](https://user-images.githubusercontent.com/48282276/173165146-29b84d58-4569-4e1f-a270-7a694471cd2e.png)

然后看setSecretKey方法被调用的位置

![470-寻找secretKey的生成方式](https://user-images.githubusercontent.com/48282276/173165147-6950295f-0637-4bf4-98bc-1c032e6c8e8f.png)

再研究类方法oJ，发现它其实就是个取出类属性Yo的方法

![480-寻找secretKey的生成方式](https://user-images.githubusercontent.com/48282276/173165149-5bb616b0-8a92-45b7-b0f0-baf0606835e7.png)

类属性Yo又是在函数g中通过函数u.b生成

进入u.b可以知道这就是一个利用publicKey对输入bytes数组做RSA加密的函数

而输入的bytes数组其实就是从36字节长的随机字符串eo逐字节转换而来

这个eo也被用于AES密钥的生成，之前的分析也提到过

![490-RSA生成secretKey](https://user-images.githubusercontent.com/48282276/173165152-9c399ab1-a4d7-44fb-86a0-65491d19d537.png)

回到上一层函数我们发现publicKey是通过函数u.q(bArr)生成

点进函数q我们发现这其实就是一个利用bArr生成公钥的方法

![500-RSA导入公钥](https://user-images.githubusercontent.com/48282276/173165153-d96e05a5-2904-414a-892b-e9b74f710539.png)

通过不断地往上级翻找，我们可以发现bArr来源于getRSAPublicKey函数

![520-找到g的调用位置](https://user-images.githubusercontent.com/48282276/173165161-1ff87fa0-fd65-46a0-abf3-c9085cc94318.png)

点进这个函数，成功回收伏笔，把这串硬编码的东西base64decode就能得到RSA公钥了

![530-找到RSA公钥的来源](https://user-images.githubusercontent.com/48282276/173165162-27bbf3ae-1373-4357-9e43-e848cffa2eae.png)

现在回头分析这个发送私信时产生的websocket包，第1字节0x88说明该包经过AES加密而未经gzip压缩

![550-重新分析ws帧](https://user-images.githubusercontent.com/48282276/173165165-d33f0b8e-4e83-4bc9-a4a0-06cc8b8db6ed.png)

利用后四个字节给出的cmd编号0x0320c9=205001我们可以搜索出发送私信功能所对应的Message子类

![560-找出私信Message](https://user-images.githubusercontent.com/48282276/173165166-c17df56f-f200-4b29-b78d-3fef0320a1f9.png)

进一步可以找出发送私信使用的protobuf字段赋值方法

![570-找出私信protobuf](https://user-images.githubusercontent.com/48282276/173165167-b6dfb8c1-106a-4daa-8b2b-5a91c5209c16.png)

以及字段定义

![580-找出私信protobuf](https://user-images.githubusercontent.com/48282276/173165169-fa7d517e-0e9e-4672-9432-93c6217362d8.png)

自行编写proto文件还原必需字段，这是客户端信息上报的proto

![590-编写客户端信息上报protobuf](https://user-images.githubusercontent.com/48282276/173165171-eb93ad50-f2b4-4b78-b0d9-c891c4d1a8e2.png)

这是私信的proto。然后用protoc编译为python格式脚本

![595-编写私信protobuf](https://user-images.githubusercontent.com/48282276/173165172-5691ce2a-5118-4f0f-ac86-f315842a72bb.png)

还需要分析websocket的解包方法，因为大部分工作都和上面重复，我这里就只放个核心分析了

需要注意的是你client发送的时候用的是什么log_id，server响应的时候返回的就是什么log_id

![600-分析websocket解包函数](https://user-images.githubusercontent.com/48282276/173165177-83e1105b-5a2f-4368-a03d-83841ef41d77.png)

到这里我们已经能完全理解某吧私信的工作流程了

首先是包格式

每个包的头部第1字节包含了是否AES加密（第8bit是否为1）、是否gzip压缩（第7bit是否为1）、是否包含extraData（第4bit是否为1）的信息

第2345字节为int32的cmd编号，用来标明该包是用于什么功能的，譬如1001对应客户端信息上报而205001对应私信，当服务端主动推送时这个cmd编号就能起到作用

第6789字节为int32的log_id，当你同时发了很多包时，这个log_id就可以用于区分哪个响应对应哪个请求

然后是websocket建立的流程

首先http101请求建立websocket，然后发送一个初始化包，里面包含用户身份信息BDUSS以及用RSA公钥加密过的密码secretKey，server用RSA密钥解密后生成和client一致的AES密钥，后续的所有包都会用这个密钥做AES加密后再传输

简单概括就是websocket建立→非对称加密协商密钥→对称加密传输数据

后面就是用python+aiohttp还原这整套流程，用我小号给大号发私信debug的效果如下

!![800-私信测试](https://user-images.githubusercontent.com/48282276/173165181-d629ae2f-e20c-4c58-8499-e86e9399d4e1.png)

!![810-私信测试](https://user-images.githubusercontent.com/48282276/173165183-61eefeee-7c7b-4549-ba51-52b5321664cc.jpg)

可以看到效果非常完美，下面我会粗略解释一下我的代码

首先是打包函数，这里AES加密的padding是手动实现的，要注意int转bytes应使用大端序

![820-编写websocket打包函数](https://user-images.githubusercontent.com/48282276/173165185-faddce86-5861-48c3-bfe9-80cb2e3bedcc.png)

然后是解包函数，要注意因为server也用了padding，这里要用bytes.rstrip把填充的东西去掉

![830-编写websocket解包函数](https://user-images.githubusercontent.com/48282276/173165187-8a683b6c-a4b0-462f-9087-85412e17ed11.png)

然后是AES加密功能的实现，salt就是从源码扒出来的ahI，密钥生成方法sha1，迭代次数参考java设置为5，生成的密钥长度是32bytes也就是AES256

![840-编写AES加密器和密码](https://user-images.githubusercontent.com/48282276/173165188-d286873c-c505-4639-9464-a266270ab482.png)

然后是比较精髓的WebsocketResponse类设计，通过一个弱引用字典实现对返回数据的异步等待

每次websocket请求都会产生一个该类的实例用于存放返回数据，产生实例的同时其初始化函数\__init\__会将实例本身添加到一个弱引用字典

当从websocket接收到返回数据时，数据分派器ws_dispatcher会按照req_id从弱引用字典中找到对应的WebsocketResponse实例，并将数据填进去，然后set _readable_event，之后read协程就会被解阻塞，最后将数据返回

为什么要使用弱引用？这是为了让WebsocketResponse实例在被丢弃时可以被自动gc，比如出现timeout。如果使用普通字典（强引用）来保存实例，那会导致作为字典值的实例无法被自动gc，内存会随着程序的运行时间无限增长

然后这里\__slots\__里添加\__weakref\__是为了允许类实例被弱引用，添加\__dict\__是为了让_websocket_request_id可写

这个_websocket_request_id在每次创建实例时都会+1以保证每个实例的请求id的唯一性

![850-编写WebsocketResponse类](https://user-images.githubusercontent.com/48282276/173165191-c90c8a3f-d134-48c3-b46d-21be4ac5d105.png)

read方法其实就是在等待_readable_event的set事件，不论有没有超时，read退出时都会将自己从弱引用字典ws_res_wait_dict里删除，意思是不再需要接收返回数据

![855-编写WebsocketResponse类的read方法](https://user-images.githubusercontent.com/48282276/173165194-39987d9d-cd62-4a1a-9f73-39ddf6341c9f.png)

然后是编写websocket的ClientSession，记得把那个http101请求里用到的headers带上

![860-编写ClientSession](https://user-images.githubusercontent.com/48282276/173165196-d19a5a33-8800-4dba-9b61-d21470e5e416.png)

然后是编写websocket的数据接收与分派器，死循环等待读数据，读到之后就将数据填进WebsocketResponse实例，并通过_readable_event发出可读通知

当Client退出时这个ws_dispatcher也会被cancel掉，不需要担心什么溢出问题

![865-编写websocket分派器](https://user-images.githubusercontent.com/48282276/173165197-6abc7c1f-a738-499d-b357-18ac1626c42c.png)

连接websocket通过ClientSession._ws_connect实现，一并被创建的还有分派器

![870-连接websocket](https://user-images.githubusercontent.com/48282276/173165201-097399c4-90da-44b9-a871-ada1e66d8a44.png)

init_websocket会发送初始化信息，RSA加密的步骤全在这里实现

![880-发送初始化信息](https://user-images.githubusercontent.com/48282276/173165202-425b295c-b36c-40ff-84db-22875cd9a87f.png)

最后就是私信方法的实现

![890-发送私信](https://user-images.githubusercontent.com/48282276/173165204-4389cbec-34ca-43f8-a0c2-506d6707338d.png)

好了全文结束

上述提到的所有python代码（不包括debug脚本）都包含在[https://github.com/Starry-OvO/Tieba-Manager/blob/master/aiotieba/client.py](https://github.com/Starry-OvO/Tieba-Manager/blob/master/aiotieba/client.py)里，食用方法参考项目的README.md

如果这篇文章能帮到你，请给我的开源项目点一个star，非常感谢
