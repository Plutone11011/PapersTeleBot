from telebot.async_telebot import AsyncTeleBot
from dotenv import dotenv_values
from paperswithcode import PapersWithCodeClient
from datetime import datetime
import random, asyncio

from extraction import KeyphraseExtractionPipeline
from format import format_response
          

def poll_papers():
    extraction = KeyphraseExtractionPipeline("ml6team/keyphrase-extraction-kbir-inspec") # first time, download takes a while
    client = PapersWithCodeClient()
    papers = client.paper_list()
    today = datetime.today()

    current_paper = None
    # keep only papers with a dataset
    # filters math, physics and other papers
    papers = [paper for paper in papers.results if len(client.paper_dataset_list(paper.id).results) > 0]
    for paper in papers:
            if today.year == paper.published.year and today.month == paper.published.month and today.day == paper.published.day:
                current_paper = paper
                break
    if current_paper is not None:
        keyphrases = extraction.inference_abstract(current_paper.abstract)    
    else:
        # pick random paper 
        n = random.randint(0, len(papers) - 1)
        current_paper = papers[n]
        keyphrases = extraction.inference_abstract(current_paper.abstract)

    return {
            "title": current_paper.title,
            "keyphrases": keyphrases,
            "url": current_paper.url_pdf
    }
        
        #bot.send_message(self.chat_id, " ".join(keyphrases)) 


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
            results = self.func()
            response = format_response(results)
            print(response)
            for chunk in response:
                await bot.send_message("@publicforbot", chunk, parse_mode='MarkdownV2') 

async def start_periodic(bot):
    
    task = PeriodicBotTask(poll_papers, 10, bot)
    await task.start()
    
async def main(bot):
    try:
        await asyncio.gather(bot.infinity_polling(), start_periodic(bot))
    except Exception as e:
        print(e)
    
if __name__ == '__main__':
    config = dotenv_values(".env")
    bot = AsyncTeleBot(config["BOT_API_KEY"])
    
    #asyncio.run(bot.polling())
    loop = asyncio.get_event_loop()
    #_main = main(bot)
    loop.run_until_complete(main(bot))
    
    

