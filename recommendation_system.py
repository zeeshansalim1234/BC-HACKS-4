import json
import os
import pickle
import torch
from sentence_transformers import SentenceTransformer, util

with open('papers.json') as fin:
  papers = json.load(fin)

model = SentenceTransformer('allenai-specter')
#To encode the papers, we must combine the title and the abstracts to a single string
paper_texts = [paper['title'] + '[SEP]' + paper['abstract'] for paper in papers]

#Compute embeddings for all papers
corpus_embeddings = model.encode(paper_texts, convert_to_tensor=True)

with open('model','wb') as f:
  pickle.dump(model,f)

torch.save(corpus_embeddings, 'tensor_research_papers.pt')