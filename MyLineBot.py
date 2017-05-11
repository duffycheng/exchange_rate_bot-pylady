# encoding: utf-8

import re
import traceback
from operator import itemgetter
from Crawler import ITERExchangeRateCrawler, GoogleExchangeRateCrawler
from datetime import datetime

class MyLineBot:
    # 支援的幣別
    support_currency = ('USD','SGD','SEK','ZAR','HKD','CHF','EUR','CNY','GBP','CAD','NZD','AUD','JPY','THB')
    # 幣別名稱
    currency_name_mapping = {'USD':'美元','SGD':'新加坡幣','SEK':'瑞典克郎','ZAR':'南非幣','HKD':'港幣','CHF':'瑞士法郎','EUR':'歐元','CNY':'人民幣 ','GBP':'英磅','CAD':'加幣','NZD':'紐西蘭幣','AUD':'澳幣','JPY':'日圓','THB':'泰銖'}
    inverse_currency_name_mapping = {v: k for k, v in currency_name_mapping.items()}
    # 使用哪些爬蟲
    crawlers = (ITERExchangeRateCrawler, GoogleExchangeRateCrawler)
    # 暫存資料
    exchange_rate_table = {}
    notify_list = {}
    table_update_timestamp = str(datetime.utcnow())+'(UTC)'

    def __init__(self, options={}):
        self.push_callback = options.get('push_callback', None)

    # ---- 通知使用者 ----
    def notify_user(self, uid, msg):
        print("notify_user '%s' '%s'" % (uid, msg))
        if self.push_callback:
            self.push_callback([uid], msg)

    # ---- 新增通知名單 ----
    def add_request_to_notify_list(self, uid, currency, updown, value):
        self.notify_list[uid+currency] = (uid, currency, updown, value)

    # ---- 取得通知名單 ----
    def get_notify_list(self):
        return self.notify_list

    # ---- 檢查通知名單 ----
    def check_notify_list(self):
        for uid, currency, updown, value in self.notify_list.values():
            cur_value = self.exchange_rate_table.get(currency, 0)
            if cur_value == 0:
                continue
            elif updown == 'up' and cur_value > value:
                self.notify_user(uid, "%s 匯率現在 %.4f ，大於你所設定的 %.4f" % (self.currency_name_mapping[currency], cur_value, value))
            elif updown == 'down' and cur_value < value:
                self.notify_user(uid, "%s 匯率現在 %.4f ，小於你所設定的 %.4f" % (self.currency_name_mapping[currency], cur_value, value))

    # ---- 更新匯率表 ----
    def update_exchange_rate_table(self):
        table = {}
        for x in self.crawlers:
            table = x.get_exchange_rate_table(self.support_currency)
            if len(table) == len(self.support_currency):
                break
        self.exchange_rate_table = table
        self.table_update_timestamp = str(datetime.utcnow())+'(UTC)'

        self.check_notify_list()

    # ---- 取得匯率表 ----
    def get_exchange_rate_table(self):
        return self.exchange_rate_table

    # ---- 取得匯率表更新時間 ----
    def get_table_update_timestamp(self):
        return self.table_update_timestamp

    # ---- 取得匯率 ----
    def get_exchange_rate(self, currency):
        return self.exchange_rate_table.get(currency, 0)

    # ---- 測試爬蟲功能 ----
    def test_crawlers(self):
        for x in self.crawlers:
            print(x.unit_test())

    # ---- 處理 line 訊息 ----
    def parse_message(self, uid, msg):
        # --- 預設選單 ---
        msg = msg.strip().replace(' ','')
        default_msg = "請輸入你想查詢的幣別（目前支援的有 %s）\n或請輸入你想被通知的幣別（範例1： 美元大於30通知我, 範例2： 日圓小於0.27通知我）" % (",".join(self.currency_name_mapping.values()))

        # --- 通知功能 ----
        if re.match(".*通知", msg):
            match_obj = re.match("(\w+)(大於|小於)(\d+\.?\d*).*通知", msg)
            if match_obj:
                try:
                    currency = self.inverse_currency_name_mapping[match_obj.group(1)]
                    if match_obj.group(2) == "大於":
                        updown = "up" 
                    else:
                        updown = "down"
                    value = round(float(match_obj.group(3)), 4)
                    self.add_request_to_notify_list(uid, currency, updown, value)
                    return "已確認，%s你" % (match_obj.group(0))
                except Exception as e:
                    traceback.print_exc()
                    
            return "請檢查你的格式（範例1： 美元大於30通知我, 範例2： 日圓小於0.27通知我）"

        # --- 匯率查詢功能 ----
        for currency, name in self.currency_name_mapping.items():
            if re.match(name, msg):
                return "%s匯率現在是 %.4f" % (name, self.get_exchange_rate(currency))

        return default_msg


if __name__ == "__main__":

    bot = MyLineBot()

    def msg_test(title, uid, msg, is_fail_pattern):
        print(title)
        r = bot.parse_message(uid, msg)
        print(r)
        if is_fail_pattern:
            return re.search("(請輸入|請檢查)", r) != None
        else:
            return re.search("(請輸入|請檢查)", r) == None

    def test():
        print("\n\n\n")
        try:
            while 1:
                print("\n[0.驗證初始狀態]")
                print(bot.get_table_update_timestamp(), bot.get_exchange_rate_table(), bot.get_notify_list())

                # print("\n[0.驗證爬蟲] test_crawlers()")
                # bot.test_crawlers()

                if msg_test("\n[1.驗證訊息 'hi' ] parse_message('hi')", "","hi", False):
                    break

                if msg_test("\n[2.驗證訊息 '美 元' ] parse_message('美 元')]", "","美 元", True):
                    break

                if msg_test("\n[3.驗證訊息 '美金' ] parse_message('美金')]", "","美金", False):
                    break

                if msg_test("\n[4.驗證訊息 '美金大於30通知我' ] parse_message('美金大於30通知我')]", "USD_TEST_UID", "美金大於30通知我", False):
                    break

                if msg_test("\n[5.驗證訊息 '如果美元大於 30 通知我' ] parse_message('如果美元大於 30 通知我')]", "USD_TEST_UID", "如果美元大於 30 通知我", False):
                    break

                if msg_test("\n[6.驗證訊息 '美元>30通知我' ] parse_message('美元>30通知我')]", "USD_TEST_UID", "美元>30通知我", False):
                    break

                if msg_test("\n[7.驗證訊息 '美元大於 30塊 通知我' ] parse_message('美元大於 30塊 通知我')]", "USD_TEST_UID", "美元大於 30塊 通知我", True):
                    break

                if msg_test("\n[8.驗證訊息 '美元大於30通知我' ] parse_message('美元大於30通知我')]", "USD_TEST_UID", "美元大於30通知我", True):
                    break

                if msg_test("\n[9.驗證訊息 '美元大於 30 通知我' ] parse_message('美元大於 30 通知我')]", "USD_TEST_UID", "美元大於 30 通知我", True):
                    break

                if msg_test("\n[10.驗證訊息 '日圓小於0.27通知我' ] parse_message('日圓小於0.27通知我')]", "JPY_TEST_UID", "日圓小於0.27通知我", True):
                    break

                print("\n[11.驗證更新匯率表] update_exchange_rate_table()")
                bot.update_exchange_rate_table()
                print(bot.get_table_update_timestamp(), bot.get_exchange_rate_table(), bot.get_notify_list())

                if msg_test("\n[12.驗證訊息 '美元' ] parse_message('美元')]", "","美元", True):
                    break

                print("\n\n A L L  T E S T  P A S S \n\n")
                break

            
        except Exception as e:
            traceback.print_exc()

    test()
