import zerorpc
from pymongo import MongoClient
from USE import USE

from datetime import datetime
import os

FILE_DICT = {}
nowtime = datetime.now()
year, month, day, hour, minute = nowtime.year, nowtime.month, nowtime.day, nowtime.hour, nowtime.minute
DATE = f'{year}_{month}_{day}_{hour}_{minute}'


class Worker():
    def log_chat(self, channel, broadcaster_id, chatter_display_name, message):
        file = get_file(channel)
        file.write(f'{chatter_display_name}\t{message}\n')
        # print(f'broadcaster id: {broadcaster_id}\nchatter display name: {chatter_display_name}\nmessage: {message}')
    def get_response(self, broadcaster_id, message):
        try:
            message_striped = message.strip()
            print(f'get_response: {broadcaster_id}, {message_striped}')
            reply = ''

            customQA_list = list(customQA.find({
                'uid': int(broadcaster_id),
                'enabled': True
            }))

            predefinedQA_list = list(predefinedQA.find({
                'uid': int(broadcaster_id),
                'enabled': True
            }))
            
            automaticQA_list = list(automaticQA.find({
                'uid': int(broadcaster_id),
                'enabled': True
            }))

            QA_list = customQA_list + predefinedQA_list + automaticQA_list
            # print(f'QA_list: {QA_list}')

            reply = check_command(QA_list, message_striped)
            if reply is '' and is_question(message_striped):
                print(f'message is question')
                reply = check_classifiable_question(QA_list, message_striped)
                if reply is '':
                    print(f'message is general_question')
                    reply = check_general_question(QA_list, message_striped)
        except Exception as e:
            print(e)
            reply = ''
        finally:
            print(f'reply: {reply}')
            return reply


def check_command(QA_list, chat):
	# check if chat is in Command of enabled automaticQA, predefinedQA, customQA
	# get commands from mongoDB by uid
	# check if chat is in the list
	# print('check_command:', QA_list)
	for QA in QA_list:
		if QA['command'] == chat:
			return QA['answer']
	return ''


def is_question(chat):
    if "?" not in chat:
        return False
    if chat[0] == "?" or chat[1] == "?":
        return False
    return True


def check_classifiable_question(QA_list, chat):
	return ''


def get_file(channel):
    global FILE_DICT
    global DATE
    if channel in FILE_DICT:
        # print(f'file for {channel} already exists')
        return FILE_DICT[channel]
    else:
        print(f'create file for {channel}')
        base_path = os.path.join('./result', channel)
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        FILE_DICT[channel] = open(os.path.join(base_path, f'{DATE}.tsv'), 'w', encoding='utf-8', buffering=1)
        return FILE_DICT[channel]


def check_general_question(QA_list, chat):
	reply = ''
	
	Q_list = list(map(lambda x: x['question'], QA_list))

	prediction = NLP.query_db(Q_list, chat, threshold=0.85)
	print(prediction)

	if prediction == -1:
		reply = ''
	else:
		reply = QA_list[prediction]['answer']

	return reply

def main():
    z_server = zerorpc.Server(Worker())
    z_server.bind("tcp://0.0.0.0:18889")
    z_server.run()

def test():
    TH = 0.85
    korean_sentence_list = ['님 나이가?', '오늘 방송 일정 뭐임?', '고양이 키움?']
    query = '몇살이에요?'
    result = NLP.query_db(korean_sentence_list, query, threshold=0.85)
    if result != -1:
        print(korean_sentence_list[result])


if __name__ == '__main__':
    NLP = USE()
    client = MongoClient('localhost', 27017)
    db = client.mujinjang
    automaticQA = db.automaticqas
    customQA = db.customqas
    predefinedQA = db.predefinedqas
    predefinedQAstatic = db.predefinedqastatics
    main()
    # test()