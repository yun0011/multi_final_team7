# multi_final_team7
멀티캠퍼스 융합프로젝트_익수예방CCTV

# #AWS lambda, AWS S3, maria DB, react, yolov5, QGIS

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
    - 수위(가평교 수위 데이터), 강수량(가평교 주변 기상청) 학습데이터
    - 유량(가평교 유량 데이터) 결과값으로 모델 생성

<br/>

```
def load_model(filepath):
    with open(filepath, 'rb') as f:
        model = pickle.load(f)
    return model

def predict_flow(rainfall, water_level, velocity):
    # 입력 데이터를 특징 벡터로 변환
    features = np.array([[rainfall, water_level, velocity]])

    # 모델 로드
    model = load_model('gradient_boosting_model.pkl')

    # 유량 예측
    flow = model.predict(features)

    return flow

def check_risk_level(rainfall, water_level, velocity):
    # 기준 수위
    threshold_level = 1.1

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

# 강수량, 수위, 유속 입력 받기
rainfall = float(input("강수량을 입력하세요: "))
water_level = float(input("수위를 입력하세요: "))
velocity = float(input("유속을 입력하세요: "))

# 유량 예측 및 위험단계 확인
predicted_flow, risk_level = check_risk_level(rainfall, water_level, velocity)

print("Predicted Flow:", predicted_flow)
print("Risk Level:", risk_level)
```

- 강수량, 수위, 유속을 입력받아 유량을 예측하고, 그에 따른 위험도를 평가하는 프로그램
- 수위와 유속은 라즈베리파이에서 가져오는 데이터를 이용한다.
    
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

```
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
```
  
   - water_flow table : 유속, 유량, 강수량 데이터, 이를 바탕으로 한 경고 json 파일
   - (date, rain, deep, ws, wf, warn)
   - rain : 강수량, deep : 수심, ws : 유속, wf : 유량, warn : 경고고


 ```
const AWS = require('aws-sdk');
const mysql = require('mysql2/promise'); // mysql2/promise 모듈을 사용하여 비동기적으로 연결

exports.handler = async (event, context) => {
  // AWS S3 및 RDS(MariaDB) 설정
  const bucketName = 'team7-water';

  const dbHost = 'database-1.clhnj2zwdisk.eu-west-2.rds.amazonaws.com';
  const dbUser = 'admin';
  const dbPassword = '12345678';
  const dbName = 'team7_database';

  // AWS S3 및 RDS(MariaDB) 클라이언트 생성
  const s3 = new AWS.S3();

  // RDS(MariaDB) 연결 설정
  const dbConfig = {
    host: dbHost,
    user: dbUser,
    password: dbPassword,
    database: dbName
  };

  try {
    // RDS(MariaDB) 연결 생성
    const dbConn = await mysql.createConnection(dbConfig);

    // S3 이벤트 레코드를 반복하여 처리
    for (const record of event.Records) {
      // 이벤트 유형 확인 (ObjectCreated)
      if (record.eventName === 'ObjectCreated:Put') {
        try {
          // 업로드된 객체의 키 가져오기
          const imageKey = record.s3.object.key;

          // S3에서 객체 가져오기
          const objectParams = { Bucket: bucketName, Key: imageKey };
          const objectData = await s3.getObject(objectParams).promise();

          // 객체 데이터 처리 로직 추가
          // 예: MariaDB에 데이터 저장
          const objectContent = objectData.Body.toString('utf-8');
          const insertQuery = INSERT INTO water_flow (date, rain, deep, ws, wf, warn) VALUES (?, ?, ?, ?, ?, ?);
          const parsedData = JSON.parse(objectContent);
          const values = [parsedData.date, parsedData.rain, parsedData.deep, parsedData.ws, parsedData.wf, parsedData.warn];

          // 데이터 삽입을 위해 RDS(MariaDB) 연결 사용
          await dbConn.execute(insertQuery, values);

          console.log('Object data has been inserted into MariaDB.'); // 로그 추가
        } catch (error) {
          console.error('Failed to process S3 object:', error);
        }
      }
    }

    await dbConn.end(); // 연결 종료
  } catch (error) {
    console.error('Failed to connect to RDS(MariaDB):', error);
  }
};

```
 <br/><br/>

  ## 설치지역 타당성(GIS 지형분석)
- CCTV설치의 타당성을 높이기 위함
- 지리정보가 포함된 데이터와, 정확한 구역별 경계를 나타내는 데이터를 가지고
- 지형적인 요인을 분석
- 가평 용추계곡을 예시로 진행

  <br/>
  
>  범위를 지정해주기 위해, 용추계곡이 있는 승안리를 선택, 하천의 실제 폭을 덧씌움

   ![image](https://github.com/user-attachments/assets/096e1aed-6b64-43ca-ac87-f7ecf0a51fd4)

  <br/>

  > QGIS의 Profile Tool을 사용, 물놀이 구간의 상류부터 하류까지 고도변화를 분석
  > 구글어스의 고도수치와 비교하며 정확한 값을 얻음
  > 추가적으로 경사도와 깊이 분석 진행

  ![image](https://github.com/user-attachments/assets/3d0af1bd-1892-40d1-921a-d144c499fb30)

  > 같은 방식으로 물놀이 사고 발생률이 높은 10개의 계곡과 낮은 10개의 계곡을 지정해 고도, 깊이, 경사도 변화를 구역별 수치값으로 추출하여 분석을 진행

<br/> <br/>

### 분석 결과

>  사고 다발지역
     
  ![image](https://github.com/user-attachments/assets/4e67f80f-5846-495a-9d2f-ec4623f251b1)

- 물놀이 구간 시작과 끝 고도차이가 30-50정도로 난다
- 고도차이가 난다면 강우발생시 유속이 빨라질 위험 + 유량이 급격히 늘어날 가능성 있음

  ![image](https://github.com/user-attachments/assets/db81fa22-07a5-457c-b11c-1aae2afbbe3e)

 - 초록 점선 : 경사도 (경사도가 0인 부분이 물놀이 구간)
 - 노란 점선 : 깊이
 - 물놀이 구간 전에 경사도가 급한 지역이 있다
 - -> 이는 물의 흐름이 빨라질 수 있고 물놀이 구간에 빠른 유속으로 물이 접근할 수 있다


  ![image](https://github.com/user-attachments/assets/040ce548-27cd-45f0-9981-ae1129aac25e)
     - 물놀이 구간(초록 점선0)에 깊이(노란선)이 깊은 구간이 있다


  <br/>

> 사고적은 지역

  ![image](https://github.com/user-attachments/assets/33743f1d-2803-4421-b280-d5c1cc96106c)
       
  - 사고가 적은 지역은 비교적 고도의 차이가 많이 나지않고 그래프가 일직선에 가깝다
       
  ![image](https://github.com/user-attachments/assets/2bc277cc-90b5-4756-a3b2-c37c466f7b8a)

  - 물놀이 구간 전에 경사가 심한 구간이 보인다 --> 하지만 깊이가 대부분 1M이하이다


### 향후계획


-AI
   - 모델 검출률 향상
- Iot
   - 검출률 향상을 위한 유량센서 강화, 수위 측정
- cloud
   - 람다함수 구현 : s3 일정 수준의 저장공간에 도달하면 자동으로 처음부터 정리해주는 람다함수 구현
   -  클라우드 환경 확대 : github action 과 AWS Amplify를 이용한 CI/CD 파이프라인 구성
- bigdata
   - 유량예측 모델 검출률 향상
   - 가평교를 중심으로 진행하였기에 댐의 영향으로 강수량에는 큰 영향을 받지 않는점이 아쉬움
   - 자연환경에서 유속과, 유량을 예측하기는 매우 복잡한 계산. 전문지식이 필요했다
   - 다른계곡의 지형분속을 통해 CCTV설치 지역을 명확히 할 필요가 있음



      
