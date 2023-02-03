import aiohttp
import asyncio
from bs4 import BeautifulSoup

async def fetch_html(session, url):
    async with session.get(url) as response:
        return await response.text()

async def get_latest_papers_title(url, start=0, end=5):
    async with aiohttp.ClientSession() as session:
        html = await fetch_html(session, url)
        soup = BeautifulSoup(html, 'html.parser')
        paper_containers = soup.find_all("div", class_="paper-card")
        latest_papers_title = []
        for latest_paper in paper_containers:
            paper_title = latest_paper.find("h1").text
            latest_papers_title.append(paper_title)
        return latest_papers_title