import telebot
from telebot import types
import requests
import json



bot = telebot.TeleBot('5255747551:AAGM3zvW7eJSorp1F8LrX4oJ0GqgYvMhK6U')

fizmeh1 = {

    '5030102/10001': '34470',      #ФИЗМЕХ1курс
    '5030102/10002': '34471',
    '5030102/10003': '34472',
    '5030102/10004': '34473',
    '5030103/10001': '34474',
    '5030103/10002': '34475',
    '5030103/10003': '34476',
    '5030103/10004': '34477',
    '5030301/10001': '34478',
    '5030301/10002': '34479',
    '5030302/10001': '34480',
    '5030302/10002': '34481',
    '5030302/10003': '34482',
    '5030302/10004': '34483',
    '5030302/10005': '34484',
    '5031503/10001': '34485',
    '5031503/10002': '34486',
    '5031503/10003': '34487'
}

fizmeh2 = {
    '5030102/00001': '34512',     #ФИЗМЕХ2курс
    '5030102/00002': '34513',
    '5030102/00003': '34514',
    '5030102/00004': '34515',
    '5030103/00001': '34516',
    '5030103/00002': '34517',
    '5030103/00003': '34518',
    '5030103/00004': '34519',
    '5030301/00001': '34520',
    '5030301/00002': '34521',
    '5030302/00001': '34522',
    '5030302/00002': '34523',
    '5030302/00003': '34524',
    '5030302/00004': '34525',
    '5031503/00001': '34526',
    '5031503/00002': '34527',
    '5031503/00003': '34528'
}


fizmeh3 = {
    '5030102/90101': '34552',     #ФИЗМЕХ3курс
    '5030102/90201': '34553',
    '5030102/90401': '34554',
    '5030103/90101': '34555',
    '5030103/90201': '34556',
    '5030103/90301': '34557',
    '5030301/90101': '34558',
    '5030301/90102': '34559',
    '5030302/90101': '34560',
    '5030302/90201': '34561',
    '5030302/90501': '34562',
    '5030302/90801': '34563',
    '5031503/90301': '34564',
    '5031503/90302': '34565',
    '5031503/90401': '34566'
}




fizmeh4 = {
    '5030102/80101': '34576',     #ФИЗМЕХ4курс
    '5030102/80201': '34577',
    '5030102/80401': '34578',
    '5030103/80101': '34579',
    '5030103/80201': '34580',
    '5030103/80301': '34581',
    '5030301/80101': '34582',
    '5030302/80101': '34583',
    '5030302/80201': '34584',
    '5030302/80501': '34585',
    '5030302/80801': '34586',
    '5031503/80301': '34587',
    '5031503/80302': '34588',
    '5031503/80401': '34589'

}

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

@bot.message_handler(commands = ['map'])
def map(message):
    photo = open('map.jpg', 'rb')
    bot.send_message(message.chat.id, 'Пока карта только такая, скоро исправим...')
    bot.send_photo(message.chat.id, photo)

@bot.message_handler(commands = ['timetable'])
def timetable(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    fizmeh = types.KeyboardButton('ФИЗМЕХ')
    markup.add(fizmeh)
    bot.send_message(message.chat.id, 'Выбери институт', reply_markup=markup)
def course(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    course1 = types.KeyboardButton('1 курс')
    course2 = types.KeyboardButton('2 курс')
    course3 = types.KeyboardButton('3 курс')
    course4 = types.KeyboardButton('4 курс')
    markup.add(course1, course2, course3, course4)
    bot.send_message(message.chat.id, 'Выбери курс', reply_markup=markup)

def fizmeh1Groups(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    group_list = []
    for link in fizmeh1:
        group_list.append(link)
    for group in group_list:
        markup.add(types.KeyboardButton(group))
    bot.send_message(message.chat.id, 'Выбери группу', reply_markup=markup)

def fizmeh2Groups(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    group_list = []
    for link in fizmeh2:
        group_list.append(link)
    for group in group_list:
        markup.add(types.KeyboardButton(group))
    bot.send_message(message.chat.id, 'Выбери группу', reply_markup=markup)

def fizmeh3Groups(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    group_list = []
    for link in fizmeh3:
        group_list.append(link)
    for group in group_list:
        markup.add(types.KeyboardButton(group))
    bot.send_message(message.chat.id, 'Выбери группу', reply_markup=markup)

def fizmeh4Groups(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    group_list = []
    for link in fizmeh4:
        group_list.append(link)
    for group in group_list:
        markup.add(types.KeyboardButton(group))
    bot.send_message(message.chat.id, 'Выбери группу', reply_markup=markup)



#отправляет get-запрос на сайт спбпу и получает json(структура данных)
def sendGet1(group_numb):
    target_url = "https://ruz.spbstu.ru/api/v1/ruz/scheduler/"
    print(group_numb)

    target_url = target_url + fizmeh1[group_numb]
    try:
        resp = requests.get(target_url)
    except:
        bot.send_message(message.chat.id, 'Что-то пошло не так')
    return resp.json()

def sendGet2(group_numb):
    target_url = "https://ruz.spbstu.ru/api/v1/ruz/scheduler/"
    print(group_numb)

    target_url = target_url + fizmeh2[group_numb]
    try:
        resp = requests.get(target_url)
    except:
        bot.send_message(message.chat.id, 'Что-то пошло не так')
    return resp.json()

def sendGet3(group_numb):
    target_url = "https://ruz.spbstu.ru/api/v1/ruz/scheduler/"
    print(group_numb)

    target_url = target_url + fizmeh3[group_numb]
    try:
        resp = requests.get(target_url)
    except:
        bot.send_message(message.chat.id, 'Что-то пошло не так')
    return resp.json()

def sendGet4(group_numb):
    target_url = "https://ruz.spbstu.ru/api/v1/ruz/scheduler/"
    print(group_numb)

    target_url = target_url + fizmeh4[group_numb]
    try:
        resp = requests.get(target_url)
    except:
        bot.send_message(message.chat.id, 'Что-то пошло не так')
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
        '''
        webinar_url = lesson['lms_url']
        print(webinar_url)
        if webinar_url != '':
            webinar_url = lesson['lms_url']
        else:
            webinar_url = ''
        '''

        full_name = ''
        try:
            full_name = teachers[0]['full_name']
        except:
            full_name = ''
        print(type(teachers))
        output_message += f'<em><strong>- {subject}</strong></em>\n'
        output_message += f'\t\t\t\t\t⏰{time_start}-{time_end}\n'
        output_message += f'\t\t\t\t\t📎{format}\n'
        output_message += f'\t\t\t\t\t🏛{building}\n'
        output_message += f'\t\t\t\t\t📍ауд. {classroom}\n'
        output_message += f'\t\t\t\t\t👨‍🏫{full_name}\n'

#TODO
# subject: aud, building, teacher,
# проверка на 200
# кнопки






@bot.message_handler(content_types=['text'])
def get_user_message(message):
    if message.text == 'Карта':
        photo = open('map.jpg', 'rb')
        bot.send_message(message.chat.id, 'Пока карта только такая, скоро исправим...')
        bot.send_photo(message.chat.id, photo)
    elif message.text == 'карта':
        bot.send_message(message.chat.id, 'Пока карта только такая, скоро исправим...')
        photo = open('map.jpg', 'rb')
        bot.send_photo(message.chat.id, photo)
    elif message.text == 'ФИЗМЕХ':
        course(message)
    elif message.text == '1 курс':
        fizmeh1Groups(message)
    elif message.text == '2 курс':
        fizmeh2Groups(message)
    elif message.text == '3 курс':
        fizmeh3Groups(message)
    elif message.text == '4 курс':
        fizmeh4Groups(message)
    else:
        if message.text in fizmeh1.keys():
            schedule_json = sendGet1(message.text)
            getDays(schedule_json['days'])
            #print(f"start week day - {schedule_json['week']['date_start']}, end week day - {schedule_json['week']['date_end']}")
            bot.send_message(message.chat.id, output_message, parse_mode= 'html')
        elif message.text in fizmeh2.keys():
            schedule_json = sendGet2(message.text)
            getDays(schedule_json['days'])
            #print(f"start week day - {schedule_json['week']['date_start']}, end week day - {schedule_json['week']['date_end']}")
            bot.send_message(message.chat.id, output_message, parse_mode= 'html')
        elif message.text in fizmeh3.keys():
            schedule_json = sendGet3(message.text)
            getDays(schedule_json['days'])
            #print(f"start week day - {schedule_json['week']['date_start']}, end week day - {schedule_json['week']['date_end']}")
            bot.send_message(message.chat.id, output_message, parse_mode= 'html')
        if message.text in fizmeh4.keys():
            schedule_json = sendGet4(message.text)
            getDays(schedule_json['days'])
            #print(f"start week day - {schedule_json['week']['date_start']}, end week day - {schedule_json['week']['date_end']}")
            bot.send_message(message.chat.id, output_message, parse_mode= 'html')
        #else:
        #    bot.send_message(message.chat.id, 'Не совсем тебя понимаю... ')
        print(f"Сообщение от {message.from_user.first_name} {message.from_user.last_name} (id = {message.from_user.id}) \n {message.text}")

@bot.message_handler(content_types=['sticker'])
def get_user_sticker(message):
    sticker_id = message.sticker.file_id
    if message.sticker.file_id == sticker_id:
        bot.send_message(message.chat.id, 'Крутой стикер, но я не понимаю как он выглядит..')
    print(f"Сообщение от {message.from_user.first_name} {message.from_user.last_name} (id = {message.from_user.id}) \n Чел прислал стикер")


bot.polling(none_stop=True)