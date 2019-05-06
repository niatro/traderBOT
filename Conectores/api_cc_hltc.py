import requests
import pandas as pd

# Documentation
# https://min-api.cryptocompare.com/documentation?key=Historical&cat=dataHistohour&api_key=0790f87f52c4f2eefe094943d95f1fd321cd4eb4d746cd02d61673856afdb1c4
# Visor JSON elements  http://jsonviewer.stack.hu/

apiKey = "0790f87f52c4f2eefe094943d95f1fd321cd4eb4d746cd02d61673856afdb1c4"


class CryptoConector():
    def __init__(self, limit, token, fiat):
        self.limit = limit
        self.token = token
        self.fiat = fiat

    def precioHora(self):
        url = "https://min-api.cryptocompare.com/data/histohour"
        payload = {
            "api_key": apiKey,
            "fsym": self.token,
            "tsym": self.fiat,
            "limit": self.limit,
        }
        result = requests.get(url, params=payload).json()
        tmp_df = pd.DataFrame(result['Data'])
        tmp_df['time'] = pd.to_datetime(tmp_df['time'], unit='s')
        return tmp_df

    def precioDia(self):
        url = "https://min-api.cryptocompare.com/data/histoday"
        payload = {
            "api_key": apiKey,
            "fsym": self.token,
            "tsym": self.fiat,
            "limit": self.limit,
        }
        result = requests.get(url, params=payload).json()
        tmp_df = pd.DataFrame(result['Data'])
        tmp_df['time'] = pd.to_datetime(tmp_df['time'], unit='s')
        return tmp_df
