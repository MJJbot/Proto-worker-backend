import numpy as np
import flask
from pymongo import MongoClient
from NLPcore import NLPcore

client = MongoClient('localhost', 27017)
db = client.mujinjang
automaticQA = db.automaticqas
customQA = db.customqas
predefinedQA = db.predefinedqas
predefinedQAstatic = db.predefinedqastatics
NLP = NLPcore()

# initialize our Flask application and the Keras model
app = flask.Flask(__name__)
classifiable_question_model = None
clqm_TH = 0.7
customQA_TH = 0.95

def make_clqm_input(chat): # clqm = classifiable_question_model
	#tokenize
	tokens = list()

	return np.array(tokens)


def check_command(QA_list, chat):
	# check if chat is in Command of enabled automaticQA, predefinedQA, customQA
	# get commands from mongoDB by uid
	# check if chat is in the list
	print('check_command:', QA_list)
	for QA in QA_list:
		if QA['command'] == chat:
			return QA['answer']
	return None


def is_question(chat):
    if "?" not in chat:
        return False
    if chat[0] == "?" or chat[1] == "?":
        return False
    return True


'''def check_classifiable_question(uid, chat):
	prediction = classifiable_question_model.predict(make_clqm_input(chat))
	if np.amax(prediction) < clqm_TH:
		return None
	else:
		target_idx = np.argmax(prediction)
		
		# mongoDB lookup with uid and target_idx on predefinedQA + automaticQA
		# check if target question is enabled
		target_collection = None
		if target_collection['enabled']:
			return target_collection['answer']
		else:
			return None'''

def check_classifiable_question(QA_list, chat):
	return None


def check_general_question(QA_list, chat):
	reply = str()
	
	Q_list = list(map(lambda x: x['question'], QA_list))

	prediction = NLP.queryDB(chat, Q_list)
	print(prediction)

	if prediction == -1:
		reply = None
	else:
		reply = QA_list[prediction]['answer']

	return reply

@app.route("/chat", methods=["GET"])
def chat_get():
	print('hi')
	data = {"success": False, "reply": None}
	return flask.jsonify(data)

@app.route("/chat", methods=["POST"])
def predict():
	# initialize the data dictionary that will be returned from the
	# view
	data = {"success": False, "reply": None}
	# get uid and chat string
	# get Commands of automaticQA, predefinedQA, automaticQA (which is enabled)
	# 1. check if chat is in Commands: if yes, return response.
	# else, 
	# 2. check if chat is a question: if yes, continue. if no, return blank response
	# 3. check if chat is a classifiable question (predefinedQA + automaticQA)
	# : if yes, check if class is enabled and if is, return response. if disabled, return blank response
	# : if no (TH), continue
	# 4. check if chat is in customQA
	# : if yes, return response.
	# : if no, return blank response.

	req_json = flask.request.get_json(silent=True, force=True)
	uid = req_json.get('uid')
	chat = req_json.get('chat').strip()

	customQA_list = list(customQA.find({
		'uid': uid,
		'enabled': True
	}))

	predefinedQA_list = list(predefinedQA.find({
		'uid': uid,
		'enabled': True
	}))
	
	automaticQA_list = list(automaticQA.find({
		'uid': uid,
		'enabled': True
	}))

	QA_list = customQA_list + predefinedQA_list + automaticQA_list

	print('customQA:', customQA_list)
	print('predefinedQA', predefinedQA_list)
	print('automaticQA', automaticQA_list)

	data["reply"] = check_command(QA_list, chat)
	if data["reply"] is None and is_question(chat):
		# data["reply"] = check_general_question(QA_list, chat)
		data["reply"] = check_classifiable_question(QA_list, chat)
		if data["reply"] is None:
			data["reply"] = check_general_question(QA_list, chat)
	
	if data["reply"] is not None:
		data["success"] = True

	# return the data dictionary as a JSON response
	return flask.jsonify(data)

# if this is the main thread of execution first load the model and
# then start the server
if __name__ == "__main__":
	print(("* Loading Keras model and Flask starting server..."
		"please wait until server has fully started"))

	app.run(port=18888, debug=True)
