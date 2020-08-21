from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from messengerbot import MessengerClient, messages
from chatbot import register_call
from django.chatbot import chat
from django.conf import settings
import json
import wikipedia
import urllib.parse
import urllib.request


# Manually initialise client
messenger = MessengerClient(access_token=settings.ACCESS_TOKEN)


def index(request):
    return render(request, "home.html")


def about(query, qtype=None):
    service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
    params = {
        'query': query,
        'limit': 10,
        'indent': True,
        'key': settings.API_KEY,
    }
    url = service_url + '?' + urllib.parse.urlencode(params)
    response = json.loads(urllib.request.urlopen(url).read())
    if not len(response['itemListElement']):
        return f"sorry, I don't know about {query}\nIf you know about {query} please tell me."
    result = ""
    if len(response['itemListElement']) == 1:
        data = response['itemListElement'][0]['result']
        if "detailedDescription" in data:
            return data['detailedDescription']["articleBody"]
        return data['name'] + " is a " + data["description"]
    for element in response['itemListElement']:
        try:
            result += element['result']['name'] + "->" + element['result']["description"]+"\n"
        except KeyError:
            pass
    return result


@register_call("tellMeAbout")
def tell_me_about(query, session_id="general"):
    return about(query)


@register_call("whoIs")
def who_is(query, session_id="general"):
    return about(query, qtype="Person")


@register_call("whereIs")
def where_is(query, session_id="general"):
    return about(query, qtype="Place")


@register_call("whatIs")
def what_is(query, session_id="general"):
    try:
        return wikipedia.summary(query)
    except Exception:
        for new_query in wikipedia.search(query):
            try:
                return wikipedia.summary(new_query)
            except Exception:
                pass
    return about(query)


def initiate_chat(sender_id):
    chat.start_new_session(sender_id)
    chat.conversation[sender_id].append('Say "Hello"')
    # Get Name of User from facebook
    url = "https://graph.facebook.com/v2.6/" + sender_id +\
          "?fields=first_name,last_name,gender&access_token=" + settings.ACCESS_TOKEN
    user_info = json.load(urllib.request.urlopen(url))
    user_info["name"] = user_info["first_name"]
    chat._memory[sender_id].update(user_info)


def respond_to_client(sender_id, message):
    recipient = messages.Recipient(recipient_id=sender_id)
    chat.attr[sender_id] = {"match": None, "pmatch": None, "_quote": False}
    chat.conversation[sender_id].append(message)
    message = message.rstrip(".! \n\t")
    result = chat.respond(message, session_id=sender_id)
    chat.conversation[sender_id].append(result)
    response = messages.MessageRequest(recipient, messages.Message(text=result))
    # send message to Messenger
    messenger.send(response)
    del chat.attr[sender_id]


def chat_handler(request):
    data = json.loads(request.body)
    # Send text message
    for i in data["entry"][0]["messaging"]:
        if "message" in i:
            sender_id = i["sender"]['id']
            if sender_id not in chat.conversation:
                # Initiate user info
                initiate_chat(sender_id)
            respond_to_client(sender_id, i["message"]["text"])
    return HttpResponse("It's working")


@csrf_exempt
def web_hook(request):
    if request.method != "POST":
        # Validate URL
        if request.GET['hub.verify_token'] == settings.VALIDATION_TOKEN:
            return HttpResponse(request.GET['hub.challenge'])
        return HttpResponse("Failed validation. Make sure the validation tokens match.")
    return chat_handler(request)
