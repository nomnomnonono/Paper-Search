import os

import numpy as np
import pandas as pd  # can't use polars
import pymysql.cursors
from omegaconf import OmegaConf
from sentence_transformers import SentenceTransformer


class Search:
    def __init__(self, config):
        self.config = OmegaConf.load(config)
        self.model = SentenceTransformer(self.config.bert_model)
        self.category = "Fairness"
        self.title_embed = np.load(
            os.path.join(self.config.path_data, f"{self.category}_title_embed.npy")
        )
        self.abst_embed = np.load(
            os.path.join(self.config.path_data, f"{self.category}_abstract_embed.npy")
        )

    def setup(self, category):
        self.category = category
        self.title_embed = np.load(
            os.path.join(self.config.path_data, f"{self.category}_title_embed.npy")
        )
        self.abst_embed = np.load(
            os.path.join(self.config.path_data, f"{self.category}_abstract_embed.npy")
        )

    def search_title(self, title, top):
        pred = self.model.encode([title]).squeeze()
        prob = np.dot(self.title_embed, pred)
        rank = np.argsort(prob)[::-1][0 : int(top)]
        return self.save_as_dataframe(rank)

    def search_abst(self, abst, top):
        pred = self.model.encode([abst]).squeeze()
        prob = np.dot(self.abst_embed, pred)
        rank = np.argsort(prob)[::-1][0 : int(top)]
        return self.save_as_dataframe(rank)

    def search_keyword(self, key1, key2, key3, target, top):
        counts = np.zeros(len(self.title_embed))

        for keyword in [key1, key2, key3]:
            connection = pymysql.connect(
                host="localhost",
                user="root",
                password=self.config.password,
                database="paper",
                cursorclass=pymysql.cursors.DictCursor,
            )

            with connection:
                with connection.cursor() as cursor:
                    sql = f"select id, title, link from {self.category} \
                            where {target} like '%{keyword}%'"
                    cursor.execute(sql)

            rows = cursor.fetchall()

            for row in rows:
                counts[row["id"] - 1] += 1

        rank = np.argsort(np.array(counts))[::-1][0 : int(top)]
        return self.save_as_dataframe(rank)

    def save_as_dataframe(self, rank):
        connection = pymysql.connect(
            host=self.config.host,
            user="root",
            password=self.config.password,
            database="paper",
            cursorclass=pymysql.cursors.DictCursor,
        )

        with connection:
            with connection.cursor() as cursor:
                s = ""
                for x in rank:
                    s += "id=" + str(x + 1) + " OR "

                sql = (
                    f"SELECT id, title, author, link FROM {self.category} WHERE "
                    + s.removesuffix(" OR ")
                )
                cursor.execute(sql)

        rows = cursor.fetchall()

        dict = {}
        for i in range(len(rank)):
            dict[rank[i] + 1] = i

        result_list = sorted(rows, key=lambda x: dict[x["id"]])

        df = pd.DataFrame([], columns=["title", "url"])
        for idx, result in enumerate(result_list):
            df.loc[idx] = (
                {
                    "title": result["title"],
                    "url": result["link"],
                }
            )

        return df
