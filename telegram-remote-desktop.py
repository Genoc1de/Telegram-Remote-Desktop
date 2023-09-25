import urllib
from telegram.ext import *
from telegram import KeyboardButton, ReplyKeyboardMarkup
from mss import mss
import tempfile
import os
import psutil
import ctypes
import webbrowser
import pyperclip
import subprocess
import json
import time
import keyboard
import pyautogui
class TelegramBot:
    def __init__(self):
        f = open('auth-test.json')
        auth = json.load(f)
        self.TOKEN = auth["TOKEN"]
        self.CHAT_ID = auth["CHAT_ID"]

    def start_command(self, update, context):
        buttons = [[KeyboardButton("На полный экран(F11)")],
                   [KeyboardButton("🔒 Заблокировать экран")],
                   [KeyboardButton("🎞 Youtube TV")],
                   [KeyboardButton("🖥 Выключить Windows")],
                   [KeyboardButton("📷 Сделать скриншот")],
                   [KeyboardButton("🌍 Закрыть браузер")],
                   [KeyboardButton("🌍 Открыть браузер(F11)")],
                   [KeyboardButton("⚙ Запущенные процессы")],
                   [KeyboardButton("💡 Больше команд")]]
        context.bot.send_message(
            chat_id=self.CHAT_ID, text="👋 Напиши любую команду, или нажми на кнопку!",
                                                        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))

    def error(self, update, context):
        print(f"Update {update} caused error {context.error}")

    def take_screenshot(self):
        TEMPDIR = tempfile.gettempdir()
        os.chdir(TEMPDIR)
        with mss() as sct:
            sct.shot(mon=-1)
        return os.path.join(TEMPDIR, 'monitor-0.png')

    def handle_message(self, update, input_text):
        global processes
        usr_msg = input_text.split()
        webbrowser.register('Chrome', None,
                            webbrowser.BackgroundBrowser('C:\Program Files\Google\Chrome\Application\chrome.exe', ))

        if input_text == "🎞 Youtube TV":
            try:
                url = f'https://youtube.com/tv#/'
                webbrowser.get('chrome').open(url, new=2, autoraise=True)
                return 'Youtube Tv успешно открыт'
            except Exception as e:
                return 'Произошла ошибка'

        if input_text == "🌍 Открыть браузер(F11)":
            try:
                pyautogui.hotkey('win', 'r')
                time.sleep(1)
                pyautogui.write('chrome --profile-directory="Profile 2')
                pyautogui.press('enter')
                time.sleep(5)
                pyautogui.hotkey('win', 'up')
                pyautogui.press('F11')
                return 'Ok'
            except Exception as e:
                return 'Произошла ошибка'

        if input_text == "На полный экран(F11)":
            try:
                pyautogui.press('F11')
                return 'Ok'
            except Exception as e:
                return 'Произошла ошибка'

        if input_text == "💡 Больше команд":
            return """/url <Ссылка или запрос>: Откроется браузер с введеной ссылкой или запросом\n\n/kill <Наименование процесса>: закрыть процесс ( /processes , чтобы вывести наименование всех активных процессов)\n\n/cmd <команда>: выполнить указанную команду\n\n/cd <путь>: выбрать директорию\n\n/download <путь до файла>: скачать файл по заданному пути"""

        if input_text in ("🔒 Заблокировать экран"):
            try:
                ctypes.windll.user32.LockWorkStation()
                time.sleep(10)
                return "Экран успешно заблокирован"
            except:
                return "Произошла ошибка"

        if input_text == "📷 Сделать скриншот":
            update.message.bot.send_photo(
                chat_id=self.CHAT_ID, photo=open(self.take_screenshot(), 'rb'))
            return "Готово"

        if input_text == "🖥 Выключить Windows":
            try:
                os.system('shutdown -s')
                time.sleep(30)
                return "Windows выключен"
            except:
                return "Произошла ошибка, Windows не был выключен"


        if input_text in ("⚙ Запущенные процессы", "/processes"):
            try:
                proc_list = []
                for proc in psutil.process_iter():
                    if proc.name() not in proc_list:
                        proc_list.append(proc.name())
                processes = "\n".join(proc_list)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
            return processes

        if input_text == "🌍 Закрыть браузер":
            try:
                PROCNAME = "chrome.exe"
                for proc in psutil.process_iter():
                    if proc.name() == PROCNAME:
                        os.system("taskkill /im chrome.exe /f")
                return "Браузер закрыт"
            except:
                return "Произошла ошибка, или браузер не запущен"

        if usr_msg[0] == '/kill':
            proc_list = []
            for proc in psutil.process_iter():
                p = proc_list.append([proc.name(), str(proc.pid)])
            try:
                for p in proc_list:
                    if p[0] == usr_msg[1]:
                        psutil.Process(int(p[1])).terminate()
                return 'Процесс был успешно закрыт'
            except:
                return 'Произошла ошибка при завершении процесса'
        if usr_msg[0] == '/url':
            try:
                if '.' in usr_msg[1]:
                    webbrowser.get('Chrome').open(usr_msg[1])
                else:
                    search_query = ' '.join(usr_msg[1:])
                    encoded_query = urllib.parse.quote(search_query, encoding='utf-8')
                    url = f'https://www.google.com/search?q={encoded_query}'
                    webbrowser.get('chrome').open(url)
                    keyboard.press('f11')
                    return 'Ссылка успешно открыта'
            except Exception as e:
                return 'Произошла ошибка'

        if usr_msg[0] == "/cd":
            if usr_msg[1]:
                try:
                    os.chdir(usr_msg[1])
                except:
                    return "Путь не найден!"
                res = os.getcwd()
                if res:
                    return res

        if usr_msg[0] == "/download":
            if usr_msg[1]:
                if os.path.exists(usr_msg[1]):
                    try:
                        document = open(usr_msg[1], 'rb')
                        update.message.bot.send_document(
                            self.CHAT_ID, document)
                    except:
                        return "Что-то пошло не так..."

        if usr_msg[0] == "/cmd":
            res = subprocess.Popen(
                usr_msg[1:], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
            stdout = res.stdout.read().decode("utf-8", 'ignore').strip()
            stderr = res.stderr.read().decode("utf-8", 'ignore').strip()
            if stdout:
                return (stdout)
            elif stderr:
                return (stderr)
            else:
                return ''

    def send_response(self, update, context):
        user_message = update.message.text
        # Please modify this
        if update.message.chat["username"] not in ("nikitaa_aleksandrovich", "milana_m_a"):
            print("[!] " + update.message.chat["username"] +
                  ' пробовал использовать бота')
            context.bot.send_message(
                chat_id=self.CHAT_ID, text="Здесь нечего смотреть.")
        else:
            encoding = 'ascii' if all(ord(char) < 128 for char in user_message) else 'utf-8'
            user_message = user_message.encode(encoding, 'ignore').decode(encoding).strip(' ')
            user_message = user_message[0] + user_message[1:]
            response = self.handle_message(update, user_message)
            if response:
                if (len(response) > 4096):
                    for i in range(0, len(response), 4096):
                        context.bot.send_message(
                            chat_id=self.CHAT_ID, text=response[i:4096+i])
                else:
                    context.bot.send_message(
                        chat_id=self.CHAT_ID, text=response)

    def start_bot(self):
        updater = Updater(self.TOKEN, use_context=True)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start_command))
        dp.add_handler(MessageHandler(Filters.text, self.send_response))
        dp.add_error_handler(self.error)
        updater.start_polling()
        print("[+] BOT has started")
        updater.idle()


bot = TelegramBot()
bot.start_bot()
