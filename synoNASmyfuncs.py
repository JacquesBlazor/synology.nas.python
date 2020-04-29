# --- The MIT License (MIT) Copyright (c) alvinlin, Sun Apr 30 03:13:00 2020 ---
from requests.compat import urljoin
from pymongo import MongoClient
from pymongo import DESCENDING
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
        logging.warning(r'無法找到你的 NAS 使用者帳號與密碼的設定檔: account.(txt)')
        logging.warning(r'請新增該設定檔, 位於 使用者帳號\.nas\account 格式為: { "account":"username", "password":"********", "ip":"10.0.0.100", "port":"5000" }')
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
        logging.debug('-- 正在執行:diskstation.login --')
        logging.debug('-- 參數: %s, %s --' % (self.auth_url, self.auth_params))
        try:
            response = requests.get(
                self.auth_url,
                params=self.auth_params,
                verify=False).json()
        except TimeoutError:
            logging.error('程式結束。因為連線的主機無法回應，連線嘗試失敗。')
            return None
        else:
            self.login = response['success']    
            self.sid = response['data']['sid']
            self.folder = None
            self.file = None
            self.path = None

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
        logging.debug('-- 正在執行:diskstation.logout --')
        logging.debug('-- 參數: %s, %s --' % (self.auth_url, self.auth_params))        
        try:
            response = requests.get(
                self.auth_url,
                params=self.auth_params,
                verify=False).json()
        except TimeoutError:
            logging.error('程式結束。因為連線的主機無法回應，連線嘗試失敗。')
            return None
        else:
            return response['success']  

# ------ 建立 NAS 中 FileStation 的 createFolder 方法 -------------------------------
    def createFolder(self, ask_folder):
        self.name = 'FileStation'
        self.folder = ask_folder
        self.crtfdr_url = urljoin(self.base_url, 'entry.cgi')
        self.crtfdr_params = {
            'api': 'SYNO.{n}.{m}'.format(n=self.name, m='CreateFolder'),
            'version': '2',
            'method': 'create',
            'folder_path': [self.base_dir],
            'name': [ask_folder],
            '_sid': self.sid
            }
        logging.debug('-- 正在執行:filestation.createFolder --')
        logging.debug('-- 參數: %s, %s --' % (self.crtfdr_url, self.crtfdr_params))
        try:              
            response = requests.get(
                self.crtfdr_url, params=self.crtfdr_params).json()
        except TimeoutError:
            logging.info('程式結束。因為連線的主機無法回應，連線嘗試失敗。')
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
        logging.debug('-- 正在執行:downloadstation.createTask --')
        logging.debug('-- 參數: %s, %s --' % (self.task_url, self.task_params))
        try:            
            response = requests.get(
                self.task_url, params=self.task_params).json()
        except TimeoutError:
            logging.error('程式結束。因為連線的主機無法回應，連線嘗試失敗。')
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
            'additional': 'detail, file',
            '_sid': self.sid
            }
        logging.debug('-- 正在執行:downloadstation.listTask --')
        logging.debug('-- 參數: %s, %s --' % (self.task_url, self.task_params))        
        try:            
            response = requests.get(
                self.task_url, params=self.task_params).json()
        except TimeoutError:
            logging.error('程式結束。因為連線的主機無法回應，連線嘗試失敗。')
            return None
        else:        
            if response['success']:
                return response['data']['tasks']

# ------ 建立 NAS 中 DownloadStation 的 deleteTask 方法 -----------------------------
    def deleteTask(self, taskstobedeleted):
        self.name = 'DownloadStation'
        self.task_url = urljoin(self.base_url, self.name + '/task.cgi')
        self.task_params = {
            'api': 'SYNO.{n}.{m}'.format(n=self.name, m='Task'),
            'version': '3',
            'method': 'delete',
            'id': ','.join(taskstobedeleted), 
            '_sid': self.sid
            }
        logging.debug('-- 正在執行:downloadstation.deleteTask --')
        logging.debug('-- 參數: %s, %s --' % (self.task_url, self.task_params))            
        try:            
            response = requests.get(
                self.task_url, params=self.task_params).json()
        except TimeoutError:
            logging.error('程式結束。因為連線的主機無法回應，連線嘗試失敗。')
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
            'additional': 'detail,file',
            '_sid': self.sid
            }
        logging.debug('-- 正在執行:downloadstation.getInfo --')
        logging.debug('-- 參數: %s, %s --' % (self.task_url, self.task_params))             
        try:            
            response = requests.get(
                self.task_url, params=self.task_params).json()
        except TimeoutError:
            logging.error('程式結束。因為連線的主機無法回應，連線嘗試失敗。')
            return None
        else:        
            return response['success']            

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
        logging.debug('-- 正在執行:downloadstation.pauseTask --')
        logging.debug('-- 參數: %s, %s --' % (self.task_url, self.task_params))             
        try:            
            response = requests.get(
                self.task_url, params=self.task_params).json()
        except TimeoutError:
            logging.error('程式結束。因為連線的主機無法回應，連線嘗試失敗。')
            return None
        else:            
            if response['success']:
                return response['data']

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
        logging.debug('-- 正在執行:downloadstation.resumeTask --')
        logging.debug('-- 參數: %s, %s --' % (self.task_url, self.task_params))             
        try:            
            response = requests.get(
                self.task_url, params=self.task_params).json()
        except TimeoutError:
            logging.error('程式結束。因為連線的主機無法回應，連線嘗試失敗。')
            return None
        else:            
            if response['success']:
                return response['data']            

# ------ 主程式 ------------------------------------------------------------------
if __name__ == '__main__':
    nasConfig = get_nasconfig()
    if nasConfig:                        
        ds214se = nasDiskStation(nasConfig)
        if not ds214se.login:
            logging.error(' == 登入 %s 失敗! == ' % ds214se.name)
        else:                    
            logging.info(' == 登入 %s 成功! 工作階段(Session ID) 為 %s == ' % (ds214se.name, ds214se.sid))
        listedTasks = ds214se.listTask()

##                listedTasks = []
##                for task in response['data']['tasks']:
##                    if task['status'] == 'finished' or ( task['status'] == 'error' and task['status_extra']['error_detail'] == 'broken_link' ):     
##                        listedTasks.append(task['id'])
##                return listedTasks
##            else:
##                return None        

##            if not ds214se.logout():
##                logging.error(' == 登出 %s 失敗! == ' % ds214se.name)
##            else:
##                logging.info(' == 已成功登出 %s . == ' % ds214se.name)

# pauseIDs = []
# for i in listedTasks:
#     pauseIDs.append(i['additional']['detail']['destination'])
# set(pauseIDs)
# for i in listedTasks:
#     if i['additional']['detail']['destination'] != 'home/ptt_Beauty/20200429':
#        pauseIDs.append(i['id'])
##{'additional': {'detail': {'completed_time': 0,
##                           'connected_leechers': 5,
##                           'connected_peers': 15,
##                           'connected_seeders': 4,
##                           'create_time': 1588003699,
##                           'destination': '下載的文件',
##                           'seedelapsed': 0,
##                           'started_time': 1588103043,
##                           'total_peers': 0,
##                           'total_pieces': 13118,
##                           'unzip_password': '',
##                           'uri': '合集 102.48G',
##                           'waiting_seconds': 0}},
## 'id': 'dbid_265159',
## 'size': 110037959350,
## 'status': 'downloading',
## 'title': '萌你一脸@第一会所@04月26日-精选高清有码三十二部合集',
## 'type': 'bt',
## 'username': 'alvinlin'}

# with open('listTask.json', 'a', encoding='utf-8-sig') as f:
#     json.dump(resp_json['data']['tasks'], f, indent=2, sort_keys=True, ensure_ascii=False)            
# for task in resp_json['data']['tasks']:
#     if task['status'] == 'finished' or ( task['status'] == 'error' and task['status_extra']['error_detail'] == 'broken_link' ):     
#         tobedeletedTasks.append(task['id'])