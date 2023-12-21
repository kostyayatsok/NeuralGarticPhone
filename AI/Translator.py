import requests
import configparser
import time
import json


class Translator:
    def __init__(self, config_file):  # 2 hours default
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.api_key = self.config["translator"]["api_key"]
        # with open(oauth_json) as f:
        #     self.oauth = json.load(f)
        # print(self.config.sections())

    #
    # def __upd_token(self):
    #     if time.time() - self.last_upd > self.upd_interval:
    #         headers = {'ContentType': 'Application/json'}
    #         url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    #         res = requests.post(url=url, headers=headers, json=self.oauth)
    #         self.last_upd = time.time()
    #         self.iam_token = json.loads(res.content.decode())["iamToken"]

    def translate(self, prompt, target_lang):
        # self.__upd_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Api-Key {0}".format(self.api_key),
        }
        body = {
            "targetLanguageCode": target_lang,
            "texts": prompt,
            "folderId": self.config["translator"]["identifier"],
        }
        response = requests.post(
            "https://translate.api.cloud.yandex.net/translate/v2/translate",
            json=body,
            headers=headers,
        )
        res_json = json.loads(response.text)
        result = [i["text"] for i in res_json["translations"]]
        return result


# trans = Translator(config_file='config2.ini')
# print(trans.translate(['Hello', 'World', 'Sleepy rabbit'], target_lang='ru'))
