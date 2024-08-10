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
 - ![image](https://github.com/user-attachments/assets/c5224cf4-7bad-465f-9425-5e83e537a7eb)
   - "수난구조 현장활동 지침"에 의하면 일반 잠수가 가능한 유속은 0.51m/s이하이고 0.77m/s 초과 유속은 모든 잠수 금지를 적시함을 근거로 삼는다

 - ![image](https://github.com/user-attachments/assets/3efe6269-2c9d-4879-af5e-0e14bc29e3c6)
    - 용추계곡 중심으로 진행(사고다발지역)
    - 환경부 한강홍수통제소 - 수위자료(크롤링)
    - 가평교 기준 2017-2022자료 수집 --> 용추계곡에서 가장 가까운 수위 측정 위
    - 자료 전처리

- ![image](https://github.com/user-attachments/assets/300d42b6-62a7-45e4-91fd-52497da03119)
    - 기상청 API허브 강수량 자료 이용 --> 관련정보만 전처리
    - 가평교 수위, 유량자료와 기상청의 해당구역 강수량 자료 통합 및 전처리

 - ![image](https://github.com/user-attachments/assets/f3049c46-0072-4bf2-9905-d043898324f6)
    - 수위, 유량, 강수량은 유사하게 변화함을 알 수 있음
    - 6-9월의 변화가 뚜렷한 것으로 확

  - ![image](https://github.com/user-attachments/assets/4ff3ff8c-54e4-4032-9092-14374240f2c1)
    - 강수량이 많을 수록 수위가 올라가는 선형적인 구조를 이용하여 강수량이 상승했을때, 유속측정기를 활용하여 유속이 증가했을때 종합하여 위험도 표시
 
<br/><br/> 

  ## 상세기능3(iot)
  ### 라즈베리파이 카메라
  > 모델 2가지를 만들었으니 라즈베리 파이에 넣고 출력물이 클라우드로 이동하는 과정이 필요하다

 ![image](https://github.com/user-attachments/assets/6439a5dd-73c9-41e0-88d6-89fd9db2c06c)

 - 2초간격으로 CCTV 화면저장 --> "live_img"파일로 이동
 - 익사 위험을 의미하는 cls0(익수인식 box) 인식시 저장 --> "detect_img"로 이동
 - 4개의 라벨중 하나라도 인식시 데이터 저장 --> "detect_json"(라벨이 인식하는 수가 사람수기 때문에 사람수를 그래프로 나타내는 서비스를 하기위해선 json형태의 파일이 필요하다)
 - 1분간격으로 수심, 유속 측정 및 강수량 값 저장 --> "waterflow_json"로 이동
    - 유속센서에서 받는 값들(1초마다 한번씩 값이 들어오고 60개를 평균내서 json으로 묶는다)
    - 실기간 강수량은 기상청 API에서 받아오는걸로 한다
    - 둘의 값을 json으로 묶어서 1분간격으로 cloud로 보낸다

   <br/><br/> 
  ## CLOUD
  ### 버켓에 라즈베리파이에서 받은 파일들 적재
  - observer가 폴더내의 파일생성 이벤트를 감시한다
  - 파일 생성 이벤트 발견시 파일명 끝자리(_l.img,_0.img,_d.json,_s.json) 로 업로드할 버켓 이름을 결정한다. 
 - ![image](https://github.com/user-attachments/assets/cac9125c-ff9a-4a11-a0bf-8f61e349b967)

  ### lambda함수를 사용하여 버켓에 있는 내용을 DB에 적재한다. 
      - swim table : detect_json파일(사람수 인식하기 위함, 익수자 파악하기 위함)
      - date, detecting, accuracy

''' 
      const AWS = require('aws-sdk');
const mysql = require('mysql2/promise');

exports.handler = async (event, context) => {
  const bucketName = 'team7-data';

  const dbHost = 'database-1.clhnj2zwdisk.eu-west-2.rds.amazonaws.com'; //프라이빗 ip 172.31.0.0
  const dbUser = 'admin';
  const dbPassword = '12345678';
  const dbName = 'team7_database';

  const s3 = new AWS.S3();

  const dbConfig = {
    host: dbHost,
    user: dbUser,
    password: dbPassword,
    database: dbName
  };

  try {
    const dbConn = await mysql.createConnection(dbConfig);

    for (const record of event.Records) {
      if (record.eventName === 'ObjectCreated:Put') {
        try {
          const imageKey = record.s3.object.key;

          const objectParams = { Bucket: bucketName, Key: imageKey };
          const objectData = await s3.getObject(objectParams).promise();

          const objectContent = objectData.Body.toString('utf-8');
          const jsonArray = JSON.parse(objectContent);

          for (const json of jsonArray) {
            const insertQuery = `INSERT INTO swim (date, detecting, accuracy) VALUES (?, ?, ?)`;
            const values = [json.date, json.detecting, json.accuracy];

            await dbConn.execute(insertQuery, values);
          }

          console.log('Object data has been inserted into MariaDB.');
        } catch (error) {
          console.error('Failed to process S3 object:', error);
        }
      }
    }

    await dbConn.end();
  } catch (error) {
    console.error('Failed to connect to RDS(MariaDB):', error);
  }
};
'''
  

 
