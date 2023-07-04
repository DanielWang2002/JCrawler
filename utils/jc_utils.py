import time

def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def logger(msg):
    print("="*30, get_time(), "="*30)
    print(msg)
    # print("="*81)