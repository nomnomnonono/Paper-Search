import os

import arxiv
import numpy as np
import polars as pl
from omegaconf import OmegaConf
from sentence_transformers import SentenceTransformer


def scrape_paper(config):
    for tag in config.paper_tags:
        search = arxiv.Search(
            query=f"cat:{tag} AND ti:fair",
            max_results=10000,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )

        authors, titles, abstracts, links, years, months = [], [], [], [], [], []
        for result in search.results():
            authors.append(str(result.authors[0]))
            titles.append(result.title)
            abstracts.append(result.summary)
            links.append(str(result.links[0]))
            year, month, _ = str(result.published).split(" ")[0].split("-")
            years.append(year)
            months.append(month)

        df = pl.DataFrame(
            {
                "title": titles,
                "abstract": abstracts,
                "author": authors,
                "year": years,
                "month": months,
                "link": links,
            }
        )

        df.write_csv(f"{config.path_data}/paper_{tag}.csv")
        print(f"GET {tag}: {len(df)} Papers !!")


def unite_tag(config):
    df = None
    for tag in config.paper_tags:
        if df is None:
            df = pl.read_csv(f"{config.path_data}/paper_{tag}.csv")
        else:
            tmp = pl.read_csv(f"{config.path_data}/paper_{tag}.csv")
            df.extend(tmp)

    df = df.unique(subset="title")
    df.write_csv(f"{config.path_data}/paper.csv")
    print(f"TOTAL: {len(df)} Papers")


def create_embed(config):
    df = pl.read_csv(f"{config.path_data}/paper.csv")
    model = SentenceTransformer(config.bert_model)

    for col in ["title", "abstract"]:
        embed = model.encode(df[col].to_list())
        np.save(f"{config.path_data}/{col}_embed.npy", embed)


def main():
    config = OmegaConf.load("config.yaml")
    os.makedirs(config.path_data, exist_ok=True)
    scrape_paper(config)
    unite_tag(config)
    create_embed(config)


if __name__ == "__main__":
    main()
