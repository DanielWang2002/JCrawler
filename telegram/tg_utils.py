# 飆幣系統
def biao_bi(message):
    """
        params:
            message: str
        return:
            signal: dict {"Symbol": {"action": Buy/Sell", "strategy": "B"}}
    """
    signal = {}
    text = message.text.split("\n")
    if text[0] == "【飆幣系統 進場】":
        for i in text[2:-1]:
            signal[i] = {'action': 'Buy', 'strategy': 'B'}
    elif text[0] == "【飆幣系統 出場】":
        for i in text[2:-1]:
            signal[i.split("：")[0]] = {'action': 'Sell', 'strategy': 'B'}
    return signal