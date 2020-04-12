# --- The MIT License (MIT) Copyright (c) alvinlin, Sun Apr 12 20:08:12 2020 ---
from requests.compat import urljoin
from datetime import datetime
import requests
import logging
import json
import os, sys
logging.basicConfig(level = logging.INFO, format='%(message)s')

# ------ 取得 NAS 帳號密碼副程式 -------------------------------------------------------
def get_nasconfig():
    try:
        with open(os.path.expanduser(r'~\.nas\account')) as f:
            nasprofile = json.load(f)
    except FileNotFoundError:
        logging.warning(r'無法找到你的 NAS 使用者帳號與密碼的設定檔: account.(txt)')
        logging.warning(r'請新增該設定檔, 位於 使用者帳號\.nas\account 格式為: { "account":"username", "password":"********", "ip":"10.0.0.100", "port":"5000" }')
        sys.exit()
    else:
        return {      
            'account': nasprofile['account'],
            'password': nasprofile['password'],
            'ip': nasprofile['ip'],
            'port': int(nasprofile['port']) }          

# ------ 啟始 NAS 物件並登入帳號密碼 -----------------------------------------------------
class nasDiskStation:
    def __init__(self, ip=None, port=None, account=None, password=None):
        self.ip = ip if ip else '10.0.0.100'
        self.port = port if port else 5000
        self.account = account
        self.password = password
        self.name =  'DiskStation'        
        self.base_dir = '/home'
        self.base_url = 'http://{}:{}/webapi/'.format(self.ip, self.port)
        self.auth_url = urljoin(self.base_url, 'auth.cgi')
        self.auth_params = {
            'api': 'SYNO.API.Auth',
            'version': '2',
            'method': 'login',
            'account': self.account,
            'passwd': self.password ,
            'session': self.name,
            'format': 'sid'
            }
        self.api_base_url = urljoin(self.base_url, self.name+'/')
        try:
            response = requests.get(
                self.auth_url,
                params=self.auth_params,
                verify=False).json()
        except TimeoutError:
            logging.error('程式結束。因為連線的主機無法回應，連線嘗試失敗。')
            sys.exit(1)
        else:
            self.login = response['success']    
            self.sid = response['data']['sid']
            self.folder = None
            self.file = None
            self.path = None
             
# ------ 建立 NAS 中 DownloadStation 的 createTask 方法 -----------------------------
    def createTask(self, task_uri):
        self.name = 'DownloadStation'
        self.file = task_uri
        self.path = self.base_dir + '/' + self.folder if self.folder else self.base_dir
        self.task_url = urljoin(self.base_url, self.name + '/task.cgi' )
        self.task_params = {
            'api': 'SYNO.{n}.{m}'.format(n=self.name, m='Task'),
            'version': '3',
            'method': 'create',
            'uri': self.file,
            'destination': self.path.lstrip('/'),
            '_sid': self.sid
            }
        try:            
            response = requests.get(
                self.task_url, params=self.task_params).json()
        except TimeoutError:
            logging.error('程式結束。因為連線的主機無法回應，連線嘗試失敗。')
            sys.exit(1)
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
        try:              
            response = requests.get(
                self.crtfdr_url, params=self.crtfdr_params).json()
        except TimeoutError:
            logging.info('程式結束。因為連線的主機無法回應，連線嘗試失敗。')
            sys.exit(1)
        else:              
            return response['success']             

# ------ 主程式 ------------------------------------------------------------------
if __name__ == '__main__':
    nasConfig = get_nasconfig()
    if nasConfig:                        
        ds214se = nasDiskStation(
            ip=nasConfig['ip'], 
            port=nasConfig['port'], 
            account=nasConfig['account'], 
            password=nasConfig['password'])
        if not ds214se.login:
            logging.info(' == 登入 %s 失敗! == ' % ds214se.name)
        else:                    
            logging.info(' == 登入 %s 成功! == ' % ds214se.name)
            logging.info(' == 目前 %s 的工作階段 (Session ID) 為 %s == ' % (ds214se.name, ds214se.sid))
            folder = datetime.now().strftime("%Y%m%d%a%H%M%S")
            logging.info(' == 正在建立儲存檔案的 [%s] 資料夾 ==' % folder)
            if not ds214se.createFolder(folder):
                logging.info(' == 新增 [%s] 資料夾失敗! ==' % folder)                    
            else:
                url = 'https://i.imgur.com/tq2fWhC.jpg'                                        
                print('  *-* 正在新增下載 [%s] ... ' % url, end='')
                if ds214se.createTask(url):
                    print('成功!')
                else:
                    print('錯誤!')