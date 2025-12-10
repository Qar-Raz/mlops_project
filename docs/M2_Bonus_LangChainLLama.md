# BONUS: LangChain Toolchains & Custom Retrievers

### Hybrid Ensemble Retriever
The system combines two retrieval methods:

- **BM25 (Sparse):** Exact keyword match
- **Chroma Dense Retriever:** Semantic search

Weighted combination: **[0.4 (BM25), 0.6 (Dense)]**

### Code Snippet
```python
bm25_retriever = BM25Retriever.from_documents(docs)
bm25_retriever.k = 3

chroma_retriever = vectordb.as_retriever(search_kwargs={"k": 3})

ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, chroma_retriever],
    weights=[0.4, 0.6]
)

results = ensemble_retriever.invoke(test_query)
```
