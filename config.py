# -*- coding: utf-8 -*- 
import os, argparse
from flask import Flask


parser = argparse.ArgumentParser()			#настройка аргументов командной строки
parser.add_argument("--port", default='7000', type=int, dest='port', help='Port to listen'),
parser.add_argument("--hash-algo", default='sha1', type=str, dest='hash_algo', help='Hashing algorithm to use'),
parser.add_argument("--content-dir", default='UPLOAD', type=str, dest='content_dir', help='Enable folder to upload'),
args = parser.parse_args()

port = args.port							#обработка параметров получаемых с консоли
hash_algo = args.hash_algo
content_dir = args.content_dir


BASE_DIR = os.path.abspath('.')
if os.path.exists(os.path.join(BASE_DIR, 'UPLOADS')) == False:				#если нету папки 'UPLOADS', в которой будут храниться все загрузки, создаем ее
	os.mkdir('UPLOADS')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'UPLOADS', content_dir)


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024			#16 mb
