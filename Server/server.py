# -*- coding: utf-8 -*-

from flask import Flask, request
from Crypto.Cipher import DES
import config as Config
import threading
import platform
import sqlite3
import random
import json
import os

# Если сервер на хосте
PATH = os.getcwd()
if platform.system() == 'Windows':
	PATH = PATH.split('\\')
	PATH = '/'.join(PATH[0:len(PATH) - 1])
else:
	PATH += '/Server'

# Если сервер на PC
# PATH = os.getcwd()
# PATH = PATH.split('\\')
# PATH = '/'.join(PATH[0:len(PATH) - 1])

# Создание всех нужных переменных
# ==================================================================
lock = threading.Lock()

app = Flask(__name__)
# ==================================================================

# Подключение DB для проекта "VK Bot"
# ==================================================================
try:
	os.mkdir(f'{PATH}/Files')
except FileExistsError:
	pass

vk_bot_accounts_db = sqlite3.connect(f'{PATH}/Files/VK_Bot-Accounts-DataBase.db', check_same_thread = False)
vk_bot_accounts_sql = vk_bot_accounts_db.cursor()

vk_bot_accounts_sql.execute("""
	CREATE TABLE IF NOT EXISTS Accounts(
		Login TEXT,
		Password BLOB,
		Unique_Key TEXT
	)
""")
vk_bot_accounts_db.commit()
# ==================================================================

# Обычные функции
# ==================================================================
def clear_key(key): # Получение чистого ключа из пароля
	if len(key) < 8:
		while len(key) < 8:
			key += 'd'
		key = key.encode('UTF-8')
	else:
		key = ''.join(list(key)[0:8]).encode('UTF-8')
	return key

def encrypt(key, data): # Шифрование
	def pad(data):
		while len(data) % 8 != 0:
			data += b' '
		return data

	key = clear_key(key)
	des = DES.new(key, DES.MODE_ECB)
	padded_data = pad(data.encode('UTF-8'))
	encrypted_data = des.encrypt(padded_data)
	return encrypted_data

def decrypt(key, encrypted_data): # Дешифровка
	key = clear_key(key)
	des = DES.new(key, DES.MODE_ECB)
	decrypted_data = des.decrypt(encrypted_data)
	return decrypted_data.decode('UTF-8').strip()

def generate_unique_key(): # Генератор уникального ключа
	uniqu_key = ''
	for i in range(20):
		uniqu_key += random.choice('abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
	return uniqu_key

def find_file_or_folder(path, name): # Посик файл/папки
	find_file_or_folder_status = False
	for i in os.listdir(path):
		if i == name:
			find_file_or_folder_status = True
			break
	return find_file_or_folder_status
# ==================================================================

# Логика сервера для проекта "VK Bot"
# ==================================================================
def check_user_login_and_password_and_unique_key_and_bot_name(func): # Декоратор
	def wrapper(login, bot_name):
		try:
			user_data = json.loads(request.data.decode('UTF-8'))
			password = user_data['Password']
			unique_key = user_data['Unique_Key']

			lock.acquire(True)
			vk_bot_accounts_sql.execute(f"SELECT * From Accounts WHERE Login = '{login}'")
			account = vk_bot_accounts_sql.fetchone()
			lock.release()

			if account != None:
				enrypted_password = encrypt(password, password)
				if enrypted_password == account[1]:
					if unique_key  == account[2]:
						if find_file_or_folder(f'{PATH}/Files/{unique_key}', bot_name) == True:
							return func(user_data, bot_name)
						else:
							return json.dumps(
								{
									'Answer': f'Бот под именем "{bot_name}" не существует!'
								}, ensure_ascii = False
							), 400
					else:
						return json.dumps(
							{
								'Answer': 'Был передан неверный "Unique_Key"!'
							}, ensure_ascii = False
						), 400
				else:
					return json.dumps(
						{
							'Answer': 'Был передан неверный "Password"!'
						}, ensure_ascii = False
					), 400
			else:
				return json.dumps(
					{
						'Answer': 'Был передан неверный "Login"!'
					}, ensure_ascii = False
				), 400
		except:
			return json.dumps(
				{
					'Answer': 'Неизвестная ошибка на сервере!'
				}, ensure_ascii = False
			), 400
	wrapper.__name__ = func.__name__
	return wrapper

def check_user_login_and_password_and_unique_key(func): # Декоратор
	def wrapper(login):
		# try:
		user_data = json.loads(request.data.decode('UTF-8'))
		password = user_data['Password']
		unique_key = user_data['Unique_Key']

		lock.acquire(True)
		vk_bot_accounts_sql.execute(f"SELECT * From Accounts WHERE Login = '{login}'")
		account = vk_bot_accounts_sql.fetchone()
		lock.release()

		if account != None:
			enrypted_password = encrypt(password, password)
			if enrypted_password == account[1]:
				if unique_key  == account[2]:
					return func(user_data)
				else:
					return json.dumps(
						{
							'Answer': 'Был передан неверный "Unique_Key"!'
						}, ensure_ascii = False
					), 400
			else:
				return json.dumps(
					{
						'Answer': 'Был передан неверный "Password"!'
					}, ensure_ascii = False
				), 400
		else:
			return json.dumps(
				{
					'Answer': 'Был передан неверный "Login"!'
				}, ensure_ascii = False
			), 400
		# except:
		# 	return json.dumps(
		# 		{
		# 			'Answer': 'Неизвестная ошибка на сервере!'
		# 		}, ensure_ascii = False
		# 	), 400
	wrapper.__name__ = func.__name__
	return wrapper

@app.route('/vk_bot/registration_account', methods = ['POST'])
def registration_account(): # Регистрация
	try:
		user_data = json.loads(request.data.decode('UTF-8'))
		login = user_data['Login']
		password = user_data['Password']

		if login == '' and password == '':
			return json.dumps(
				{
					'Answer': 'Введите "Login" и "Password"!'
				}, ensure_ascii = False
			), 400
		elif login == '':
			return json.dumps(
				{
					'Answer': 'Введите "Login"!'
				}, ensure_ascii = False
			), 400
		elif password == '':
			return json.dumps(
				{
					'Answer': 'Введите "Password"!'
				}, ensure_ascii = False
			), 400
		else:
			lock.acquire(True)
			vk_bot_accounts_sql.execute(f"SELECT * From Accounts WHERE Login = '{login}'")
			account = vk_bot_accounts_sql.fetchone()
			lock.release()

			if account == None:
				# Шифрования пароля
				encrypted_password = encrypt(password, password)

				# Создания уникального ключа для пользователя
				generate_unique_key_status = True
				while generate_unique_key_status:
					unique_key = generate_unique_key()
					vk_bot_accounts_sql.execute(f"SELECT * FROM Accounts WHERE Unique_Key = '{unique_key}'")
					account = vk_bot_accounts_sql.fetchone()
					if account == None:
						generate_unique_key_status = False

				# Запись нового аккаунта в базу данных аккаунтов
				vk_bot_accounts_sql.execute("INSERT INTO Accounts VALUES (?, ?, ?)", (login, encrypted_password, unique_key))
				vk_bot_accounts_db.commit()

				# Создаём директорию для нового аккаунта пользователя
				os.mkdir(f'{PATH}/Files/{unique_key}')

				return json.dumps(
					{
						'Answer': 'Вы успешно создали аккаунт.'
					}, ensure_ascii = False
				), 200
			else:
				return json.dumps(
					{
						'Answer': f'Login "{login}" уже занят!'
					}, ensure_ascii = False
				), 400
	except:
		return json.dumps(
			{
				'Answer': 'Неизвестная ошибка на сервере!'
			}, ensure_ascii = False
		), 400

@app.route('/vk_bot/authorization_at_account', methods = ['POST'])
def authorization_at_account(): # Авторизация
	try:
		user_data = json.loads(request.data.decode('UTF-8'))
		login = user_data['Login']
		password = user_data['Password']

		if login == '' and password == '':
			return json.dumps(
				{
					'Answer': 'Введите "Login" и "Password"!'
				}, ensure_ascii = False
			), 400
		elif login == '':
			return json.dumps(
				{
					'Answer': 'Введите "Login"!'
				}, ensure_ascii = False
			), 400
		elif password == '':
			return json.dumps(
				{
					'Answer': 'Введите "Password"!'
				}, ensure_ascii = False
			), 400
		else:
			lock.acquire(True)
			vk_bot_accounts_sql.execute(f"SELECT * From Accounts WHERE Login = '{login}'")
			account = vk_bot_accounts_sql.fetchone()
			lock.release()

			if account != None:
				enrypted_password = encrypt(password, password)
				if enrypted_password == account[1]:
					return json.dumps(
						{
							'Answer': 'Вы успешно авторизовались.',
							'Unique_Key': account[2]
						}, ensure_ascii = False
					), 200
				else:
					return json.dumps(
						{
							'Answer': 'Неверный "Login" или "Password"!'
						}, ensure_ascii = False
					), 400
			else:
				return json.dumps(
					{
						'Answer': 'Такого аккаунта не существует!'
					}, ensure_ascii = False
				), 400
	except:
		return json.dumps(
			{
				'Answer': 'Неизвестная ошибка на сервере!'
			}, ensure_ascii = False
		), 400

@app.route('/vk_bot/<string:login>/create_user_bot', methods = ['POST'])
@check_user_login_and_password_and_unique_key
def create_user_bot(user_data): # Создание бота
	bot_name = user_data['Bot_Name']
	bot_settings = user_data['Bot_Settings']
	password = user_data['Password']
	unique_key = user_data['Unique_Key']

	server_answer = ''
	if bot_name == '':
		server_answer += 'придумайте имя боту'
	if bot_settings['VK_Token'] == '':
		if server_answer == 'придумайте имя боту':
			server_answer += ' и '
		server_answer += 'введите "VK Token"'
	if bot_settings['Group_ID'] == '':
		if server_answer.find('введите "VK Token"') != -1:
			server_answer += ' и "Group ID"'
		else:
			server_answer += 'введите "Group ID"'
	server_answer += '!'
	server_answer = list(server_answer)[0].capitalize() + ''.join(list(server_answer)[1:-1])
	if server_answer ==  'Придумайте имя боту и введите "VK Token" и "Group ID"':
		server_answer = 'Заполните форму добавления бота!'

	if server_answer == '!':
		if find_file_or_folder(f'{PATH}/Files/{unique_key}', bot_name) == False:
			bot_files_path = f'{PATH}/Files/{unique_key}/{bot_name}'
			os.mkdir(bot_files_path)

			with open(f'{bot_files_path}/Bot-Settings.json', 'wb') as file:
				bot_settings = json.dumps(bot_settings, ensure_ascii = False, indent = 2)
				bot_settings = encrypt(password, bot_settings)
				file.write(bot_settings)
			with open(f'{bot_files_path}/User-Commands.json', 'wb') as file:
				user_commands = json.dumps(Config.BOT_DEAFAULT_FILES['User-Commands.json'], ensure_ascii = False, indent = 2)
				user_commands = encrypt(password, user_commands)
				file.write(user_commands)
			with open(f'{bot_files_path}/Log.txt', 'wb') as file:
				log = json.dumps(Config.BOT_DEAFAULT_FILES['Log.txt'], ensure_ascii = False, indent = 2)
				log = encrypt(password, log)
				file.write(log)
			db = sqlite3.connect(f'{bot_files_path}/VK_Bot-Users-DataBase.db')
			db.close()

			return json.dumps(
				{
					'Answer': 'Успешное создание бота.'
				}, ensure_ascii = False
			), 200
		else:
			return json.dumps(
				{
					'Answer': f'Бот под именем "{bot_name}" уже существует!'
				}, ensure_ascii = False
			), 400
	else:
		return json.dumps(
			{
				'Answer': server_answer
			}, ensure_ascii = False
		), 400

@app.route('/vk_bot/<string:login>/get_user_bot_list', methods = ['POST'])
@check_user_login_and_password_and_unique_key
def get_user_bot_list(user_data): # Получение списка ботов
	unique_key = user_data['Unique_Key']

	return json.dumps(
		{
			'Answer': 'Запрос к списку ботов был успешно выполнен.',
			'User_Bot_List': os.listdir(f'{PATH}/Files/{unique_key}')
		}, ensure_ascii = False
	), 200

@app.route('/vk_bot/<string:login>/delete_user_bot', methods = ['POST'])
@check_user_login_and_password_and_unique_key
def delete_user_bot(user_data): # Удаление бота
	bot_name = user_data['Bot_Name']
	unique_key = user_data['Unique_Key']

	if find_file_or_folder(f'{PATH}/Files/{unique_key}', bot_name) == True:
		for file in os.listdir(f'{PATH}/Files/{unique_key}/{bot_name}'):
			os.remove(f'{PATH}/Files/{unique_key}/{bot_name}/{file}')
		os.rmdir(f'{PATH}/Files/{unique_key}/{bot_name}')

		return json.dumps(
			{
				'Answer': 'Успешное удаление бота.'
			}, ensure_ascii = False
		), 200
	else:
		return json.dumps(
			{
				'Answer': f'Бот под именем "{bot_name}" не существует!'
			}, ensure_ascii = False
		), 400

@app.route('/vk_bot/<string:login>/<string:bot_name>/bot_settings/get', methods = ['POST'])
@check_user_login_and_password_and_unique_key_and_bot_name
def user_bot_settings_get(user_data, bot_name): # Получение настроек бота
	password = user_data['Password']
	unique_key = user_data['Unique_Key']

	with open(f'{PATH}/Files/{unique_key}/{bot_name}/Bot-Settings.json', 'rb') as file:
		bot_settings = file.read()
		bot_settings = decrypt(password, bot_settings)
		bot_settings = json.loads(bot_settings)

	return json.dumps(
		{
			'Answer': 'Запрос к файлу "Bot-Settings.json" бота "{bot_name}" был успешно выполнен.',
			'Bot_Settings': bot_settings
		}, ensure_ascii = False
	), 200

@app.route('/vk_bot/<string:login>/<string:bot_name>/bot_settings/update', methods = ['POST'])
@check_user_login_and_password_and_unique_key_and_bot_name
def user_bot_settings_update(user_data, bot_name): # Обновление настроек бота
	password = user_data['Password']
	unique_key = user_data['Unique_Key']

	with open(f'{PATH}/Files/{unique_key}/{bot_name}/Bot-Settings.json', 'wb') as file:
		bot_settings = json.dumps(user_data['Bot_Settings'], ensure_ascii = False, indent = 2)
		bot_settings = encrypt(password, bot_settings)
		file.write(bot_settings)

	return json.dumps(
		{
			'Answer': 'Запрос к файлу "Bot-Settings.json" бота "{bot_name}" был успешно выполнен.'
		}, ensure_ascii = False
	), 200

@app.route('/vk_bot/<string:login>/<string:bot_name>/user_commands/get', methods = ['POST'])
@check_user_login_and_password_and_unique_key_and_bot_name
def user_commands_get(user_data, bot_name): # Получение команд бота
	password = user_data['Password']
	unique_key = user_data['Unique_Key']

	with open(f'{PATH}/Files/{unique_key}/{bot_name}/User-Commands.json', 'rb') as file:
		user_commands = file.read()
		user_commands = decrypt(password, user_commands)
		user_commands = json.loads(user_commands)

	return json.dumps(
		{
			'Answer': 'Запрос к файлу "User-Commands.json" бота "{bot_name}" был успешно выполнен.',
			'User_Commands': user_commands
		}, ensure_ascii = False
	), 200

@app.route('/vk_bot/<string:login>/<string:bot_name>/user_commands/update', methods = ['POST'])
@check_user_login_and_password_and_unique_key_and_bot_name
def user_commands_update(user_data, bot_name): # Обновление команд бота
	password = user_data['Password']
	unique_key = user_data['Unique_Key']

	with open(f'{PATH}/Files/{unique_key}/{bot_name}/User-Commands.json', 'wb') as file:
		user_commands = json.dumps(user_data['User_Commands'], ensure_ascii = False, indent = 2)
		user_commands = encrypt(password, user_commands)
		file.write(user_commands)

	return json.dumps(
		{
			'Answer': 'Запрос к файлу "User-Commands.json" бота "{bot_name}" был успешно выполнен.'
		}, ensure_ascii = False
	), 200

@app.route('/vk_bot/<string:login>/<string:bot_name>/log/get', methods = ['POST'])
@check_user_login_and_password_and_unique_key_and_bot_name
def log_get(user_data, bot_name): # Получение логов бота
	password = user_data['Password']
	unique_key = user_data['Unique_Key']

	with open(f'{PATH}/Files/{unique_key}/{bot_name}/Log.txt', 'rb') as file:
		log = file.read()
		log = decrypt(password, log)
		log = json.loads(log)

	return json.dumps(
		{
			'Answer': 'Запрос к файлу "Log.txt" бота "{bot_name}" был успешно выполнен.',
			'Log': log
		}, ensure_ascii = False
	), 200

@app.route('/vk_bot/<string:login>/<string:bot_name>/log/update', methods = ['POST'])
@check_user_login_and_password_and_unique_key_and_bot_name
def log_update(user_data, bot_name): # Обновление логов бота
	password = user_data['Password']
	unique_key = user_data['Unique_Key']

	with open(f'{PATH}/Files/{unique_key}/{bot_name}/Log.txt', 'wb') as file:
		log = json.dumps(user_data['Log'], ensure_ascii = False, indent = 2)
		log = encrypt(password, log)
		file.write(log)

	return json.dumps(
		{
			'Answer': 'Запрос к файлу "Log.txt" бота "{bot_name}" был успешно выполнен.'
		}, ensure_ascii = False
	), 200

@app.route('/vk_bot/<string:login>/<string:bot_name>/database/find', methods = ['POST'])
@check_user_login_and_password_and_unique_key_and_bot_name
def user_database_find(user_data, bot_name): # Поиск одной записи в БД
	unique_key = user_data['Unique_Key']

	vk_bot_user_db = sqlite3.connect(f'{PATH}/Files/{unique_key}/{bot_name}/VK_Bot-Users-DataBase.db', check_same_thread = False)
	vk_bot_user_sql = vk_bot_user_db.cursor()
	vk_bot_user_sql.execute(user_data['SQLite3_Command'])
	result = vk_bot_user_sql.fetchone()
	vk_bot_user_db.close()

	return json.dumps(
		{
			'Answer': 'Запрос к базе данных бота "{bot_name}" был успешно выполнен.',
			'Result': result
		}, ensure_ascii = False
	), 200

@app.route('/vk_bot/<string:login>/<string:bot_name>/database/find_all', methods = ['POST'])
@check_user_login_and_password_and_unique_key_and_bot_name
def user_database_find_all(user_data, bot_name): # Поиск несколько записей в БД
	unique_key = user_data['Unique_Key']

	vk_bot_user_db = sqlite3.connect(f'{PATH}/Files/{unique_key}/{bot_name}/VK_Bot-Users-DataBase.db', check_same_thread = False)
	vk_bot_user_sql = vk_bot_user_db.cursor()
	vk_bot_user_sql.execute(user_data['SQLite3_Command'])
	result = vk_bot_user_sql.fetchall()
	vk_bot_user_db.close()

	return json.dumps(
		{
			'Answer': 'Запрос к базе данных бота "{bot_name}" был успешно выполнен.',
			'Result': result
		}, ensure_ascii = False
	), 200

@app.route('/vk_bot/<string:login>/<string:bot_name>/database/edit_database', methods = ['POST'])
@check_user_login_and_password_and_unique_key_and_bot_name
def edit_user_database(user_data, bot_name): # Редактирования БД
	unique_key = user_data['Unique_Key']

	vk_bot_user_db = sqlite3.connect(f'{PATH}/Files/{unique_key}/{bot_name}/VK_Bot-Users-DataBase.db', check_same_thread = False)
	vk_bot_user_sql = vk_bot_user_db.cursor()

	if 'Values' in user_data:
		vk_bot_user_sql.execute(user_data['SQLite3_Command'], user_data['Values'])
	else:
		vk_bot_user_sql.execute(user_data['SQLite3_Command'])
	vk_bot_user_db.commit()
	vk_bot_user_db.close()

	return json.dumps(
		{
			'Answer': 'Запрос к базе данных бота "{bot_name}" был успешно выполнен.'
		}, ensure_ascii = False
	), 200
# ==================================================================

if __name__ == '__main__':
	app.run(debug = True)