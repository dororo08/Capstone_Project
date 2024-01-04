import socket
from typing import Deque
import cv2
import pickle
import struct 
import threading
import collections
import numpy as np
import pytesseract
import time
from twilio.rest import Client
import pymysql
import pyodbc 

pytesseract.pytesseract.tesseract_cmd = "C:\\Users\\alswo\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Python 3.10\\tesseract.exe"

#자동차 번호판에 사용되는 한글
symbol=[
    '가', '나', '다', '라', '마','거', '너',
    '더', '러', '머', '버', '서', '어', '저',
    '고', '노', '도', '로', '모', '보', '소', '오', '조',
    '구', '누', '두', '루', '무', '부', '수', '우', '주',
    '아', '바', '사', '자', '배', '하', '허', '호', '국', '합', '육', '해', '공']


def convert(img, pos):  
  
    pts1 = np.float32(pos)

    # 변환 후 영상에 사용할 서류의 폭과 높이 계산 ---③ 
    w1 = abs(pos[1][0] - pos[0][0])    # 상단 좌표간의 거리
    w2 = abs(pos[2][0] - pos[3][0])         # 하단 좌표간의 거리
    h1 = abs(pos[1][1] - pos[2][1])      # 우측 좌표간의 거리
    h2 = abs(pos[0][1] - pos[3][1])        # 좌측 좌표간의 거리
   
    width = max([w1, w2])                  
    height = max([h1, h2])
    
    pts2 = np.float32([[0,0], [width-1,0], [width-1,height-1], [0,height-1]])

    mtrx = cv2.getPerspectiveTransform(pts1, pts2)
   
    result = cv2.warpPerspective(img, mtrx, (width, height))

    return result

def extractLicensePlate(img): #번호판 영역 추출
   
    net = cv2.dnn.readNet("./yolov3_last2.weights", "yolov3.cfg")
    
    classes = []
    with open("obj.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i-1] for i in net.getUnconnectedOutLayers()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))
    
    img = cv2.resize(img, None, fx=0.4, fy=0.4)

    height, width, channels = img.shape

    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)  

    temp_ext_img = img
    net.setInput(blob)
    outs = net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores) 
            confidence = scores[class_id]
            if confidence > 0.5:
               
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
               
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    font = cv2.FONT_HERSHEY_PLAIN
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            color=(0,0,255)
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
           
    try:
        #번호판을 정확히 잡아온 경우
        #만약 좌표가 음수인 경우 양수로 변환
        x, y, w, h=abs(x),abs(y),abs(w),abs(h)
    except UnboundLocalError:
        #번호판을 추출 실패시 원본 사이즈로 설정
        
        x,y,w,h=0,0,416,416
    pos1 = [x, y]
    pos2 = [x+w, y] 
    pos3 = [x+w, y+h] 
    pos4 = [x, y+h]
    src=np.array([pos1, pos2, pos3, pos4])
    img=convert(temp_ext_img, src) 

    return img

def ApplyGaussianBlur(img): 
   
    height, width, channel = img.shape 

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #흑백 이미지로 변환

    structuringElement = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
  
    imgTopHat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, structuringElement) 
    imgBlackHat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, structuringElement)

    imgGrayscalePlusTopHat = cv2.add(gray, imgTopHat)
    gray = cv2.subtract(imgGrayscalePlusTopHat, imgBlackHat)
    img_blurred = cv2.GaussianBlur(gray, ksize=(5, 5), sigmaX=0) # 가우시안 블러 적용

    img_thresh = cv2.adaptiveThreshold(
       img_blurred, 
       maxValue=255.0, 
       adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
       thresholdType=cv2.THRESH_BINARY_INV, 
       blockSize=19, 
       C=9 
    )# Adaptive Threshold를 적용하여 엣지 추출

    return img_thresh 

def is_validChar(chars, result):
    global symbol
    index=0
    back=0
    back_count=0
    result_chars=[]
    chars.strip()
    #print(chars)
    for c in chars:
            if (c in symbol) or c.isdigit(): # 번호판의 숫자나 문자면 저장
                if back_count==4: 
                    break
                result_chars.append(c)
                if back==1:
                    back_count+=1
                if not c.isdigit(): 
                    index=result_chars.index(c)
                    back=1 
    front_part=result_chars[0:index] #한글 앞부분
    back_part=result_chars[index+1:len(result_chars)] #한글 뒷부분

    if len(front_part)==3: 
        index-=1
        front_part=result_chars[1:index+1] 
        result_chars=result_chars[1:]
    #print(result_chars)
    #print()
    if len(front_part)==2 and len(back_part)==4:
       
        s=''.join(result_chars)
        
        if s in result: #대상 번호가 감지된 횟수 탐색
            result[s]+=1
        else:
            result[s]=0
    #print("Detect Number = ", result)
    return result

def is_validNum(img):
    count = 10  # 원본 이미지와 GaussianBlur 처리된 이미지 각각에 대해 반복할 횟수
    
    L = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]  

    result = {}  
    original_img = extractLicensePlate(img) 
    gaussian_img = ApplyGaussianBlur(original_img) 

    for i in range(count+1):
        img_thresh = original_img

        height, width, channel = img_thresh.shape
        matrix = cv2.getRotationMatrix2D((width/2, height/2), L[i], 1) 
        dst = cv2.warpAffine(img_thresh, matrix, (width, height))  
        chars = pytesseract.image_to_string(dst, lang='kor', config='--psm 7 --oem 3')  # 이미지에서 문자 추출
        result = is_validChar(chars, result)  # 문자열이 유효한 차량 번호인지 확인

    for i in range(count+1):
        img_thresh = gaussian_img

        height, width = img_thresh.shape
        matrix = cv2.getRotationMatrix2D((width/2, height/2), L[i], 1) 
        dst = cv2.warpAffine(img_thresh, matrix, (width, height)) 
        chars = pytesseract.image_to_string(dst, lang='kor', config='--psm 7 --oem 3')  # 이미지에서 문자 추출
        result = is_validChar(chars, result)  # 문자열이 유효한 차량 번호인지 확인

    print("result =", result)

    if len(result) != 0:
        return max(result, key=result.get)  # 가장 많이 검출된 차량 번호 반환
    else:
        return False 

    
def sendText(txt, Phone):
    account_sid = 'AC5d19786de5bd022ce43d7e8fa624e424'
    auth_token = '0492806b4d6bccdf88ae64f78d15ab7e'
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        to="+82" + Phone,  
        from_="+12708132673",
        body=txt
    )
    print("사용자에게 문자메시지 전송 완료.")


def get_picture(conn):
    data = b"" 
    payload_size = struct.calcsize(">L") 

    while len(data) < payload_size:
        data += conn.recv(4096) 
    packed_msg_size = data[:payload_size] 
    data = data[payload_size:]
    msg_size = struct.unpack(">L", packed_msg_size)[0]

    while len(data) < msg_size:
        data += conn.recv(4096) 
    frame_data = data[:msg_size]
    data = data[msg_size:]

    frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes") #직렬화된 파일이나 바이트를 원래의 객체로 복원

    #cv2.imshow("input picture", frame)
    #cv2.waitKey()
    #cv2.destroyAllWindows()
    
    return frame


def SEND(lock):
    global addr_table, sendQue

    while True:
        try:
            # 전송할 데이터가 대기열에 있는 경우
            if len(sendQue) != 0:
                print(sendQue)
                data = sendQue.pop()  # 대기열에서 첫 번째 데이터를 추출
                addr, msg = data[0], data[1]  # 추출한 데이터에서 클라이언트 소켓과 메시지를 추출
                addr_table[addr].send(msg.encode())  # 메시지를 클라이언트에게 전송
            time.sleep(0.01)
        except socket.timeout:
            print("시간 초과")
        except socket.error:
            print("소켓 오류")


            
def RECV(conn, lock):
    """
    RECV Thread
    주어진 조건에 따라 Send Queue에 msg를 담아줌
    """
    global addr_table, sendQue, carName, count

    while True:
        try:
            print("수신 시작")
            data = conn.recv(1024).decode()  # 데이터 수신
            print(data)
            if data == '':
                count += 100
                if count >= 100:
                    break
                pass
            else:
                count = 0
                print(data)
            machin, option = data.split('/')  # 클라이언트로부터 받은 메시지를 기기 번호와 옵션으로 분리
            if option == 'init':  # 기기가 처음 연결된 경우
                addr_table[machin] = conn  # 해당 기기의 소켓 주소 저장
            elif option == 'picture':  # 사진 전송 요청이 온 경우
                print("기기로부터 사진 전송 중")
                img = get_picture(conn)  # 사진을 받아옴
                carNumber = is_validNum(img)  # 차량 번호 인식
                print(carNumber)
                if carNumber == False:  # 차량 번호 인식 실패, 재전송 요청
                    print("번호 인식 실패! 재전송 요청")
                    sendQue.append([machin, 'retransmit'])
                else:
                    # 번호 인식이 성공한 경우 데이터베이스 조회
                    print("번호 인식 성공!")
                    flag = sqldb('valid', carNumber)  # 데이터베이스 조회
                    if flag == -1:
                        print("존재하지 않는 차량입니다. 재전송 요청")
                        sendQue.append([machin, 'retransmit'])
                    else:
                        print("데이터베이스 조회 성공")
                        if carName == '' or carName != carNumber:
                            print("처음 주차된 차량입니다.")
                            carName = carNumber
                            if flag == 1:
                                print("차량번호 {} 장애인 차량입니다. 주차 완료.".format(carNumber))
                                sendQue.append([machin, 'valid'])
                            elif flag == 0:
                                print("차량번호 {} 장애인 주차구역 위반 차량입니다.".format(carNumber))
                                phoneNum = sqldb('phone', carNumber)
                                print("phoneNum = ", phoneNum)
                                text = "[Web발신] 해당 주차 구역은 장애인 전용 주차 구역입니다. 다른 곳으로 이동 주차 바랍니다. 5분 이내로 이동 주차하지 않으면 과태료가 부과됩니다."
                                print("첫번째 문자 내용 = ", text)
                                sendText(text, phoneNum)
                                print("첫번째 문자 메시지 전송 성공.")
                                sendQue.append([machin, 'invalid'])

                        elif carName == carNumber:
                            print("차량번호 {} 장애인 주차구역 위반 차량. 경고 메시지에 불응.".format(carNumber))
                            sendQue.append([machin, 'invalid'])
                            text = "[Web발신] 주차위반 후 5분이 경과하였습니다. 과태료가 부과됩니다."
                            print("두번째 문자 내용 = ", text)
                            phoneNum = sqldb('phone', carNumber)
                            print("phoneNum = ", phoneNum)
                            sendText(text, phoneNum)
                            print("두번째 문자 메시지 전송 성공.")
                            sqldb('violate', carNumber)
                            print("차량번호 {}, 과태료가 부과되었습니다.".format(carNumber))
                            carName = ''
        except TypeError:
            pass
        except ValueError:
            pass
        except socket.error:
            break
        time.sleep(0.001)


def sqldb(type, car):
    global cursor, cardb
    if type=='phone': #해당 차주의 휴대폰 번호 조회
        query="SELECT phoneNum FROM information WHERE carNumber=%s"
        cursor.execute(query, (car))
    if type=='valid': #해당 차량이 장애인 차량인지 판단
        query="SELECT prove FROM information WHERE carNumber=%s"
        cursor.execute(query, (car))
    elif  type=='violate':#주차구역을 위반한 경우 database에 위반 표시 및 벌금 부과
        #print ("wewqe12") 
        query="UPDATE information SET violate = violate + %s WHERE carNumber = %s"
        cursor.execute(query, (1,car))
        query="UPDATE information SET fee = fee + %s WHERE carNumber = %s"
        cursor.execute(query, (50000,car))
        cardb.commit()
        return
    
    rows = cursor.fetchall() #쿼리한 결과를 읽어옴
    if len(rows)==0:
        return -1
    return rows[0][0]

ip = '172.20.10.2' # ip 주소
port = 3500 # port 번호
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # 소켓 객체를 생성
addr_table={}
carName=''
#ACK=[0,0]
sendQue=collections.deque()
LOCK=threading.Lock()

send_trd=threading.Thread(target=SEND, args=(LOCK,)).start()
cardb = pymysql.connect(
    user="root", 
    passwd="1234", 
    host="127.0.0.1", 
    db="cardb", 
    charset="utf8"
)
cursor = cardb.cursor()
sql = "Select * from car where carnumber=%s"
count=0


s.bind((ip, port)) # 바인드(bind) : 소켓에 주소, 프로토콜, 포트를 할당
s.listen(10) # 연결 수신 대기 상태(리스닝 수(동시 접속) 설정)
while True:
    print('기기 연결 대기')
    # 연결 수락(클라이언트 소켓 주소를 반환)
    conn, addr = s.accept()
    print("기기", addr, " 연결") # 클라이언트 주소 출력
    recv_trd=threading.Thread(target=RECV, args=(conn, LOCK)).start()