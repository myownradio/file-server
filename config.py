# -*- coding: utf-8 -*- 
import os, argparse
from flask import Flask


parser = argparse.ArgumentParser()			#настройка аргументов принимаемых с консоли
parser.add_argument("--port", default='7000', type=int, help='Port to listen'),
parser.add_argument("--hash-algo", default='sha1', type=str, help='Hashing algorithm to use'),
parser.add_argument("--content-dir", default='UPLOADS', type=str, help='Enable folder to upload'),
parser.add_argument("--secret", default='d41d8cd98f00b204e9800998ecf8427e', type=str, help='secret key'),
args = parser.parse_args()

port = args.port				#обработка параметров получаемых с консоли
hash_algo = args.hash_algo
content_dir = args.content_dir
secret = args.secret

BASE_DIR = os.path.abspath('.')

if os.path.exists(os.path.join(BASE_DIR, content_dir)) == False:		#если нету папки 'UPLOADS', в которой будут храниться все загрузки, создаем ее
	os.mkdir(content_dir)


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, content_dir)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024						#Максимальный размер загружаемых файлов (16 mb)
