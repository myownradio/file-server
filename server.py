# -*- coding: utf-8 -*- 
import os, hashlib, shutil
from flask import request, Response, send_from_directory, jsonify, abort
from config import *


def sha1(stream):						#функция возвращает sha1 хеш, загружаемого файла
	hash_sha1 = hashlib.sha1()
	for chunk in iter(lambda: stream.read(4096), b""):
			hash_sha1.update(chunk)
	return hash_sha1.hexdigest()


def get_size(stream):			#функция возвращает размер файла в bytes
	stream.seek(0, 2)			#перемещаем курсор в конец файла
	size = stream.tell()		#запоминаем размер
	stream.seek(0)				#возвращаем курсор в начало
	return size


def make_folder_for_file(file_hash):		#функция создает папку и возвращает путь к директории куда будет перемещен загружаемый файл
	path = os.path.join(app.config['UPLOAD_FOLDER'], file_hash[0], file_hash[1])	#если нужной нам папки не существует
	if os.path.exists(path) == False:
		_dir = os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], file_hash[0], file_hash[1]))	#создаем папку
	else:
		_dir = path 	#в случае если нужная папка была создана ранее
	return _dir			#возвращаем путь к директории


def get_token(*args):	#генерируем ключ для авторизации входящих запросов и сверки ответов
	token = ':'.join(str(arg) for arg in args)		#склевиваем строку из условных ключей
	return hashlib.md5(token).hexdigest()	#возвращаем md5 хеш


@app.route('/file', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		file = request.files['file']
		token = request.form['token']
		file_size = get_size(file.stream)
		if file and token:
			if hash_algo == 'sha1':				#получаем хеш файла по алгоритму
				file_hash = sha1(file.stream)
			file_name = file.filename.encode('utf8')
			client_ip = request.remote_addr
			if token != get_token(file_name, file_size, client_ip, args.secret):		#сверяем пришедшей токен с сгенерированым
				abort(404)
			folder = make_folder_for_file(file_hash)		#создаем папку для загрузки файла
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_hash[0], file_hash[1], file_hash))		#сохраняем
			confirm_token = get_token(file_name, file_size, client_ip, args.secret, file_hash)		#токен для подтверждения корректной загрузки
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
      <input type="hidden" name="token" value="ca7938276d84240587df58f99f42310d">
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
