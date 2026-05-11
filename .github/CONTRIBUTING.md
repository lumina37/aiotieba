
# 开发规范

## 代码风格

- Python代码风格遵循`ruff.toml`
- C代码风格遵循`.clang-format`

## 命名约定

| 类型 | 约定 | 示例 |
| ------ | ------ | ------ |
| 类名 | PascalCase | `Client` |
| 函数/方法 | snake_case | `pack_proto` |
| 常量 | UPPER_CASE | `APP_SALT` |

## 异常处理规范

- 使用`@handle_exception(ResponseType)`装饰器捕获所有异常。`ResponseType`必须继承自`TbErrorExt`

示例

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
- 涉及网络IO的测试需使用`@pytest.mark.flaky(reruns=2, reruns_delay=5.0)`抑制网络抖动

## 新增API时的检查清单

- [ ] 在 `src/aiotieba/api/`中创建新的API模块包
- [ ] 在 `src/aiotieba/client.py` 中添加公开方法，使用`@handle_exception`+可选的`@_try_websocket`或`@_force_websocket` 装饰
- [ ] 在`src/aiotieba/client.py`顶部的import中导入新API模块
- [ ] 如有新的protobuf定义，运行`python scripts/proto_compile.py`编译
- [ ] 如有新的数据类型定义，添加到`src/aiotieba/api/<mod>/_classdef.py`
- [ ] 如有新的数据类型定义，创建`docs/ref/classdef/<name>.md`并添加到`mkdocs.yml`的navigate列表末尾
- [ ] 如有新的枚举类型，添加到 `src/aiotieba/enums.py`
- [ ] 运行`uvx ruff check .`和`uvx ruff format . --check`对应的代码检查
