import blockchain, os,random,socket

if not(os.path.exists('wallet_data\\private_key') and os.path.exists('wallet_data\\public_key')):
    if not os.path.exists('wallet_data\\'): os.system('mkdir wallet_data')
    private, public = blockchain.Utils.generate_keys() #private key, public key
    f = open('wallet_data\\private_key','w')
    f.write(blockchain.Utils.pk2str(private))
    f.close()
    f = open('wallet_data\\public_key','w')
    f.write(blockchain.Utils.public_key2str(public))
    f.close()
    f = open('wallet_data\\address.txt','w')
    p2str = blockchain.Utils.public_key2str(public).replace('-----BEGIN PUBLIC KEY-----\n','').replace('-----END PUBLIC KEY-----\n','')
    str_t_b58 = blockchain.Utils.b58str_e(p2str)
    f.write(str_t_b58.decode('utf-8'))
    f.close()

socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while 1:
    print("Выберите опцию:")
    print('[1] Создать транзакцию')

    k = input()

    if k == "1":
        print(f"Введите получателя транзакции. Убедитесь что вы ввели корректный адрес, иначе все ваши {blockchain.coin_symbol} пропадут!")
        recepient = input('>')
        print(f'Введите количество {blockchain.coin_symbol}, которое вы хотите отправить')
        amount = float(input('>'))

        f = open('wallet_data\\address.txt','r')
        address = f.read();f.close()
        transaction = [address,recepient,amount]

        f = open('wallet_data\\private_key')
        
        pk = blockchain.Utils.str2pk(f.read());f.close()
        signature = blockchain.Utils.sign_message_sha256(str(transaction),pk)
        str_signature = blockchain.base64.b64encode(signature).decode()
        transaction.append(str_signature)
        tmp_txid = '--txid_tmp:'+str(random.randint(0,99999999999999999))+str(random.randint(-99999999999999999999,1))
        transaction.append(tmp_txid)

        transaction_data = blockchain.Utils.json_dump(transaction)
        
        if blockchain.wallet_display_transaction_data:
            print("Сформирована и подписана новая транзакция\n",transaction_data,'\n\n')

        print("Транзакция начала распостранятся по сети...")

        f = open('blockchain_data\\peers.txt')
        peers = f.read().split('\n');f.close()

        ready_data = transaction_data.encode('utf-8')

        for peer in peers:
            peer = peer.split(':')
            peer_addr = (peer[0],int(peer[1]))
            print(f'Отправка транзакции по адресу: {peer[0]}:{peer[1]}')
            socket_.sendto(ready_data,peer_addr)