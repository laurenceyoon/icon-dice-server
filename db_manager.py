import leveldb
import json
from config import CONFIG


class DBManager:
    def __init__(self, db: leveldb.LevelDB):
        self.__db = db
        self.__user_data = dict()  # {address: {'token': [token], 'nickname': [nickname]}}
        self.__update_user_data_from_db()

    def __update_user_data_from_db(self):
        self.__user_data = {address.decode('utf-8'): json.loads(info.decode('utf-8'))
                            for address, info in self.__db.RangeIter()}

    def get_tokens(self) -> list:
        tokens = [info['token'] for address, info in self.__user_data.items()]
        return tokens

    def get_addresses(self) -> list:
        return list(self.__user_data)

    def add_user(self, address, token, nickname=''):
        additional_info = json.dumps({
            'token': token,
            'nickname': nickname
        })
        self.__db.Put(address.encode('utf-8'),
                      additional_info.encode('utf-8'))
        self.__update_user_data_from_db()

    def get_nickname_by_address(self, address):
        return self.__user_data[address]['nickname']


DB = leveldb.LevelDB(CONFIG.db_path)
db_manager = DBManager(DB)
