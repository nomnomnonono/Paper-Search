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
            ["title", "author", "link"]
        ]
        self.model = SentenceTransformer(self.config.bert_model)

    def search_title(self, title, top):
        pred = self.model.encode([title]).squeeze()
        prob = np.dot(self.title_embed, pred)
        rank = np.argsort(prob)[::-1]
        return self.df.iloc[rank[0 : int(top)]]

    def search_abst(self, abst, top):
        pred = self.model.encode([abst]).squeeze()
        prob = np.dot(self.abst_embed, pred)
        rank = np.argsort(prob)[::-1]
        print(rank)
        return self.df.iloc[rank[0 : int(top)]]
