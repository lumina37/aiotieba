# API模块规范

每个API对应一个独立的Python包，统一遵循以下规范
完整的代码风格要求参阅`.github/CONTRIBUTING.md`的“代码风格”一节，本文件只摘录并补充与API模块相关的部分

## 目录结构规范

```text
api/<api_name>/
├── __init__.py     # 导出函数与数据类型
├── _api.py         # 实现请求打包（pack_xx）、发包（request_xx）与回包解析（parse_body）
├── _classdef.py    # API的专用数据类型
└── protobuf/       # API的专用protobuf定义
```

## 通用代码风格

- Python代码风格遵循项目根目录的`ruff.toml`
- 除`__init__.py`等纯声明模块外，文件首行写`from __future__ import annotations`
- 公开函数、方法与数据类字段均需类型标注，仅用于标注的导入放入`if TYPE_CHECKING:`块
- 注释与文档使用中文；JSON解析统一用`parse_json`、序列化优先用`pack_json`，以兼容orjson
- 非布尔返回值尽量先赋给局部变量再`return`，便于断点观察；布尔值可直接返回

## `_api.py`规范

- 每个`_api.py`必须导出`request_xx`函数以供`Client`中的入口方法调用
- 对于可以走websocket协议的API，必须定义protobuf相关的`pack_proto`函数，并导出`request_http`和`request_ws`两个请求方法
- `pack_*`、`request_http`/`request_ws`、`parse_body`等内部函数不写docstring，文档写在`Client`的公开方法上
- 解析回包（`parse_body`与`from_proto`/`from_json`）时只考虑正常情况：不做多余的类型转换、`.get`兜底、不可达的`raise`或条件判断，其余异常交给`@handle_exception`兜底

## `_classdef.py`规范

- 所有数据类统一放在`_classdef.py`并由`dataclass`装饰
- 数据类优先通过静态构造方法`from_proto(data)`或`from_json(data)`建立，返回`Self`，不把多种初始化方式塞进`__init__`
- 构造数据类实例时尽量只使用位置参数（实参为单一变量，不写表达式），避免关键字传参
- 数据类字段尽量不用`None`做默认值，保证用户取到的字段始终有效
- 避免使用继承，优先考虑组合，尽量不使用多级继承
- 如果两个类的有效字段不完全相同，则必须针对两种场景单独定义数据类型，尽可能避免为了覆盖多种场景去使用通用的超大类
- API调用返回时，所有类成员变量都应当被赋值，未被赋值的字段应从类定义中移除
- 顶层容器（如`Threads`）需继承`TbErrorExt`以获得用于存放运行时异常的`.err`属性
- API专用的类型应使用与API名称相关联的后缀如`_t`、`_st`以避免命名冲突
