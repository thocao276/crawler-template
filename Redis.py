import os.path
import urllib.parse

import redis
import zlib

from tqdm import tqdm


class RedisCustom:
    def __init__(self, host='localhost', port=6379, db=1):
        self.redis = redis.Redis(host=host, port=port, db=db)

    def string_compress(self, content):
        return zlib.compress(content.encode())

    def string_decompress(self, content):
        return zlib.decompress(content).decode()

    def string_hashed(self, content):
        return content
        # return hashlib.md5(content)

    def hash_is_exist(self, name, key_hashed):
        if self.redis.hexists(name, key_hashed):
            return True
        return False

    def list_add_left(self, name, data):
        self.redis.lpush(name, data)

    def list_add_right(self, name, data):
        self.redis.rpush(name, data)

    def list_pop_right(self, name):
        return self.redis.rpop(name)

    def list_pop_left(self, name):
        return self.redis.lpop(name)

    def list_len(self, name):
        return self.redis.llen(name)

    def hash_add(self, name, diction: dict):
        for i, v in diction.items():
            self.redis.hset(name, key=i, value=v)

    def hash_get(self, name, key):
        return self.redis.hget(name, key).decode()

    def hash_get_all_keys(self, name):
        return self.redis.hkeys(name)

    def set_add(self, name, key):
        self.redis.sadd(name, key)

    def set_is_exist(self, name, key):
        if self.redis.sismember(name, key) == 1:
            return True
        return False

    def copy_all_hash_to(self, source_name, destination_name):
        for key in tqdm(self.hash_get_all_keys(source_name), position=0):
            value = self.hash_get(source_name, key)
            key = key.decode()
            if key[0] == "/":
                key = urllib.parse.urljoin("http://tuoitre.vn", key)
            try:
                self.hash_add(destination_name, {key: value})
            except Exception as e:
                print("[ERROR]: ", e)

    def dump_to_file(self, name, file_name):
        if not os.path.isfile(file_name):
            raise FileNotFoundError
        storage = list()
        try:
            for key in tqdm(self.hash_get_all_keys(name), position=0):
                value = self.hash_get(name, key)
                storage.append(value)
        except Exception as e:
            print(e)
            with open(file_name, "w+") as fw:
                for i in storage:
                    fw.write(i + "\n")
        with open(file_name, "w+") as fw:
            for i in storage:
                fw.write(i + "\n")

    def format_set(self, name, newname):
        all_key = list(self.redis.smembers(name))
        for k in tqdm(all_key, position=0):
            k = k.decode()
            v = urllib.parse.urljoin("http://tuoitre.vn", k)
            REDIS_CUSTOM.set_add(newname, v)

    def format_hash(self, name, newname):
        for key in tqdm(self.hash_get_all_keys(name), position=0):
            value = self.hash_get(name, key).strip()
            key = key.decode()
            if len(value.strip()) > 0:
                if key[0] == "/":
                    key = urllib.parse.urljoin("http://tuoitre.vn", key)
                try:
                    self.hash_add(newname, {key: value})
                except Exception as e:
                    print("[ERROR]: ", e)


REDIS_CUSTOM = RedisCustom(host="localhost", port=6379, db=0)

# if __name__ == "__main__":
    # REDIS_CUSTOM.format_hash("keywords", "keywords2")
    # compress_str = REDIS_CUSTOM.compress_str("rác quảng cáo, rao vặt tín dụng đen tại cột điện 52, trong rất mất mỹ quan thành phố. kính mong cơ quan chức năng xử lý")
    # decom = REDIS_CUSTOM.decompress_str(compress_str)
    # print(compress_str, decom)

    # REDIS_CUSTOM.format_hash("keywords", "keywords2")
    # for ar in range(3, 8):
    #     REDIS_CUSTOM.copy_all_hash_to(f"article{ar}", "backup")

    # REDIS_CUSTOM.copy_all_hash_to("article", "backup")

    # REDIS_CUSTOM.dump_to_file("backup", "../resource/backup.txt")

    # for key in tqdm(REDIS_CUSTOM.hash_get_all_keys("backup"), position=0):
    #     key = key.decode()
    #     if key[0] == "/":
    #         key = urllib.parse.urljoin("http://tuoitre.vn", key)
    #     try:
    #         REDIS_CUSTOM.set_add("visited", key)
    #     except Exception as e:
    #         print("[ERROR]: ", e)
    #
