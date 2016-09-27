# -*- coding: utf-8 -*- 
import os, hashlib, shutil
from flask import request, Response, send_from_directory, jsonify, abort
from werkzeug.utils import secure_filename
from config import *


def sha1(file):						#функция возвращает sha1 хеш, загружаемого файла
	hash_sha1 = hashlib.sha1()
	with open(file, 'rb') as f:
		for chunk in iter(lambda: f.read(4096), b""):
			hash_sha1.update(chunk)
	return hash_sha1.hexdigest()


def make_folder_for_file(file_hash):		#функция создает папку и возвращает путь к директории куда будет перемещен загружаемый файл
	path = os.path.join(app.config['UPLOAD_FOLDER'], file_hash[0], file_hash[1])	#если нужной нам папки не существует
	if os.path.exists(path) == False:
		_dir = os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], file_hash[0], file_hash[1]))	#создаем папку
	else:
		_dir = path 	#в случае если нужная папка была создана ранее
	return _dir			#возвращаем путь к директории


def get_token(*args):	#генерируем ключ для проверки авторизации входящих запросов при upload(е) файлов
	token = ''
	token += ':'.join(str(arg) for arg in args)			#склевиваем строку из условных ключей
	return hashlib.md5(token.encode('utf8')).hexdigest()	#возвращаем md5 хеш, который будем использовать для сверки


def get_confirm_token(*args):
	confirm_token = ''
	confirm_token += ':'.join(str(arg) for arg in args)
	return hashlib.md5(confirm_token.encode('utf8')).hexdigest()


@app.route('/file', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		file = request.files['file']
		token = request.form['token']
		if file:
			file_name = secure_filename(file.filename)			#защита от инъекций в имени загружаемого файла
			file_size = request.headers['Content-Length']
			client_ip = request.remote_addr
			if token != get_token(file_name, file_size, client_ip, args.secret):
				abort(404)
			path_to_file = os.path.join(app.config['UPLOAD_FOLDER'], file_name)					
			file.save(path_to_file)
			if hash_algo == 'sha1':
				file_hash = sha1(path_to_file)			#получаем хеш файла по алгоритму
			confirm_token = get_confirm_token(file_name, file_size, client_ip, args.secret, file_hash)		#токен для подтверждения корректной загрузки
			folder = make_folder_for_file(file_hash)			#создаем папку для файла основываясь на его префексах
			shutil.move(path_to_file, (os.path.join(app.config['UPLOAD_FOLDER'], file_hash[0], file_hash[1], file_hash)))
			#перемещает файл в созданую папку и заменяем его имя на созданый хеш
			response = jsonify({																							
								"file_name": file_name,																			
  								"file_size": file_size,
  								"file_hash": file_hash,
  								"confirm_token": confirm_token,
							})
			return response
		return abort(404)
	return '''													
    <!doctype html>
    <title>Upload new File</title>		
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
      <input type="hidden" name="token" value="3e9122bdc4a976a8698c4a5b685b505a">
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
		os.remove(file)					#удаляем файл с диска
		return 'remove %s' %file_hash
	else:
		abort(404)


@app.route('/status', methods=['GET'])		#функция возвращает оставшееся свободное место на диске в bytes
def get_status():
	disc = os.statvfs(BASE_DIR)
	free_space = disc.f_bsize * disc.f_bavail	
	return jsonify({'free_space':free_space})


if __name__ == '__main__':
   	app.run(host='127.0.0.1', port=args.port, threaded=True, debug=True)	#host='0.0.0.0'; threaded=True - рекамендация по запуску приложений без настроенного WSGI
