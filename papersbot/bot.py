from telebot.async_telebot import AsyncTeleBot
from dotenv import dotenv_values
from paperswithcode import PapersWithCodeClient
import json, asyncio, re, os
from telebot.formatting import escape_markdown

from extraction import KeyphraseExtractionPipeline
from formatting import format_response
from paperswithcode_scraper import get_latest_papers_title

async def poll_papers():

    latest_papers_title = await get_latest_papers_title("https://paperswithcode.com/latest")
    # filter out papers with math formula in titles since it is
    # not possible to render latex natively in telegram
    math_reg = r'\$.+?\$'
    latest_papers_title = [paper_title for paper_title in latest_papers_title if re.match(math_reg, paper_title) is None]
    
    # find out the paper
    # to send to telegram
    history_papers_filename = "history_papers.json"
    if not os.path.exists(history_papers_filename):
        with open(history_papers_filename, "w") as history_paper_file:
            json.dump({"history": []}, history_paper_file)
    
    current_paper_title = None
    history_papers = []
    with open(history_papers_filename, "r") as history_paper_file:
        history_papers = json.load(history_paper_file).get("history")
        if len(history_papers) > 0:
            for latest_paper_title in latest_papers_title:
                if latest_paper_title not in history_papers:
                    current_paper_title = latest_paper_title
                    
        else:
            current_paper_title = latest_papers_title[0]
    if current_paper_title is not None:
        with open(history_papers_filename, "w") as history_paper_file:
            json.dump({"history": history_papers + [current_paper_title]}, history_paper_file)
        
        
        client = PapersWithCodeClient()
        
        papers_page = client.paper_list(q=f"{current_paper_title}")
        
        current_paper = papers_page.results[0]    
        extraction = KeyphraseExtractionPipeline("ml6team/keyphrase-extraction-kbir-inspec") # first time, download takes a while
        keyphrases = extraction.inference_abstract(current_paper.abstract)

        return {
                "title": current_paper_title,
                "keyphrases": keyphrases,
                "url": current_paper.url_pdf
        }
    else:
        # every latest paper returned by the scraper
        # is already in the history, so no new paper today
        # might randomize (?)
        return {
            "title": "",
            "keyphrases": [],
            "url": "",
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
            if results["title"] and len(results["keyphrases"]) and results["url"]:
                text = format_response(results)
            else:
                text = escape_markdown("No new paper today.\n")
            await bot.send_message("@publicforbot", text, parse_mode='MarkdownV2') 

async def start_periodic(bot):
    
    task = PeriodicBotTask(poll_papers, 10, bot)
    await task.start()
    
    
if __name__ == '__main__':
    config = dotenv_values(".env")
    bot = AsyncTeleBot(config["BOT_API_KEY"])
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(bot.infinity_polling(), start_periodic(bot)))
    
    

