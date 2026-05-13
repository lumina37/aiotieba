# aiotieba开发指南

本文档旨在帮助开发者快速了解项目结构，以便参与aiotieba的开发

## 项目概述

aiotieba是一个使用Python编写的百度贴吧API集合库

## 目录结构

```text
aiotieba/
├── src/aiotieba/               # 源代码
│   ├── client.py               # Client类（所有api的调用入口）
│   ├── config.py               # ProxyConfig / TimeoutConfig 配置数据类
│   ├── const.py                # 版本号等常量
│   ├── enums.py                # 所有枚举类型
│   ├── exception.py            # 异常包装
│   ├── logging.py              # 日志系统
│   ├── typing.py               # 类型别名
│   ├── __version__.py          # 版本号
│   ├── api/                    # 多个API模块，每个自成一个子包
│   │   ├── _classdef/          # 通用数据类型（UserInfo等）
│   │   ├── _protobuf/          # 通用protobuf定义
│   │   └── get_xx...           # 各个API模块
│   ├── core/                   # 网络会话类
│   │   ├── account.py          # Account类（存放与用户信息相关的不变量）
│   │   ├── net.py              # NetCore（连接池、代理与超时配置）
│   │   ├── http.py             # HttpCore（http会话）
│   │   ├── websocket.py        # WsCore（websocket会话）
│   │   └── blcp.py             # BLCPCore（BLCP私有协议会话）
│   └── helper/                 # 内部辅助工具
│       ├── utils.py            # 实用方法
│       ├── cache.py            # 吧名↔fid的双向缓存
│       └── crypto/             # 密码学 C 扩展
│           ├── CMakeLists.txt  # C扩展构建
│           └── src/            # C扩展源码
├── tests/                      # pytest单元测试
│   ├── conftest.py             # Client fixture（需要TB_BDUSS和TB_STOKEN环境变量）
│   └── test_xx.py              # 各API的单元测试
├── docs/                       # mkdocs文档源文件
│   ├── tutorial/               # 教程
│   └── ref/                    # 参考文档
│       └── classdef/           # 各API相关的数据类型文档
├── scripts/
│   └── proto_compile.py        # Protobuf一键编译脚本
├── pyproject.toml              # 项目元数据与依赖项
├── CMakeLists.txt              # 辅助scikit-build-core生成C扩展
├── mkdocs.yml                  # MkDocs文档配置
└── README.md                   # 项目介绍
```

## 核心概念

### 术语定义

| 术语 | 说明 |
| ------ | ------ |
| **BDUSS** | 192字符的用户身份认证token |
| **STOKEN** | 64字符的额外token，部分API需要 |
| **fid** | 吧数字ID |
| **fname** | 吧名称 |
| **tid** | 主题帖数字ID |
| **pid** | 回复帖数字ID |
| **user_name** | 用户名（下面四项用户标识均为全局唯一） |
| **portrait** | 用户头像标识（如`tb.0.xxx`） |
| **user_id** | 旧版用户数字ID |
| **tieba_uid** | 新版用户主页数字ID |

### 核心状态容器

1. **`Client`**：主客户端类，封装所有贴吧API的入口
2. **`Account`**：BDUSS等用户身份相关token的容器
3. **`NetCore`**：管理TCP连接池。同时保存代理、超时等配置信息
4. **`HttpCore`**：HTTP的会话状态容器
5. **`WsCore`**：WebSocket的会话状态容器
6. **`BLCPCore`**：百度直播聊天协议的会话状态容器

### 数据流概览

```text
用户调用 Client.get_threads("天堂鸡汤")
    │
    ├── @handle_exception(Threads) 装饰器（异常捕获 + 日志）
    ├── @_try_websocket 装饰器（优先 WebSocket，失败降级 HTTP）
    │
    ├── WebSocket 路径:
    │   ├── pack_proto() → 构造请求
    │   ├── WsCore.send(data, cmd=301001) → 加密+压缩+发送
    │   └── parse_body() → 解析响应
    │
    └── HTTP 路径:
        ├── pack_proto() → 构造请求
        ├── HttpCore.pack_proto_request() → 签名+multipart打包
        └── parse_body() → 解析响应
```

## API模块规范

参阅`src/aiotieba/api/AGENTS.md`

## 开发规范

参阅`.github/CONTRIBUTING.md`

## 可用的skills

可用的skills位于`skills`目录下
