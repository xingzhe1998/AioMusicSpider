class IterGetDict:

    @staticmethod
    def dict_get(upload_dict, objkey, default):
        if objkey in upload_dict.keys():
            return upload_dict[objkey]
        else:
            for key, val in upload_dict.items():
                if type(val).__name__ == "dict":
                    upload_dict = val
                    res = IterGetDict.dict_get(upload_dict, objkey, default)
                    if not res == default:
                        return res
            else:
                return default


# it = IterGetDict()
# d = {'s1':{'s2':{'s3': 'data'}}}
# res1 = it.dict_get(d, 's3', 'default')
# res2 = it.dict_get(d, 's4', 'default')
# print(res1, res2)
