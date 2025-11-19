import os

import pandas
import numpy as np
import psycopg2 as pg
from pydantic import BaseModel
from tqdm import tqdm

from llm import prompt
from llm.categories import category_mapper

# Lazy import do OpenAI para evitar erro de inicialização
try:
    from openai import OpenAI
    client = OpenAI()
except Exception as e:
    print(f"⚠️  OpenAI não disponível: {e}")
    client = None


class AdTheme(BaseModel):
    category: int


def classify_ad(title, tag):
    if client is None:
        print("⚠️  OpenAI não disponível, retornando classificação padrão")
        return 0, "Não classificado"
        
    tag = tag or ""
    full_prompt = prompt.content.format(title=title, tag=tag)
    
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.0,
            response_format=AdTheme,
        )
        category = completion.choices[0].message.parsed.category
        category_verbose = category_mapper(category)
        return category, category_verbose
    except Exception as e:
        print(f"⚠️  Erro na classificação OpenAI: {e}")
        return 0, "Erro na classificação"


if __name__ == "__main__":
    engine = pg.connect(os.environ.get("DATABASE_URL"))
    df = pandas.read_sql("SELECT * FROM advertisement_mv WHERE internal_url=false", con=engine)

    for index, row in enumerate(tqdm(df.itertuples())):
        if row.llm_classification is not np.nan:
            continue
        category, category_verbose = classify_ad(row.title)
        df.loc[index, "category"] = category
        df.loc[index, "category_verbose"] = category_verbose
