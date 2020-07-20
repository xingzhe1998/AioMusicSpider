import msgpack
from aio_pika import Message

msg = {'msg': 'intro_aio_pika'}

# dd = msgpack.dumps(d)
# ld = msgpack.loads(dd)
# print(dd, ld)
# b'\x81\xa1a\x01' {'a': 1}

task = msgpack.packb(msg)
# packb方法是对数据进行打包，类似于json.dumps()方法，一般用于数据推入队列时进行的操作
# unpackb方法对数据进行解包，类似于json.dumps()方法，一般用于数据推出队列时进行的操作
res = Message(task)
print(res.body)  # b'\x81\xa3msg\xaeintro_aio_pika'
