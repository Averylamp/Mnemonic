import httplib, urllib, base64
import os,sys, ast, json, copy, random, ssl
from flask import Flask, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from watson_developer_cloud import SpeechToTextV1, AlchemyLanguageV1
ssl._create_default_https_context = ssl._create_unverified_context


#these paths should be changed when running on the server
UPLOAD_IMAGE_FOLDER = '/root/mnemonic/uploads/imagesets/'
UPLOAD_AUDIO_FOLDER = '/root/mnemonic/uploads/audio/'
USER_TEXT_FOLDER = '/root/mnemonic/database/text/'
USER_IMAGE_FOLDER = '/root/mnemonic/database/images/'
ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
ALLOWED_AUDIO_EXTENSIONS = set(['wav', 'mp3'])

app = Flask(__name__)
app.config['UPLOAD_IMAGE_FOLDER'] = UPLOAD_IMAGE_FOLDER
app.config['UPLOAD_AUDIO_FOLDER'] = UPLOAD_AUDIO_FOLDER

state = "DEFAULT" #valid states are default, listening, done, found, editing

current_folder = ""
UPLOAD_COUNT = 0

# @app.route('/')
# def hello_world():
# 	return 'Hello, World!'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS.union(ALLOWED_AUDIO_EXTENSIONS)

@app.route('/upload/audio', methods=['GET', 'POST'])
def upload_audio():
	if request.method == 'POST':
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		# submit a empty part without filename
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_AUDIO_FOLDER'], filename))
			return redirect(url_for('upload_audio', filename=filename))
	return '''
	<!doctype html>
	<title>Upload new Audio File</title>
	<h1>Upload new Audio File</h1>
	<form method=post enctype=multipart/form-data>
	  <p><input type=file name=file>
		 <input type=submit value=Upload>
	</form>
	'''

def checkForMatch(set_number):
	global microsoft_path
	faceheaders = {
	    # Request headers
		'Content-Type': 'application/octet-stream',
		'Ocp-Apim-Subscription-Key': '7c8d348d98b34b189840400a9ae58bcb',
	}

	params = urllib.urlencode({
		# Request parameters
		'returnFaceId': 'true',
		'returnFaceLandmarks': 'false',
		'returnFaceAttributes': 'age,gender,smile,facialHair,headPose,glasses',
	})

	emotionheaders = {
	    # Request headers
	    'Content-Type': 'application/octet-stream',
	    'Ocp-Apim-Subscription-Key': '1f92c2b0429e45958c79ef4e9f9e47cc',
	}

	emotionparams = urllib.urlencode({
	})

	faceIDS = {}
	faceIDS["id"] = []
	faceIDS["gender"] = []
	faceIDS["age"] = []
	faceIDS["smile"] = []

	for i in range(3):
		output_num = '%d' % i
		filename = "image" + str(output_num) + ".jpg"
		
		fullFilePath = microsoft_path + "imageset" + str(0) + "/" + filename
		print(fullFilePath)
		try:
			
			inputdata = read_zipfile(fullFilePath)
			conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
			# print("/face/v1.0/detect?%s" % params, "http://img.timeinc.net/time/daily/2010/1011/poy_nomination_agassi.jpg")
			conn.request("POST", "/face/v1.0/detect?%s" % params, inputdata, faceheaders)
			# conn.request("POST", "/face/v1.0/detect?%s" % params, "{\"url\":\"http://img.timeinc.net/time/daily/2010/1011/poy_nomination_agassi.jpg\"}", headers)
			response = conn.getresponse()
			data = response.read()
			data_dict = ast.literal_eval(data)
			# print data_dict
			if len(data_dict):
				faceIDS["id"].append(data_dict[0]["faceId"])
				faceIDS["gender"].append(data_dict[0]["faceAttributes"]["gender"])
				faceIDS["age"].append(data_dict[0]["faceAttributes"]["age"])
				faceIDS["smile"].append(data_dict[0]["faceAttributes"]["smile"])
			conn.close()
		except Exception as e:
		    print("[Error {0}] ".format(e))
		    print("e")
		if i == 1:
			try:
				conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
				conn.request("POST", "/emotion/v1.0/recognize?%s" % emotionparams, inputdata, emotionheaders)
				response = conn.getresponse()
				data = response.read()
				print("emotion data ---------------------")
				data_dict = ast.literal_eval(data)
				emotion_dict = copy.deepcopy(data_dict)
				print(data_dict)
				print("END emotion data ---------------------\n")
				conn.close()
			except Exception as e:
				print("[Errno {0}] {1}".format(e.errno, e.strerror))
	print("Face Data ---------------------")
	print(faceIDS)
	print("END Face Data ----------------------\n")

	if faceIDS['id'] == []:
		complete = "Sorry, no faces detected."
		with open("Output.txt", "w") as text_file:
			text_file.write(complete)
		print(complete)
		os._exit(1)
		#make it stop running the program
	headers = {
	    # Request headers
	    'Content-Type': 'application/json',
	    'Ocp-Apim-Subscription-Key': '7c8d348d98b34b189840400a9ae58bcb',
	}

	params = urllib.urlencode({
	})
	body = {"personGroupId":"people", "maxNumOfCandidatesReturned":1,"confidenceThreshold":0.5}
	body["faceIds"] = faceIDS["id"]
	try:
		conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
		conn.request("POST", "/face/v1.0/identify?%s" % params, str(body), headers)
		response = conn.getresponse()
		data = response.read()
		print("Detection ---------")
		print(data)
		print("Detection End ---------")
		conn.close()
	except Exception as e:
		print("[Errno {0}] {1}".format(e.errno, e.strerror))
	# print(ast.literal_eval(data))
	person_data = {}
	for result in ast.literal_eval(data):
		print(result)
		candidates = result["candidates"]
		for person in candidates:
			if person["personId"] in person_data:
				person_data[person["personId"]] += person["confidence"]
			else:
				person_data[person["personId"]] = person["confidence"]
	max_conf = -1
	max_id = ""
	for person in person_data.items():
		if person[1] > max_conf:
			max_conf = person[1]
			max_id = person[0]
	print("Max - {}".format(max_id))
	if person_data == {}:
		return False

	conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
	# print("/face/v1.0/detect?%s" % params, "http://img.timeinc.net/time/daily/2010/1011/poy_nomination_agassi.jpg")
	conn.request("GET", "/face/v1.0/persongroups/people/persons/%s" % max_id, "" , headers)
	# conn.request("POST", "/face/v1.0/detect?%s" % params, "{\"url\":\"http://img.timeinc.net/time/daily/2010/1011/poy_nomination_agassi.jpg\"}", headers)
	response = conn.getresponse()
	data = response.read()
	data_dict = ast.literal_eval(data)

	#emotion_dict and faceIDS
	print(data_dict)

	person_name = data_dict["name"]
	response = "You have just met " + person_name + ".  " + data_dict["userData"]
	print(response)
	return response

@app.route('/upload/image', methods=['GET', 'POST'])
def upload_image():
	global UPLOAD_COUNT
	global current_folder
	global state
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		# if user does not select file, browser also
		# submit a empty part without filename
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			if UPLOAD_COUNT % 3 == 0:
				# print "lol"
				current_folder = "imageset" + str(0) + "/"
				# current_folder = "imageset" + str(UPLOAD_COUNT/3) + "/"
				state = "LISTENING"
				if (not os.path.exists(os.path.join(UPLOAD_IMAGE_FOLDER, current_folder))):
    					os.makedirs(os.path.join(UPLOAD_IMAGE_FOLDER, current_folder))
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_IMAGE_FOLDER'], current_folder, filename))
			UPLOAD_COUNT += 1
			if UPLOAD_COUNT % 3 == 0:
				resp = checkForMatch(UPLOAD_COUNT/3)
				if resp == False:
					print "match not found"
				else:
					with open("Output.txt", "w") as text_file:
						text_file.write(resp)
					state = "FOUND"
					return resp
					#do whatever
					print "a"
			return redirect(url_for('upload_image', filename=filename))
	return '''
	<!doctype html>
	<title>Upload new Image</title>
	<h1>Upload new Image</h1>
	<form method=post enctype=multipart/form-data>
	  <p><input type=file name=file>
		 <input type=submit value=Upload>
	</form>
	'''

@app.route('/users', methods=['GET'])
def get_users():
	string = "["
	files = [f for f in os.listdir(os.path.join(USER_TEXT_FOLDER)) if os.path.isfile(os.path.join(USER_TEXT_FOLDER, f))]
	for f in files:
		with open(USER_TEXT_FOLDER + f) as file:
			string += file.read()
			string += ","
	if string[-1] == ",":
		string = string[:-1]
	string += "]"
	return string

@app.route('/images/<img_name>', methods=['GET'])
def get_image(img_name):
	print (USER_IMAGE_FOLDER + img_name)
	return send_file(USER_IMAGE_FOLDER + img_name, mimetype='image/gif')

def read_zipfile(path):
	with open(path, 'rb') as f:
		return f.read()

microsoft_path = "/root/mnemonic/uploads/imagesets/"



def addPersonToDatabase(name, info):
	global microsoft_path
	headers = {
	    # Request headers
		'Content-Type': 'application/json',
		'Ocp-Apim-Subscription-Key': '7c8d348d98b34b189840400a9ae58bcb',
	}
	faceheaders = {
	    # Request headers
		'Content-Type': 'application/octet-stream',
		'Ocp-Apim-Subscription-Key': '7c8d348d98b34b189840400a9ae58bcb',
	}
	body = {}
	body["name"] = name
	body["userData"] = info
	print ("Body - {}".format(body))
	conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
	conn.request("POST", "/face/v1.0/persongroups/people/persons", str(body), headers)
	response = conn.getresponse()
	data = response.read()
	data_dict = ast.literal_eval(data)
	print(data_dict)
	personID = data_dict["personId"]
	conn.close()
	for i in range(3):
		output_num = '%d' % i
		filename = "image" + str(output_num) + ".jpg"
		# fullFilePath = microsoft_path + "imageset" + str(set_number) + "/" + filename
		fullFilePath = microsoft_path + "imageset0" + "/" + filename
		print(fullFilePath)
		try:
			
			inputdata = read_zipfile(fullFilePath)
			conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
			# print("/face/v1.0/detect?%s" % params, "http://img.timeinc.net/time/daily/2010/1011/poy_nomination_agassi.jpg")
			conn.request("POST", "/face/v1.0/persongroups/people/persons/" + personID + "/persistedFaces", inputdata, faceheaders)
			# conn.request("POST", "/face/v1.0/detect?%s" % params, "{\"url\":\"http://img.timeinc.net/time/daily/2010/1011/poy_nomination_agassi.jpg\"}", headers)
			response = conn.getresponse()
			data = response.read()
			data_dict = ast.literal_eval(data)
			print (data_dict)
			print("Added Photo " + str(i) + " to " + name)
			conn.close()
		except Exception as e:
		    print("[Error {0}] ".format(e))
		    print("e")
	print("END Face Added ----------------------\n")
	print("Train datrabase")

	conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
	conn.request("POST", "/face/v1.0/persongroups/people/train", "", headers)
	response = conn.getresponse()
	data = response.read()
	print(data)
	print("Finished Training Data")

@app.route('/microsoft', methods=['POST'])
def microsoft_confirm():
	global state
	print request.args.get("image_name")
	print("Name - {}, json_data - {}".format(request.args.get("name"),request.args.get("json_data")))
	addPersonToDatabase(request.args.get("name"),request.args.get("json_data"))
	#write json data to text file in database,
	#write image to database

	state = "DONE"

@app.route('/doneListening', methods=['POST'])
def finished_listening():
	global state
	if state == "FOUND":
		return state
	print "State now Editing"
	state = "EDITING"
	return state

def keywords(speech_text):

	if speech_text is None:
		return []

	alchemy_language = AlchemyLanguageV1(api_key='13789e5c96c9a0aecfaa20c4e4dd2731e60e026a')
	url = 'https://gateway-a.watsonplatform.net/calls'

	json_form = json.dumps(alchemy_language.keywords(max_items=6, text=speech_text))
	json_data = json.loads(json_form)
	if len(json_data["keywords"]) == 0:
		return []
	json_keywords = json_data["keywords"]
	keywords = []
	for i in json_keywords:
		keywords.append(i['text'])
	return keywords

@app.route('/ibm/<text>', methods=['GET'])
def get_keywords(text):
	result = keywords(text)
	return ",".join(result)



@app.route('/state', methods=['GET'])
def get_state():
	global state
	return state
