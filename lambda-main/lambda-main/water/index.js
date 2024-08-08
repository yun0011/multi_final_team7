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
          const insertQuery = `INSERT INTO water_flow (date, rain, deep, ws, wf, warn) VALUES (?, ?, ?, ?, ?, ?)`;
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
