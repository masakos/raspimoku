import RPi.GPIO as GPIO
import datetime
import sqlite3
import time

# ポート番号の定義
SWITCH = 18
LED = 21
led_value = GPIO.LOW

# GPIOの初期化
GPIO.setmode(GPIO.BCM)
GPIO.setup(SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED, GPIO.OUT)

dbname = 'timerecoder.db'


def get_str_now():
    date_time_format = '%Y-%m-%d %H:%M:%S'
    now = datetime.datetime.now()
    return now.strftime(date_time_format)


def record_start_time():
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()

    cur.execute('SELECT max(id) FROM recorder')
    max_id = cur.fetchone()[0] + 1
    data = (max_id, get_str_now())
    cur.execute('insert into recorder values (?,?, "")', data)
    conn.commit()

    cur.close()
    conn.close()


def record_end_time():
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    end_time = get_str_now()

    cur.execute('SELECT max(id) FROM recorder')
    max_id = cur.fetchone()[0]
    data = (end_time, max_id)
    cur.execute('update recorder set end_time=? where id=?', data)
    conn.commit()

    cur.close()
    conn.close()


def callback_change_switch(ch):
    global led_value
    if ch != SWITCH: return
    if led_value == GPIO.LOW:
        GPIO.output(LED, GPIO.HIGH)
        led_value = GPIO.HIGH
        record_start_time()
        print('記録スタート')
    else:
        GPIO.output(LED, GPIO.LOW)
        led_value = GPIO.LOW
        record_end_time()
        print('記録終了!')


# イベントの設定
GPIO.add_event_detect(
    SWITCH,  # ポート番号
    GPIO.RISING,  # イベントの種類
    callback=callback_change_switch,
    bouncetime=200)  # 連続イベントを制限

# LEDを消灯
GPIO.output(LED, GPIO.LOW)

try:
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()

