import numpy as np
import os
import polars as pl
from omegaconf import OmegaConf
from sentence_transformers import SentenceTransformer


class Search:
    def __init__(self, config):
        self.config = OmegaConf.load(config)
        self.title_embed = np.load(os.path.join(self.config.path_data, "title_embed.npy"))
        self.abst_embed = np.load(os.path.join(self.config.path_data, "abstract_embed.npy"))
        self.df = pl.read_csv(os.path.join(self.config.path_data, "paper.csv"))
        self.model = SentenceTransformer(self.config.bert_model)
    
    def search(self, sentence, method, top):
        if method == "title":
            self._search_title(sentence, top)
        elif method == "abstract":
            self._search_abst(sentence, top)
        elif method == "keyword":
            self._search_keyword(sentence, top)
        else:
            raise ValueError("Unknown Search Method.")
    
    def _search_title(self, title, top):
        embed = self.model.encode([title])
        prob = np.dot(self.title_embed, embed)
        rank = np.sort(prob)[::-1]
        return self.df[rank[0:top]]

    def _search_abst(self, abst, top):
        embed = self.model.encode([abst])
        prob = np.dot(self.abst_embed, embed)
        rank = np.sort(prob)[::-1]
        return self.df[rank[0:top]]

    def _search_keyword(self, keyword, top):
        keywords = keyword.split(" ")
