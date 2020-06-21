from datetime import datetime, timedelta
import logging, os, sys
logging.basicConfig(filename='%s/.scheduler/.log/.manualTemptask/%s.log' % (os.path.expanduser('~'), datetime.now().strftime('%Y%m%d_%H%M%S')), level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
from time import strftime, sleep
import json
import pickle
from opencc import OpenCC 
import myNASsynofuncs as nas
import re
import urllib.parse

def downloadProcess(diskStation):
    givenNo2Start = 1256
    givenNo2Stop = 4152
    accumulateCounter = 0
    contentKeys = ('casterZip', 'casterImg', 'thumbnail')
    for casterIndexer in range(givenNo2Start, givenNo2Stop):
        accumulateCounter += 1            
        task = sequenceCaster[casterIndexer]
        caster = cc.convert(task['name'])        
        logging.debug('=== 目前擷取第[%d]個_序號[%d] ===' % (accumulateCounter, casterIndexer))
        # ------ 主播上層主資料夾 --------------------------
        folderExists = None
        folder = 'ig_%s' % task['caster']  
        ds_folder = '%s/%s' % (storageDownload, folder)                
        logging.debug('=== 檢查 ds folder 為 [%s] ===' % ds_folder)
        diskStation.folder = ds_folder        
        if os.path.isdir('%s/%s' % (userbaseDir, ds_folder)):  # ------ 資料夾已存在
            folderExists = True  
            logging.debug('=== 資料夾 [%s] 已存在 ===' % ds_folder)
        else:  # ------ 資料夾不存在
            folderExists = False
            logging.info('=== 資料夾 [%s] 不存在 ===' % ds_folder) 
        logging.debug('===[ 上層資料夾位置: %s/%s ]===' % (userbaseDir, diskStation.folder)) 
        # ------ 找出主播序號 -----------------------------               
        if re.search(r'\d+', caster):
            folderNumberstr = re.search(r'\d+', caster).group()
        else:
            folderNumberstr = None
        # ------ 主播下層主資料夾為名字和序號做尾碼 -----------------------------
        subFolderExists = None  
        subFolder = '%s%s' % (task['caster'], folderNumberstr)
        ds_subFolder = '%s/%s' % (ds_folder, subFolder)
        diskStation.folder = ds_subFolder
        if os.path.isdir('%s/%s' % (userbaseDir, ds_subFolder)):  # ------ 資料夾已存在
            subFolderExists = True
            logging.debug('=== 子資料夾 [%s] 已存在 ===' % ds_subFolder)            
        else:  # ------ 資料夾不存在
            subFolderExists = False
            logging.info('=== 子資料夾 [%s] 不存在 ===' % ds_subFolder)        
        # ------ 主播_檔案s -----------------------------        
        downloadUris = []
        for contentKey in contentKeys: 
            contentValue = os.path.basename(task[contentKey])
            if contentValue:
                if os.path.isfile('%s/%s' % (ds_subFolder, contentValue)):  # ------ 檔案已存在
                    logging.debug('=== 此 [%s] %s [%s] 已下載過 ===' % (caster, contentKey, task[contentKey]))
                else:  # ------ 檔案不存在
                    if not urllib.parse.urlparse(task[contentKey]).scheme:
                        task[contentKey] = appScheme + task[contentKey]
                    logging.info('=== 即將下載 [%s] 的 %s 檔案 [%s] ===' % (caster, contentKey, task[contentKey]))
                    downloadUris.append(task[contentKey].replace(' ', r'%20'))
            else:
                logging.warning('=== 注意，第 [%d] 筆資料內容 [%s] 似乎有問題 ===' % (casterIndexer, contentKey))                       
        # ------ 下載主播的檔案 -----------------------------
        if downloadUris:
            if not subFolderExists:
                # ------ 建立子資料夾 -----------------------------
                if diskStation.FileStation('create', folder=ds_subFolder):
                    logging.debug('=== [%s] 建立子資料夾 [%s] 成功 ===' % (caster, diskStation.folder))
                else:
                    logging.error('=== [%s] 建立子資料夾 [%s] 失敗 ===' % (caster, diskStation.folder))
                    return False
            elif not folderExists:
                # ------ 建立主資料夾 -----------------------------
                if diskStation.FileStation('create', folder=ds_folder):
                    logging.debug('=== 建立資料夾 [%s] 成功 ===' % diskStation.folder)
                else:
                    logging.error('=== 建立資料夾 [%s] 失敗 ===' % diskStation.folder)
                    return False
            logging.info('===[ 第 %d 位主播 %s，序號：%d，資料夾： %s/%s ]===' % (accumulateCounter, caster, casterIndexer, userbaseDir, ds_subFolder))                
            logging.info('=========[ 主播 %s 共有 %s 個影像檔, 嘗試建立下載清單 ]' % (caster, len(downloadUris)))
            if diskStation.DownloadStation('create', data=downloadUris):
                logging.info('=========[ 主播 %s 共有 %s 個影像檔, 已成功建立下載清單 ]=========' % (caster, len(downloadUris)))
            else:
                logging.error('=========[ 主播 %s 共有 %s 個影像檔, 建立下載清單時失敗 ]=========' % (caster, len(downloadUris)))
                return False
        else:     
            logging.info('=========[ 第 %d 位主播 %s，序號：%d，沒有檔案需要下載 ]=========' % (accumulateCounter, caster, casterIndexer)) 
    return True

if __name__ == '__main__':
    timeFreeze = datetime.now()
    name = 'korea19j2020'
    appScheme = 'https://www.19j2020.com'   
    timeFreezeNow = timeFreeze.strftime('%Y%m%d')
    timeYesterday = (timeFreeze - timedelta(days=1)).strftime('%Y%m%d')                     
    userbaseDir = os.path.expanduser('~')        
    storageData = '%s/%s/%s' % ('.scheduler', name, 'crawlerdata')
    storageDownload = '%s/%s/%s' % ('.scheduler', name, 'downloads')
    lastSequencedCaster = '%s/%s/sequenceCaster_%s.pickle' % (userbaseDir, storageData, timeYesterday)  
    sequenceCasterPickle = '%s/%s/sequenceCaster_%s.pickle' % (userbaseDir, storageData, timeFreezeNow)
    sequenceCasterJson = '%s/%s/sequenceCaster_%s.json' % (userbaseDir, storageData, timeFreezeNow)
    sequenceCasterUfPickle = '%s/%s/sequenceCaster_%s_unfinished.pickle' % (userbaseDir, storageData, timeFreezeNow)
    accumulatedCasterPickle = '%s/%s/accumulatedCaster_%s.pickle' % (userbaseDir, storageData, timeFreezeNow)
    accumulatedCasterJson = '%s/%s/accumulatedCaster_%s.json' % (userbaseDir, storageData, timeFreezeNow)
    cc = OpenCC('s2twp')  # opencc.Converter(from_variant='cn', to_variant='twp')
    sequenceCaster = None  
    target = '%s/%s/%s/%s/%s' % (userbaseDir, '.scheduler', name, 'crawlerdata', 'sequenceCaster_20200620.pickle')
    with open(target, 'rb') as f:
            sequenceCaster = pickle.load(f)    
    ds214se = nas.nasDiskStation()
    if ds214se.login:
        downloadProcess(ds214se)
    if ds214se.logout():
        logging.info('Logout successfully!')

