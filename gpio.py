# coding=utf-8

import RPi.GPIO as GPIO
import time

GPIO_PIN = 24

GPIO.setmode(GPIO.BOARD)#物理引脚编号
GPIO.setup(GPIO_PIN, GPIO.OUT)#输出

GPIO.output(GPIO_PIN,GPIO.HIGH)#高电平
time.sleep(1)
GPIO.output(GPIO_PIN,GPIO.LOW)#低电平

GPIO.setup(GPIO_PIN, GPIO.IN)#输入
print GPIO.input(GPIO_PIN)#读取状态

GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)#输入，启用下拉电阻
GPIO.wait_for_edge(GPIO_PIN, GPIO.RISING)#阻塞等待上升沿中断