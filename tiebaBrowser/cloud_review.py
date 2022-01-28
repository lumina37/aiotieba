# -*- coding:utf-8 -*-
__all__ = ('CloudReview',)


import re
from urllib.parse import unquote

import imagehash
import pyzbar.pyzbar as pyzbar

from .logger import log
from .mysql import MySQL
from .api import Browser


class RegularExp(object):

    contact_exp = re.compile(
        '(\+|加|联系|私|找).{0,2}我|(d|滴)我|(私|s)(信|我|聊)|滴滴|di?di?', re.I)
    contact_rare_exp = re.compile('(在|看|→|👉|☞放).{0,3}(我|俺|偶).{0,3}((贴|帖)(子|里)|关注|主页|主业|资料|签名|尾巴|简介|(头|投)(像|象))|(头|投).(像|象)|主.页|(关注|主页|主业|资料|签名|尾巴|简介|(头|投)(像|象))(有|安排|上车)|威(信|辛)|v信|(\+|加|联系|了解|十|＋|私|找|伽).{0,2}(微信|威|薇|徽|微|wx|v|q|企鹅|扣扣|❤|蔻|寇|偶)|(十|＋|伽).{0,2}(我|俺|偶)|(威|薇|威|微|wx|v|企鹅|扣扣|❤|蔻|寇).{0,2}(:|：|号|楼下|签名)|q.?\d{6,11}|有意.{0,3}(s|私)|连细方式|罔址|芷|个.?性.?签.?名|簽|萜|貼|∨|Ⓥ|✙|➕|徾', re.I)

    course_exp = re.compile(
        '摄影|视频(剪辑|特效)|(绘|画|国)画|后期|CAD|素描|彩铅|板绘|设计|ps|美术|水彩|领取.{0,3}课程|英语口语|演唱|声乐|唱.{0,3}技巧|学历|备注贴吧', re.I)
    course_check_exp = re.compile(
        '交流群|课程|徒弟|素材|资料|教(程|学)|学习|邮箱|留言|扣.?1|(想|要)学|提升|小伙伴')

    app_nocheck_exp = re.compile(
        'tao寳|tb口令|(淘宝|抖音).{0,2}(号|hao)|绿色.{0,2}平台|赛事预测|【支付宝】|解封微信|扫码.{0,3}送红包|关注.{0,2}微博|语音社交|帮注册|茨|视频助手|呅|嬴|瀛|複制|收soul.?天|↓住|流亮|聊天.?有惊喜|【娛】|缅甸.{0,3}娱乐|租房神器|浮力车车|面团|口令打开淘宝', re.I)
    app_exp = re.compile(
        '拼(夕夕|多多|dd)|京(东|d)|抖音|支付宝|淘.?宝|火山小视频|微信|饿.?了.?么|美.?团|唯品会|苏宁|快手|易购|app.{0,4}下载|双(11|十一)|语音平台|起点读书|需要.{0,2}app', re.I)
    app_check_exp = re.compile(
        '点一下|点赞|任务|复制|账号|绿色|开店|店铺|运营|搜|红.?包|福利|推广|聘|免费|(广告|精准)投放|活动|助力|特价|邀请码|佣.?金|变现')

    business_exp = re.compile(
        '[^\d]1[345789]\d{9}[^\d]|(高仿|复刻|购).{0,3}(鞋|包|表)|鞋文化|潮.{0,2}鞋|呺|核雕|莆田|工厂直供|品质保证|免费鉴定|价格美丽|潮牌复刻|奢潮|本店主营|(实惠|羊毛).*群|撸货|线报|厂家货源|助力微商|#后期#.*做熟悉|绿色正规行业|价格可谈|金钱自由|零售商|网赌|火爆招商|对接工厂|实拍区别|臻情|钜献|火热预约|电子商务|有限公司|公司.{0,2}注册|蓷|廣|教育品牌|引流招商|自主研发|全国客服电话|回馈客户|可接定制|培训辅导|(投放).{0,2}广|高(转化|收益)|借贷|朋友推荐.*产品|区块链|进裙|福利.*进群|华强北|AirPods|玻尿酸', re.I)

    job_nocheck_exp = re.compile(
        '成立工作室|想做单|宝妈[^妈]|(跟着|动手指).{0,2}赚钱|免费入职|(招|收).{0,4}(临时工|徒|代理)|(在家|轻松).{0,2}(可|能|没事).?做|时间自由|煎直|兼耳只|勉费|上迁.*没问题|不收.?任何费用|包食宿|vx辅助|闲时无聊|坚持.*日入过|赚米|语音聊天|一对一直播|有想.*的(朋友|兄弟)|包学会|包分配|工作(轻松|简单)|不收(米|钱)|名额有限|在家.{0,4}操作|转发朋友圈|手工活|号商|(刷|做)(单|销量)', re.I)
    job_exp = re.compile(
        '佣金|押金|会费|培训|结算|(日|立)(结|洁)|高佣|餐补|想做的|有兴趣|(急|长期|大量)招|招(募|聘)|稳赚|(一|每)(天|日|月)\d{2,3}|(日|月)(入|进).{0,2}(元|块|百|佰|万|千|w)|(利润|收益|工资|薪资|收入|福利|待遇)(高|好|\d{3,})|(高|好)(利润|收益|工资|薪资|收入|福利|待遇)|低(风险|投入)|风险低|正规合法|合作愉快|手机.*就(行|可)|(有|一).?手机|扶持|长期单', re.I)
    job_check_exp = re.compile(
        '(暑假|临时|短期)工|合伙|兼职|主播|声播|签约|艺人|模特|陪玩|试音|播音|写手|点赞员|接单|工作室|工厂|手工|项目|电商|游泳健身|有声(读物|书)|创业|自媒体|加盟|副业|代理|(免费|需要|诚信|诚心)(带|做)|想(赚|挣)钱|不甘.?现状|微商|微信|投资|写好评|不嫌少|需工作|形象好|气质佳|赢.{0,2}奖金')

    game_nocheck_exp = re.compile(
        '(招|找).{0,4}(托|拖|内部|人员|体验员)|(狗|手游|游戏|内部).?(托|拖|脱|资格|号)|(托|拖|脱)(裙|群)|进游(有|给)|上线就送|来人体验|刺激玩家消费|(走心|手游|本吧|本帖|本贴).{0,2}推荐|体验氪金大佬|等级直接调|(真实|有效)(冲|充)值|(等级|线下)扶持|茗额|游推荐|特权礼包|新区.{0,2}开|霸服|喜欢玩.*仙侠|(日|天|送|领|给你|免费).{0,2}(648|元宝)|手游.{0,2}(招|爱好者)|大.?不.?同.{1,4}网|官网.{1,7}变态|手游官网|B（版）T（本）|dbt.?apk|B-T版本|в|(当|做)游戏主播|来就.{0,2}送|蝣|遊|戲|號|侗|皮肤最新获取|鎹|區|輑|避免玩家流失')
    game_exp = re.compile('手游|游戏|玩家|仙侠|国战|新区')
    game_check_exp = re.compile(
        '神豪|托|演员|充值|试玩|内玩|限时|速来|体验|开服|内测|资源|福利|每天都有|推广|关注下|内部号|扶持|嘴严|追杀|特权礼包')

    name_nocheck_exp = re.compile(
        '魸|莆田|^恋魂.{2,3}🔥$|^轰炸(软件|机)|老司机看片|导航|引流|推广|赚钱|手游|(提|变)现|推广|电商|平台|签名|(头|投)(像|象)|(主|煮)页|资(源|料)')
    name_exp = re.compile('😍|☜|☞|💌|💋')
    name_check_exp = re.compile('wx|\d{6,}|企鹅')

    maipian_exp = re.compile(
        '(下|↓).{0,3}有惊喜|浮力车|网红.{0,3}作品|成人看的|那边那谁20|免費|宅.{0,5}度娘|[𝟙-𝟡]|仓井空在等尼|小情侣|注意身体|明艳动人的小姐姐|推荐.{0,3}资源|回复.*:你(帖|贴).*可以看|自己上微.?薄|自己.*捜|都有.*看我关注的人|范 做|看偏神器|学姐给我吃|推荐发展对象|^麦片$|卖淫|嫂子直接.*那个|小哥哥们.*看我|进去.*弄得喷水|(看|有)女神|噜.?个月|肾不好|箹|〖.〗|诚人|28.ME|湖北厕所|\.xyz')
    female_check_exp = re.compile(
        '9\d年|(盆|朋|交|处).?友|有人聊|聊天|表姐|老娘|好孤单|单身|睡不着|恋爱|爱会消失|爱情|对象|奔现|网恋|亲密|约会|(超|甜)甜|干点啥|对我做|无聊|手牵手|我的b|被你骑|(約|悦)炮|小gg|勾搭|(大|小)可爱|憋疯了|认识一下|我.?有趣|呆在家里|带个人回家|相个?亲|认真处|真心|性感|希望遇到|嫁不出去|大叔|越来越懒|可悦|签收|手纸|内衣|陪我|发泄|身材|婚|我都有|的我')

    hospital_exp = re.compile('医院.*好不好|狐臭|痔疮|性腺|阳痿|早泄|不孕不育|前列腺|妇科|会所|手相')

    lv1_exp = re.compile(
        '公众号|传媒|新媒体|婚恋|财经|鱼胶|信︄用卡|看手相|出租|塔罗|代骂|消灾|问卷调查|有意者|(邪|手)淫.{0,3}危害|急需.{0,10}钱|(免费|资源)分享|懂(的|得)来|代练|我发表了一篇图片')

    kill_thread_exp = re.compile('地祉|特价版', re.I)


class CloudReview(Browser):
    """
    云审查基类
    CloudReview(BDUSS_key,tieba_name,sleep_time=0)

    参数:
        BDUSS_key: str 用于获取BDUSS
        tieba_name: str 贴吧名
        sleep_time: float 每两次云审查的间隔时间
    """

    __slots__ = ['tieba_name',
                 'sleep_time',
                 'exp',
                 'mysql']

    def __init__(self, BDUSS_key, tieba_name, sleep_time=0):
        super().__init__(BDUSS_key)

        self.tieba_name = tieba_name
        self.sleep_time = sleep_time

        self.mysql = MySQL()

        self.exp = RegularExp()

    def close(self):
        self.mysql.close()
        super().close()

    def update_user_id(self, id, mode=True):
        """
        向名单中插入user_id
        update_user_id(id,mode=True)
        """

        if type(mode) != bool:
            log.warning("Wrong mode in update_user_id!")
            return False

        user = UserInfo(id)
        user = self.get_userinfo_weak(user)
        if not user.user_id:
            return False

        return self.mysql.update_user_id(self.tieba_name, user.user_id, mode)

    def del_user_id(self, id=None):
        """
        从名单中删除user_id
        del_user_id(id=None)
        """

        user = UserInfo(id)
        user = self.get_userinfo_weak(user)
        if not user.user_id:
            return False

        return self.mysql.del_user_id(self.tieba_name, user.user_id)

    def scan_QRcode(self, img_url):
        """
        扫描img_url对应图像中的二维码
        """

        try:
            image = self.url2image(img_url)
            if image:
                raw = pyzbar.decode(image)
                data = unquote(raw[0].data.decode('utf-8')) if raw else None
        except Exception as err:
            log.error(f"Failed to decode image. reason:{err}")
            data = None

        return data

    def has_img_hash(self, img_url):
        """
        判断img_url对应的图像的dhash是否在黑名单中
        """

        image = self.url2image(img_url)
        if image:
            img_hash = imagehash.dhash(image)
            if self.mysql.has_img_hash(self.tieba_name, img_hash):
                return True
            else:
                return False
        else:
            return False
