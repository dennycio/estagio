from fastapi import APIRouter, HTTPException
import requests

api_router = APIRouter()

# Sua chave da NewsAPI
NEWS_API_KEY = "640ff9e0afe54964af0b37485de0c22f"
NEWS_API_URL = "https://newsapi.org/v2/everything"


@api_router.get("/")
def read_root():
    return {"message": "Bem-vindo à API com NewsAPI!"}


@api_router.get("/news/")
def get_news(query: str):
    """
    Consulta notícias com base em um termo de busca.
    :param query: Termo de busca (palavra-chave).
    :return: Lista de artigos relacionados ao termo.
    """
    params = {
        "q": query,
        "apiKey": NEWS_API_KEY
    }
    response = requests.get(NEWS_API_URL, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Erro ao consultar NewsAPI")

    data = response.json()
    articles = [
        {"title": article["title"], "url": article["url"]}
        for article in data.get("articles", [])
    ]

    return {"query": query, "articles": articles}
