from functools import wraps


def multi_wrap(**kwargs):

    flag = kwargs.pop('flag')
    print(f"flag is {flag}")

    def start(func):
        # @wraps(func)
        def __start(*args, **kwargs):
            print(f"{func.__name__} is run")
            func(*args, **kwargs)
        return __start
    return start


'''
wrapped = multi_wrap(flag=True)(wrapped())

step1:
    multi_wrap(flag=True) -> start

step2:
    @start
    def wrapped():
        a = b = 1
        print(f"result is {a+b}")

step3:
    start(wrapped()) -> __start

fin:
    wrapped -> __start
'''
@multi_wrap(flag=True)
def wrapped():
    a = b = 1
    print(f"result is {a+b}")


if __name__ == '__main__':
    wrapped()
    print(wrapped.__name__)
