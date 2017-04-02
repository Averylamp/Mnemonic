import httplib, urllib, base64
import os,sys, ast, json, copy, random, ssl
ssl._create_default_https_context = ssl._create_unverified_context

def read_zipfile(path):
	with open(path, 'rb') as f:
		return f.read()

path = "/Users/josh/temp/Mnemonic/imageset2/"

def checkForMatch():
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
		
		fullFilePath = path + filename
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



def addPersonToDatabase(name, info):
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
	body = {"name":name, "userData":info}
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
		fullFilePath = path + filename
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
	
# response = checkForMatch()
# if response == False:
# 	addPersonToDatabase("Arlene Siswanto" ,"Arlene is a current Freshman at MIT.  She studies computer science.")
	
