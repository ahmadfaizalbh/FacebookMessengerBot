from chatbot import Chat,reflections,multiFunctionCall
import wikipedia

def whoIs(query,session_id="general"):
    try:
        return wikipedia.summary(query)
    except:
        for newquery in wikipedia.search(query):
            try:
                return wikipedia.summary(newquery)
            except:
                pass
    return "I don't know about "+query
        
    

call = multiFunctionCall({"whoIs":whoIs})
firstQuestion="Hi, how are you?"
chat=Chat("Example.template", reflections,call=call)

sender_id="1,2,3"
chat._startNewSession(sender_id)             
chat.conversation[sender_id].append('Say "Hello"')
#firstQuestion='Say "Hello"'
#chat.converse(firstQuestion,session_id=sender_id)
message=""
while message!="bye":
    message=raw_input(">")
    chat.conversation[sender_id].append(message)
    result = chat.respond(message,session_id=sender_id)               
    chat.conversation[sender_id].append(result)
    print result
