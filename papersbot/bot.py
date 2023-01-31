import telebot
from dotenv import dotenv_values
from paperswithcode import PapersWithCodeClient
from datetime import datetime
import queue
import threading, time, random, signal

from extraction import KeyphraseExtractionPipeline


class PaperBot:

    def __init__(self) -> None:
        config = dotenv_values(".env")
        self.bot = telebot.TeleBot(config["BOT_API_KEY"])
        self.chat_id = self.bot.get_chat("@publicforbot").id
        self.extraction = KeyphraseExtractionPipeline("ml6team/keyphrase-extraction-kbir-inspec") # first time, download takes a while
        
        
        self.queue = queue.Queue()
        self.event_post = threading.Event()
        self.event_paperscode = threading.Event()
        self.post_thread = threading.Thread(target=self.post_paper)
        self.post_thread.start()
        self.paperscode_thread = threading.Thread(target=self.poll_papers)
        self.paperscode_thread.start()
        
        
        self.bot.infinity_polling()

    def post_paper(self):    
        while not self.event_post.wait(20):
            try:
                print('Checking queue')
                msg = self.queue.get_nowait()
                self.bot.send_message(self.chat_id, " ".join(msg)) 
                # time.sleep(86400) # sleep a day
            except queue.Empty:
                print("No message yet")
                

    def poll_papers(self):
        while not self.event_paperscode.wait(60):   
            client = PapersWithCodeClient()
            papers = client.paper_list()
            today = datetime.today()

            current_paper = None
            for paper in papers.results:
                if today.year == paper.published.year and today.month == paper.published.month and today.day == paper.published.day:
                    current_paper = paper
                    break
            if current_paper is not None:
                keyphrases = self.extraction.inference_abstract(paper.abstract)
                self.queue.put(keyphrases)    
            else:
                # pick random paper 
                n = random.randint(0, len(papers.results) - 1)
                keyphrases = self.extraction.inference_abstract(papers.results[n].abstract)
                print(keyphrases)
                self.queue.put(keyphrases)


    

if __name__ == '__main__':
    paperbot = PaperBot()

    def stop(signum, frame):
        print(signum)
        paperbot.event.set()
        paperbot.post_thread.join()
        paperbot.paperscode_thread.join()
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

