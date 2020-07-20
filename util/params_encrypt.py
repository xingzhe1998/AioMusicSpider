import hashlib


class ParamsEncrypt:

    @staticmethod
    def get_sign(*args, **kwargs):
        query = kwargs.pop("query")
        _url = kwargs.pop("_url")
        xm_sg_tk = kwargs.pop("xm_sg_tk")
        prefix_string = ''.join([xm_sg_tk.split('_')[0], '_xmMain_']) + _url + '_' + query
        encrypt_params = bytes(prefix_string, encoding='utf-8')
        m = hashlib.md5()
        m.update(encrypt_params)
        return m.hexdigest()
