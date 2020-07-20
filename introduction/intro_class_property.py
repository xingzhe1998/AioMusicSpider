import time


data = {'key': 'value'}
value = getattr(data, 'values')
print(value())  # dict_values(['value'])
print(data.values())  # # dict_values(['value'])

'''
    getattr(object, name[, default]) -> value
    Get a named attribute from an object; getattr(x, 'y') is equivalent to x.y
'''

# getattr(self, callback.__name__)(item, msg)
# 相当于获取`callback`所代表的函数，然后用`item`和`msg`初始化此函数


class GetAttr():

    def call_back(self, url):
        print(url)

    def main(self, url):
        getattr(self, 'call_back')(url)


get_attr = GetAttr()
url = 'xxx.com'
get_attr.main(url)
