# --- The MIT License (MIT) Copyright (c) alvinconstantine(alvin.constantine@outlook.com), Sat Jun 20 00:10am 2020 ---
import requests
import logging
import os, sys
import json

# ------ 定義 LINE 通知設定函式 -------------------------- 
class lineNotification():
    def __init__(self):
        self.userbaseDir = os.path.expanduser('~')        
        self.lineToken = None
        self.headers = None        
        # ------ 讀取 LINE 的 Token -------------------------- 
        tokenCredentialJson = '%s/%s/%s' % (self.userbaseDir, '.line', 'myDailyPttAlertor')
        try:            
            with open(tokenCredentialJson, 'r', encoding='utf-8') as f:
                tokenProfile = json.load(f)
                self.lineToken = tokenProfile['token']
        except FileNotFoundError:
            logging.error('=== 請先設定 Line Notify 的 token file 檔案: %s。格式為: {"token":"xxxxx"} ===' % tokenCredentialJson)
        else:
            self.headers = {
                "Authorization" : "Bearer " + self.lineToken,
                "Content-Type" : "application/x-www-form-urlencoded"
                }                    
    # ------ 傳送 LINE 的 message -------------------------- 
    def sendMessage(self, msg):        
        params = { 
            "message" : msg
            }
        logging.info('=== %s ===' % msg)        
        try:
            responsedPage = requests.post("https://notify-api.line.me/api/notify", headers=self.headers, params=params)
        except Exception as e:
            logging.error('=== 嘗試傳送 [%s] 時發生未知的 LINE 錯誤 [%s] ===' % (msg, str(e)))
            sys.exit()
        else:            
            if responsedPage.status_code != 200:
                logging.error('=== 傳送 LINE 訊息 [%s] 失敗, 錯誤狀態碼為 [%d] ===' % (msg, responsedPage.status_code))
