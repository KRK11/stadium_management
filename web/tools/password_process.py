'''
**************************************************
@File   ：stadium_management -> password_process
@IDE    ：PyCharm
@Author ：TheOnlyMan
@Date   ：2022/11/25 16:09
**************************************************
'''

mod1 = int(1333333333333333331)
mod2 = int(1) << 64

def get_hash(password):
    hash = int(0)
    for i in password:
        hash = (hash * mod1 + ord(i)) % mod2
    return str(hash)


def test_equal(password:str, hash_password:str):
    return get_hash(password) == hash_password
