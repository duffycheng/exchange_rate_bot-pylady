# encoding: utf-8

import re
import traceback
from operator import itemgetter
from Crawler import ITERExchangeRateCrawler, GoogleExchangeRateCrawler
from datetime import datetime

class MyLineBot:
    # 支援的幣別
    support_currency = ('USD','JPY')
    # 幣別名稱
    currency_name_mapping = {'USD':'美元','JPY':'日圓'}
    inverse_currency_name_mapping = {v: k for k, v in currency_name_mapping.items()}
    # 使用哪些爬蟲
    crawlers = (ITERExchangeRateCrawler, GoogleExchangeRateCrawler)
    # 暫存資料
    # exchange_rate_table 格式如下： {'JPY': '0.2648', 'USD': '30.2550'}
    exchange_rate_table = {}
    notify_list = {}
    table_update_timestamp = str(datetime.utcnow())+'(UTC)'

    def __init__(self, options={}):
        pass

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
        default_msg = "請輸入你想查詢的幣別（目前支援的有 %s）" % (",".join(self.currency_name_mapping.values()))

        # --- ** 匯率查詢功能 ----
        # HERE! ->
        #
        # 如何知道使用者想查詢的是哪個幣別?
        #
        # 例如  使用者的訊息為 "請問現在美元匯率"
        #
        # 我們要能知道他問的是 "美元"
        #
        # 再來，我們要利用 self.get_exchange_rate 去查表 回傳匯率
        #
        # 你或許會用到 self.currency_name_mapping 幣別名稱和代碼的轉換表
        #
        pass
        #
        # HERE! <-

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

                print("\n[0.驗證爬蟲] test_crawlers()")
                bot.test_crawlers()

                msg_test("\n[1.驗證訊息 'hi' ] parse_message('hi')", "","hi", False)

                msg_test("\n[2.驗證訊息 '美 元' ] parse_message('美 元')]", "","美 元", True)

                msg_test("\n[3.驗證訊息 '美金' ] parse_message('美金')]", "","美金", False)

                print("\n[4.驗證更新匯率表] update_exchange_rate_table()")
                bot.update_exchange_rate_table()
                print(bot.get_table_update_timestamp(), bot.get_exchange_rate_table(), bot.get_notify_list())

                msg_test("\n[5.驗證訊息 '美元' ] parse_message('美元')]", "","美元", True)
                
                break

            
        except Exception as e:
            traceback.print_exc()

    test()
