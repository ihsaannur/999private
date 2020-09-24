#!/usr/bin/python
# coding: utf-8

import getpass, requests, sys
from random import randint
from colorama import init, Fore, Back, Style
from optparse import OptionParser
from requests.auth import HTTPProxyAuth
from bs4 import BeautifulSoup

init()

splash = u'''
 █████╗  █████╗  █████╗   ██████╗ ██╗ ██████╗███████╗██████╗  ██████╗ ████████╗
██╔══██╗██╔══██╗██╔══██╗  ██╔══██╗██║██╔════╝██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝
╚██████║╚██████║╚██████║  ██║  ██║██║██║     █████╗  ██████╔╝██║   ██║   ██║   
 ╚═══██║ ╚═══██║ ╚═══██║  ██║  ██║██║██║     ██╔══╝  ██╔══██╗██║   ██║   ██║   
 █████╔╝ █████╔╝ █████╔╝  ██████╔╝██║╚██████╗███████╗██████╔╝╚██████╔╝   ██║   
 ╚════╝  ╚════╝  ╚════╝   ╚═════╝ ╚═╝ ╚═════╝╚══════╝╚═════╝  ╚═════╝    ╚═╝   
                                                                               '''
key = '11347137341f4a11afbfb9c68e66114c'
bet = [(0, 499499), (500500, 999999)]

parser = OptionParser()
parser.add_option("-u", "--Username", type="string",
                  help="username on 999dice.com")
parser.add_option("-p", "--Password", type="string")
parser.add_option("-P", "--PayIn", type="string",
                  help="your minimal bet")
parser.add_option("-M", "--MaxPayIn", type="int", default=0,
                  help="The maximum bet amount, or 0 for no maximum. (default=0) in satoshis")
parser.add_option("-S", "--StopMinBalance", type="int", default=0,
                  help="After a bet, if your balance is less than this amount, then stop betting. (default=0) in satoshis")
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print most messages to stdout")

(options, args) = parser.parse_args()
class MakeVars(object):
    def __init__(self, data):
        for key, val in data.items():
            setattr(self, key, val)


def request_api(data):
    for attempt in range(20):
        try:
            r = requests.post('https://www.999dice.com/login', data=data) 
            print "----------------------------------" #r.text
            return MakeVars(r.json())
        except requests.exceptions.ConnectionError as error:
            print (Fore.RED + 'Connection error')
            if not attempt == 9:
                print (Fore.RED + 'retrying...')
            else:
                print (Fore.RESET + 'Connection error. Details: ' + str(error))
                sys.exit()


class Bot(object):
    def __init__(self, key):
        self.PayIn_origin = 10
        self.PayIn = 10
        self.Key = key
        if options.Username and options.Password:
            self.Username = options.Username
            self.Password = options.Password
        else:
            self.Username = raw_input('Username:')
            self.Password = getpass.getpass('Password:')
        #self.bet = [(0, 499499), (500500, 999999)],
    
    def login(self):
        data = dict(
            a = 'Login',
            Key = self.Key,
            Username = self.Username,
            Password = self.Password,
            )
        self._ = request_api(data)
        

    def get_balance(self):
        data = dict(
            a = 'GetBalance',
            s = self._.SessionCookie,
        )
        r = request_api(data)
        self._.Balance = r.Balance
        print 'You balance:', self._.Balance,'satoshis'
        
    def place_bet(self, b):
        data = dict(
            a = 'PlaceBet',
            s = self._.SessionCookie,
            PayIn = self.PayIn,
            Currency="ltc",
            Low = bet[b][0],
            High = bet[b][1],
        )
        r = request_api(data)
        self._.PayOut = r.PayOut
        
    def place_auto_bet(self, b):
        data = dict(
            a = 'PlaceAutomatedBets',
            s = self._.SessionCookie,
            BasePayIn = self.PayIn,
            Low = bet[b][0],
            High = bet[b][1],
            Currency="ltc",
            MaxBets = 200,
            ResetOnWin = True,
            IncreaseOnLosePercent = 1,
            MaxPayIn = options.MaxPayIn,
            StopOnLoseMaxBet = True,
            StopMinBalance = options.StopMinBalance,
            Compact = True
        )
        r = request_api(data)
        self.ab = r

def main():
    print(Fore.YELLOW + Style.BRIGHT + splash)
    print(Fore.RESET + Back.RESET + Style.RESET_ALL)
    
    bot = Bot(key)
    bot.login()
    bot._.Balance_origin = bot._.Balance
    totalprofit=0
    print '1 satoshis = 0.0000001 BTC'
    print 'You balance:', bot._.Balance, 'satoshis'
    
    while True:
        b = randint(0, len(bet)-1)
        bot.place_auto_bet(b)
        totalprofit+=bot.ab.PayOut + bot.ab.PayIn
        print 'Result :', bot.ab.PayOut + bot.ab.PayIn
        print 'Balance :', bot.ab.StartingBalance + bot.ab.PayOut + bot.ab.PayIn
        print 'Total Profit :',totalprofit 
        if bot.ab <= options.StopMinBalance:
            break
    
    """if options.PayIn:
        pay_in = options.PayIn
    else:
        pay_in = raw_input('Pay in (default:1 satoshis):')
    if pay_in.isdigit() and int(pay_in) != 1:
        bot.PayIn_origin = bot.PayIn = int(pay_in)
    
    print 'Here we go!!'
    lose_count = 0
    while True:
        try:
            b = randint(0, len(bet)-1)
            bot.place_bet(b)
            result = bot._.PayOut - bot.PayIn
            bot._.Balance = bot._.Balance + result
            if lose_count == options.LoseControl and options.LoseControl:
                print (Back.YELLOW + Fore.RED + 'Lose ' + str(lose_count) + ' times. Back to minimal.')
                result = 0
                
            if result < 0:
                lose_count += 1
                bot.PayIn = bot.PayIn*2
                print(Back.RED + Fore.WHITE)
                if bot.PayIn > bot._.Balance:
                    print (Style.BRIGHT + 'Out of money. Last failure bet: ' + str(bot.PayIn/2))
                    break
            else:
                lose_count = 0
                bot.PayIn = bot.PayIn_origin
                print(Back.GREEN + Fore.WHITE + Style.BRIGHT)
                
            if options.verbose:
                print('Bet result: ' + str(result) + ' satoshis. H:'+str(b))
                print('Balance: ' + str(bot._.Balance) + ' satoshis')
                print(Fore.RESET + Back.RESET + Style.RESET_ALL)
            
        except KeyboardInterrupt:
            print(Fore.YELLOW + Style.BRIGHT +'='*80)
            print(Fore.RESET + Back.RESET + Style.RESET_ALL + 'You have earned: ' + str(bot._.Balance-bot._.Balance_origin) + ' satoshis')
            break
    """
    bot.get_balance()
    print "Bye"
    sys.exit()

if __name__ == '__main__':
    main()

# EOF
