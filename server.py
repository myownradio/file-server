# -*- coding: utf-8 -*- 
import os, hashlib, shutil
from flask import request, Response, send_from_directory, jsonify, abort
from werkzeug.utils import secure_filename
from config import *


def sha1(file):				#функция возвращает sha1 хеш, загружаемого файла
	hash_sha1 = hashlib.sha1()
	with open(file, 'rb') as f:
		for chunk in iter(lambda: f.read(4096), b""):
			hash_sha1.update(chunk)
	return hash_sha1.hexdigest()


def take_folder_for_file(file_hash):		#функция создает папки с названиями префексов [0] и [1] от хеша
	path = os.path.join(app.config['UPLOAD_FOLDER'], file_hash[0], file_hash[1])
	if os.path.exists(path) == False:			# если такой папки не существует
		_dir = os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], file_hash[0], file_hash[1]))
	else:
		_dir = path 	#если нужная папка была создана ранее
	return _dir


@app.route('/file', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		file = request.files['file']
		if file:
			filename = secure_filename(file.filename)	#защита от инъекций в имени загружаемого файла
			path_to_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)						
			file.save(path_to_file)
			if hash_algo == 'sha1':					#получаем хеш файла по алгоритму
				file_hash = sha1(path_to_file)
			folder = take_folder_for_file(file_hash)	#создаем папку для файла основываясь на его префексах
			shutil.move(path_to_file, (os.path.join(app.config['UPLOAD_FOLDER'], file_hash[0], file_hash[1], file_hash)))		#перемещает файл в созданую папку и... 
			response = jsonify({'hash':file_hash})																				#...меняет его имя на созданый хеш
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


@app.route('/file/<file_hash>')
def get_file(file_hash):
	folder = os.path.join(app.config['UPLOAD_FOLDER'], file_hash[0], file_hash[1])		#склеиваем путь к папке с файлом
	if folder:
		return send_from_directory(folder,
			file_hash), {'Content-Type': 'audio/mpeg; charset=utf-8'}	#если запрашиваемый файл найден - возвращаем его с заданным "Content-Type"									
	else:
		abort(404)


@app.route('/file/<file_hash>', methods=['DELETE'])
def delete_file(file_hash):
	file = os.path.join(app.config['UPLOAD_FOLDER'], file_hash[0], file_hash[1], file_hash)
	if file:					
		os.remove(file)							#удаляем файл с диска
		return pass
	else:
		abort(404)


@app.route('/status', methods=['GET'])
def get_status():
	disc = os.statvfs(BASE_DIR)
	free_space = disc.f_bsize * disc.f_bavail / 1024 / 1024			#функция возвращает оставшееся свободное место на диске в mb
	return jsonify({'free_space':free_space, 'units':'mb'})


if __name__ == '__main__':
   	app.run(host='127.0.0.1', port=args.port, threaded=True)		#host='0.0.0.0'; threaded = True - рекамендация по запуску приложений без настроенного WSGI
