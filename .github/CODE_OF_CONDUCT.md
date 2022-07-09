# 开发规范

## 格式规范

+ 本项目所使用的格式化工具为[`black`](https://github.com/psf/black)

```bash
pip install black
```

+ `black`命令行配置参数如下

```bash
--line-length 120 --skip-string-normalization
```

## 开发环境推荐（可选）

+ IDE: [`VSCode`](https://code.visualstudio.com/)

+ VSCode Plugin - Language Support: [`Python`](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
  
+ VSCode Plugin - Language Server: [`Pylance`](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)

+ Linting: [`flake8`](https://github.com/PyCQA/flake8)

+ `flake8`命令行配置参数如下

```bash
--max-line-length=120 --ignore=E402,E203,E501,W503
```
