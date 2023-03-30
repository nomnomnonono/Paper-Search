import os

import numpy as np
import pandas as pd  # can't use polars
from omegaconf import OmegaConf
from sentence_transformers import SentenceTransformer


class Search:
    def __init__(self, config):
        self.config = OmegaConf.load(config)
        self.title_embed = np.load(
            os.path.join(self.config.path_data, "title_embed.npy")
        )
        self.abst_embed = np.load(
            os.path.join(self.config.path_data, "abstract_embed.npy")
        )
        self.df = pd.read_csv(os.path.join(self.config.path_data, "paper.csv"))[
            ["title", "abstract", "link"]
        ]
        self.model = SentenceTransformer(self.config.bert_model)

    def search_title(self, title, top):
        pred = self.model.encode([title]).squeeze()
        prob = np.dot(self.title_embed, pred)
        rank = np.argsort(prob)[::-1]
        return self.df.iloc[rank[0 : int(top)]][["title", "link"]]

    def search_abst(self, abst, top):
        pred = self.model.encode([abst]).squeeze()
        prob = np.dot(self.abst_embed, pred)
        rank = np.argsort(prob)[::-1]
        return self.df.iloc[rank[0 : int(top)]][["title", "link"]]

    def search_keyword(self, key1, key2, key3, target, top):
        keyword_counts = []
        for i in range(len(self.df)):
            line = self.df.iloc[i][target.lower()].lower()
            count = 0
            for keyword in [key1, key2, key3]:
                if keyword.lower() in line:
                    count += 1
            keyword_counts.append(count)
        rank = np.argsort(np.array(keyword_counts))[::-1]
        return self.df.iloc[rank[0 : int(top)]][["title", "link"]]
