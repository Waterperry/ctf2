#!/usr/bin/env python

# This is a dummy script to demo a possible solution to the problem.
# The solution is not complete, but clearly indicates the region to explore
#    to find the actual solution in reasonable time on old hardware (<15 seconds).

import random

from datetime import datetime, timedelta

import torch

from plotly import express as px
from transformers import AutoTokenizer, AutoModel, PreTrainedTokenizerFast, PreTrainedModel


def cosine_sim(t1, t2):
    denom = torch.linalg.norm(t1) * torch.linalg.norm(t2) + 1e-8
    return torch.dot(t1, t2) / denom

tokenizer: PreTrainedTokenizerFast = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model: PreTrainedModel = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")


def nan_safe_mean_pool(embs: torch.Tensor, attn_mask: torch.Tensor) -> torch.Tensor:
    attn_mask = attn_mask.squeeze()
    assert len(attn_mask.shape) == 1
    masked_emb = embs[attn_mask.bool()].squeeze()
    return masked_emb.nanmean(0)


@torch.no_grad
def embed(s: str) -> torch.Tensor:
    global tokenizer, model
    tokenized = tokenizer(s, return_tensors="pt", truncate=True, padding="longest")
    out = model(**tokenized).last_hidden_state.squeeze()
    return nan_safe_mean_pool(out, tokenized["attention_mask"])


# recover DOB from embedding
d1 = "1322-10-22"
date_string = "%d/%m/%Y"
# date_string = "%Y-%m-%d"

year = 1322
month = 10
day = 22

print(year, month, day)
tgt = embed(d1)

with open("target.pt", "wb") as f:
    torch.save(tgt, f)

tokenizer.save_pretrained("./tokenizer")
model.save_pretrained("./model")

dates = []
for y in range(year - 100, year + 100, 10):
    dates.append(datetime(y, 1, 1))
    try:
        dates.append(datetime(y, random.randint(1, 12), random.randint(1, 31)))
    except ValueError:
        pass
for m in range(1, 13):
    dates.append(datetime(year, m, 1))
    try:
        dates.append(datetime(year, m, random.randint(1, 31)))
    except ValueError:
        pass
for d in range(1, 32):
    dates.append(datetime(year, month, d))

dates.sort()
embs = [embed(date.strftime(date_string)) for date in dates]
sims = [cosine_sim(e, tgt) for e in embs]

dataset = [
    {
        "datetime": d,
        "sim": float(sim),
    }
    for d, sim in zip(dates, sims)
]
fig = px.line(dataset, "datetime", "sim")
fig.write_html("./plot.html")
fig.write_image("./plot.jpg")
