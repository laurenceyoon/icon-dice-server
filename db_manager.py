import leveldb
import json


class UserManager:
    def __init__(self, db_path):
        self.users_dict = dict()
        self.db = leveldb.LevelDB(db_path)


class DBManager:
    def __init__(self, db_path):
        self.__db = leveldb.LevelDB(db_path)
        self.__user_data = dict()  # {address: {'token': [token], 'username': [username]}}

    def __update_user_data_from_db(self):
        self.__data = {address.decode('utf-8'): json.loads(info.decode('utf-8'))
                       for address, info in self.__db.RangeIter()}

    def get_tokens(self) -> list:
        []

    def get_addresses(self) -> list:
        return list(self.__user_data)

    def add_token(self, address, token):
        additional_info = json.dumps({
            'token': token,
            'username': address
        })
        self.__db.Put(address.encode('utf-8'),
                      additional_info.encode('utf-8'))
        self.__update_user_data_from_db()

    def add_username(self, address, username):
        pass
