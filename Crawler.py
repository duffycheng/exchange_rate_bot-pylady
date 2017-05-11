
import requests, time, datetime, re;

class Crawler():
    @classmethod
    def unit_test(cls):
        c = ('USD','JPY')
        t = datetime.datetime.now()
        r = cls.get_exchange_rate_table(c)
        t = datetime.datetime.now()-t
        return "\n Test crawler '%s' by table '%s'\n Result: %s\n In %d.%d seconds\n" % (cls.__name__, c, r, t.seconds, t.microseconds) 
    
    @classmethod
    def get_exchange_rate_table(cls, currency_table):
        '''
        input:
            (USD','JPY')
        output:
            {'JPY': '0.2648', 'USD': '30.2550'}
        '''
        pass

class ITERExchangeRateCrawler(Crawler):    
    @classmethod    
    def get_exchange_rate_table(cls, currency_table):
        ret = {}
        r = requests.get('https://tw.rter.info/capi.php')
        j = r.json()

        # HERE! ->
        #
        # 預期的 input 參數 currency_table 為 (USD','JPY')
        #
        # 我們希望使用 問回來的 資料把它轉換成一個 dictionary 像這樣
        #
        # {'JPY': '0.2648', 'USD': '30.2550'}
        #
        #
        pass
        #
        # HERE! <-

        return ret

class GoogleExchangeRateCrawler(Crawler):
    @classmethod
    def get_exchange_rate_table(cls, currency_table):
        ret = {}
        
        # HERE! ->
        #
        # 預期的 input 參數 currency_table 為 (USD','JPY')
        #
        # 我們希望使用 問回來的 資料把它轉換成一個 dictionary 像這樣
        #
        # {'JPY': '0.2648', 'USD': '30.2550'}
        #
        # 你可以用下面方式抓取整個網頁回來研究看資料在哪邊
        #
        # r = requests.get("https://www.google.com/finance/converter?a=1&from=%s&to=%s" % (currency, 'TWD'))
        #
        pass
        #
        # HERE! <-
        return ret
