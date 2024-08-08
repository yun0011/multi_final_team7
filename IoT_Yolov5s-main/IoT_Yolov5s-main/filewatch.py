# import os
# import time
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler

# class Target:
#     # watchDir = os.getcwd()
#     # #watchDir에 감시하려는 디렉토리를 명시한다.

#     def __init__(self, watchDir):
#         self.observer = Observer()   #observer객체를 만듦
#         self.watchDir = watchDir

#     def run(self):
#         event_handler = Handler()
#         self.observer.schedule(event_handler, self.watchDir, recursive=True)
#         self.observer.start()
#         try:
#             while True:
#                 time.sleep(1)
#         except:
#             self.observer.stop()
#             print("Error")
#             self.observer.join()

# class Handler(FileSystemEventHandler):
# #FileSystemEventHandler 클래스를 상속받음.
# #아래 핸들러들을 오버라이드 함
#     def on_created(self, event): #파일, 디렉터리가 생성되면 실행
#         print(event)
#         print(event.file_name)
#     def on_deleted(self, event): #파일, 디렉터리가 삭제되면 실행
#         print(event)

# if __name__ == "__main__": #본 파일에서 실행될 때만 실행되도록 함
#     live_folder = Target("/home/seok/yolov5/runs/live")
#     live_folder.run()







# import os
# import time
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler

# class Target:
#     def __init__(self, watchDirs):
#         self.observer = Observer()
#         self.watchDirs = watchDirs

#     def run(self):
#         event_handler = Handler()
#         for watchDir in self.watchDirs:
#             self.observer.schedule(event_handler, watchDir, recursive=True)
#         self.observer.start()
#         try:
#             while True:
#                 time.sleep(1)
#         except:
#             self.observer.stop()
#             print("Error")
#             self.observer.join()

# class Handler(FileSystemEventHandler):
#     def on_created(self, event):
#         if not event.is_directory:
#             print(f"Created file: {event.src_path}")
#             file_name = os.path.basename(event.src_path)
#             print(f"Created file name: {file_name}")

#             send_json_to_s3()

#     def on_deleted(self, event):
#         if not event.is_directory:
#             print(f"Deleted file: {event.src_path}")
#             file_name = os.path.basename(event.src_path)
#             print(f"Deleted file name: {file_name}")

# def send_json_to_s3(json_data, bucket_name, file_name):
#   access_key = 'AKIA5VZTIAOJ5WLDE5PE'
#   secret_key = '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'


#   s3 = boto3.client('s3', region_name='eu-west-2',
#                       aws_access_key_id=access_key,
#                       aws_secret_access_key=secret_key)

#   # JSON 데이터를 문자열로 변환
#   json_str = json.dumps(json_data)

#   try:
#   # S3 버킷에 JSON 파일 업로드
#     response = s3.put_object(Body=json_str, Bucket=bucket_name, Key=file_name)
#     print("JSON 파일을 S3로 전송하였습니다.")
#   except Exception as e:
#     print("S3로 JSON 파일을 전송하는 동안 오류가 발생하였습니다.")
#     print(str(e))

# if __name__ == "__main__":
#     watchDirs = [
#         "/home/seok/yolov5/runs/live",
#         "/home/seok/yolov5/runs/json",
#         "/home/seok/yolov5/runs/detect"
#     ]
#     w = Target(watchDirs)
#     w.run()


# import os
# import boto3
# from botocore.exceptions import NoCredentialsError
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler

# # AWS S3 정보 설정
# AWS_ACCESS_KEY_ID = 'AKIA5VZTIAOJ5WLDE5PE'
# AWS_SECRET_ACCESS_KEY = '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'
# BUCKET_NAME = 'team7-water'

# class Handler(FileSystemEventHandler):
#     def __init__(self, s3_client):
#         self.s3_client = s3_client

#     def on_created(self, event):
#         if not event.is_directory:
#             file_path = event.src_path
#             file_name = os.path.basename(file_path)
#             print(f"Created file: {file_name} at {file_path}")

#             try:
#                 # S3에 파일 업로드
#                 self.s3_client.upload_file(file_path, BUCKET_NAME, file_name)
#                 print("File uploaded to S3 successfully")
#             except FileNotFoundError:
#                 print("The file was not found")
#             except NoCredentialsError:
#                 print("AWS credentials were not found")

# if __name__ == "__main__":
#     # AWS S3 클라이언트 생성
#     s3_client = boto3.client('s3', region_name='eu-west-2', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

#     # 파일 감시 핸들러 생성
#     event_handler = Handler(s3_client)
    
#     # 파일 감시 설정
#     observer = Observer()
#     observer.schedule(event_handler, path="/home/seok/yolov5/runs/json", recursive=False)
#     observer.start()

#     try:
#         while True:
#             pass
#     except KeyboardInterrupt:
#         observer.stop()
#     observer.join()


import os
import boto3
from botocore.exceptions import NoCredentialsError
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Thread

# AWS S3 정보 설정
AWS_ACCESS_KEY_ID = 'AKIA5VZTIAOJ5WLDE5PE'
AWS_SECRET_ACCESS_KEY = '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'
# BUCKET_NAME_CAM = 'team7-cam' # 실시간 이미지 img + 익사 디텍 img
# BUCKET_NAME_DATA = 'team7-data' # 익사 위험 json
# BUCKET_NAME_WATER = 'team7-water' # 센서 값 json

class Handler(FileSystemEventHandler):
    def __init__(self, s3_client, folder_path):
        self.s3_client = s3_client
        self.folder_path = folder_path

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            file_name = os.path.basename(file_path)

            # 파일명에 따른 버켓 네임 지정
            if file_name[-5:] == "l.jpg": # 라이브 이미지
                BUCKET_NAME = "team7-cam"
            elif file_name[-5:] == "0.jpg" or file_name[-5:] == "n.jpg": # 1개라도 검출된 이미지
                BUCKET_NAME = "team7-cam2"
            elif file_name[-6:] == "d.json": # 1개라도 검출된 json
                BUCKET_NAME = "team7-data"
            elif file_name[-6:] == "s.json": # 센서 값과 강수량에 따른 위험도 json
                BUCKET_NAME = "team7-water"
                
            try:
                # S3에 파일 업로드
                self.s3_client.upload_file(file_path, BUCKET_NAME, file_name)
                print(file_name, "을", BUCKET_NAME, "에 성공적으로 전송하였습니다.")
            except FileNotFoundError:
                print("The file was not found")
            except NoCredentialsError:
                print("AWS credentials were not found")

if __name__ == "__main__":
    # AWS S3 클라이언트 생성
    s3_client = boto3.client('s3', region_name='eu-west-2', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    # 폴더 경로 리스트
    folder_paths = [
         "/home/seok/yolov5/runs/live_img",
         "/home/seok/yolov5/runs/detect_json",
         "/home/seok/yolov5/runs/detect_img",
         "/home/seok/yolov5/runs/waterflow_json"
    ]

    # Observer 및 Thread 리스트
    observers = []
    threads = []

    # 파일 감시 설정
    for folder_path in folder_paths:
        event_handler = Handler(s3_client, folder_path)
        observer = Observer()
        observer.schedule(event_handler, path=folder_path, recursive=False)
        observers.append(observer)

        # Observer를 별도의 스레드로 실행
        thread = Thread(target=observer.start)
        thread.start()
        threads.append(thread)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        for observer in observers:
            observer.stop()
            observer.join()

        for thread in threads:
            thread.join()