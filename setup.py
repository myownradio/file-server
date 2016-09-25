# -*- coding: utf-8 -*- 
import os, argparse
from flask import Flask


parser = argparse.ArgumentParser()			#настройка приема аргументов с командной строки
parser.add_argument("--port", default='7000', type=int, dest='port', help='Port to listen'),
parser.add_argument("--hash-algo", default='sha1', type=str, dest='hash_algo', help='Hashing algorithm to use'),
parser.add_argument("--content-dir", type=str, default='UPLOAD', dest='content_dir', help='Enable folder to upload'),
args = parser.parse_args()

port = args.port							#параметры получаемые с консоли
hash_algo = args.hash_algo
content_dir = args.content_dir


BASE_DIR = os.path.abspath('.')
if os.path.exists(os.path.join(BASE_DIR, 'UPLOADS')) == False:				#если нету папки 'UPLOADS', в которой будут все загрузки, создаем ее
	os.mkdir('UPLOADS')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'UPLOADS', content_dir)


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024			#16 mb