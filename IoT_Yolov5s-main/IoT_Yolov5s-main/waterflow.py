import time
import RPi.GPIO as GPIO
import math
import requests
import xml.etree.ElementTree as ET
import json
import torch
import numpy as np
import os
import boto3
import pickle
import joblib
import warnings
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from gpiozero import LED
from datetime import datetime, timedelta

FLOW_SENSOR_PIN = 17 
TRIGGER_PIN = 20  # 초음파 센서 Trigger핀 추가
ECHO_PIN = 21     # 초음파 센서 Echo핀 추가

GPIO.setmode(GPIO.BCM)
GPIO.setup(FLOW_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(TRIGGER_PIN, GPIO.OUT)  # Trigger 핀 출력 모드 설정
GPIO.setup(ECHO_PIN, GPIO.IN)      # Echo 핀 입력 모드 설정

led1 = LED(23)  # GPIO 핀 번호 23을 사용하는 LED 객체 생성
led2 = LED(24)  # GPIO 핀 번호 24을 사용하는 LED 객체 생성
led3 = LED(13)  # GPIO 핀 번호 13을 사용하는 LED 객체 생성
led4 = LED(19)  # GPIO 핀 번호 19을 사용하는 LED 객체 생성

warnings.filterwarnings("ignore")

global count
count = 0

global ledcount
ledcount=0
leds = [led1, led2, led3, led4]  # LED 객체들을 리스트에 저장


def load_model(filepath):
    with open(filepath, 'rb') as f:
        model = pickle.load(f)
    return model


def predict_flow(rainfall, water_level, velocity):
    # 입력 데이터를 특징 벡터로 변환
    features = np.array([[rainfall, water_level, velocity]])

    # 모델 로드
    model = load_model('/home/seok/yolov5/weights/gradient_boosting_model.pkl')

    # 유량 예측
    flow = model.predict(features)

    return flow


def check_risk_level(rainfall, water_level, velocity):
    # 기준 수위
    threshold_level = 0

    # 유량 예측
    flow = predict_flow(rainfall, water_level, velocity)

    # 강수량에 따른 위험도 계산
    if rainfall >= 10:
        rainfall_risk = 5
    else:
        rainfall_risk = 1

    # 수위에 따른 위험도 계산
    if threshold_level + water_level >= 1.3:
        water_level_risk = 5
    else:
        water_level_risk = 1

    # 유속에 따른 위험도 계산
    if velocity <= 0.1:
        velocity_risk = 1
    elif velocity <= 0.3:
        velocity_risk = 2
    elif velocity <= 0.5:
        velocity_risk = 3
    elif velocity <= 0.7:
        velocity_risk = 4
    else:
        velocity_risk = 5

    # 종합 위험도 계산
    total_risk = 0

    if rainfall_risk >= 4 or water_level_risk >= 4 or velocity_risk >= 4:
        total_risk = 5
    elif rainfall_risk >= 3 or water_level_risk >= 3 or velocity_risk >= 3:
        total_risk = 4
    elif rainfall_risk >= 2 or water_level_risk >= 2 or velocity_risk >= 2:
        total_risk = 3
    elif rainfall_risk >= 1 or water_level_risk >= 1 or velocity_risk >= 1:
        total_risk = 2
    else:
        total_risk = 1

    # 위험도를 텍스트로 표시
    if total_risk == 1:
        risk_level = '0'
    elif total_risk == 2:
        risk_level = '1'
    elif total_risk == 3:
        risk_level = '2'
    elif total_risk == 4:
        risk_level = '3'
    else:
        risk_level = '4'

    return flow, risk_level

# warn 수치에 따른 led 개수 조절
def led_on(warn):
    for i in range(int(warn)):
        leds[i].on()


# 모든 led off
def led_off():
    for led in leds:
        led.off()

def led_as_risk(warn):
    if int(warn) == 0:
        led.off()
    else:
        led_off()
        led_on(warn)



def count_pulse(channel):
    global count
    count += 1

GPIO.add_event_detect(FLOW_SENSOR_PIN, GPIO.FALLING, callback=count_pulse)

pipe_diameter = 18  # 관의 직경=1.7(mm)
pipe_area = math.pi * ((pipe_diameter / 2) / 1000)**2  # 직경을 미터로 변환 후 면적 계산

def get_fw():
    # 현재 시간 가져오기
    current_time = datetime.now()
    # 현재 시간에서 10분전 시간 가져오기
    current_time = current_time - timedelta(minutes=10)


    adjusted_minutes = current_time.minute - (current_time.minute % 10) 
    current_time = current_time.replace(minute=adjusted_minutes).strftime("%Y%m%d%H%M")  # 예: "202306261630"


    api_key ="1C95FEA2-529E-489B-9104-9823A2462274"
    waterlevel_url = f"https://api.hrfco.go.kr/{api_key}/rainfall/list/10M/10134020/{current_time}/{current_time}.xml"

    # print(waterlevel_url)
    response = requests.get(waterlevel_url)
    xml_data = response.content

    # XML 파싱
    root = ET.fromstring(xml_data)
    waterlevel_element = root.find(".//Rainfall")

    fw_value = waterlevel_element.find("rf").text

    return fw_value


def get_distance():
    GPIO.output(TRIGGER_PIN, False)
    time.sleep(0.0002)

    GPIO.output(TRIGGER_PIN, True)
    time.sleep(0.00001)  # 10마이크로초의 신호 발생
    GPIO.output(TRIGGER_PIN, False)

    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    # 공기중 초음파 속도=약 453 m/s, 수중 약 1500 m/s
    # distance = pulse_duration * 750 # 수중
    distance = pulse_duration * 171 # 공기
    distance = round(distance, 2)

    return distance




try:
    while True:
        count = 0
        time.sleep(1)
        flow_rate = count / 7.5 # 1L당 펄스 수(7.5 펄스/L)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        flow_rate_m3s = flow_rate / 1000 / 60 # L/min에서 m^3/s 단위로 변환
        velocity = flow_rate_m3s / pipe_area  # 유속 계산(V = Q / A)

        distance = get_distance()  # 초음파 센서 거리 측정
        fw_value = get_fw()

        predicted_flow, risk_level = check_risk_level(float(fw_value), distance, velocity)

        #print(f"{timestamp}]", "유속: {:.2f} m/s".format(flow_rate), "수심: {:.2f} m".format(distance), "실시간 강수량:", fw_value)

        bigdata = {"date":timestamp, "rain":float(fw_value), "deep":distance, "ws":velocity, "wf":int(predicted_flow), "warn":risk_level}
        print(bigdata)

        with open(f"/home/seok/yolov5/runs/waterflow_json/{timestamp}_s.json", "w") as json_file:
            json.dump(bigdata, json_file)

        led_as_risk(risk_level)





except KeyboardInterrupt:
    print("\n프로그램 종료")
    GPIO.cleanup()