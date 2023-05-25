import os

import arxiv
import numpy as np
import pymysql.cursors
from omegaconf import OmegaConf
from sentence_transformers import SentenceTransformer


class Scraper:
    def __init__(self, config: str) -> None:
        """
        初期設定を行う

        Args:
            config (str): 設定ファイルパス
        """

        self.config = OmegaConf.load(config)
        os.makedirs(self.config.path_data, exist_ok=True)

    def run(self) -> None:
        """実行関数"""

        self.create_database()
        self.scrape_paper()
        self.create_embed()

    def create_database(self) -> None:
        """論文情報用のデータベースを作成する"""

        connection = pymysql.connect(
            user="root",
            password=self.config.password,
            host=self.config.host,
        )

        with connection:
            with connection.cursor() as cursor:
                cursor.execute("CREATE DATABASE paper")

                for category in self.config.category:
                    cursor.execute(
                        f"""
                        CREATE TABLE paper.{category} (
                        id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
                        title VARCHAR(200),
                        abstract TEXT,
                        author VARCHAR(50),
                        year INT,
                        month INT,
                        link VARCHAR(100)
                        );
                        """
                    )

                connection.commit()

        cursor.close()

    def scrape_paper(self) -> None:
        """論文情報をarxivからスクレイピングする"""

        tags = " OR ".join(self.config.paper_tags)
        for category in self.config.category:
            data = []
            search = arxiv.Search(
                query=f"({tags}) AND ti:{category}",
                max_results=10000,
                sort_by=arxiv.SortCriterion.SubmittedDate,
            )

            for result in search.results():
                year, month, _ = str(result.published).split(" ")[0].split("-")
                data.append(
                    (
                        result.title.replace("'", "").replace('"', ""),
                        result.summary.replace("'", "").replace('"', ""),
                        str(result.authors[0]),
                        int(year),
                        int(month),
                        str(result.links[0]),
                    ),
                )

            connection = pymysql.connect(
                host=self.config.host,
                user="root",
                password=self.config.password,
                database="paper",
                cursorclass=pymysql.cursors.DictCursor,
            )

            with connection:
                with connection.cursor() as cursor:
                    sql = (
                        f"INSERT INTO {category} (title, abstract, author, year, month, link)"
                        + " VALUES ('%s', '%s', '%s', '%d', '%d', '%s')"
                    )

                    for i in range(len(data)):
                        try:
                            cursor.execute(sql % data[i])
                        except Exception:
                            pass

                    connection.commit()

            print(f"{category} Paper: Get {len(data)} !!")

    def create_embed(self) -> None:
        """論文タイトルとアブストラクトの埋め込みベクトルを作成する"""

        model = SentenceTransformer(self.config.bert_model)

        for category in self.config.category:
            connection = pymysql.connect(
                host=self.config.host,
                user="root",
                password=self.config.password,
                database="paper",
                cursorclass=pymysql.cursors.DictCursor,
            )

            with connection:
                with connection.cursor() as cursor:
                    sql = """
                    SELECT title, abstract FROM Fairness;
                    """
                    cursor.execute(sql)

                    titles, abstracts = [], []
                    for row in cursor:
                        title, abstract = row.values()
                        titles.append(title)
                        abstracts.append(abstract)
                    title_embed = model.encode(titles)
                    abstract_embed = model.encode(abstracts)
                    np.save(
                        f"{self.config.path_data}/{category}_title_embed.npy",
                        title_embed,
                    )
                    np.save(
                        f"{self.config.path_data}/{category}_abstract_embed.npy",
                        abstract_embed,
                    )


def main(config: str) -> None:
    """
    論文情報収集スクリプト実行関数

    Args:
        config (str): 設定ファイルパス
    """

    scraper = Scraper(config)
    scraper.run()


if __name__ == "__main__":
    main("config.yaml")
