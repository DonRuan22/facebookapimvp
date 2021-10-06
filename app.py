from flask import Flask, request
import requests
import json
import config
import logging
import os
from deep_translator import GoogleTranslator




app = Flask(__name__)
SECRET_KEY = 'b8d43ce14d05828c73257013c8e67b95'
#PAGE_ACCESS_TOKEN = "EAACCGdwRfhABANBdZCtGQWTBPWLiH2wnRLreO6vZAtP6WZBvTAsmDkCVYkVD7fmUtGu5ARlGtI1tV8nhSyZCjy0sHGfKRNZAJcemHpaQ0glcfqITZBxuZA6Y6RrehcrgWvZCzAWVT9T3Rln5lOMArSy9A64HPOg19AT9T2PyWWdZAQdeFTuESLpqS"
VERIFY_TOKEN = 'rasa-don'
global INIT_VARI
global mId 
mId = []
INIT_VARI=''



#Function to access the Sender API
def callSendAPI(senderPsid, response, type_response='message'):
    #PAGE_ACCESS_TOKEN = config.PAGE_ACCESS_TOKEN
    logging.warning("Response: "+ str(response)) 
    if(type_response == 'message'):
        payload = {
        'recipient': {'id': senderPsid},
        'message': response,
        'messaging_type': 'RESPONSE'
        }
    if(type_response == 'model'):
        logging.warning(response) 
        payload = {
        'recipient': {'id': senderPsid},
        'message': {
                "attachment":{
                    "type":"template",
                    "payload":{
                        "template_type":"generic",
                        "elements":[
                           {
                            "title":"Welcome!",
                            "image_url":"https://petersfancybrownhats.com/company_image.png",
                            "subtitle":"We have the right hat for everyone.",
                            "default_action": {
                              "type": "web_url",
                              "url": "https://petersfancybrownhats.com/view?item=103",
                              "webview_height_ratio": "tall",
                            }        
                           }
                        ]
                    }
                }
        },
        'messaging_type': 'RESPONSE'
        }
    if(type_response == "sender_action"):
        payload = {
        'recipient': {'id': senderPsid},
        "sender_action": "typing_on",
        }    
    headers = {'content-type': 'application/json'}

    url = 'https://graph.facebook.com/v2.6/me/messages?access_token={}'.format(os.environ.get('PAGE_ACCESS_TOKEN'))
    r = requests.post(url, json=payload, headers=headers)
    logging.warning(r.request.headers) 
    logging.warning(r.url) 
    logging.warning(r.content) 
    logging.warning(r.__dict__) 
    print(r.text)



#Function for handling a message from MESSENGER
def handleMessage(senderPsid, receivedMessage):
    print("handle message")
    callSendAPI(senderPsid, "","sender_action")
    global INIT_VARI
    global mId
    logging.warning('mId variable = '+ str(mId))
    logging.warning('mId message = '+ str(receivedMessage['mid']))
    if (not(receivedMessage['mid'] in mId)):
        
        mId.append(receivedMessage['mid'])
        #check if received message contains text
        if 'text' in receivedMessage:
            receivedMessage['text'] = GoogleTranslator(source='auto', target='en').translate(text=receivedMessage['text'])
            payload = {'sender': senderPsid,'message': receivedMessage['text']}
            #payload_json = json.loads(payload)
            #print(payload)
            response_rasa = requests.post('https://don-mvp-vc5xcezzwa-uc.a.run.app/webhooks/rest/webhook', json = payload, timeout=None)
            logging.warning('response') 
            logging.warning(response_rasa.json()) 
            response_data={}
            if(len(response_rasa.json())>0):
                response_data = response_rasa.json()
                #response_port = GoogleTranslator(source='auto', target='pt').translate(text=response_rasa.json()[0]["text"] )
            else:
                response_data['text'] = 'Sorry error server'
            #print(response_rasa.json()[0]["text"])
            #response = {"text": 'You just sent: {}'.format(receivedMessage['text']) }
            logging.warning("init: "+str(response_data))
            if(INIT_VARI != response_rasa):
                INIT_VARI = response_rasa
                if('custom' in response_data):
                    if('model' in response_data['custom'][0]):
                        response = response_data['custom']
                        callSendAPI(senderPsid, response, 'model')
                elif('text' in response_data):
                    logging.warning(response_data) 
                    response = {"text": response_data['text'] }
                    callSendAPI(senderPsid, response)
            #logging.warning(response)
        else:
            response = {"text": 'This chatbot only accepts text messages'}
            callSendAPI(senderPsid, response)




@app.route('/', methods=["GET", "POST"])
def home():

    return 'HOME'

@app.route('/webhooks/facebook/webhook', methods=["GET", "POST"])
def index():
    if request.method == 'GET':
        #do something.....
        #VERIFY_TOKEN = config.VERIFY_TOKEN

        if 'hub.mode' in request.args:
            mode = request.args.get('hub.mode')
            print(mode)
        if 'hub.verify_token' in request.args:
            token = request.args.get('hub.verify_token')
            print(token)
        if 'hub.challenge' in request.args:
            challenge = request.args.get('hub.challenge')
            print(challenge)

        if 'hub.mode' in request.args and 'hub.verify_token' in request.args:
            mode = request.args.get('hub.mode')
            token = request.args.get('hub.verify_token')

            if mode == 'subscribe' and token == VERIFY_TOKEN:
                print('WEBHOOK VERIFIED')

                challenge = request.args.get('hub.challenge')

                return challenge, 200
            else:
                return 'ERROR', 403

        return 'SOMETHING', 200


    if request.method == 'POST':
        #do something.....
        #VERIFY_TOKEN = config.VERIFY_TOKEN
        if 'hub.mode' in request.args:
            mode = request.args.get('hub.mode')
            print(mode)
        if 'hub.verify_token' in request.args:
            token = request.args.get('hub.verify_token')
            print(token)
        if 'hub.challenge' in request.args:
            challenge = request.args.get('hub.challenge')
            print(challenge)

        if 'hub.mode' in request.args and 'hub.verify_token' in request.args:
            mode = request.args.get('hub.mode')
            token = request.args.get('hub.verify_token')

            if mode == 'subscribe' and token == VERIFY_TOKEN:
                print('WEBHOOK VERIFIED')

                challenge = request.args.get('hub.challenge')

                return challenge, 200
            else:
                return 'ERROR', 403

        #do something else
        data = request.data
        body = json.loads(data.decode('utf-8'))
        

        if 'object' in body and body['object'] == 'page':
            entries = body['entry']
            for entry in entries:
                webhookEvent = entry['messaging'][0]
                print(webhookEvent)

                senderPsid = webhookEvent['sender']['id']
                print('Sender PSID: {}'.format(senderPsid))

                if 'message' in webhookEvent:
                    handleMessage(senderPsid, webhookEvent['message'])

                return 'EVENT_RECEIVED', 200
        else:
            return 'ERROR', 404



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get("PORT", 5005)), debug=True)
