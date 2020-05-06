# --- The MIT License (MIT) Copyright (c) alvinconstantine(alvin.constantine@outlook.com), Wed May 6 10:55:00am 2020 ---
from requests.compat import urljoin
from datetime import datetime
import requests
import logging
import json
import os, sys

logging.basicConfig(level = logging.INFO, format = '%(levelname)s: %(message)s')
# ------ 取得 NAS 帳號密碼副程式 -------------------------------------------------------
def get_nasconfig():
    try:
        with open(os.path.expanduser(r'~/.nas/account')) as f:
            nasConfig = json.load(f)
    except FileNotFoundError:
        logging.warning('=== 無法找到你的 NAS 使用者帳號與密碼的設定檔: account.(txt)。 ===')
        logging.warning('=== 請新增該設定檔, 位於 使用者帳號/.nas/account 格式為: { "account":"username", "password":"********", "ip":"10.0.0.100", "port":"5000" }。 ===')
        return None
    else:
        return nasConfig        

# ------ 啟始 NAS 物件並登入帳號密碼 -----------------------------------------------------
class nasDiskStation:
    def __init__(self, nasConfig):
        self.ip = nasConfig['ip'] if nasConfig['ip'] else '10.0.0.100'
        self.port = int(nasConfig['port']) if nasConfig['port'] else 5000
        self.account = nasConfig['account'] if nasConfig['account'] else None
        self.password = nasConfig['password'] if nasConfig['password'] else None
        self.name =  'DiskStation'        
        self.base_dir = '/home'
        self.base_url = 'http://{}:{}/webapi/'.format(self.ip, self.port)
        self.auth_url = urljoin(self.base_url, 'auth.cgi')
        self.auth_params = {
            'api': 'SYNO.API.Auth',
            'version': '6',
            'method': 'login',
            'account': self.account,
            'passwd': self.password ,
            'session': self.name,
            'format': 'sid'
            }
        logging.debug('===  正在執行:diskstation.login ===')
        logging.debug('===  參數: %s, %s ===' % (self.auth_url, self.auth_params))
        try:
            response = requests.get(
                self.auth_url,
                params=self.auth_params,
                verify=False).json()
        except TimeoutError:
            logging.error('=== 連線的主機無法回應，連線嘗試失敗。 ===')
            self.login = None
        else:
            self.login = response['success']    
            self.sid = response['data']['sid']
            self.folder = None
            self.file = None
            self.path = None
            self.designated = None

# ------ 建立 NAS 中 DownloadStation 的 createTask 方法 -----------------------------
    def logout(self):
        self.name =  'DiskStation'        
        self.base_url = 'http://{}:{}/webapi/'.format(self.ip, self.port)
        self.auth_url = urljoin(self.base_url, 'auth.cgi')
        self.auth_params = {
            'api': 'SYNO.API.Auth',
            'version': '6',
            'method': 'logout',
            'session': self.name,
            }
        logging.debug('=== 正在執行:diskstation.logout ===')
        logging.debug('=== 參數: %s, %s ===' % (self.auth_url, self.auth_params))        
        try:
            response = requests.get(
                self.auth_url,
                params=self.auth_params,
                verify=False).json()
        except TimeoutError:
            logging.error('=== 連線的主機無法回應，連線嘗試失敗。 ===')
            return None
        else:
            return response['success']  

# ------ 建立 NAS 中 FileStation 的 createFolder 方法 -------------------------------
    def createFolder(self, designated):
        self.name = 'FileStation'
        self.folder = designated
        self.crtfdr_url = urljoin(self.base_url, 'entry.cgi')
        self.crtfdr_params = {
            'api': 'SYNO.{n}.{m}'.format(n=self.name, m='CreateFolder'),
            'version': '2',
            'method': 'create',
            'folder_path': [self.base_dir],
            'name': [designated],
            '_sid': self.sid
            }
        logging.debug('=== 正在執行:filestation.createFolder ===')
        logging.debug('=== 參數: %s, %s ===' % (self.crtfdr_url, self.crtfdr_params))
        try:              
            response = requests.get(
                self.crtfdr_url, params=self.crtfdr_params).json()
        except TimeoutError:
            logging.error('=== 連線的主機無法回應，連線嘗試失敗。 ===')
            return None
        else:              
            return response['success']          

# ------ 建立 NAS 中 DownloadStation 的 createTask 方法 -----------------------------
    def createTask(self, task_uri):
        self.name = 'DownloadStation'
        self.file = task_uri
        self.path = self.base_dir + '/' + self.folder if self.folder else self.base_dir
        self.task_url = urljoin(self.base_url, self.name + '/task.cgi')
        self.task_params = {
            'api': 'SYNO.{n}.{m}'.format(n=self.name, m='Task'),
            'version': '3',
            'method': 'create',
            'uri': self.file,
            'destination': self.path.lstrip('/'),
            '_sid': self.sid
            }
        logging.debug('=== 正在執行:downloadstation.createTask ===')
        logging.debug('=== 參數: %s, %s ===' % (self.task_url, self.task_params))
        try:            
            response = requests.get(
                self.task_url, params=self.task_params).json()
        except TimeoutError:
            logging.error('=== 連線的主機無法回應，連線嘗試失敗。 ===')
            return None
        else:        
            return response['success']

# ------ 建立 NAS 中 DownloadStation 的 listTask 方法 -----------------------------
    def listTask(self):
        self.name = 'DownloadStation'
        self.task_url = urljoin(self.base_url, self.name + '/task.cgi')
        self.task_params = {
            'api': 'SYNO.{n}.{m}'.format(n=self.name, m='Task'),
            'version': '3',
            'method': 'list',
            'additional': 'detail,transfer,file',
            '_sid': self.sid
            }
        logging.debug('=== 正在執行:downloadstation.listTask ===')
        logging.debug('=== 參數: %s, %s ===' % (self.task_url, self.task_params))        
        try:            
            response = requests.get(
                self.task_url, params=self.task_params).json()
        except TimeoutError:
            logging.error('=== 連線的主機無法回應，連線嘗試失敗。 ===')
            return None
        else:        
            if response['success']:
                return response['data']['tasks']
            else:
                return None

# ------ 建立 NAS 中 DownloadStation 的 deleteTask 方法 -----------------------------
    def deleteTask(self, taskids):
        self.name = 'DownloadStation'
        self.task_url = urljoin(self.base_url, self.name + '/task.cgi')
        self.task_params = {
            'api': 'SYNO.{n}.{m}'.format(n=self.name, m='Task'),
            'version': '3',
            'method': 'delete',
            'id': ','.join(taskids), 
            '_sid': self.sid
            }
        logging.debug('=== 正在執行:downloadstation.deleteTask ===')
        logging.debug('=== 參數: %s, %s ===' % (self.task_url, self.task_params))            
        try:            
            response = requests.get(
                self.task_url, params=self.task_params).json()
        except TimeoutError:
            logging.error('=== 連線的主機無法回應，連線嘗試失敗。 ===')
            return None
        else:        
            return response['success']

# ------ 建立 NAS 中 DownloadStation 的 getInfo 方法 -----------------------------
    def getInfo(self, taskids):
        self.name = 'DownloadStation'
        self.task_url = urljoin(self.base_url, self.name + '/task.cgi')
        self.task_params = {
            'api': 'SYNO.{n}.{m}'.format(n=self.name, m='Task'),
            'version': '3',
            'method': 'getinfo',
            'id': ','.join(taskids),
            'additional': 'detail,transfer,file',
            '_sid': self.sid
            }
        logging.debug('=== 正在執行:downloadstation.getInfo ===')
        logging.debug('=== 參數: %s, %s ===' % (self.task_url, self.task_params))             
        try:            
            response = requests.get(
                self.task_url, params=self.task_params).json()
        except TimeoutError:
            logging.error('=== 連線的主機無法回應，連線嘗試失敗。 ===')
            return None
        else:        
            if response['success']:
                return response['data']['tasks']
            else:
                return None   

# ------ 建立 NAS 中 DownloadStation 的 pauseTask 方法 -----------------------------
    def pauseTask(self, taskids):
        self.name = 'DownloadStation'
        self.task_url = urljoin(self.base_url, self.name + '/task.cgi')
        self.task_params = {
            'api': 'SYNO.{n}.{m}'.format(n=self.name, m='Task'),
            'version': '3',
            'method': 'pause',
            'id': ','.join(taskids),
            '_sid': self.sid
            }
        logging.debug('=== 正在執行:downloadstation.pauseTask ===')
        logging.debug('=== 參數: %s, %s ===' % (self.task_url, self.task_params))             
        try:            
            response = requests.get(
                self.task_url, params=self.task_params).json()
        except TimeoutError:
            logging.error('=== 連線的主機無法回應，連線嘗試失敗。 ===')
            return None
        else:            
            if response['success']:
                return response['data']
            else:
                return None                

# ------ 建立 NAS 中 DownloadStation 的 resumeTask 方法 -----------------------------
    def resumeTask(self, taskids):
        self.name = 'DownloadStation'
        self.task_url = urljoin(self.base_url, self.name + '/task.cgi')
        self.task_params = {
            'api': 'SYNO.{n}.{m}'.format(n=self.name, m='Task'),
            'version': '3',
            'method': 'resume',
            'id': ','.join(taskids),
            '_sid': self.sid
            }
        logging.debug('=== 正在執行:downloadstation.resumeTask ===')
        logging.debug('=== 參數: %s, %s ===' % (self.task_url, self.task_params))             
        try:            
            response = requests.get(
                self.task_url, params=self.task_params).json()
        except TimeoutError:
            logging.error('=== 連線的主機無法回應，連線嘗試失敗。 ===')
            return None
        else:            
            if response['success']:
                if response['data']['error'] == 0:
                    return True
                else:
                    return response['data']['error']        

# ------ 建立 NAS 中 DownloadStation 的 editTask 方法 -----------------------------
    def editTask(self, taskids, designated):
        self.name = 'DownloadStation'
        self.task_url = urljoin(self.base_url, self.name + '/task.cgi')
        self.designated = designated if designated else self.base_dir
        self.task_params = {
            'api': 'SYNO.{n}.{m}'.format(n=self.name, m='Task'),
            'version': '3',
            'method': 'edit',
            'id': ','.join(taskids),
            'destination': self.designated.lstrip('/'),
            '_sid': self.sid
            }
        logging.debug('=== 正在執行:downloadstation.editTask ===')
        logging.debug('=== 參數: %s, %s ===' % (self.task_url, self.task_params))             
        try:            
            response = requests.get(
                self.task_url, params=self.task_params).json()
        except TimeoutError:
            logging.error('=== 連線的主機無法回應，連線嘗試失敗。 ===')
            return None
        else:            
            if response['success']:
                if response['data']['error'] == 0:
                    return True
                else:
                    return response['data']['error']     

# ------ 建立 NAS 中 DownloadStation 的 catagorizedTask 方法  -----------------------------
    def catagorizedTask(self):
        classifiedTasks = self.listTask()
        # 這方法會利用原來的 DownloadStation 的 listTask 方法來分類(catagorize)並計算下載項目效率的函式
        # 狀態有: 'status': 'downloading', 'error', 'paused', 'finished', 'waiting', 'finishing' 或 task['status_extra']['error_detail'] == 'broken_link' 
        if classifiedTasks:
            logging.info('全部數量: %s 個. ' %  len(classifiedTasks))
            downloadingTasks = list(filter(lambda i: i['status'] == 'downloading', classifiedTasks))
            if downloadingTasks:
                logging.info('下載中: %s 個. ' % len(downloadingTasks))            
                logging.debug(downloadingTasks)
                timenow = datetime.now()  
                for i in downloadingTasks:           
                    downloaded = int(i['additional']['transfer']['downloaded_pieces'])  # 已下載了的總片段
                    speed = int(i['additional']['transfer']['speed_download'])  # 每秒傳輸率 n byte
                    elapsed = round(((timenow - datetime.fromtimestamp(int(i['additional']['detail']['started_time']))).days + ((timenow - datetime.fromtimestamp(int(i['additional']['detail']['started_time']))).seconds /86400)), 5)  # 已經開始下載經過 n.m 天了
                    size = round(int(i['size']) / 1073741824, 3)  # 檔案大小 n GB
                    percentage = round(downloaded / int(i['additional']['detail']['total_pieces']), 3) if downloaded != 0 else 0  # 已下載的百分比率
                    expected = round((speed * 60 * 60 * 24) / 1073741824, 3) if speed != 0 else 0  # 按目前速率預期一天應可以下載 n GB
                    downloads = round(size * percentage, 3)
                    actual = round(downloads / elapsed, 3)  # 按目前速率實際一天可以下載 n GB 
                    ratio = round(actual / expected, 3) if speed != 0 else 0  # 實際/預期 比率, 愈高代表過去效率愈高
                    i['elapsed'] = elapsed
                    i['sizeGB'] = size
                    i['downloadGB'] = downloads
                    i['speed'] = speed
                    i['percentage'] = percentage
                    i['expected'] = expected
                    i['actual'] = actual
                    i['ratio'] = ratio
                downloadingTasks.sort(key = lambda s: s['ratio'])  # 按 ratio 效率將目前下載中的項目排序
            finishedTasks = list(filter(lambda i: i['status'] == 'finished', classifiedTasks))
            if finishedTasks:
                logging.info('已完成: %s 個. ' % len(finishedTasks))
                logging.debug(finishedTasks)
            finishingTasks = list(filter(lambda i: i['status'] == 'finishing', classifiedTasks))
            if finishingTasks:
                logging.info('正在完成: %s 個. ' % len(finishingTasks))
                logging.debug(finishingTasks)    
            pausedTasks = list(filter(lambda i: i['status'] == 'paused', classifiedTasks))
            if pausedTasks:
                logging.info('暫停中: %s 個. ' % len(pausedTasks))
                logging.debug(pausedTasks)                
            waitingTasks = list(filter(lambda i: i['status'] == 'waiting', classifiedTasks))
            if waitingTasks:
                logging.info('等待中: %s 個. ' % len(waitingTasks))
                logging.debug(waitingTasks)                        
            errorTasks = list(filter(lambda i: i['status'] == 'error', classifiedTasks))
            if errorTasks:
                logging.info('有錯誤: %s 個. ' % len(errorTasks))            
                logging.debug(errorTasks)                
            del classifiedTasks
            classifiedTasks = {}
            classifiedTasks['downloading'] = downloadingTasks
            classifiedTasks['finished'] = finishedTasks
            classifiedTasks['finishing'] = finishingTasks
            classifiedTasks['paused'] = pausedTasks
            classifiedTasks['waiting'] = waitingTasks
            classifiedTasks['error'] = errorTasks
            return classifiedTasks 
        else:
            return None 

# ------ 主程式 ------------------------------------------------------------------
if __name__ == '__main__':
    nasConfig = get_nasconfig()
    if nasConfig:
        # ------ 啟始並登入 ----------------------------- 
        ds214se = nasDiskStation(nasConfig)
        if ds214se.login:      
            logging.info('=== 登入 %s 成功! === ' % ds214se.name)
            logging.debug('=== 工作階段 (Session ID) 為 %s ===' % ds214se.sid)             
            # ------ 主要功能 -----------------------------     
            classifiedTasks = ds214se.catagorizedTask()
            if classifiedTasks:
                if classifiedTasks['downloading']:
                    for i, j in enumerate(classifiedTasks['downloading']):
                        print('{}. 項目: [{}], 已完成比率: [{}%], 效率: [{}].'.format(i+1, j['title'], round(j['percentage'] * 100, 1), j['ratio']))
            # ------ 登出 ----------------------------- 
            if not ds214se.logout():
                logging.error('=== 登出 %s 失敗! == '  % ds214se.name)
            else:
                logging.info('=== 已成功登出 %s! == ' % ds214se.name)  
        else:
            logging.error('=== 登入 %s 失敗! === ' % ds214se.name)
