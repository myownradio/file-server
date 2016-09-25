# -*- coding: utf-8 -*- 
import os, hashlib
from flask import Flask, request, Response, send_from_directory, jsonify, abort
from werkzeug.utils import secure_filename


port = 7000							#параметры получаемые с консоли
hash_algo = 'sha1'
content_dir = 'UPLOAD1'

BASE_DIR = os.path.abspath('.')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'UPLOADS', content_dir)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def sha1(file):								#функция возвращает sha1 хеш, загружаемого файла
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
			path = app.config['UPLOAD_FOLDER']
			if os.path.exists(path) == False:
				os.mkdir(app.config['UPLOAD_FOLDER'])
			filename = secure_filename(file.filename)									#защита от инъекций в имени загружаемого файла
			path_to_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)						
			file.save(path_to_file)
			if hash_algo == 'sha1':
				sha1_hash = sha1(path_to_file)
			os.rename(path_to_file, os.path.join(app.config['UPLOAD_FOLDER'], sha1_hash))		#замена имени файла на его хеш
			response = jsonify({'hash':sha1_hash})
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


def get_file_folder(filename_hash):						#фун-я определяет в каком каталоге находиться запрашиваемый файл
	for obj in os.listdir(BASE_DIR + '/UPLOADS'):
		path = os.path.join(BASE_DIR, 'UPLOADS', obj)
		if os.path.isdir(path):
			path_to_folder = path
			if filename_hash in os.listdir(path_to_folder):
				return(path_to_folder)


@app.route('/file/<filename_hash>', methods=['GET', 'DELETE'])
def file_detail(filename_hash):
	if len(filename_hash) == 40:
		try:
			FOLDER = get_file_folder(filename_hash)
		except AttributeError:
			abort(404)

		if request.method == 'GET':
			return send_from_directory(FOLDER,
				filename_hash), {'Content-Type': 'audio/mpeg; charset=utf-8'}			#если запрашиваемый файл найден - возвращаем его с заданным "Content-Type"

		if request.method == 'DELETE':
			file = os.path.join(FOLDER, filename_hash)
			os.remove(file)										#удаляем указаный файл
			return 'remove %s' %filename_hash
	else:
		abort(404)


@app.route('/status', methods=['GET'])
def get_status():
	disc = os.statvfs(BASE_DIR)
	free_space = disc.f_bsize * disc.f_bavail / 1024 / 1024					#функция возвращает оставшееся свободное место на диске в мб
	return jsonify({'free space':free_space, 'units':'mb'})


if __name__ == '__main__':
    app.run(host='localhost', port=port, threaded=True)						#host='0.0.0.0'
