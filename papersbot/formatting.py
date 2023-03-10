from telebot.formatting import escape_markdown


def format_response(results: dict) -> list[str]:

    text = ''
    message_sections_order = ["title", "keyphrases", "url"]
    


    for message_section in message_sections_order:
        
        if message_section not in results or results[message_section] is None:
            continue

        if message_section == 'title':
            #text += f'<b>{results["title"]}</b>'
            text += f'*{escape_markdown(results["title"])}*'
    
        elif message_section == 'keyphrases':
            text += "*Keywords*\n"
            text += f'_{escape_markdown(", ".join(results[message_section]))}_'
            #text += "<b>Keywords</b>\n"
            #text += f'<i>{", ".join(results[message_section])}</i>'
            
        elif message_section == 'url':
            text += f'[{escape_markdown(results["url"])}]({escape_markdown(results["url"])})'
            #text += f'{results["url"]}'

        text += "\n\n"
    
    return text