import dataclasses as dcs
import hashlib
import secrets
from functools import cached_property

from Crypto.Cipher import AES

from ..helper.crypto import c3_aid, cuid_galaxy2


@dcs.dataclass
class Account:
    """
    贴吧的用户信息容器

    Args:
        BDUSS (str, optional): BDUSS. Defaults to ''.
        STOKEN (str, optional): 网页STOKEN. Defaults to ''.

    Attributes:
        BDUSS (str): BDUSS
        STOKEN (str): 网页STOKEN
        tbs (str): 长度为26的小写16进制字符串 例:91be894d01799c4991be894d01
        android_id (str): 长度为16的小写16进制字符串 包含8字节信息 例:91be894d01799c49
        uuid (str): 包含16字节信息 例:e4200716-58a8-4170-af15-ea7edeb8e513
        client_id (str): 例:wappc_1653660000000_123
        sample_id (str): 例:104505_3-105324_2-...-107269_1
        cuid (str): 例:baidutiebaappe4200716-58a8-4170-af15-ea7edeb8e513
        cuid_galaxy2 (str): 例:A3ED2D7B9CFC28E8934A3FBD3A9579C7|VZ5FKB5XS
        c3_aid (str): 例:A00-ZNU3O3EP74D727LMQY745CZSGZQJQZGP-3JXCKC7X
        z_id (str): z_id
        aes_ecb_sec_key (bytes): 供贴吧AES-ECB加密使用的随机密码 长度为31字节
        aes_ecb_chiper (Any): AES-ECB加密器
        aes_cbc_sec_key (bytes): 供贴吧AES-CBC加密使用的随机密码 长度为16字节
        aes_cbc_chiper (Any): AES-CBC加密器
    """

    BDUSS: str = ''
    STOKEN: str = ''

    tbs: str = ''
    client_id: str = ''
    sample_id: str = ''
    z_id: str = ''

    def __init__(self, BDUSS: str = '', STOKEN: str = '') -> None:
        if BDUSS and len(BDUSS) != 192:
            raise ValueError(f"BDUSS的长度应为192个字符 而输入的{BDUSS}有{len(BDUSS)}个字符")
        self.BDUSS = BDUSS

        if STOKEN and len(STOKEN) != 64:
            raise ValueError(f"STOKEN的长度应为64个字符 而输入的{STOKEN}有{len(STOKEN)}个字符")
        self.STOKEN = STOKEN

    @cached_property
    def android_id(self) -> str:
        android_id = secrets.token_hex(8)
        return android_id

    @cached_property
    def uuid(self) -> str:
        import uuid

        uuid_ = str(uuid.uuid4())
        return uuid_

    @cached_property
    def cuid(self) -> str:
        cuid = "baidutiebaapp" + self.uuid
        return cuid

    @cached_property
    def cuid_galaxy2(self) -> str:
        cuid_galaxy2_ = cuid_galaxy2(self.android_id)
        return cuid_galaxy2_

    @cached_property
    def c3_aid(self) -> str:
        c3_aid_ = c3_aid(self.android_id, self.uuid)
        return c3_aid_

    @cached_property
    def aes_ecb_sec_key(self) -> bytes:
        aes_ecb_sec_key = secrets.token_bytes(31)
        return aes_ecb_sec_key

    @cached_property
    def aes_ecb_chiper(self):
        salt = b'\xa4\x0b\xc8\x34\xd6\x95\xf3\x13'
        ws_secret_key = hashlib.pbkdf2_hmac('sha1', self.aes_ecb_sec_key, salt, 5, 32)
        aes_ecb_chiper = AES.new(ws_secret_key, AES.MODE_ECB)
        return aes_ecb_chiper

    @cached_property
    def aes_cbc_sec_key(self) -> bytes:
        aes_cbc_sec_key = secrets.token_bytes(16)
        return aes_cbc_sec_key

    @cached_property
    def aes_cbc_chiper(self):
        aes_cbc_chiper = AES.new(self.aes_cbc_sec_key, AES.MODE_CBC, iv=b'\x00' * 16)
        return aes_cbc_chiper
