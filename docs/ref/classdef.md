# 类型定义

## UserInfo

用户信息

### 构造参数

class `UserInfo`(*_id: str | int | None = None*)

<div class="docstring" markdown="1">
**_id** - 用于快速构造UserInfo的自适应参数 输入[user_id](../tutorial/start.md#user_id)或[portrait](../tutorial/start.md#portrait)或[用户名](../tutorial/start.md#user_name)
</div>

### 类属性

<div class="docstring" markdown="1">
**user_id** - *(int)* [user_id](../tutorial/start.md#user_id)

**portrait** - *(str)* [portrait](../tutorial/start.md#portrait)

**user_name** - *(str)* [用户名](../tutorial/start.md#user_name)

**nick_name** - *(str)* 用户昵称

**tieba_uid** - *(int)* [tieba_uid](../tutorial/start.md#tieba_uid)

**level** - *(int)* 等级

**gender** - *(int)* 性别 0未知 1男 2女

**age** - *(int)* 吧龄 以年为单位

**post_num** - *(int)* 发帖数 是回复数和主题帖数的总和

**fan_num** - *(int)* 粉丝数

**follow_num** - *(int)* 关注数

**sign** - *(str)* 个性签名

**ip** - *(str)* ip归属地

**is_bawu** - *(bool)* 是否吧务

**is_vip** - *(bool)* 是否vip

**is_god** - *(bool)* 是否大神

**priv_like** - *(int)* 公开关注吧列表的设置状态 1完全可见 2好友可见 3完全隐藏

**priv_reply** - *(int)* 帖子评论权限的设置状态 1允许所有人 5仅允许我的粉丝 6仅允许我的关注

**log_name** - *(str)* 用于在日志中记录用户信息

**show_name** - *(str)* 显示名称
</div>

## BasicForum

贴吧基本信息

### 类属性

<div class="docstring" markdown="1">
**fid** - *(int)* 贴吧id

**fname** - *(str)* 贴吧名
</div>

## Page

页信息

### 类属性

<div class="docstring" markdown="1">
**page_size** - *(int)* 页大小

**current_page** - *(int)* 当前页码

**total_page** - *(int)* 总页码

**total_count** - *(int)* 总计数

**has_more** - *(bool)* 是否有后继页

**has_prev** - *(bool)* 是否有前驱页
</div>

## Fragments

内容碎片列表

主题帖/回复/楼中楼...的正文内容由多种内容碎片组成

### 类属性

<div class="docstring" markdown="1">
**text** - *(str)* 全部文本内容 由**texts**拼接而成

**texts** - *(list[[TypeFragText](#TypeFragText)])* 纯文本碎片列表

**emojis** - *(list[[FragEmoji](#fragemoji)])* 表情碎片列表

**imgs** - *(list[[FragImage](#fragimage)])* 图像碎片列表

**ats** - *(list[[FragAt](#fragat)])* @碎片列表

**links** - *(list[[FragLink](#fraglink)])* 链接碎片列表

**tiebapluses** - *(list[[FragTiebaPlus](#fragtiebaplus)])* 贴吧plus碎片列表

**has_voice** - *(bool)* 是否包含音频

**has_video** - *(bool)* 是否包含视频
</div>

### 类方法

def `__iter__`() -> *Iterator[_TypeFragment]*

<div class="docstring" markdown="1">
**返回**: 碎片列表的迭代器
</div>

def `__getitem__`(*idx: [slice](https://docs.python.org/zh-cn/3/library/functions.html#slice)*) -> *list[_TypeFragment]*

<div class="docstring" markdown="1">
**参数**: 切片

**返回**: 碎片列表
</div>

def `__getitem__`(*idx: [SupportsIndex](https://docs.python.org/zh-cn/3/library/typing.html#typing.SupportsIndex)*) -> *_TypeFragment*

<div class="docstring" markdown="1">
**参数**: 下标

**返回**: 单个碎片
</div>

def `__len__`() -> *int*

<div class="docstring" markdown="1">
**返回**: 碎片列表长度
</div>

def `__bool__`() -> *bool*

<div class="docstring" markdown="1">
**返回**: True则碎片列表不为空
</div>

### FragText

纯文本碎片

#### 类属性

<div class="docstring" markdown="1">
**text** - *(str)* 文本内容
</div>

### TypeFragText

实现了**text**接口的鸭子类型

### FragEmoji

表情碎片

#### 类属性

<div class="docstring" markdown="1">
**desc** - *(str)* 表情描述
</div>

### FragImage

图像碎片

#### 类属性

<div class="docstring" markdown="1">
**src** - *(str)* 压缩图像链接 宽720px

**origin_src** - *(str)* 原图链接

**hash** - *(str)* 百度图床hash

**show_width** - *(int)* 图像在客户端预览显示的宽度

**show_height** - *(int)* 图像在客户端预览显示的高度
</div>

### FragAt

@碎片

#### 类属性

<div class="docstring" markdown="1">
**text** - *(str)* 被@用户的昵称 含@

**user_id** - *(int)* 被@用户的user_id
</div>

### FragLink

链接碎片

#### 类属性

<div class="docstring" markdown="1">
**text** - *(str)* 原链接

**title** - *(str)* 链接标题

**url** - *([httpx.URL](https://www.python-httpx.org/api/#url))* 解析后的链接 外链会在解析前先去除前缀

**raw_url** - *(str)* 原链接 外链会在解析前先去除前缀

**is_external** - *(bool)* 是否外部链接
</div>

### FragTiebaPlus

贴吧plus广告碎片

#### 类属性

<div class="docstring" markdown="1">
**text** - *(str)* 贴吧plus广告描述

**url** - *(str)* 贴吧plus广告跳转链接
</div>

## Thread

主题帖信息

### 类属性

<div class="docstring" markdown="1">
**text** - *(str)* 文本内容

**contents** - *([Fragments](#fragments))* 正文内容碎片列表

**title** - *(str)* 标题

**fid** - *(int)* 标题

**fname** - *(str)* 所在贴吧名

**tid** - *(int)* 主题帖tid

**pid** - *(int)* 首楼回复pid

**user** - *([UserInfo](#userinfo))* 发布者的用户信息

**author_id** - *(int)* 发布者的user_id

**tab_id** - *(int)* 分区编号

**is_good** - *(bool)* 是否精品帖

**is_top** - *(bool)* 是否置顶帖

**is_share** - *(bool)* 是否分享帖

**is_hide** - *(bool)* 是否被屏蔽

**is_livepost** - *(bool)* 是否为置顶话题

**vote_info** - *(VoteInfo)* 投票信息

**share_origin** - *(ShareThread)* 转发来的原帖内容

**view_num** - *(int)* 浏览量

**reply_num** - *(int)* 回复数

**share_num** - *(int)* 分享数

**agree** - *(int)* 点赞数

**disagree** - *(int)* 点踩数

**create_time** - *(int)* 创建时间 10位时间戳

**last_time** - *(int)* 最后回复时间 10位时间戳
</div>

## Threads

主题帖列表

### 类属性

<div class="docstring" markdown="1">
**page** - *([Page](#page))* 页信息

**has_more** - *(bool)* 是否还有下一页

**forum** - *([BasicForum](#basicforum))* 所在吧信息

**tab_map** - *(dict[str, int])* 分区名到分区id的映射表
</div>

## Post

楼层信息

### 类属性

<div class="docstring" markdown="1">
**text** - *(str)* 文本内容

**contents** - *([Fragments](#fragments))* 正文内容碎片列表

**sign** - *(str)* 小尾巴文本内容

**comments** - *(list[[Comment](#comment)])* 楼中楼列表

**fid** - *(int)* 所在吧id

**tid** - *(int)* 所在主题帖id

**pid** - *(int)* 回复id

**user** - *([UserInfo](#userinfo))* 发布者的用户信息

**author_id** - *(int)* 发布者的user_id

**vimage** - *(VirtualImage)* 虚拟形象信息

**floor** - *(int)* 楼层数

**reply_num** - *(int)* 楼中楼数

**agree** - *(int)* 点赞数

**disagree** - *(int)* 点踩数

**create_time** - *(int)* 创建时间 10位时间戳

**is_thread_author** - *(bool)* 是否楼主
</div>

## Posts

回复列表

### 类属性

<div class="docstring" markdown="1">
**page** - *([Page](#page))* 页信息

**has_more** - *(bool)* 是否还有下一页

**forum** - *([BasicForum](#basicforum))* 所在吧信息

**thread** - *([Thread](#thread))* 所在吧信息

**has_fold** - *(bool)* 是否存在折叠楼层
</div>

## Comment

楼层信息

### 类属性

<div class="docstring" markdown="1">
**text** - *(str)* 文本内容

**contents** - *([Fragments](#fragments))* 正文内容碎片列表

**fid** - *(int)* 所在吧id

**tid** - *(int)* 所在主题帖id

**pid** - *(int)* 回复id

**user** - *([UserInfo](#userinfo))* 发布者的用户信息

**author_id** - *(int)* 发布者的user_id

**reply_to_id** - *(int)* 被回复者的user_id

**agree** - *(int)* 点赞数

**disagree** - *(int)* 点踩数

**create_time** - *(int)* 创建时间 10位时间戳
</div>

## Comments

回复列表

### 类属性

<div class="docstring" markdown="1">
**page** - *([Page](#page))* 页信息

**has_more** - *(bool)* 是否还有下一页

**forum** - *([BasicForum](#basicforum))* 所在吧信息

**thread** - *([Thread](#thread))* 所在吧信息

**post** - *([Post](#post))* 所在吧信息
</div>

