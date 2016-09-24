# -*- coding: utf-8 -*- 
import os
from flask import Flask, request, redirect, url_for, jsonify, abort, render_template
from werkzeug.utils import secure_filename
from flask import send_from_directory
import hashlib


host = 'localhost'				#0.0.0.0
port = 7000
hash_algo = 'sha1'
content_dir = 'UPLOAD'


UPLOAD_FOLDER = os.path.abspath(content_dir)
BASE_DIR = os.path.abspath('.')
HASH_BASE = {}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def sha1_hash_filename(filename):
	filename = filename.encode('utf-8')
	hashed_filename = hashlib.sha1(filename)
	hash_code = hashed_filename.hexdigest()
	HASH_BASE[hash_code] = filename
	return hash_code


@app.route('/file', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		file = request.files['file']
		if file:
			path = os.path.abspath(content_dir)
			if os.path.exists(path) == False:
				os.mkdir(content_dir)
			else:
				pass
			filename = secure_filename(file.filename)
			filename_hash = sha1_hash_filename(filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			response = jsonify({'hash':filename_hash})
			return response
	return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


@app.route('/file/<filename_hash>')
def uploaded_file(filename_hash):
	try:
		filename = HASH_BASE[filename_hash]
	except	KeyError:
		abort(404)
	return send_from_directory(app.config['UPLOAD_FOLDER'],
			filename)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='localhost', port=7000)				#настройки ip адреса и порта сервера