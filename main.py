import os
import serial
import psutil
import sys
from time import sleep
from re import findall
from subprocess import check_output
from datetime import datetime

ARDUINO_DEV_PATH = "/dev/ttyUSB0"
ARDUINO_BAND_SPEED = 9600


def is_night_mode() -> bool:
    hour = datetime.now().time().hour
    if hour >= 22 or hour < 8:
      return True
    return False


def get_temp() -> int:
    temp = check_output(["vcgencmd","measure_temp"]).decode()    # Выполняем запрос температуры
    temp = float(findall('\d+\.\d+', temp)[0])                   # Извлекаем при помощи регулярного выражения значение температуры из строки "temp=47.8'C"
    return int(temp)


def form_send_string() -> str:
    cpu_temp = get_temp()
    gpu_temp = 0
    cpu_load = int(psutil.cpu_percent())
    gpu_load = 0
    ram_use = int(psutil.virtual_memory().percent)
    gpu_memory_use = 0
    night_mode = 100 if is_night_mode() else 0
    result = f"{cpu_temp};{gpu_temp};{night_mode};0;{cpu_load};{gpu_load};{ram_use};{gpu_memory_use};E"
    return result


class ArduinoStatsDisplay:
    RECONNECT_TIMEOUT = 5
    RECONNECT_ATTEMP = 3

    def __init__(self, dev_path, band_speed):
        self.dev_path = dev_path
        self.band_speed = band_speed
        self.serial = None
        self.connect_to_arduino()
        self.reconnect_attemps = self.RECONNECT_ATTEMP

    def connect_to_arduino(self):
        if self.serial is not None and self.serial.is_open:
            print("Already connected")
            return

        try:
            self.serial = serial.Serial(self.dev_path, self.band_speed)
            print("Successfully connected")
            self.reconnect_attemps = self.RECONNECT_ATTEMP
        except Exception as e:
            #print(f"Can't connect to Ardruino. Error: {e}. Retry after: {self.RECONNECT_TIMEOUT} seconds")
            sleep(self.RECONNECT_TIMEOUT)
            if (self.reconnect_attemps > 0):
              self.reconnect_attemps -= 1
              self.connect_to_arduino()
            else:
              sys.exit(1)

    def send_to_arduino(self, msg: bytes):
        try:
            self.serial.write(msg)
        except Exception as e:
            #print(f"Can't send msg to arduino: Error: {e}. Close connection and retry")
            self.close()
            self.connect_to_arduino()
            sleep(self.RECONNECT_TIMEOUT)
            self.send_to_arduino(msg)

    def close(self):
        if self.serial is not None:
            self.serial.close()
            self.serial = None


if __name__ == '__main__':
    arduino_display = ArduinoStatsDisplay(ARDUINO_DEV_PATH, ARDUINO_BAND_SPEED)
    while 1:
        send_data = form_send_string()
        arduino_display.send_to_arduino(send_data.encode("utf-8"))
        sleep(1)
