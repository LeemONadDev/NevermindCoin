import blockchain, os

blockchain_ = blockchain.Utils.load_dump('blockchain_data\\blockchain')

while 1:
    print('Выберите действие:')
    print('[1] Просмотреть блокчейн')
    print('[2] Просмотреть баланс')

    k = input()

    if k == "1":
        print(blockchain.ConUI.get_blockchain_data(blockchain_))
    if k == "2":
        print("Введите адрес")
        addr = input()
        addr_compact = addr[:5] +'...'+addr[len(addr)-4:]
        os.system('cls')
        print(f"Адрес {addr_compact}\nБаланс: {blockchain.ConUI.get_balance_raw(addr,blockchain_)} {blockchain.coin_symbol}")