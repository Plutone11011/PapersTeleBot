from telebot.async_telebot import AsyncTeleBot
from dotenv import dotenv_values
from paperswithcode import PapersWithCodeClient
from datetime import datetime
import random, asyncio, re

from extraction import KeyphraseExtractionPipeline
from formatting import format_response
from paperswithcode_scraper import get_latest_papers_title

async def poll_papers():

    latest_papers_title = await get_latest_papers_title("https://paperswithcode.com/latest")
    # filter out papers with math formula in titles since it is
    # not possible to render latex natively in telegram
    math_reg = r'\$.+?\$'
    latest_papers_title = [paper_title for paper_title in latest_papers_title if re.match(math_reg, paper_title) is None]

    
    
    client = PapersWithCodeClient()
    
    papers_page = client.paper_list(q=f"{latest_papers_title[0]}")
    
    current_paper = papers_page.results[0]    
    extraction = KeyphraseExtractionPipeline("ml6team/keyphrase-extraction-kbir-inspec") # first time, download takes a while
    keyphrases = extraction.inference_abstract(current_paper.abstract)

    return {
            "title": current_paper.title,
            "keyphrases": keyphrases,
            "url": current_paper.url_pdf
    }
        
    

class PeriodicBotTask:

    def __init__(self, func, time, bot) -> None:
        self.func = func
        self.time = time
        self.is_started = False
        self._task = None
        self.bot = bot

    async def start(self):
        if not self.is_started:
            self.is_started = True
            
            self._task = asyncio.ensure_future(self._run())

    async def stop(self):
        if self.is_started:
            self.is_started = False
            # Stop task and await it stopped:
            self._task.cancel()
            try:
                await self._task

            finally:
                self._task = None

    async def _run(self):
        while True:
            await asyncio.sleep(self.time)
            results = await self.func()
            text = format_response(results)
            await bot.send_message("@publicforbot", text, parse_mode='MarkdownV2') 

async def start_periodic(bot):
    
    task = PeriodicBotTask(poll_papers, 10, bot)
    await task.start()
    
    
if __name__ == '__main__':
    config = dotenv_values(".env")
    bot = AsyncTeleBot(config["BOT_API_KEY"])
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(bot.infinity_polling(), start_periodic(bot)))
    
    

