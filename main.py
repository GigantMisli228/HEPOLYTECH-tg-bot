import telebot
from telebot import types
import requests
import sqlite3
import re

import os
import sys
import vk_api
import configparser
from telebot.types import InputMediaPhoto

bot = telebot.TeleBot('...')

# Считываем настройки
config_path = os.path.join(sys.path[0], 'settings.ini')
config = configparser.ConfigParser()
config.read(config_path)
#print(config['VK'])
LOGIN = config.get('VK', 'LOGIN')
PASSWORD = config.get('VK', 'PASSWORD')
DOMAIN = config.get('VK', 'DOMAIN')
DOMAIN2 = config.get('VK', 'DOMAIN2')
DOMAIN3 = config.get('VK', 'DOMAIN3')
domains = [DOMAIN, DOMAIN2, DOMAIN3]
COUNT = config.get('VK', 'COUNT')
VK_TOKEN = config.get('VK', 'TOKEN', fallback=None)
BOT_TOKEN = config.get('Telegram', 'BOT_TOKEN')
CHANNEL = config.get('Telegram', 'CHANNEL')
INCLUDE_LINK = config.getboolean('Settings', 'INCLUDE_LINK')
PREVIEW_LINK = config.getboolean('Settings', 'PREVIEW_LINK')


message_breakers = [':', ' ', '\n']
max_message_length = 4091

#bot = telebot.TeleBot(BOT_TOKEN)


# Получаем данные из vk.com
def get(domain, count):
	global LOGIN
	global PASSWORD
	global VK_TOKEN
	global config
	global config_path

	# подключаемся к ВК и получаем токен
	if VK_TOKEN is not None:
		vk_session = vk_api.VkApi(LOGIN, PASSWORD, VK_TOKEN)
		vk_session.auth(token_only=True)
	else:
		vk_session = vk_api.VkApi(LOGIN, PASSWORD)
		vk_session.auth()

	new_token = vk_session.token['access_token']

	# записываем токен в конфиг
	if VK_TOKEN != new_token:
		VK_TOKEN = new_token
		config.set('VK', 'TOKEN', new_token)
		with open(config_path, "w") as config_file:
			config.write(config_file)

	vk = vk_session.get_api()

	# Используем метод wall.get из документации по API vk.com
	response = vk.wall.get(domain=domain, count=count)

	return response


# Проверяем данные по условиям перед отправкой
def check(chat_id):
	#global DOMAIN
	global domains
	global COUNT
	global INCLUDE_LINK
	global bot
	global config
	global config_path

	for DOMAIN in domains:

		response = get(DOMAIN, COUNT)
		response = reversed(response['items'])

		for post in response:

			# читаем последний известный id из файла
			id = 0
			if DOMAIN == domains[0]:
				id = config.get('Settings', 'LAST_ID')
			elif DOMAIN == domains[1]:
				id = config.get('Settings', 'LAST_ID2')
			else:
				id = config.get('Settings', 'LAST_ID3')

			# сравниваем id, пропускаем уже опубликованные
			#if int(post['id']) <= int(id):
			#	continue

			print('------------------------------------------------------------------------------------------------')
			print(post)

			# текст
			text = post['text']

			# проверяем есть ли что то прикрепленное к посту
			images = []
			links = []
			attachments = []
			if 'attachments' in post:
				attach = post['attachments']
				for add in attach:
					if add['type'] == 'photo':
						img = add['photo']
						images.append(img)
					elif add['type'] == 'audio':
						continue
					elif add['type'] == 'video':
						video = add['video']
						if 'player' in video:
							links.append(video['player'])
					else:
						for (key, value) in add.items():
							if key != 'type' and 'url' in value:
								attachments.append(value['url'])

			# прикрепляем ссылку на пост, если INCLUDE_LINK = true в конфиге
			if INCLUDE_LINK:
				post_url = "https://vk.com/" + DOMAIN + "?w=wall" + \
					str(post['owner_id']) + '_' + str(post['id'])
				links.insert(0, post_url)
			post_link = ['Cсылка на пост:']
			text = '\n'.join([text] + post_link + links)


			# если картинка будет одна, то прикрепим её к посту, как ссылку
			if len(images) == 1:
				image_url = str(max(img["sizes"], key=lambda size: size["type"])["url"])

				bot.send_message(chat_id, '<a href="' + image_url + '">⁠</a>' + text, parse_mode='HTML')

			# если их несколько, то текст отправим в одном посте, картинки - в другом
			elif len(images) > 1:
				image_urls = list(map(lambda img: max(
					img["sizes"], key=lambda size: size["type"])["url"], images))
				print(image_urls)

				send_text(text)

				bot.send_media_group(chat_id, map(lambda url: InputMediaPhoto(url), image_urls))
			else:
				send_text(text, chat_id)

			# проверяем есть ли репост другой записи
			if 'copy_history' in post:
				copy_history = post['copy_history']
				copy_history = copy_history[0]
				print('--copy_history--')
				print(copy_history)
				text = copy_history['text']
				send_text(text)

				# проверяем есть ли у репоста прикрепленное сообщение
				if 'attachments' in copy_history:
					copy_add = copy_history['attachments']
					copy_add = copy_add[0]

					# если это картинки
					if copy_add['type'] == 'photo':
						attach = copy_history['attachments']
						for img in attach:
							image = img['photo']
							send_img(image)

			# записываем id в файл


			if DOMAIN == domains[0]:
				config.set('Settings', 'LAST_ID', str(post['id']))
			elif DOMAIN == domains[1]:
				config.set('Settings', 'LAST_ID2', str(post['id']))
			else:
				config.set('Settings', 'LAST_ID3', str(post['id']))
			with open(config_path, "w") as config_file:
				config.write(config_file)


	# отправляем посты в телеграмм

# текст
def send_text(text, chat_id):
	global CHANNEL
	global PREVIEW_LINK
	global bot

	if text == '':
		print('without text')
	else:
		# в телеграмме есть ограничения на длину одного сообщения в 4091 символ, разбиваем длинные сообщения на части
		for msg in split(text):
			bot.send_message(chat_id, msg, disable_web_page_preview=not PREVIEW_LINK)


# разделитель
def split(text):
	global message_breakers
	global max_message_length

	if len(text) >= max_message_length:
		last_index = max(
			map(lambda separator: text.rfind(separator, 0, max_message_length), message_breakers))
		good_part = text[:last_index]
		bad_part = text[last_index + 1:]
		return [good_part] + split(bad_part)
	else:
		return [text]


# Отправка изображений
def send_img(img):
	global bot

	# Находим картинку с максимальным качеством
	url = max(img["sizes"], key=lambda size: size["type"])["url"]
	bot.send_photo(CHANNEL, url)


#работа с базой SQLite

#открываем базу
def sqliteOpenDB():
	try:
		sqlite_connection = sqlite3.connect('poly.db', check_same_thread=False)
		return sqlite_connection

	except sqlite3.Error as error:
		print("Ошибка при подключении к sqlite", error)




#получаем последний цифра урла по номеру группы
def selectAddUrl(sqlite_connection, group_numb):
	query = f"select add_url from poly_groups where group_number='{group_numb}';"
	cursor = sqlite_connection.cursor()
	res = cursor.execute(query)
	add_url = res.fetchall()
	cursor.close()
	return add_url[0][0]

#получаем список институтов
def selectInstitutes(sqlite_connection):
	query = f"select DISTINCT institute from poly_groups;"
	cursor = sqlite_connection.cursor()
	res = cursor.execute(query)
	institutes = []
	institutes_res = res.fetchall()
	cursor.close()
	for institute_cortege in institutes_res:
		institutes.append(institute_cortege[0])
	return institutes

#получаем список курсов для конкретного института
def selectСourses(sqlite_connection, institute):
	query = f"select DISTINCT course from poly_groups WHERE institute='{institute}';"
	cursor = sqlite_connection.cursor()
	res = cursor.execute(query)
	courses = []
	courses_res = res.fetchall()
	cursor.close()
	for course_cortege in courses_res:
		courses.append(course_cortege[0])
	return courses

#получаем группы для конкретного института и курса
def selectGroups(sqlite_connection, institute, course):
	query = f"select group_number from poly_groups WHERE institute='{institute}' and course='{course}';"
	cursor = sqlite_connection.cursor()
	res = cursor.execute(query)
	groups = []
	groups_res = res.fetchall()
	cursor.close()
	for group_cortege in groups_res:
		groups.append(group_cortege[0])
	return groups

def closeDB(sqlite_connection):
	if (sqlite_connection):
		sqlite_connection.close()
		print("Соединение с SQLite закрыто")






weekdays = {
	1: 'ПОНЕДЕЛЬНИК',
	2: 'ВТОРНИК',
	3: 'СРЕДА',
	4: 'ЧЕТВЕРГ',
	5: 'ПЯТНИЦА',
	6: 'СУББОТА'
}


@bot.message_handler(commands=['start'])
def start(message):
	bot.send_message(message.chat.id, 'Приветствую, Политехник!. Чтобы увидеть расписание, введи номер своей группы в формате <b>ХХХХХХХ/ХХХХХ</b>, либо воспользуйся командой /timetable. Нажми /map чтобы посмотреть карту кампуса.', parse_mode= 'html')


@bot.message_handler(commands = ['news'])
def news(message):
	check(message.chat.id)


@bot.message_handler(commands = ['map'])
def map(message):
	photo = open('map.jpg', 'rb')
	bot.send_message(message.chat.id, 'Пока карта только такая, скоро исправим...')
	bot.send_photo(message.chat.id, photo)

@bot.message_handler(commands = ['autonews'])
def autonews(message):
	markup = types.InlineKeyboardMarkup()
	markup.add(types.InlineKeyboardButton('Подписаться на Новостной канал', url = 'https://t.me/joinchat/AAAAAFjVVKqhtUWyzcBSfg'))
	bot.send_message(message.chat.id, 'Чтобы получать новости автоматически, подпишись на новостной канал 👇🏻', reply_markup=markup)

#создаем кнопки с институтами
@bot.message_handler(commands = ['timetable'])
def timetable(message):
	global connection
	markup = types.ReplyKeyboardMarkup(resize_keyboard = True ,row_width=1)
	#fizmeh = types.KeyboardButton('ФИЗМЕХ')
	institutes = selectInstitutes(connection)
	for institute in institutes:
		markup.add(institute)
	bot.send_message(message.chat.id, 'Выбери институт', reply_markup=markup)

#создаем кнопки с курсами
def course(message, institute):
	global connection
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
	courses = selectСourses(connection, institute)
	for course in courses:
		markup.add(f'{course} курс')
	bot.send_message(message.chat.id, 'Выбери курс', reply_markup=markup)

#создаем кнопки с группами
def groups(message, institute, course):
	global connection
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
	groups = selectGroups(connection, institute, course)
	for group in groups:
		markup.add(group)
	bot.send_message(message.chat.id, 'Выбери группу', reply_markup=markup)




#отправляет get-запрос на сайт спбпу и получает json(структура данных)
def sendGet(message, add_url):
	target_url = "https://ruz.spbstu.ru/api/v1/ruz/scheduler/"
	target_url = target_url + add_url
	try:
		print('start')
		resp = requests.get(target_url)
		print('stop')
	except:
		bot.send_message(message.chat.id, 'Что-то пошло не так')
		return
	return resp.json()

#разбиваем полученный json на дни недели
def getDays(days):
	global output_message
	output_message = ''
	for day in days:

		day_of_week = weekdays[day['weekday']]
		date = day['date']
		date = date.split('-')
		date.reverse()
		date = '.'.join(date)
		output_message += f'📅{date}\n'
		output_message += f'📚<b>{day_of_week}:</b>\n'
		lessons = day['lessons']

		getLessons(lessons)
		output_message += '\n\n'


#разбиваем дни на пары
def getLessons(lessons):
	global output_message
	for lesson in lessons:
		subject = lesson['subject']
		time_start = lesson['time_start']
		time_end = lesson['time_end']
		typeObj = lesson['typeObj']
		format = typeObj['name']
		teachers = lesson['teachers']
		classrooms = lesson['auditories']
		classroom = classrooms[0]['name']
		buildings = classrooms[0]['building']
		building = buildings['name']


		full_name = ''
		try:
			full_name = teachers[0]['full_name']
		except:
			full_name = ''
		#print(type(teachers))
		output_message += f'<em><strong>- {subject}</strong></em>\n'
		output_message += f'\t\t\t\t\t⏰{time_start}-{time_end}\n'
		output_message += f'\t\t\t\t\t📎{format}\n'
		output_message += f'\t\t\t\t\t🏛{building}\n'
		output_message += f'\t\t\t\t\t📍ауд. {classroom}\n'
		output_message += f'\t\t\t\t\t👨‍🏫{full_name}\n'



#обработка сообщений юзера
@bot.message_handler(content_types=['text'])
def get_user_message(message):
	global connection, institute, course_numb, group_numb
	if message.text == 'Карта':
		photo = open('map.jpg', 'rb')
		bot.send_message(message.chat.id, 'Пока карта только такая, скоро исправим...')
		bot.send_photo(message.chat.id, photo)
	elif message.text == 'карта':
		bot.send_message(message.chat.id, 'Пока карта только такая, скоро исправим...')
		photo = open('map.jpg', 'rb')
		bot.send_photo(message.chat.id, photo)
	elif message.text in selectInstitutes(connection):
		institute = message.text
		course(message, institute)
	elif  re.match(r'\d курс', message.text) and int(message.text[:1]) in selectСourses(connection, institute):
		course_numb = message.text
		groups(message, institute, course_numb[:1])
	elif message.text == 'новости':
		check(message.chat.id)
	elif message.text == 'Новости':
		check(message.chat.id)
	elif re.match('[0-9]{7}/[0-9]{5}', message.text):
		group_numb = message.text
		add_url = selectAddUrl(connection, group_numb)
		schedule_json = sendGet(message, str(add_url))
		getDays(schedule_json['days'])
		# print(f"start week day - {schedule_json['week']['date_start']}, end week day - {schedule_json['week']['date_end']}")
		bot.send_message(message.chat.id, output_message, parse_mode='html')
		pass

	else:
		bot.send_message(message.chat.id, 'Я тебя не понимаю')
	print(f"Сообщение от {message.from_user.first_name} {message.from_user.last_name} (id = {message.from_user.id}) \n {message.text}")

@bot.message_handler(content_types=['sticker'])
def get_user_sticker(message):
	sticker_id = message.sticker.file_id
	if message.sticker.file_id == sticker_id:
		bot.send_message(message.chat.id, 'Крутой стикер, но я не понимаю как он выглядит..')
	print(f"Сообщение от {message.from_user.first_name} {message.from_user.last_name} (id = {message.from_user.id}) \n Чел прислал стикер")

global connection, institute, course_numb, group_numb
connection = sqliteOpenDB()
group_numb = ""
institute = ''
course_numb = ''


bot.polling(none_stop=True)

closeDB(connection)
