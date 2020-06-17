# --- The MIT License (MIT) Copyright (c) alvinconstantine(alvin.constantine@outlook.com), Tue Jun 17 08:33:00pm 2020 ---
from synology_api import sys_info
from datetime import datetime
import myNASlinefuncs as line 
import os, sys, stat, json, logging

logging.basicConfig(filename='%s/.scheduler/.log/.dailyUsageCheck/%s.log' % (os.path.expanduser('~'), datetime.now().strftime('%Y%m%d_%H%M%S')), level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
# --- 取得資料夾大小 -----------------------------  
def getStorageSize(sysinfo):
    getstoragesize = sysinfo.storage()
    totalsize = round(int(getstoragesize['data']['volumes'][0]['size']['total'])/1024/1024/1024, 1)
    usedsize = round(int(getstoragesize['data']['volumes'][0]['size']['used'])/1024/1024/1024, 1)
    lefsize = round(totalsize - usedsize, 1)
    ratio = round(usedsize / totalsize * 100, 1)
    returnStoragesize = '儲存空間總容量: %.1f GB, 已使用容量: %.1f GB, 剩餘可用容量: %.1f GB, 使用率 %.1f%%' % (totalsize, usedsize, lefsize, ratio)
    return returnStoragesize
# --- 移除唯讀資料夾 -----------------------------  
def remove_readonly(func, path):  # --- 定義回呼函數 ---
    os.chmod(path, stat.S_IWRITE)  # --- 刪除檔案的唯讀屬性 ---
    func(path)  # --- 再次呼叫剛剛失敗的函數 ---
# --- 啟始 LINE 通知的物件 -----------------------------  
def del_dir(path, onerror=None):
    for file in os.listdir(path):
        file_or_dir = os.path.join(path,file)
        if os.path.isdir(file_or_dir) and not os.path.islink(file_or_dir):
            del_dir(file_or_dir)  # --- 遞迴刪除子資料夾及其檔案 ---
        else:
            try:
                logging.debug('=== 刪除 %s ===' % file_or_dir)
                os.remove(file_or_dir)  # --- 嘗試刪除該檔 ---
            except:  #刪除失敗
                if onerror and callable(onerror):
                    onerror(os.remove, file_or_dir)  # --- 自動呼叫回呼函數 ---
                else:
                    logging.error('=== 刪除資料時發生未預期的錯誤 ===')
    try:
        logging.info('=== 移除 %s ===' % path)
        os.rmdir(path)  # --- 刪除資料夾 ---
    except Exception as a:
        logging.error('=== 移除資料夾 %s 時發生未預期的錯誤: %s ===' % (path, str(e)))

# --- 主程式 -----------------------------  
if __name__ == '__main__':
    # --- 先啟始 LINE 通知的物件 -----------------------------       
    myLineNotificator = line.lineNotification()
    if not myLineNotificator.lineToken:
        logging.error('=== 建立 LINE Notify 時發生未預期的錯誤 ===')
        sys.exit(1)
    try:            
        with open(os.path.expanduser(r'~/.nas/nasconfig')) as f:  # --- 取得 NAS 帳號密碼 ---
            nasConfig = json.load(f)
    except FileNotFoundError:
        logging.error('=== 無法找到 NAS 使用者帳號與密碼的設定檔: nasconfig 。請於 ~/.nas/nasconfig 新增設定檔。格式為: { "account":"username", "password":"********", "ip":"10.0.0.100", "port":"5000" } ===')
        sys.exit(1)
    except Exception as e:
        logging.error('=== 試圖載入 NAS 使用者帳號與密碼的設定檔時發生意外錯誤: %s。 ===' % str(e))
        sys.exit(1)
    else:
        # --- 篩選要刪除的資料夾 -----------------------------        
        removalTarget = '/volume1/homes/webcam'
        os.chdir(removalTarget)
        for i in os.listdir():
            subfolder = os.path.join(removalTarget, i)
            getDirLists = os.listdir(subfolder)
            if len(getDirLists) > 21:
                getDirLists.sort(reverse=True)
                folderCounts = len(getDirLists) - 21
                for j in range(folderCounts):
                    getPath = getDirLists.pop()
                    removalFolder = os.path.join(removalTarget, i, getPath)
                    del_dir(removalFolder, remove_readonly)  # --- 呼叫函數，並指定回呼函數 ---
                    myLineNotificator.sendMessage('已移除 %s 資料夾' % removalFolder)
        # --- 啟始 NAS 的物件並計算可用空間 ----------------------------- 
        ip = nasConfig['ip'] if nasConfig['ip'] else '10.0.0.100'
        port = int(nasConfig['port']) if nasConfig['port'] else 5000
        account = nasConfig['account'] if nasConfig['account'] else None
        password = nasConfig['password'] if nasConfig['password'] else None   
        sysinfo = sys_info.SysInfo(ip, port, account, password)
        getUsageStastistics = getStorageSize(sysinfo)
        myLineNotificator.sendMessage(getUsageStastistics)
        logging.debug('=== 程式結束 ===')