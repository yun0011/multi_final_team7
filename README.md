# multi_final_team7
멀티캠퍼스 융합프로젝트_익수예방CCTV

## 프로젝트 목적
- CCTV + AI --> 안전사고 예방
- 이미 많이 진행되고 있는 분야지만 익수에 관한 CCTV는 부족한 상황

<br/><br/>

## 서비스구상

- 익수자(행동패턴) --> CCTV식별(AI) --> 자동 신고 --> 구조대에서 상황판단
- 강우(실시간 유속, 수심측정)측정 --> 강우발생 --> 예측모델분석 --> 경고 및 알림
- ### react 화면

  ![image](https://github.com/user-attachments/assets/a70a589e-4778-4b26-8f4d-6b9e4018a4fc)
  - 왼쪽 위 : 실시간 전송화면
  - 오른쪽 위 : CCTV에 모델을 적용하여 익수자를 판별하는 화면
  - 왼쪽 아래 : 화면에 잡히고 있는 사람 수
  - 오른쪽 아래 : 실시간 유속 그래프

 <br/><br/> 

 ## 프로젝트 구상도
 ![image](https://github.com/user-attachments/assets/1aa0f65f-a737-4b93-9903-b2e264f75427)

 - 라즈베리 파이(iot)
     - 외부에서 학습한 익수자 감지 모델
     - 유량 예측모델

 - cloud(AWS)
     - S3버켓
     - cctv 감지 이미지
     - 익수자 감지시 이미지 따로 캡쳐
     - text는 모델이 감지하고 있는 box(사람 수), 익수 예측(%), 유량, 유속 측정값을 저장

 - cloud(Lambda)
     - severless로 진행
     - S3에 있는 내용을 정제하여 DB에 넣는 내용의 함수
         -  DB : 1개, table : 2개
         -  table1(date, x, y, 정확도, 익사여부), table2(time, 유량, 유속)
 - REACT
     - cloud API를 받아 DB에 접속, S3의 이미지 받아옴
     - table에서 필요한 자료 추출 후 시각화 서비스
  
<br/><br/> 

 ## 상세기능1(익사예방 모델)
 ### AI모델 준비
  - yolov5 사용
      - 탐지 네트워크 모델의 가중치 파일크기가 작음
      - 실시간 탐지를 구현하기 위해 디바이스에 배포하기 적합하다고 판단
      - 라즈베리 파이에 모델을 심을 예정이었기 때문에 선택
  - 4개의 lable(사고자, 수영, 튜브, 사람)으로 나누어 데이터를 수집함
      - 계곡에 있는 사람은 크게 4가지 유형으로 분류될 수 있다고 판단함
  - 약 2000장의 Data를 수집(유튜브, 구글링 등)(익수자 600장, 수영 1000장, 튜브 200장, 사람 200장)
![image](https://github.com/user-attachments/assets/0e03b219-2673-4b26-926d-6de0839cfdad)
  - testdata로 테스트했을대 약 0.71정도의 정확도가 나옴을 파악


<br/><br/> 

 ## 상세기능2(유량예측모델)

 - ![image](https://github.com/user-attachments/assets/3efe6269-2c9d-4879-af5e-0e14bc29e3c6)
    - 용추계곡 중심으로 진행(사고다발지역)
    - 환경부 한강홍수통제소 - 수위자료(크롤링)
    - 가평교 기준 2017-2022자료 수집 --> 용추계곡에서 가장 가까운 수위 측정 위
    - 자료 전처리



 
       

 
