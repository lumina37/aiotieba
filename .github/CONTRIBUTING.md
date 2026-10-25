# 开发规范

## commit规范

提交信息须遵循简化版的[Conventional Commits](https://www.conventionalcommits.org/zh-hans/)，格式为 `<type>: <description>`。

| 类型 | 说明 |
| ------ | ------ |
| `feat` | 新功能 |
| `fix` | Bug修复 |
| `refactor` | 重构（既非新功能也非修复） |
| `perf` | 性能优化 |
| `chore` | 日常维护（依赖更新、脚本改进等） |
| `docs` | 文档变更 |
| `test` | 测试相关 |
| `style` | 代码格式（不影响逻辑的空白、缩进等） |
| `ci` | CI/CD 配置变更 |

外部PR和commit须向develop分支而不是master分支提交

## 代码风格

- Python代码风格遵循`ruff.toml`，C代码风格遵循`.clang-format`
- 除`__init__.py`、`const.py`、`typing.py`等纯声明模块外，文件首行写`from __future__ import annotations`；公开函数、方法与数据类字段均需类型标注，仅用于标注的导入放入`if TYPE_CHECKING:`块
- 注释与文档使用中文，JSON解析统一用`parse_json`、序列化优先用`pack_json`，以兼容orjson
- API的数据类统一放在`_classdef.py`并由`dataclass`装饰；优先组合，尽量不使用多级继承，字段集合不同的场景单独建模，顶层容器继承`TbErrorExt`
- 数据类优先通过静态方法构造（`from_json`、`from_proto`，返回`Self`），不把多种初始化方式塞进`__init__`
- 构造数据类实例时尽量只使用位置参数（实参为单一变量，不写表达式），避免关键字传参
- 数据类字段尽量不用`None`做默认值，保证用户取到的字段始终有效；API返回时所有字段都应被赋值，未赋值的字段从类定义中删除
- 非布尔返回值尽量先赋给局部变量再`return`，便于断点观察；布尔值可直接返回
- 解析回包时只考虑正常情况：不做多余的类型转换、`.get`兜底、不可达的`raise`或条件判断，其余异常交给`@handle_exception`兜底
- `api/*/_api.py`的内部函数（`pack_*`、`request`、`parse_body`）不写docstring，文档写在`Client`的公开方法上

## 命名约定

| 类型 | 约定 | 示例 |
| ------ | ------ | ------ |
| 类名 | PascalCase | `Client` |
| 函数/方法 | snake_case | `pack_proto` |
| 常量 | UPPER_CASE | `APP_SALT` |

## 异常处理规范

- 使用`@handle_exception(ResponseType)`装饰器捕获API调用过程抛出的所有异常。`ResponseType`必须继承自`TbErrorExt`

示例：

```python
@handle_exception(Threads)
async def get_threads(self, fname_or_fid: str | int, ...) -> Threads:
    ...
```

- 使用`raise Exception from another_err`的方式确保异常链可回溯
- 在服务端返回非0错误码或非预期的http码时，将对应的错误码和错误描述打包进`TiebaServerError(code, msg)`并抛出
- 在解析得到非预期的值时，将对应的错误值和错误描述打包进`TiebaValueError(val, msg)`并抛出

## 文档更新规范

- 变更API时需同步更新对应的`docs/ref/classdef/*.md`
- API方法的文档遵循现有docstring格式

docstring示例：
```text
"""
方法功能简述

Args:
    参数名 (参数类型): 参数含义

Returns:
    返回值类型: 返回值含义

Note:
    可选的补充说明
"""
```

## 测试编写规范

- 使用`client`入参捕获fixture，不要在测试内自行构造`Client`
- 涉及网络IO的测试需使用`@pytest.mark.flaky(reruns=2, reruns_delay=5.0)`抑制偶发错误

## 新增API时的检查清单

- [ ] 在`src/aiotieba/api/`中创建新的API模块包
- [ ] 在`src/aiotieba/client.py`中添加公开方法，使用`@handle_exception`+可选的`@_try_websocket`或`@_force_websocket` 装饰
- [ ] 在`src/aiotieba/client.py`顶部的import中导入新API模块
- [ ] 如有新的protobuf定义，运行`python scripts/proto_compile.py`编译
- [ ] 如有新的数据类型定义，添加到`src/aiotieba/api/<mod>/_classdef.py`
- [ ] 如有新的数据类型定义，创建`docs/ref/classdef/<name>.md`并添加到`mkdocs.yml`的navigate列表末尾
- [ ] 如有新的枚举类型，添加到 `src/aiotieba/enums.py`
- [ ] 运行`uvx ruff check .`和`uvx ruff format . --check`执行代码检查
