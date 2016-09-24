# -*- coding: utf-8 -*- 
import os, hashlib
from flask import Flask, request, redirect, url_for, jsonify, abort, Response, send_from_directory
from werkzeug.utils import secure_filename


port = 7000								#параметры получаемые с консоли
hash_algo = 'sha1'
content_dir = 'UPLOAD'

UPLOAD_FOLDER = os.path.abspath(content_dir)
BASE_DIR = os.path.abspath('.')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def sha1(file):										#функция возвращает sha1 хеш, загружаемого файла
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
			filename = secure_filename(file.filename)										#защита от инъекций в имени загружаемого файла
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			file = app.config['UPLOAD_FOLDER'] + '/' + filename
			if hash_algo == 'sha1':
				sha1_hash = sha1(file)
			os.rename(file, app.config['UPLOAD_FOLDER'] + '/' + sha1_hash)					#замена имени файла на его хеш
			response = jsonify({'hash':sha1_hash})											#возврат response с полученным sha1 хешем файла
			return response
		return abort(404)
	return '''													
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


def get_file_folder(filename_hash):							#фун-я определяет в каком каталоге находиться запрашиваемый файл
	for obj in os.listdir(BASE_DIR):
		if os.path.isdir(obj) and obj != '.git':
			folder = BASE_DIR + '/' + obj
			if filename_hash in os.listdir(folder):
				return(folder)


@app.route('/file/<filename_hash>', methods=['GET', 'DELETE'])
def get_file(filename_hash):
	if request.method == 'GET':
		FOLDER = get_file_folder(filename_hash)
		try:
			return send_from_directory(FOLDER,
				filename_hash), {'Content-Type': 'audio/mpeg; charset=utf-8'}			#если запрашиваемый файл найден - возвращаем его с заданным "Content-Type"
		except KeyError:
			abort(404)
	if request.method == 'DELETE':
		pass


@app.route('/status', methods=['GET'])
def get_status():
	disc = os.statvfs(BASE_DIR)
	free_space = disc.f_bsize * disc.f_bavail / 1024 / 1024			#функция возвращает оставшееся свободное место на диске в мб
	return jsonify({'free space':free_space, 'units':'mb'})


if __name__ == '__main__':
    app.run(host='localhost', port=port, threaded=True)				#host='0.0.0.0'