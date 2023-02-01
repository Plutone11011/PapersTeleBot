

def format_response(results: dict) -> list[str]:

    text = ''
    message_sections_order = ["title", "keyphrases", "url"]
    
    for message_section in message_sections_order:
        
        if message_section not in results or results[message_section] is None:
            continue

        if message_section == 'title':
            text += f'<b>{results["title"]}</b>'
    
        elif message_section == 'keyphrases':
            #text += "*Keywords*\n"
            #text += f'_{", ".join(results[message_section])}_'
            text += "<b>Keywords</b>\n"
            text += f'<i>{", ".join(results[message_section])}</i>'

        #elif message_section == 'abstract':
        #    text += results["abstract"] 
            
        elif message_section == 'url':
            #text += f'[PDF]({results["url"]})'
            text += f'{results["url"]}'

        text += "\n\n"
    # telegram has a max length for a single message
    # so we truncate the abstract in different text chunks
    max_length_telegram_message = 4096
    n_iter = (len(text) // max_length_telegram_message) + 1
    response = []
    for i in range(n_iter):
        response.append(text[max_length_telegram_message * i: max_length_telegram_message * (i+1)])

    return response