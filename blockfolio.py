#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import json
import requests
from prettytable import PrettyTable

class BlockFolio(object):
    API_TOKEN   = "INSERT TOKEN HERE"
    API_URL     = "https://api-v0.blockfolio.com"
    USER_AGENT  = {'User-Agent':'okhttp/3.6.0'}
    PORTFOLIO   = None
    COINFOLIO   = None

    def __init__(self):
        # Check API
        if self.system_status() == False:
            print "No Internet or API is down !"
            exit()

        # Load the portfolio and coinfolio configuration
        self.get_all_positions()

    def get_all_positions(self):
        OPTIONS = "?fiat_currency=USD&locale=fr-FR&use_alias=true"
        PATH    = "/rest/get_all_positions/"
        data    = requests.get(self.API_URL+PATH+self.API_TOKEN+OPTIONS, headers=self.USER_AGENT).text
        js      = json.loads(data)
        self.PORTFOLIO = js['portfolio']
        self.COINFOLIO = js['positionList']

    def system_status(self):
        try:
            if requests.get(self.API_URL+"/rest/system_status?platform=android_rn", \
            headers=self.USER_AGENT).status_code != 200:
                return False
        except Exception as e:
            return False
        return True

    def sparks_data(self, coin):
        # NOTE : histohour, histoday, histominute
        SPARKS_URL  = "https://min-api.cryptocompare.com/data/histoday?fsym=%s&tsym=USD&limit=7&aggregate=1&toTs=%s"
        SPARKS_DATA = ["▁","▂","▃","▅","▇"]

        epoch_time = int(time.time())
        coin_data  = SPARKS_URL % ( coin, epoch_time )
        data       = json.loads(requests.get(coin_data).text)

        sparks = ""
        for day in data['Data']:
            if day['close']-day['open'] > 0:
                block = SPARKS_DATA[int((day['open']/day['close']) * 5) - 1]
                sparks += ("\033[92m%s\033[0m" % block)
            else:
                block = SPARKS_DATA[int((day['close']/day['open']) * 5) - 1]
                sparks += ("\033[91m%s\033[0m" % block)


        # Cryptocurrency not found
        if sparks == "":
            sparks = "\033[93m▅\033[0m"*8

        return sparks

    def colorize(self, value, header=False):
        COLOR_HEAD  = "\033[93;1m%s\033[0m"
        COLOR_RED   = "\033[91m%s\033[0m"
        COLOR_GREEN = "\033[92m%s\033[0m"
        COLOR_COIN  = "\033[94m%s\033[0m"

        # Simple value parsing
        string = str(value)
        string = string.replace("%","")
        string = string.replace("$","")
        string = string.replace("+","")
        string = string.replace(",",".")

        try:
            if header == True:
                return COLOR_HEAD % (value)

            if float(string) < 0:
                return COLOR_RED % (value)
            else:
                return  COLOR_GREEN % (value)
        except Exception as e:
            return COLOR_COIN % (value)


    def __str__(self):
        header_portfolio = [
            self.colorize("Portfolio value (Fiat $)", True),
            self.colorize("24h chg (%)", True),
            self.colorize("24h chg (Fiat $)", True)
        ]
        portfolio = PrettyTable(header_portfolio)
        portfolio.add_row([
            self.PORTFOLIO['portfolioValueFiat'],
            self.colorize(self.PORTFOLIO['percentChangeFiat']),
            self.colorize(self.PORTFOLIO['changeFiat'])
        ])

        header_coinfolio = [
            self.colorize("Coin", True),
            self.colorize("Holding value (Fiat $)", True),
            self.colorize("Quantity", True),
            self.colorize("Price (Fiat $)", True),
            self.colorize("24h chg (Fiat $)", True),
            self.colorize("24h chg (%)", True),
            self.colorize("Chg/Week", True)
        ]
        coinfolio = PrettyTable(header_coinfolio)
        for json_coin in self.COINFOLIO:
            coinfolio.add_row([
                self.colorize(json_coin['coin']),
                json_coin['holdingValueFiat'],
                json_coin['quantity'],
                json_coin['lastPriceFiat'],
                self.colorize(json_coin['twentyFourHourChangeFiat']),
                self.colorize(json_coin["twentyFourHourPercentChangeFiatString"]),
                self.sparks_data(json_coin['coin'])
            ])

        portfolio.align = 'c'
        coinfolio.align = 'l'
        coinfolio_sort  = header_coinfolio[1]
        coinfolio.reversesort = True

        return (portfolio.get_string() + "\n" + coinfolio.get_string(sortby=coinfolio_sort)).encode('utf-8')

if __name__ == '__main__':
    block = BlockFolio()
    print block

# TODO Want to help ? here are some options you can add :)
# --sortby:      coinfolio_sort  = header_coinfolio[1]
# --reversesort: coinfolio.reversesort = True
# --no-check :   do not check if API is up
