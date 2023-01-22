import aiohttp

CHECK_URL_PERFIX = "http://tieba.baidu.com/mo/q/checkurl?url="

APP_SECURE_SCHEME = "https"
APP_INSECURE_SCHEME = "http"

DEFAULT_TIMEOUT = aiohttp.ClientTimeout(connect=3.0, sock_read=12.0, sock_connect=4.0)
