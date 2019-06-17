# coding: utf8
#
# 在线验证邮箱真实性
#

import random
import smtplib
import logging
import time

import dns.resolver

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s [line:%(lineno)d] - %(levelname)s: %(message)s')

logger = logging.getLogger()


def fetch_mx(host):
    #
    # 解析服务邮箱
    # :param host:
    # :return:
    # 
    logger.info('Finding mail server...')
    answers = dns.resolver.query(host, 'MX')
    res = [str(rdata.exchange)[:-1] for rdata in answers]
    logger.info('Search result：%s' % res)
    return res


def verify_istrue(email):
    #
    # :param email:
    # :return:
    #
    email_list = []
    email_obj = {}
    final_res = {}
    if isinstance(email, str) or isinstance(email, bytes):
        email_list.append(email)
    else:
        email_list = email

    for em in email_list:
        name, host = em.split('@')
        if email_obj.get(host):
            email_obj[host].append(em)
        else:
            email_obj[host] = [em]

    for key in email_obj.keys():
        host = random.choice(fetch_mx(key))
        logger.info('Connecting server...：%s' % host)
        s = smtplib.SMTP(host, timeout=10)
        for need_verify in email_obj[key]:
            helo = s.docmd('HELO chacuo.net')
            logger.debug(helo)

            send_from = s.docmd('MAIL FROM:<james.li@nike.com>')
            logger.debug(send_from)
            send_from = s.docmd('RCPT TO:<%s>' % need_verify)
            logger.debug(send_from)
            if send_from[0] == 250 or send_from[0] == 451:
                final_res[need_verify] = True  # 存在
            elif send_from[0] == 550:
                final_res[need_verify] = False  # 不存在
            else:
                final_res[need_verify] = None  # 未知

        s.close()

    return final_res


if __name__ == '__main__':
    final_list = verify_istrue(['V19309950748@snkrs.mobi', '51931701@qq.com',
    '1260472871361@qq.com', 'lmbcop7845@foxmail.com'
                                ])
    print(final_list)
