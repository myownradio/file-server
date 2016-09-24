# -*- coding: utf-8 -*- 
import os, hashlib
from flask import Flask, request, redirect, url_for, jsonify, abort, Response
from werkzeug.utils import secure_filename
from flask import send_from_directory


host = 'localhost'				#0.0.0.0
port = 7000
hash_algo = 'sha1'
content_dir = 'UPLOAD2'


UPLOAD_FOLDER = os.path.abspath(content_dir)
BASE_DIR = os.path.abspath('.')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def sha1(file):
	hash_sha1 = hashlib.sha1()
	with open(file, 'r') as f:
		for chunk in iter(lambda: f.read(4096), b""):
			hash_sha1.update(chunk)
	return hash_sha1.hexdigest()


@app.route('/file', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		file = request.files['file']
		if file:
			path = os.path.abspath(content_dir)
			if os.path.exists(path) == False:
				os.mkdir(content_dir)
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			file = app.config['UPLOAD_FOLDER'] + '/' + filename
			if hash_algo == 'sha1':
				sha1_hash = sha1(file)
			os.rename(file, app.config['UPLOAD_FOLDER'] + '/' + sha1_hash)
			response = jsonify({'hash':sha1_hash})
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


@app.route('/file/<filename_hash>', methods=['GET', 'DELETE'])
def detail_file(filename_hash):
	if request.method == 'GET':
		try:
			return send_from_directory(app.config['UPLOAD_FOLDER'],
				filename_hash), {'Content-Type': 'audio/mpeg; charset=utf-8'}
		except	KeyError:
			abort(404)
	if request.method == 'DELETE':
		pass


@app.route('/status')
def get_status():
	disc = os.statvfs('.')
	free_space = disc.f_bsize * disc.f_bavail / 1024 / 1024			#место на диске в мб
	return jsonify({'free space':free_space, 'units':'mb'})

if __name__ == '__main__':
    app.run(host='localhost', port=7000, debug=True)				#настройки ip адреса и порта сервера
