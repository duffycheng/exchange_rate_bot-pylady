import time, os, requests
time.sleep(20)
while 1:
    try:
        url = "http://0.0.0.0:%s/update-exchange-rate-table/now" % (os.environ['PORT'])
        print("call api", url)
        requests.get(url)
        time.sleep(3600)
    except:
        pass
