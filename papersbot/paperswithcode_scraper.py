import aiohttp
import asyncio
from bs4 import BeautifulSoup

async def fetch_html(session, url):
    async with session.get(url) as response:
        return await response.text()

async def get_latest_papers_title(url):
    async with aiohttp.ClientSession() as session:
        html = await fetch_html(session, url)
        soup = BeautifulSoup(html, 'html.parser')
        paper_containers = soup.find_all("div", class_="paper-card")
        latest_papers = []
        for i in range(5):
            paper_title = paper_containers[i].find("h1").text
            latest_papers.append(paper_title)
        return latest_papers