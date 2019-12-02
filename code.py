import time
import math

import board
import displayio
import terminalio
import adafruit_displayio_ssd1306
import label
from adafruit_onewire.bus import OneWireBus
import adafruit_ds18x20
from digitalio import DigitalInOut, Direction, Pull

target_temp=72
compressor_status = False
#set the initial state of this so it doesn't get mad :D
compressor_start_ticks = time.time()

compressor = DigitalInOut(board.D6)
compressor.direction = Direction.OUTPUT

ow_bus = OneWireBus(board.D5)
devices = ow_bus.scan()
ds18b20 = adafruit_ds18x20.DS18X20(ow_bus, devices[0])


displayio.release_displays()
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)
 
# Make the display context
splash = displayio.Group(max_size=10)
display.show(splash)
line1 = "This is a kegerator..."
line2 = "...only a test"
text_area1 = label.Label(terminalio.FONT, text=line1, color=0xFFFFFF, x=10, y=10)
text_area2 = label.Label(terminalio.FONT, text=line2, color=0xFFFFFF, x=10, y=27)
splash.append(text_area1)
splash.append(text_area2)

while True:
    temp_c = ds18b20.temperature
    current_temp = math.floor((temp_c * 9/5) + 32)
    temperature_display_string = 'Temp:{current_temp}F Targt:{target_temp}F'.format(current_temp=current_temp, target_temp=target_temp)
    temp_text_area = label.Label(terminalio.FONT, text=temperature_display_string, color=0xFFFFFF, x=10, y=10)
    new_compressor_status = current_temp > target_temp
    if (new_compressor_status != compressor_status):
        compressor_status = new_compressor_status
        if new_compressor_status:
            compressor_start_ticks = time.time()

    compressor_status_string = 'ON' if compressor_status else 'OFF';
    current_ticks = time.time()
    compressor_time_elapsed = current_ticks - compressor_start_ticks
    compressor_sec_elapsed = math.floor(compressor_time_elapsed % 60)
    compressor_min_elapsed = math.floor(compressor_time_elapsed / 60)
    compressor_hr_elapsed = math.floor(compressor_min_elapsed / 60)
    compressor_sec_elapsed_string = '0{compressor_sec_elapsed}'.format(
        compressor_sec_elapsed=compressor_sec_elapsed) if compressor_sec_elapsed < 10 else compressor_sec_elapsed
    compressor_min_elapsed_string = '0{compressor_min_elapsed}'.format(
        compressor_min_elapsed=compressor_min_elapsed) if compressor_min_elapsed < 10 else compressor_min_elapsed
    compressor_hr_elapsed_string = '0{compressor_hr_elapsed}'.format(
        compressor_hr_elapsed=compressor_hr_elapsed) if compressor_hr_elapsed < 10 else compressor_hr_elapsed
    compressor_time_elapsed_string = '{compressor_hr_elapsed_string}:{compressor_min_elapsed_string}:{compressor_sec_elapsed_string}'.format(
        compressor_hr_elapsed_string = compressor_hr_elapsed_string,
        compressor_min_elapsed_string = compressor_min_elapsed_string,
        compressor_sec_elapsed_string = compressor_sec_elapsed_string) if compressor_status else '--:--:--'
    compressor_status_display_string='Cool:{compressor_status_string}   {compressor_time_elapsed_string}'.format(
        compressor_status_string=compressor_status_string,
        compressor_time_elapsed_string = compressor_time_elapsed_string)
    compressor_text_area = label.Label(terminalio.FONT, text=compressor_status_display_string, color=0xFFFFFF, x=10, y=27)
    splash.pop()
    splash.pop()
    splash.append(temp_text_area)
    splash.append(compressor_text_area)
    compressor.value = compressor_status
    time.sleep(5) 
