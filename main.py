from mnemonic import Mnemonic
from web3 import Web3
from web3.eth import Account
import requests
import json
import concurrent.futures as pool
import sys

def mnemonic_from_file(file):
    raw = open(file,'r',encoding="utf-8")
    mnemonic_list = raw.read().split('\n')
    return mnemonic_list
def wallet_check(wallet):
    req = requests.get(f'https://openapi.debank.com/v1/user/total_balance?id={wallet}').content
    info = json.loads(req)
    wallet_price = info['total_usd_value']
    return wallet_price
min_balance = 0.00000001
def run():
    while True:
        mnemo = Mnemonic("english")
        words = mnemo.generate(strength=128)
        w3 = Web3()
        w3.eth.account.enable_unaudited_hdwallet_features()
        account = Account.from_mnemonic(words, account_path="m/44'/60'/0'/0/0")
        amount = wallet_check(account.address)
        if amount>min_balance:
            print(f'{account.address} - Balance: {amount}\n')
            file = open('balance.txt','a')
            file.write(f'{account.address} - Balance: {amount} - Mnemonic [{words}]\n')
            file.close()
        else:
            print(f'{account.address} - Balance: {amount}\n')
def main(threads):
    with pool.ThreadPoolExecutor(max_workers=threads) as executor:
        future_list = {executor.submit(run): i for i in range(threads)}
        for future in pool.as_completed(future_list):
            future.result()
def run_with_list(file):
    mnemonic_list = mnemonic_from_file(file)
    for words in mnemonic_list:
        w3 = Web3()
        w3.eth.account.enable_unaudited_hdwallet_features()
        try:
            account = Account.from_mnemonic(words, account_path="m/44'/60'/0'/0/0",)
        except:
            continue
        amount = wallet_check(account.address)
        if amount > min_balance:
            print(f'{account.address} - Balance: {amount}\n')
            file = open('balance.txt', 'a')
            file.write(f'{account.address} - Balance: {amount} - Mnemonic [{words}]\n')
            file.close()
        
if __name__ == '__main__':
    try:
        threads = int(sys.argv[1])
        mode = sys.argv[2]
        if mode == '1':
            if threads:
                main(threads)
            else:
                print("Введите число потоков - пример: 'python main.py 100 1' - 100 потоков")
        elif mode == '2':
            file = input('Название файла: ')
            run_with_list(file)
        else:
            print('Неверное значение mode - пример: "python main.py 100 1" - работа с генератором мнемоник фраз')
    except Exception as e:
        print('Отсутствуют аргументы запуска - пример: "python main.py 100 1"')
        print(e)
