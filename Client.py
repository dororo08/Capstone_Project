from serial import Serial
import cv2
import socket
import struct
import pickle
import time
import os
import pygame
import pigpio
import RPi.GPIO as GPIO
from time import sleep

pygame.init()
pygame.mixer.init()

pi = pigpio.pi()

GPIO.setmode(GPIO.BCM)
pin = 18  # 서보 모터 핀 번호
led_pin = 2  # LED 핀 번호
green_pin = 3  # 초록색 LED 핀 번호
GPIO.setup(pin, GPIO.OUT)
servo_pwm = GPIO.PWM(pin, 50)
servo_pwm.ChangeDutyCycle(7.5)
servo_pwm.start(0)

def Servo_Angle(pin, angle):
    # 서보 모터 각도 설정 함수
    duty = 2 + (angle / 18)
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.1)

# Rest of the code remains the same

def control_led(pin, state):
    # LED 제어 함수
    GPIO.output(pin, state)

def control_green(pin1, state1):
    # 초록색 LED 제어 함수
    GPIO.output(pin1, state1)    

def turn_on_led():
    # LED 켜기 함수
    control_led(led_pin, GPIO.HIGH)

def turn_on_green():
    # 초록색 LED 켜기 함수
    GPIO.setup(green_pin, GPIO.OUT)
    control_green(green_pin, GPIO.HIGH)
   
# 주차 위반 감지 시 LED 끄기 함수
def turn_off_led():
    control_led(led_pin, GPIO.LOW)

def turn_off_green():
    control_green(green_pin, GPIO.LOW)

def speak(txt):  
    # 텍스트를 음성으로 출력하는 함수
    filename = txt + '.mp3'
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    time.sleep(8)

def getTFminiData(ser):
    # TFmini 거리 데이터 읽기 함수
    while True:
        count = ser.in_waiting
        if count > 8:
            recv = ser.read(9)
            ser.reset_input_buffer()
            if recv[0] == 0x59 and recv[1] == 0x59:
                distance = recv[2] + recv[3] * 256
                ser.reset_input_buffer()
                print(distance,"cm")
                return distance

def socketsend(client_socket): 
    # 이미지 데이터를 소켓을 통해 전송하는 함수
    camera = cv2.VideoCapture(0) 
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640) 
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

    ret, frame = camera.read()
    data = pickle.dumps(frame, 0) 
    size = len(data) 
    client_socket.sendall(struct.pack(">L", size) + data) 
    print('SEND COMPLETE')
    camera.release()

if __name__ == '__main__':
    ip = '172.20.10.2'  # 서버 IP 주소
    port = 3500  # 서버 포트 번호

    GPIO.setup(led_pin, GPIO.OUT)
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    client_socket.send('1/init'.encode())
    print('CONNECTION COMPLETE')
    ser = Serial("/dev/ttyS0", 115200)
    count = 0
    data = ''
    angle = [90, 120, 110, 100, 90, 60, 70, 80, 90]  # 서보 모터 각도 리스트
    if ser.is_open == False:
        print("serial not open")
        ser.open()
    i = 0
    while True:
        try:
            first_detect = getTFminiData(ser)
            if first_detect < 85:  # 주차 공간 감지
                if count == 0:  # 처음 감지되었을 때
                    client_socket.send('1/picture'.encode())  # 사진 요청 메시지 전송
                    socketsend(client_socket)  # 이미지 데이터 전송
                    data = client_socket.recv(1024).decode()  # 서버로부터 메시지 수신
                    #print(data)
                    if data != 'retransmit':  # 이미지 데이터 전송이 정상적으로 수신되었을 때
                        i = 0
                        if data == 'valid':  # 주차가 유효할 때
                            #print(412421312311123)
                            Servo_Angle(18, 90)  # 서보 모터 각도 조절
                            turn_on_green()  # 초록색 LED 켜기
                            time.sleep(10)
                            turn_off_green()  # 초록색 LED 끄기
                            count = 2  # 카운트 상태 변경
                        elif data == 'invalid' :
                            count = 1  # 주차가 유효하지 않을 때
                        else:  # 이미지 데이터 전송이 실패하였을 때
                            Servo_Angle(18, angle[i % len(angle)])  # 서보 모터 각도 변경
                            i += 1
                if data == 'invalid' and count == 1:  # 주차가 유효하지 않을 때
                    print(11111)
                    turn_on_led()  # LED 켜기
                    speak('INVALID')  # 음성 출력
                    time.sleep(8)
                    turn_off_led()  # LED 끄기
                    #print('5 MINUTE OVER')
                while True:
                        second_detect = getTFminiData(ser)
                        if second_detect < 85:  # 주차 공간 감지
                            client_socket.send('1/picture'.encode())  # 사진 요청 메시지 전송
                            socketsend(client_socket)  # 이미지 데이터 전송
                            data = client_socket.recv(1024).decode()  # 서버로부터 메시지 수신
                            if data == 'retransmit':  # 이미지 데이터 전송이 실패하였을 때
                                Servo_Angle(18, angle[i % len(angle)])  # 서보 모터 각도 변경
                                i += 1
                                continue
                            if data == 'invalid':  # 주차가 유효하지 않을 때
                                print(22222)
                                turn_on_led()  # LED 켜기
                                speak('INVALID2')  # 음성 출력
                                time.sleep(10)
                                turn_off_led()  # LED 끄기
                            else:  # 주차가 유효할 때
                                Servo_Angle(18, 90)  # 서보 모터 각도 조절
                                i = 0
                                count = 2  # 카운트 상태 변경
                                break
            elif count == 2 and first_detect > 85:  # 주차 공간 감지되지 않을 때
                Servo_Angle(18, 90)  # 서보 모터 각도 조절
                i = 0
                data = ''  # 데이터 초기화
                count = 0  # 카운트 상태 변경
        except KeyboardInterrupt:  # 프로그램 종료
            if ser != None:
                ser.close()
GPIO.cleanup()