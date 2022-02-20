# -*- coding: utf8 -*-

from base64 import b64encode
import logging
import re
from time import time
from sys import exit

import requests
import rsa

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def main(*args):
    __username = r"19139313130"
    __password = r"QazPlm666...TYYP"
    session = login(__username, __password)
    rand = str(round(time() * 1000))
    surl = f"https://api.cloud.189.cn/mkt/userSign.action?rand={rand}&clientType=TELEANDROID&version=8.6.3&model=SM-G930K"
    url1 = f"https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN&activityId=ACT_SIGNIN"
    url2 = f"https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN_PHOTOS&activityId=ACT_SIGNIN"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clientId/355325117317828 clientModel/SM-G930K imsi/460071114317824 clientChannelId/qq proVersion/1.0.6",
        "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
        "Host": "m.cloud.189.cn",
        "Accept-Encoding": "gzip, deflate",
    }

    # 签到
    signResp = session.get(surl, headers=headers, timeout=10).json()
    netdiskBonus = signResp["netdiskBonus"]
    signMsg = (
        f"还未签到, 签到获得 {netdiskBonus}M 空间...\n"
        if signResp["isSign"] == "false"
        else f"已经签到过了, 签到获得 {netdiskBonus}M 空间..."
    )
    logger.info(signMsg)

    # 两次抽奖
    for index, url in enumerate((url1, url2), 1):
        lotteryResp = session.get(url, headers=headers, timeout=10)
        html = lotteryResp.text
        if "errorCode" in html:
            if "User_Not_Chance" in html:
                logger.info("今天已经抽过奖了, 抽奖次数不足...")
            elif "InternalError" in html:
                logger.info("内部错误, 可能是活动下线...")
            else:
                logger.info(f"第{index}次抽奖出错...\n" + html)
        else:
            try:
                description = lotteryResp.json()["description"]
            except:
                description = "未知"
            logger.info(f"抽奖获得 {description}...")


BI_RM = list("0123456789abcdefghijklmnopqrstuvwxyz")
b64map = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


def int2char(a):
    return BI_RM[a]


def b64tohex(a):
    d = ""
    e = 0
    c = 0
    for i in range(len(a)):
        if list(a)[i] != "=":
            v = b64map.index(list(a)[i])
            if 0 == e:
                e = 1
                d += int2char(v >> 2)
                c = 3 & v
            elif 1 == e:
                e = 2
                d += int2char(c << 2 | v >> 4)
                c = 15 & v
            elif 2 == e:
                e = 3
                d += int2char(c)
                d += int2char(v >> 2)
                c = 3 & v
            else:
                e = 0
                d += int2char(c << 2 | v >> 4)
                d += int2char(15 & v)
    if e == 1:
        d += int2char(c << 2)
    return d


def rsa_encode(j_rsakey, string):
    rsa_key = f"-----BEGIN PUBLIC KEY-----\n{j_rsakey}\n-----END PUBLIC KEY-----"
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(rsa_key.encode())
    result = b64tohex((b64encode(rsa.encrypt(string.encode(), pubkey))).decode())
    return result


def login(username, password):
    session = requests.Session()
    url1 = "https://cloud.189.cn/api/portal/loginUrl.action?redirectURL=https://cloud.189.cn/web/redirect.html"
    html = session.get(url1).text
    captchaToken = re.findall(r"captchaToken' value='(.+?)'", html)[0]
    lt = re.findall(r'lt = "(.+?)"', html)[0]
    returnUrl = re.findall(r"returnUrl = '(.+?)'", html)[0]
    paramId = re.findall(r'paramId = "(.+?)"', html)[0]
    j_rsakey = re.findall(r'j_rsaKey" value="(\S+)"', html, re.M)[0]
    session.headers.update({"lt": lt})

    username = rsa_encode(j_rsakey, username)
    password = rsa_encode(j_rsakey, password)
    url2 = "https://open.e.189.cn/api/logbox/oauth2/loginSubmit.do"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/76.0",
        "Referer": "https://open.e.189.cn/",
    }
    data = {
        "appKey": "cloud",
        "accountType": "01",
        "userName": f"{{RSA}}{username}",
        "password": f"{{RSA}}{password}",
        "validateCode": "",
        "captchaToken": captchaToken,
        "returnUrl": returnUrl,
        "mailSuffix": "@189.cn",
        "paramId": paramId,
    }
    resp = session.post(url2, data=data, headers=headers, timeout=10).json()
    if resp["result"] != 0:
        logger.info("登录出错...\n")
        logger.info(resp["msg"])
        exit()
    logger.info("登录成功...")
    redirect_url = resp["toUrl"]
    session.get(redirect_url)
    return session
