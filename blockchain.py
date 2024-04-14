from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

import hashlib, os, time, pickle, base58, base64, json #type: ignore

blockchain = []


blockchain_difficulty = "0000"
max_block_transactions_len = 10
maximal_mining_reward = 5.0
key_size = 2048
coin_symbol = "NVM"

show_mining_process = False
wallet_display_transaction_data = False
make_blockchain_dump_on_every_block = True


class Utils:
    def s2sha512(data):
        data = str(data)
        hash_ = hashlib.sha512()
        hash_.update(data.encode())
        return hash_.hexdigest()
    
    def s2sha256(data):
        data = str(data)
        hash_ = hashlib.sha256()
        hash_.update(data.encode())
        return hash_.hexdigest()

    def address_have_amount(address, amount:float):
        balance = 0.0
        for block in blockchain:
            for transaction in block[2]:
                if transaction[0] == address:
                    balance = balance + float(transaction[2]) * -1
                if transaction[1] == address:
                    balance = balance + float(transaction[2])
        if balance >= amount:
            return True
        else:
            return False
    
    def sign_message(message, private_key):
        message = bytes(message,'utf-8')
        signature = private_key.sign(message,padding.PSS(mgf=padding.MGF1(hashes.SHA512()),salt_length=padding.PSS.MAX_LENGTH),hashes.SHA512())
        return signature
    
    def verify(message,signature,public_key):
        try:
            message = bytes(message,'utf-8')
            public_key.verify(signature,message,padding.PSS(mgf=padding.MGF1(hashes.SHA512()),salt_length=padding.PSS.MAX_LENGTH),hashes.SHA512())
            return True
        except: return False

    def sign_message_sha256(message,private_key):
        message = bytes(message,'utf-8')
        signature = private_key.sign(message,padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH),hashes.SHA256())
        return signature
    
    def verify_sha256(message,signature,public_key):
        try:
            message = bytes(message,'utf-8')
            public_key.verify(signature,message,padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH),hashes.SHA256())
            return True
        except: return False

    def generate_keys():
        private_key = rsa.generate_private_key(public_exponent=65537,key_size=key_size,backend=default_backend())
        public_key = private_key.public_key()
        return private_key,public_key
    
    def object_file_dump(object,file):
        with open(file, 'wb') as f:
            pickle.dump(object, f)

    def load_dump(file):
        with open(file, 'rb') as f:
            return pickle.load(f)
        
    def json_dump(object):return json.dumps(object)
    def json_load(str): return json.loads(str)
        
    def b58str_e(message):return base58.b58encode_check(bytes(message,'utf-8'))
    def b58str_d(message):return base58.b58decode_check(message)

    def pk2str(private_key):return private_key.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.PKCS8,encryption_algorithm=serialization.NoEncryption()).decode('utf-8')
    def public_key2str(public_key):return public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8')
    def str2public_key(public_keystr):return serialization.load_pem_public_key(public_keystr.encode('utf-8'),backend=default_backend())
    def str2pk(pkstr):return serialization.load_pem_private_key(pkstr.encode('utf-8'),password=None,backend=default_backend())



class Block():
    prev_hash = '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    timestamp = 0.0
    transactions = []
    hash_ = '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    nonce = 0
    index = 0
    block_data = [prev_hash,timestamp,transactions,nonce]
    
    def add_transaction(self,sender, recipient, amount, signature):
        if len(self.transactions) < max_block_transactions_len:
            timestamp = time.time()
            transaction = [sender,recipient,amount,signature]
            self.transactions.append(transaction)

    def mine_block(self,blockchain_=blockchain):
        self.timestamp = time.time()

        if len(blockchain_) == 0:
            pass
        else:
            self.prev_hash = blockchain_[-1][4]
            self.index = blockchain_[-1][5] + 1
        self.block_data = [self.prev_hash,self.timestamp,self.transactions,self.nonce]
        while 1:
            self.hash_ = Utils.s2sha512(str(self.block_data))
            self.block_data = [self.prev_hash,self.timestamp,self.transactions,self.nonce]
            if show_mining_process == True: print(self.nonce,self.hash_)
            if self.hash_[0:len(blockchain_difficulty)] == blockchain_difficulty:
                break
            else:
                self.nonce = self.nonce + 1
        self.block_data.append(self.hash_)
        self.block_data.append(self.index)
        return self.block_data
    
    def clear_block(self):
        self.prev_hash = '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
        self.timestamp = 0.0
        self.transactions = []
        self.hash_ = '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
        self.nonce = 0
        self.index = 0
        self.block_data = [self.prev_hash,self.timestamp,self.transactions,self.nonce]

class Storage:
    def save_block():pass
    
class ConUI:
    def get_blockchain_data(blockchain_):
        data = ""
        id_of_block = -1
        for element in blockchain_:
            id_of_block = id_of_block + 1
            data = data + f"\n\nBlockID #{id_of_block}\n-----Данные блока-----\nПредыдущий хеш: {element[0]}\nТекущий хеш: {element[4]}\n"
            data = data + f"Временная метка: {element[1]}\nNonce: {element[3]}\nИндекс: {element[5]}\nДанные блока (транзакции):"
            for transaction in element[2]:
                transaction_data = f" От: {transaction[0]} | Кому: {transaction[1]} | Стоимость: {transaction[2]} | Цифровая подпись: {transaction[3]}"
                data = data + '\n' +transaction_data
        return data
    def get_balance(address):
        balance = 0
        for block in blockchain:
            for transaction in block[2]:
                if transaction[0] == address:
                    balance = balance + float(transaction[2]) * -1
                if transaction[1] == address:
                    balance = balance + float(transaction[2])
        data = f"Баланс адреса {address}: {balance}"
        return data

    def get_balance_raw(address,blockchain_=blockchain):
        balance = 0.0
        for block in blockchain_:
            for transaction in block[2]:
                if transaction[0] == address:
                    balance = balance + float(transaction[2]) * -1
                if transaction[1] == address:
                    balance = balance + float(transaction[2])
        return balance
#block = Block()
#block.add_transaction('leemonad','leemonadick','11',None)
#blockchain.append(block.mine_block())
#block.clear_block()
#
#
##blockchain.append(block.mine_block())
##block.clear_block()
#
#
#print(blockchain)
#
#
#print('\n'*100)
##print(ConUI.get_blockchain_data())
#print(blockchain[-1])
#
#
#while 1:
#    print("\nВыберите действие: \n[1] Добавить транзакцию\n[2] Добыть блок\n[3] Отобразить блокчейн")
#
#    k = input()
#    if k == "1":
#        print("Введите транзакцию [отправитель получатель количество], разделяйте значения пробелом")
#        transaction_new = input().split()
#        transaction_new[2] = float(transaction_new[2])
#        block.add_transaction(transaction_new[0],transaction_new[1],transaction_new[2],'none')
#        os.system('cls')
#    if k == "2":
#        blockchain.append(block.mine_block())
#        block.clear_block()
#        os.system('cls')
#    if k == "3":
#        print(ConUI.get_blockchain_data())