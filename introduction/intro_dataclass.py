from dataclasses import dataclass
from dataclasses import field
from typing import Optional
import aioredis


'''
合理使用dataclass将会大大减轻开发中的负担，将我们从大量的重复劳动中解放出来，这既是dataclass的魅力，
不过魅力的背后也总是有陷阱相伴，最后我想提几点注意事项： - dataclass通常情况下是unhashable的，
因为默认生成的`__hash__`是`None`，所以不能用来做字典的key，如果有这种需求，那么应该指定你的数据类为
frozen dataclass - 小心当你定义了和`dataclass`生成的同名方法时会引发的问题 - 当使用可变类型（如list）时，
应该考虑使用`field`的`default_factory` - 数据类的属性都是公开的，如果你有属性只需要初始化时使用而不需要在
其他时候被访问，请使用`dataclasses.InitVar`只要避开这些陷阱，dataclass一定能成为提高生产力的利器。'''

# dataclass原型如下
# dataclasses.dataclass(*, init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False)
# dataclass装饰器将根据类属性生成数据类和数据类需要的方法。
@dataclass
class Lang:
    """a dataclass that describes a programming language"""
    name: str = 'python'
    strong_type: bool = True
    static_type: bool = False
    age: int = 28

pyl = Lang()
print(pyl)
# Lang(name='python', strong_type=True, static_type=False, age=28)
jsl = Lang('js', False, False, 23)
print(jsl)
# Lang(name='js', strong_type=False, static_type=False, age=23)


@dataclass
class C:
    a: int
    b: int
    c: int = field(init=False)

    def __post_init__(self):
        self.c = self.a + self.b

'''init参数如果设置为False，表示不为这个field生成初始化操作，dataclass提供了hook——
__post_init__供我们利用这一特性：
__post_init__在__init__后被调用，我们可以在这里`初始化那些需要前置条件的field`。'''
cc = C(a=1, b=2)
print(cc)  # C(a=1, b=2, c=3)
print(cc.c)  # 3


@dataclass
class AioRedis:
    session_flag: bool = False
    redis_client: Optional[aioredis.create_redis_pool] = None

# redis_client: Optional[aioredis.create_redis_pool] = None
# 变量名: 理想变量类型(此处是`Optional`可选择的类型) = 默认值
aio_redis = AioRedis()
print(aio_redis)
# AioRedis(session_flag=False, redis_client=None)
