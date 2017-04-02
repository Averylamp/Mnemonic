import os
from flask import Flask, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import microsoftface
# import ibmtext

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

state = "default" #valid states are default, listening, done, found

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

@app.route('/upload/image', methods=['GET', 'POST'])
def upload_image():
	global UPLOAD_COUNT
	global current_folder
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
				print "lol"
				current_folder = "imageset" + str(UPLOAD_COUNT/3) + "/"
				state = "LISTENING"
				if (not os.path.exists(os.path.join(UPLOAD_IMAGE_FOLDER, current_folder))):
    					os.makedirs(os.path.join(UPLOAD_IMAGE_FOLDER, current_folder))
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_IMAGE_FOLDER'], current_folder, filename))
			UPLOAD_COUNT += 1
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


