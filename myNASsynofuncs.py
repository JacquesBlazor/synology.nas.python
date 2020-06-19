# --- The MIT License (MIT) Copyright (c) alvinconstantine(alvin.constantine@outlook.com), Tue Jun 19 08:24:00pm 2020 ---
from requests.compat import urljoin
from datetime import datetime
import requests
import logging
import json
import os, sys 

# ------ 啟始 NAS 物件並登入帳號密碼 -----------------------------------------------------
class nasDiskStation:
    def __init__(self):        
        self.name = 'DiskStation'
        self.method = 'login'
        try:            
            with open(os.path.expanduser(r'~/.nas/nasconfig')) as f:  # --- 取得 NAS 帳號密碼 ---
                nasConfig = json.load(f)
        except FileNotFoundError:
            logging.error('=== 無法找到 NAS 使用者帳號與密碼的設定檔: nasconfig 。請於 ~/.nas/nasconfig 新增設定檔。格式為: { "account":"username", "password":"********", "ip":"10.0.0.100", "port":"5000" } ===')
        except Exception as e:
            logging.error('=== 試圖載入 NAS 使用者帳號與密碼的設定檔時發生意外錯誤: %s ===' % str(e)) 
        else:       
            self.ip = nasConfig['ip'] if nasConfig['ip'] else '10.0.0.100'
            self.port = int(nasConfig['port']) if nasConfig['port'] else 5000
            self.account = nasConfig['account'] if nasConfig['account'] else None
            self.password = nasConfig['password'] if nasConfig['password'] else None                
            self.base_dir = '/home'
            self.base_url = 'http://{i}:{p}/webapi/'.format(i=self.ip, p=self.port)
            self.auth_url = urljoin(self.base_url, 'auth.cgi')
            self.auth_params = {
                'api': 'SYNO.API.Auth',
                'version': '6',
                'method': self.method,
                'account': self.account,
                'passwd': self.password,
                'session': self.name,
                'format': 'sid'
                }            
            logging.debug('=== 正在執行: %s, %s 作業 ===' % (self.name, self.method))
            logging.debug('=== 參數: %s, %s ===' % (str(self.auth_url), str(self.auth_params)))
            self.login = None            
            try:
                response = requests.get(self.auth_url, params=self.auth_params, verify=False).json()
            except TimeoutError:
                logging.error('=== 連線的主機 %s:%d 沒有回應，連線嘗試失敗 ===' % (self.ip, self.port))
            else:
                self.folder, self.path = None, None
                self.login = response['success']    
                self.sid = response['data']['sid']                
                self.staMapping = {
                    'waiting' : '等待中',        
                    'downloading' : '下載中',
                    'paused' : '已暫停',
                    'finishing' : '正在完成',
                    'finished' : '已完成',
                    'hash_checking' : '雜湊檢查中',
                    'seeding' : '傳送中',
                    'filehosting_waiting' : '檔案等待中',
                    'extracting' : '解壓縮中',
                    'error' : '錯誤'                
                    }
                self.errMapping = {
                    '100' : '未知的錯誤_(100)',
                    '101' : '不正確的參數_(101)',
                    '102' : '請求的 API 不存在_(102)',
                    '103' : '請求的方法不存在_(103)',
                    '104' : '請求的版本中不包含該功能_(104)',
                    '105' : '登入的 Session 沒有權限_(105)',
                    '106' : '時間 Session 逾時_(106)',
                    '107' : '重複的登入導致 Session 被中斷_(107)',
                    '400' : '檔案上傳失敗_(400)',        
                    '401' : '已達到最大作業數量_(401)',
                    '402' : '目的地被拒絕_(402)',
                    '403' : '目的地不存在_(403)',
                    '404' : '不正確的作業編號_(404)',
                    '405' : '不正確的作業行為_(405)',
                    '406' : '沒有預設的目的地_(406)',
                    '407' : '設定目的地失敗_(407)',
                    '408' : '檔案不存在_(408)'             
                    }

# ------ 建立 NAS 中 DownloadStation 的 createTask 方法 -----------------------------
    def logout(self):
        self.name =  'DiskStation'
        self.method = 'logout'        
        self.base_url = 'http://{i}:{p}/webapi/'.format(i=self.ip, p=self.port)
        self.auth_url = urljoin(self.base_url, 'auth.cgi')
        self.auth_params = {
            'api': 'SYNO.API.Auth',
            'version': '6',
            'method': self.method,
            'session': self.name,
            }
        logging.debug('=== 正在執行: %s, %s 作業 ===' % (self.name, self.method))
        logging.debug('=== 參數: %s, %s ===' % (str(self.auth_url), str(self.auth_params)))        
        try:
            response = requests.get(self.auth_url, params=self.auth_params, verify=False).json()
        except TimeoutError:
            logging.error('=== 連線的主機 %s:%d 沒有回應，連線嘗試失敗 ===' % (self.ip, self.port))
            return False
        else:
            if not response['success']:
                errorCode = response['error']['code']
                logging.error('=== 執行 %s 的 %s 作業時發生錯誤: %s ===' % (self.name, self.task_params['method'], self.errMapping[str(errorCode)]))             
            return response['success']  

# ------ 建立 NAS 中的 Storage 方法 -------------------------------
    def Storage(self, method, **kwargs):
        self.name = 'Storage'        
        if isinstance(method, str) and method.lower() in ('load_info', 'get_usage'):
            self.method = method.lower()
            logging.debug('=== 開始執行: %s, %s 作業 ===' % (self.name, self.method))
        else:
            logging.error('=== 此 %s 中沒有指定的 %s 作業方法 ===' % (self.name, str(method)))
            return False
        # ------ 建立 NAS 中 Storage 的 load_info 方法 -------------------------------    
        if self.method == 'load_info':
                self.task_url = urljoin(self.base_url, 'entry.cgi')
                self.task_params = {
                    'api': 'SYNO.{n}.{m}'.format(n=self.name, m='CGI.Storage'),
                    'version': '1',
                    'method': self.method,
                    '_sid': self.sid,
                    }            
                logging.debug('=== 正在執行: %s, %s 作業 ===' % (self.name, self.method))
                logging.debug('=== 參數: %s, %s ===' % (str(self.task_url), str(self.task_params)))
                try:              
                    response = requests.get(self.task_url, params=self.task_params).json()
                except TimeoutError:
                    logging.error('=== 連線的主機 %s:%d 沒有回應，連線嘗試失敗 ===' % (self.ip, self.port))
                    return False
                else:
                    if not response['success']:
                        errorCode = response['error']['code']
                        logging.error('=== 執行 %s 的 %s 作業時發生錯誤: %s ===' % (self.name, self.task_params['method'], self.errMapping[str(errorCode)]))             
                    return response['data']
        # ------ 建立 NAS 中 Storage 的 get_usage 方法 -------------------------------           
        elif self.method == 'get_usage':
            # --- 這方法會利用原來的 Storage 的 load_info 方法來取得磁碟空間大小 ----------------------------- 
            getstoragesize = self.Storage('load_info')
            if getstoragesize:
                totalsize = round(int(getstoragesize['volumes'][0]['size']['total']) /1024 /1024 /1024, 1)
                usedsize = round(int(getstoragesize['volumes'][0]['size']['used']) /1024 /1024 /1024, 1)
                lefsize = round(totalsize - usedsize, 1)
                ratio = round(usedsize / totalsize * 100, 1)
                returnStoragesize = '儲存空間總容量: %.1f GB, 已使用容量: %.1f GB, 剩餘可用容量: %.1f GB, 使用率 %.1f%%' % (totalsize, usedsize, lefsize, ratio)
                return returnStoragesize
            else:
                return False

# ------ 建立 NAS 中 FileStation 的 createFolder 方法 -------------------------------
    def FileStation(self, method, **kwargs):
        self.name = 'FileStation'
        self.method = method
        # ------ 建立 NAS 中 DownloadStation 的 remove 方法  -----------------------------
        if self.method == 'create':
            if not kwargs:
                logging.error('=== 執行 %s 的 %s 作業缺少了資料參數  ===' % (self.name, self.method))
                return False
            data = 'folder'
            if data in kwargs:                                   
                self.folder = kwargs[data]
                self.task_url = urljoin(self.base_url, 'entry.cgi')
                self.task_params = {
                    'api': 'SYNO.{n}.{m}'.format(n=self.name, m='CreateFolder'),
                    'version': '2',
                    'method': 'create',
                    'folder_path': [self.base_dir],
                    'name': [self.folder],
                    '_sid': self.sid,
                    }
                logging.debug('=== 正在執行: %s, %s 作業 ===' % (self.name, self.method))
                logging.debug('=== 參數: %s, %s ===' % (str(self.task_url), str(self.task_params)))
                try:              
                    response = requests.get(self.task_url, params=self.task_params).json()
                except TimeoutError:
                    logging.error('=== 連線的主機 %s:%d 沒有回應，連線嘗試失敗 ===' % (self.ip, self.port))
                    return False
                else:
                    if not response['success']:
                        errorCode = response['error']['code']
                        logging.error('=== 執行 %s 的 %s 作業時發生錯誤: %s ===' % (self.name, self.task_params['method'], self.errMapping[str(errorCode)]))             
                    return response['success'] 
            else:
                logging.error('=== 執行 %s 的 %s 作業缺少了資料參數 ===' % (self.name, self.method))
                return False                         

# ------ 建立 NAS 中 DownloadStation 的 share param 方法 -----------------------------
    def DownloadStation(self, method, **kwargs):
        # ------ 確認傳入的參數是 NAS 中 DownloadStation 中已實作的方法 -----------------------------
        self.name = 'DownloadStation'
        if isinstance(method, str) and method.lower() in ('filter', 'remove', 'list', 'create', 'edit', 'getinfo', 'delete', 'resume'):
            self.method = method.lower()
            logging.debug('=== 開始執行: %s, %s 作業 ===' % (self.name, self.method))
        else:
            logging.error('=== 此 %s 中沒有指定的 %s 作業方法 ===' % (self.name, str(method)))
            return False
        # ------ 建立 NAS 中 DownloadStation 的 remove 方法  -----------------------------
        if self.method == 'remove':
            # 這方法會利用原來的 DownloadStation 的 list 方法來找到 finished, error 中可以移除的工作
            taskItemLists = []
            finished, brokenlinks = 0, 0
            for taskItem in self.DownloadStation('list'):
                if taskItem['status'] in ('finished', 'error'):
                    if taskItem['status'] == 'finished':
                        finished+=1
                        logging.debug('=== [ %s: (%d) %s/%s ] ===' % (self.staMapping[taskItem['status']], finished, taskItem['additional']['detail']['destination'], taskItem['title']))
                        taskItemLists.append(taskItem['id'])
                    elif taskItem['status_extra']['error_detail'] == 'broken_link':
                        brokenlinks+=1
                        logging.info('=== [ %s: (%d) %s/%s ] ===' % (self.staMapping[taskItem['status']], brokenlinks, taskItem['additional']['detail']['destination'], taskItem['title']))
                        taskItemLists.append(taskItem['id'])
            logging.info('=== 需清理的項目，總共有 %d 項。已完成的有 %d 項，有錯誤連結的 %d 項 ===' % (len(taskItemLists), finished, brokenlinks))
            if taskItemLists:
                if self.DownloadStation('delete', data=taskItemLists):
                    logging.info('=== 已成功刪除: %d 項已完成工作 ===' % len(taskItemLists))
                    return True
                else:
                    logging.info('=== 刪除工作 %d 項沒有正確完成 ===' % len(taskItemLists))
                    return False
            else:
                logging.info('=== 已成功執行移除作業但沒有工作需要移除 ===')
                return True
        # ------ 建立 NAS 中 DownloadStation 的 filter 方法  -----------------------------
        elif self.method == 'filter':            
            # 這方法會利用原來的 DownloadStation 的 list 方法來分類(catagorize)並計算下載項目效率的函式
            # 狀態有: 'status': 'downloading', 'error', 'paused', 'finished', 'waiting', 'finishing' 或 task['status_extra']['error_detail'] == 'broken_link'           
            getTaskLists = self.DownloadStation('list')
            if getTaskLists:
                logging.info('===[ 列出 %s 清單數量共: %d 個 ]===' % (self.name, len(getTaskLists)))
                getClassifiedTasks = {
                    'waiting' : [],        
                    'downloading' : [],
                    'paused' : [],
                    'finishing' : [],
                    'finished' : [],
                    'hash_checking' : [],
                    'seeding' : [],
                    'filehosting_waiting' : [],
                    'extracting' : [],
                    'error' : []    
                    }                            
                for i in getTaskLists:
                    getClassifiedTasks[i['status']].append(i)
                del getTaskLists
                if getClassifiedTasks['downloading']:         
                    timenow = datetime.now()  
                    for i in getClassifiedTasks['downloading']:           
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
                    getClassifiedTasks['downloading'].sort(key = lambda s: s['ratio'])  # 按 ratio 效率將目前下載中的項目排序
                # --- 列出狀態 ---                    
                for status, tasks in getClassifiedTasks.items():
                    if tasks:
                        logging.info('===[ %s: 有 %d 個 ]===' % (self.staMapping[status], len(tasks)))
                    if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                        for itemIndex, taskItem in enumerate(tasks):
                            logging.debug('=== [%d]_[ %s/%s ] ===' % (itemIndex, taskItem['additional']['detail']['destination'], taskItem['title']))
                return getClassifiedTasks
        # ------ 建立 NAS 中 DownloadStation 的 list, create, edit, getinfo, delete, resume 方法  -----------------------------
        elif self.method in ('list', 'create', 'edit', 'getinfo', 'delete', 'resume'):
            self.task_url = urljoin(self.base_url, self.name + '/task.cgi')        
            self.path = '{b}/{f}'.format(b=self.base_dir, f=self.folder) if self.folder else ''
            self.task_params = {
                'api': 'SYNO.{n}.{m}'.format(n=self.name, m='Task'),
                'version': '3',
                'method' : self.method, 
                '_sid': self.sid,
                }
            uriLoops = 1
            data = None
            taskUris = None
            if self.method == 'list':   
                self.task_params['additional'] = 'detail,transfer,file'  # 注意逗號 detail,transfer,file 中間不能有空格          
            elif kwargs:
                data = 'data'              
                if data in kwargs:               
                    if isinstance(kwargs[data], str):
                        taskUris = kwargs[data]
                    elif isinstance(kwargs[data], list):
                        taskUris = ','.join(kwargs[data])
                    else:
                        logging.error('=== 執行 %s 的 %s 作業時 %s 參數型別必須是字串或串列 ===' % (self.name, self.method, data))
                        return False
                    paramKey = 'id'                
                    if self.method == 'create':
                        paramKey = 'uri'                     
                        self.path = '{b}/{f}'.format(b=self.base_dir, f=self.folder) if self.folder else ''
                        self.task_params[paramKey] = taskUris
                        self.task_params['destination'] = self.path.lstrip('/') if self.path else None                  
                    elif self.method == 'edit':               
                        self.task_params['destination'] = kwargs['destination'].lstrip('/')
                    elif self.method == 'getinfo':
                        self.task_params['additional'] = 'detail, transfer, file'
                else:
                    logging.error('=== 執行 %s 的作業 %s 缺少了關鍵參數 %s  ===' % (self.name, self.method, data))
                    return False
                uriLength = len(taskUris)
                uriMaxlength = 800
                uriLoops = ( uriLength // uriMaxlength ) + 1
            else:
                logging.error('=== 執行 %s 的 %s 作業缺少了資料參數  ===' % (self.name, self.method))
                return False
            logging.debug('=== 正在執行: %s, %s 作業 ===' % (self.name, self.method))
            for itemIndex in range(uriLoops):
                if data:
                    self.task_params[paramKey] = taskUris[:taskUris[:taskUris.find(',', uriMaxlength)].rfind(',')] if len(taskUris) > uriMaxlength else taskUris
                    logging.debug('=== 正在執行: %s, %s 作業，參數為 %s, 長度為 %d ===' % (self.name, self.method, paramKey, len(self.task_params[paramKey])))               
                logging.debug('=== 參數: %s, %s ===' % (str(self.task_url), str(self.task_params)))
                try:           
                    response = requests.get(self.task_url, params=self.task_params).json()
                except TimeoutError:
                    logging.error('=== 連線的主機 %s:%d 沒有回應，連線嘗試失敗 ===' % (self.ip, self.port))
                    return False
                except Exception as e:
                    logging.error('=== 嘗試進行 %s, %s作業時發生未預期的錯誤: %s ===' % (self.name, self.method, str(e)))
                else:
                    if not response['success']:
                        errorCode = response['error']['code']
                        logging.error('=== 執行 %s, %s 作業時發生錯誤: %s ===' % (self.name, self.method, self.errMapping[str(errorCode)]))
                        return False
                    elif data:
                        taskUris = taskUris[taskUris[:taskUris.find(',', uriMaxlength)].rfind(',')+1:] if len(taskUris) > uriMaxlength else taskUris
                    elif self.method in ('list', 'getinfo'):
                        return response['data']['tasks']
                    elif self.method in ('pause', 'resume'):
                        return response['data']['id']
            return response['success']                
