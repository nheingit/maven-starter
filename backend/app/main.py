from fastapi import FastAPI

from bs4 import BeautifulSoup
from typing import List

app = FastAPI()

def crawl_hexdocs(url: str) -> List[dict]:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    content_sections = []

    for section in soup.find_all(['h1', 'h2', 'h3', 'p', 'pre']):
        text = section.get_text(separator=' ', strip=True)
        if text:
            content_sections.append({
                'tag': section.name,
                'text': text,
                'link': url + '#' + section.get('id', ''),
            })
    return content_sections