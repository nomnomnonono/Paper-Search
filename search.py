import os

import numpy as np
import pandas as pd  # can't use polars
import pymysql.cursors
from omegaconf import OmegaConf
from sentence_transformers import SentenceTransformer


class Search:
    def __init__(self, config: str) -> None:
        """
        初期設定を行う

        Args:
            config (str): 設定ファイルパス
        """

        self.config = OmegaConf.load(config)
        self.model = SentenceTransformer(self.config.bert_model)
        self.category = "Fairness"
        self.title_embed = np.load(
            os.path.join(self.config.path_data, f"{self.category}_title_embed.npy")
        )
        self.abst_embed = np.load(
            os.path.join(self.config.path_data, f"{self.category}_abstract_embed.npy")
        )

    def setup(self, category: str) -> None:
        """
        選択されたカテゴリー用のファイルを読み込む

        Args:
            category (str): 論文カテゴリー
        """

        self.category = category
        self.title_embed = np.load(
            os.path.join(self.config.path_data, f"{self.category}_title_embed.npy")
        )
        self.abst_embed = np.load(
            os.path.join(self.config.path_data, f"{self.category}_abstract_embed.npy")
        )

    def search_title(self, title: str, top: str) -> pd.DataFrame:
        """
        類似タイトルの論文検索を行う

        Args:
            title (str): 論文タイトル
            top (str): 上位何件取得するか

        Returns:
            pd.DataFrame: 検索結果
        """

        pred = self.model.encode([title]).squeeze()
        prob = np.dot(self.title_embed, pred)
        rank = np.argsort(prob)[::-1][0 : int(top)]
        return self.save_as_dataframe(rank)

    def search_abst(self, abst: str, top: str) -> pd.DataFrame:
        """
        類似アブストラクトの論文検索を行う

        Args:
            title (str): 論文アブストラクト
            top (str): 上位何件取得するか

        Returns:
            pd.DataFrame: 検索結果
        """

        pred = self.model.encode([abst]).squeeze()
        prob = np.dot(self.abst_embed, pred)
        rank = np.argsort(prob)[::-1][0 : int(top)]
        return self.save_as_dataframe(rank)

    def search_keyword(
        self, key1: str, key2: str, key3: str, target: str, top: str
    ) -> pd.DataFrame:
        """
        キーワードによる論文検索を行う

        Args:
            key1 (str): 1つ目のキーワード
            key2 (str): 2つ目のキーワード
            key3 (str): 3つ目のキーワード
            target (str): 検索対象（タイトル or アブストラクト）
            top (str): 上位何件取得するか

        Returns:
            pd.DataFrame: 検索結果
        """

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

    def save_as_dataframe(self, rank: str) -> pd.DataFrame:
        """
        SQLの問い合わせ結果をpd.DataFrame形式で出力する

        Args:
            rank (str): 上位何件を取得するか

        Returns:
            pd.DataFrame: 検索結果
        """

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
            df.loc[idx] = {
                "title": result["title"],
                "url": result["link"],
            }

        return df
