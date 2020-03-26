from chatbot import Chat, register_call
import wikipedia

@register_call("whoIs")
def who_is(query,session_id="general"):
    try:
        return wikipedia.summary(query)
    except:
        for newquery in wikipedia.search(query):
            try:
                return wikipedia.summary(newquery)
            except:
                pass
    return "I don't know about "+query


chat=Chat("Example.template")

sender_id="1,2,3"
chat.start_new_session(sender_id)
chat.conversation[sender_id].append('Say "Hello"')

message=""
while message!="bye":
    message=input(">")
    chat.conversation[sender_id].append(message)
    result = chat.respond(message,session_id=sender_id)
    chat.conversation[sender_id].append(result)
    print(result)
