import blockchain,os,socket,time

blockchain_ = []

server = ('', 50000)
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind(server)

if os.path.exists('blockchain_data\\blockchain'):
    print("Loading blockchain dump from blockchain_data\\blockchain")
    blockchain_=blockchain.Utils.load_dump('blockchain_data\\blockchain')
else:
    print("Blockchain dump not found! Generating genesis block...")
    block = blockchain.Block()
    blockchain_.append(block.mine_block())
    block.clear_block()
    blockchain.Utils.object_file_dump(blockchain_,'blockchain_data\\blockchain')
    exit(0)

print('\n')

f = open('wallet_data\\address.txt','r')
address = f.read()
f.close()

block = blockchain.Block()
peer_list = []

timestamp = int(time.time())
block.add_transaction('mining_reward',address,blockchain.maximal_mining_reward,'not_need')
block_txids = []
#print(blockchain.ConUI.get_blockchain_data(blockchain_))
while 1:
    block = blockchain.Block()
    data, addr = udp.recvfrom(4096)

    if not(addr in peer_list): peer_list.append(addr)

    str_data = data.decode('utf-8')
    transaction_data = blockchain.Utils.json_load(str_data)

    #print(transaction_data)

    if transaction_data[4] not in block_txids:
        block_txids.append(transaction_data[4])
        transaction_data = transaction_data[:-1]

        #Checking for amount 
        if transaction_data[2] > 0.0:

            if blockchain.ConUI.get_balance_raw(transaction_data[0],blockchain_) > 0.0:

                public_key = blockchain.Utils.str2public_key('-----BEGIN PUBLIC KEY-----\n'+blockchain.Utils.b58str_d(transaction_data[0]).decode('utf-8')+'-----END PUBLIC KEY-----\n')
                signable_message = str([transaction_data[0],transaction_data[1],transaction_data[2]])

                str_signature = transaction_data[-1]
                signature = blockchain.base64.b64decode(str_signature)

                if blockchain.Utils.verify_sha256(signable_message,signature,public_key):
                    block.add_transaction(transaction_data[0],transaction_data[1],transaction_data[2],transaction_data[3])
                else:
                    print('Транзакция отклонена: Не удалось проверить валидность сигнатуры')
            else:
                print('Транзакция отклонена: Недостаточно средств на балансе')
        else:
            print('Транзакция отклонена: Сумма должна быть больше 0')
    else:
        print('Транзакция отклонена: Она уже включена на очередь в майнинг')
    new_block = block.mine_block(blockchain_)
    blockchain_.append(new_block) #mining block
    print(f'--Добыт блок #--{block.index}')
    block.clear_block()
    block_txids = []

    new_block_bytedata = bytes(blockchain.Utils.json_dump(new_block),'utf-8')

    for peer in peer_list:
        udp.sendto(new_block_bytedata,(peer[0],peer[1]))

    if blockchain.make_blockchain_dump_on_every_block:
        blockchain.Utils.object_file_dump(blockchain_,'blockchain_data\\blockchain')

    block.add_transaction('mining_reward',address,blockchain.maximal_mining_reward,'not_need')