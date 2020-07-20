from functools import wraps
import time
from datetime import datetime


def singal_wrap(func):
    @wraps(func)
    def __start(*args, **kwargs):
        print(f"{func.__name__} is run")
        func(*args, **kwargs)
    return __start


@singal_wrap
def wrapped():
    a = b = 1
    print(f"result is {a+b}")


#### 高阶函数
def foo():
    print('this is foo')


def test(func):
    start_time = time.time()
    func()
    end_time = time.time()
    print('foo cost %s' % (start_time-end_time))
    return func


#### 函数嵌套
def father():
    def son():
        def grandson():
            x = y = 1
            return x + y
        return grandson()
    return son()


#### 闭包
def make_filter(keep):
    def the_filter(file_name):
        file = open(file_name)
        lines = file.readlines()
        file.close()
        filter_doc = [i for i in lines if keep in i]
        return filter_doc
    return the_filter


#### 装饰器实现用户登录
def login_required(func):
    def wrap(*args, **kwargs):
        username = input('请输入用户名:').strip()
        passwd = input('请输入密码:').strip()
        print('正在验证...')
        if username == 'xyz' and passwd == '123':
            res = func(*args, **kwargs)
            print('验证成功')
            return res
        else:
            print('验证失败')
            return "请检查用户名或密码"
    return wrap


# login = login_required(login) = wrap
@login_required
def login(username):
    now = int(time.time())
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    result = f"{otherStyleTime} 用户{username}登录"
    return result


if __name__ == '__main__':
    wrapped()
    print(wrapped.__name__)

    foo = test(foo)
    foo()

    print(father())

    the_filter = make_filter("pass")
    filter_result = the_filter("result.txt")
    print(filter_result)

    res = login('xyz')
    print(res)
    print(login.__name__)  # wrap
