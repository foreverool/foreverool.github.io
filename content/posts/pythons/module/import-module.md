---
title: '模块的导入'
date: '2026-03-26T21:20:05+08:00'
hero: 
draft: false
description: ""
theme: Toha
tags:

menu:
  sidebar:
    name: 模块的导入
    identifier: import-module
    parent: python-module
    weight: 10
---


# python模块的导入

每一个以`.py`结尾的源文件都是一个模块。在`python`中不需要任何特殊代码或者语法来使文件成为模块。

其它模块也可以导入其它模块，导入的本质就是**载入另一个文件**，一个模块的内容都是通过其属性从而被外部世界所使用。

一个完整的`python`程序往往是由多个模块组成，其中一个模块文件被指定为主文件，或者称为顶层文件。

如果一个模块被好几个模块导入，只需要导入一次，而不需要将同一个模块导入多次。

## 模块的属性

在`python`中一切皆是对象，那么模块也应该是对象，底层也就是一个`PyObject`结构体。

```c
typedef struct {
    PyObject_HEAD
    PyObject *md_dict;    // 模块的字典（命名空间），存储所有变量
    PyModuleDef *md_def;  // 模块的定义（对于 C 扩展模块尤为重要）
    void *md_state;       // 模块的状态（用于多解释器隔离）
    PyObject *md_weakreflist; // 弱引用列表
    PyObject *md_name;    // 模块名 (__name__)
} PyModuleObject;
```

在导入模块的时候，就是在初始化这个结构体中的每一个字段。

简而言之就是一个模块的顶层的所有属性（变量，函数，类）都会放在模块的字典当中。

![image-20260326204735429](/images/posts/python/image-20260326204735429.png)

代码如下：

```python
# password.py
def hash_password(password):
    return password

class Password:
    def __init__(self, password):
        self.password = password


title = "password"
```

```python
from password import  title
class User:
    def __new__(cls, *args, **kwargs):
        print("__new__")
        instance = super().__new__(cls)
        return instance
    def __init__(self, name):
        print("__init__")
        self.name = name
        self.phone = ""
        self.email = ""
        self.password = ""
    def __str__(self):
        return "name:"+self.name + "\n" + "phone:"+self.phone + "\n" + "email:"+self.email

    def __getattr__(self, item):
        print(item,"不存在")

    def set_phone(self, phone):
        self.phone = phone

    def set_email(self, email):
        self.email = email

    def set_password(self, pwd):
        self.password = title


# top level code
topUser =User("top")
topUser.set_phone("111111111")
topUser.set_email("top@top.com")

topUser = "topuser"
print(topUser)
```

这里需要注意的是`import password`和`from password import title`的区别：

- `import`会生成`password`模块对象，并添加到模块字典中。

```python
>>> dir(user)
['User', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', 'password', 'topUser']

>>> user.password
<module 'password' from 'Z:\\projects\\python\\base-concept\\core-programming\\chapter3\\password.py'>
```

- `from password import title`，它只会将`title`对象赋值到模块字典中，至于`password`模块对象是不会被复制到字典当中的。但是这里需要注意的是，如果`password`模块对象没有被创建，那么这里会创建一个模块对象，然后放在`sys.modules`中。

## python中的包和go中的包

`go`语言通过`package`指定一个文件属于某个包。

`python`把单个文件当作一个模块或者包，那么这个包的功能很多时，单个模块文件就很大。所以可以采用`__init__.py`文件构成类似于`go`的包的概念。

```shell
network/
    ├── __init__.py
    ├── protocol.py   (存放协议逻辑)
    ├── client.py     (存放客户端逻辑)
    └── server.py     (存放服务端逻辑)
```

在`__init__.py`中拉去内容。

```python
# network/__init__.py
from .protocol import Protocol
from .client import HttpClient
from .server import HttpServer
```

然后就可以像使用模块中的属性那样使用该`包`中的内容。

```python
import network

client = network.HttpClient()  # 看起来就像 network 是一个大模块
```



