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
