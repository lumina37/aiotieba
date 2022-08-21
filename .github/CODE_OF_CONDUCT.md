# 开发规范

## 格式规范

+ 本项目所使用的格式化工具为[`black`](https://github.com/psf/black)

```bash
pip install black
```

+ 配置`black`命令行参数，或使用`pyproject.toml`中的配置

```bash
--line-length 120 --skip-string-normalization
```

## 开发环境推荐（可选）

+ IDE: [`VSCode`](https://code.visualstudio.com/)

+ VSCode Plugin - Language Support: [`Python`](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
  
+ VSCode Plugin - Language Server: [`Pylance`](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)

+ Linting: [`flake8`](https://github.com/PyCQA/flake8)

+ 配置`flake8`命令行参数，或使用`pyproject.toml`中的配置

```bash
--max-line-length=120 --ignore=E402,E203,E501,W503
```
