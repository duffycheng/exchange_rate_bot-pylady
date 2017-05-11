
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
            (USD','SGD','SEK','ZAR','HKD','CHF','EUR','CNY','GBP','CAD','NZD','AUD','JPY','THB')
        output:
            {'SGD': '21.4240', 'THB': '0.8694', 'CHF': '29.9822', 'NZD': '20.6702', 'HKD': '3.8854', 'GBP': '39.1246', 'ZAR': '2.2403', 'SEK': '3.3882', 'JPY': '0.2648', 'USD': '30.2550', 'EUR': '32.8758', 'CNY': '4.3825', 'CAD': '22.0670', 'AUD': '22.2553'}
        '''
        pass

class ITERExchangeRateCrawler(Crawler):    
    @classmethod    
    def get_exchange_rate_table(cls, currency_table):
        ret = {}
        r = requests.get('https://tw.rter.info/capi.php')
        j = r.json()
        for currency in currency_table:
            if currency == 'USD':
                ret['USD'] = round(j['USDTWD']['Exrate'], 4)
            else:
                ret[currency] = round(j['USDTWD']['Exrate'] / j['USD'+currency]['Exrate'], 4)
        return ret

class GoogleExchangeRateCrawler(Crawler):
    @classmethod
    def get_exchange_rate_table(cls, currency_table):
        ret = {}
        for currency in currency_table:
            # find the pattern like "<div id=currency_converter_result>1 USD = <span class=bld>30.2550 TWD</span>"
            r = requests.get("https://www.google.com/finance/converter?a=1&from=%s&to=%s" % (currency, 'TWD'))
            match_obj = re.search("<span class=bld>(\d+\.?\d*) [A-Z]{3}<\/span>", r.text)
            if match_obj:
                ret[currency] = match_obj.group(1)
            time.sleep(0.2)
        return ret
