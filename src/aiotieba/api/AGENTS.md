# API模块规范

每个API对应一个独立的Python包，统一遵循以下规范：

## 目录结构规范

```text
api/<api_name>/
├── __init__.py     # 导出函数与数据类型
├── _api.py         # 实现请求打包（pack_xx）、发包（request_xx）与回包解析（parse_body）
├── _classdef.py    # API的专用数据类型
└── protobuf/       # API的专用protobuf定义
```

## `_api.py`规范

- 每个`_api.py`必须导出`request_xx`函数以供`Client`中的入口方法调用
- 对于可以走websocket协议的API，必须定义protobuf相关的`pack_proto`函数，并导出`request_http`和`request_ws`两个请求方法

## `_classdef.py`规范

- 所有数据类通过静态构造方法`from_proto(data)`或`from_json(data)`，根据传入的回包数据构造
- 尽可能避免使用继承，优先考虑组合
- 如果两个类的有效字段不完全相同，则必须针对两种场景单独定义数据类型，尽可能避免为了覆盖多种场景去使用通用的超大类
- API调用返回时，所有类成员变量都应当被赋值，未被赋值的字段应从类定义中移除
- 顶层容器（如`Threads`）需继承`TbErrorExt`以获得用于存放运行时异常的`.err`属性
- API专用的类型应使用与API名称相关联的后缀如`_t`、`_st`以避免命名冲突
