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
    # exchange_rate_table 格式如下： {'SGD': '21.4240', 'THB': '0.8694', 'CHF': '29.9822', 'NZD': '20.6702', 'HKD': '3.8854', 'GBP': '39.1246', 'ZAR': '2.2403', 'SEK': '3.3882', 'JPY': '0.2648', 'USD': '30.2550', 'EUR': '32.8758', 'CNY': '4.3825', 'CAD': '22.0670', 'AUD': '22.2553'}
    exchange_rate_table = {}
    # notify_list 格式自訂
    notify_list = {}
    table_update_timestamp = str(datetime.utcnow())+'(UTC)'

    def __init__(self, options={}):
        # **
        self.push_callback = options.get('push_callback', None)
        self.exchange_rate_table = options.get('exchange_rate_table', {})

    # ---- ** 通知使用者 ----
    def notify_user(self, uid, msg):
        print("notify_user '%s' '%s'" % (uid, msg))
        if self.push_callback:
            self.push_callback([uid], msg)

    # ---- ** 新增通知名單 ----
    def add_request_to_notify_list(self, uid, currency, updown, value):
        # HERE! ->
        #
        # 當一位使用者 "ab123" 的通知需求為 '當美元大於35.0元的時候請記得通知該使用者''
        # 我們預期會得到以下的參數：
        #
        # (uid, currency, updown, value) -> (ab123, 美元, 大於, 35.0)
        # 
        # 請利用 self.notify_list 將參數記錄下來
        #
        # 另外，我們要如何避免 使用者重複記錄同一種幣別通知?
        #
        #     例如 
        #     add_request_to_notify_list( ab123, 美元, 大於, 35.0)
        #     add_request_to_notify_list( ab123, 美元, 大於, 25.0)
        #
        # 記錄了兩次 USD 的通知請求，我們該如何只保留最後一筆資料?
        #
        pass
        #
        # HERE! <-


    # ---- ** 檢查通知名單 ----
    def check_notify_list(self):
        # HERE! ->
        #
        # 當我們取得最新匯率表的時候，按照 self.notify_list 裡面的參數 決定是否要通知使用者
        #
        # 請使用 self.notify_user() 將訊息傳遞給使用者，例如
        #
        #     self.notify_user("ab123", "你好，......")
        #
        pass
        #
        # HERE! <-

    # ---- 取得通知名單 ----
    def get_notify_list(self):
        return self.notify_list

    # ---- 更新匯率表 ----
    def update_exchange_rate_table(self):
        table = {}
        for x in self.crawlers:
            table = x.get_exchange_rate_table(self.support_currency)
            if len(table) == len(self.support_currency):
                break
        self.exchange_rate_table = table
        self.table_update_timestamp = str(datetime.utcnow())+'(UTC)'

        # ** 
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

        # --- ** 通知功能 ----
        if re.match(".*通知", msg):  
            # HERE! ->
            #
            # 將使用者的訊息 拆解成三個字串參數出來 ， 分別對應到 （currency, updown, value）
            #
            #    例如 "美元大於30通知我" -> (美元, 大於, 30)
            #
            # 也有可能發生使用者的參數拆解出來無意義的時候：
            #
            #    例如 "黃金大於30通知我" -> (黃金, 大於, 30)
            #
            #    例如 "美元30通知我" -> (美元, ?, 30)
            #
            # 試著想想如何處理以上這些問題
            #
            currency = ""
            updown = ""
            value = ""
            #
            # HERE! <-
            if len(currency) > 0 and len(updown) > 0 and len(value) > 0:
                self.add_request_to_notify_list(uid, currency, updown, value)
                return "已確認，%s%s%s通知你" % (currency, updown, value)
            else:
                return "請檢查你的格式（範例1： 美元大於30通知我, 範例2： 日圓小於0.27通知我）"

        # --- 匯率查詢功能 ----
        for currency, name in self.currency_name_mapping.items():
            if re.match(name, msg):
                return "%s匯率現在是 %.4f" % (name, self.get_exchange_rate(currency))

        return default_msg


if __name__ == "__main__":

    bot = MyLineBot({'exchange_rate_table':{'USD':35.5, 'JPY':0.29}})

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

                msg_test("\n[4.驗證訊息 '黃金大於30通知我' ] parse_message('黃金大於30通知我')]", "abcd1234", "黃金大於30通知我", False)
                bot.check_notify_list()
                bot.get_notify_list()

                msg_test("\n[5.驗證訊息 '如果美元大於 30 通知我' ] parse_message('如果美元大於 30 通知我')]", "abcd1234", "如果美元大於 30 通知我", False)
                bot.get_notify_list()
                bot.check_notify_list()

                msg_test("\n[7.驗證訊息 '美元大於 30塊 通知我' ] parse_message('美元大於 30塊 通知我')]", "abcd1234", "美元大於 30塊 通知我", True)
                bot.get_notify_list()
                bot.check_notify_list()
                
                msg_test("\n[8.驗證訊息 '美元大於40通知我' ] parse_message('美元大於40通知我')]", "abcd1234", "美元大於40通知我", True)
                bot.get_notify_list()
                bot.check_notify_list()

                msg_test("\n[9.驗證訊息 '美元大於 30 通知我' ] parse_message('美元大於 30 通知我')]", "abcd1234", "美元大於 30 通知我", True)
                bot.get_notify_list()
                bot.check_notify_list()

                break

            
        except Exception as e:
            traceback.print_exc()

    test()
