from datetime import datetime, timedelta
from bs4 import BeautifulSoup, Tag
from time import strftime, sleep
from opencc import OpenCC
import os, sys, shutil
import urllib.parse
import requests
import logging
import pickle
import json
import ast
import re

# ------ 定義 korea crawler 類別 -------------------------- 
class crawlerKorea():
    def __init__(self):
        # ------ 常變數設定 --------------------------
        self.name = 'korea'
        self.userbaseDir = os.path.expanduser('~')        
        self.storageData = '%s/%s/%s' % ('.scheduler', 'crawlerdata', self.name)
        self.storageDownload = '%s/%s/%s' % ('.scheduler', 'downloads', self.name)
        self.appScheme = 'https://www.korea.com'
        self.accumulatedCaster = []        
        self.cookies = {
            'txbrowse_10535': '10535',
            'txbrowse_12126': '12126',
            'txbrowse_1530': '1530',
            'txbrowse_991': '991',
            'txbrowse_992': '992',
            'txbrowse_989': '989',
            'txbrowse_993': '993',
            'txbrowse_988': '988',
            'txbrowse_1000': '1000',
            'txbrowse_1001': '1001',
            'txbrowse_999': '999',
            'txbrowse_998': '998',
            'txbrowse_996': '996',
            'txbrowse_995': '995',
            'txbrowse_997': '997',
            'txbrowse_994': '994',
            'txbrowse_990': '990',
            'txbrowse_1025': '1025',
            'txbrowse_1017': '1017',
            'txbrowse_1015': '1015',
            'txbrowse_1028': '1028',
            'txbrowse_1021': '1021',
            'txbrowse_1019': '1019',
            'txbrowse_1327': '1327',
            'txbrowse_1035': '1035',
            'txbrowse_1048': '1048',
            'txbrowse_1034': '1034',
            'txbrowse_1065': '1065',
            'txbrowse_1078': '1078',
            'txbrowse_1098': '1098',
            'txbrowse_1096': '1096',
            'txbrowse_1151': '1151',
            'txbrowse_1149': '1149',
            'txbrowse_1148': '1148',
            'txbrowse_1182': '1182',
            'txbrowse_1010': '1010',
            'txbrowse_1056': '1056',
            'txbrowse_1058': '1058',
            'txbrowse_1061': '1061',
            'txbrowse_6979': '6979',
            'txbrowse_1085': '1085',
            'txbrowse_9181': '9181',
            'txbrowse_9177': '9177',
            'txbrowse_7912': '7912',
            'txbrowse_7913': '7913',
            'txbrowse_8243': '8243',
            'txbrowse_13876': '13876',
            'txbrowse_13732': '13732',
            'txbrowse_13729': '13729',
            'txbrowse_13871': '13871',
            'timezone': '8',
            }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0',
            'Accept': '*/*',
            'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://www.korea.com',
            'Connection': 'keep-alive',
            'Referer': 'https://www.korea.com/?login',
            'TE': 'Trailers',
            }
        self.cc = OpenCC('s2twp')  #cc = opencc.Converter(from_variant='cn', to_variant='twp')    
        self.timeFreeze = datetime.now()
        self.timeFreezeNow = self.timeFreeze.strftime('%Y%m%d')
        self.timeYesterday = (self.timeFreeze - timedelta(days=1)).strftime('%Y%m%d')
        self.lastSequencedCaster = 'sequenceCaster_%s.pickle' % self.timeYesterday
        self.sequenceCasterPickle = 'sequenceCaster_%s.pickle' % self.timeFreezeNow
        self.sequenceCasterJson = 'sequenceCaster_%s.json' % self.timeFreezeNow
        self.sequenceCasterUfPickle = 'sequenceCaster_%s_unfinished.pickle' % self.timeFreezeNow       
        self.accumulatedCasterPickle = 'accumulatedCaster_%s.pickle' % self.timeFreezeNow
        self.accumulatedCasterJson = 'accumulatedCaster_%s.json' % self.timeFreezeNow       
        self.params = None
        self.session = None  
    # ------ 取得 getLoginCredential 登入網站並取得 Session -------------------------- 
    def getLoginSession(self):
        def getLoginCredential():       
            credentialAccessPickle = '%s/%s/%s' % (self.userbaseDir, '.korea', 'credentialAccess.pickle')
            try:
                with open(credentialAccessPickle, 'rb') as f:
                    self.params = pickle.load(f)
            except Exception as e:
                logging.error('=== 讀取網站帳號密碼檔錯誤, 失敗原因: %s ===' % str(e))
        # ------ 定義登入圖影像網站函式 --------------------------          
        with requests.Session() as session:  
            login_url = 'https://www.korea.com/zb_users/plugin/tx_reg/login.php'
            getLoginCredential()
            if self.params:
                responsedLogin = session.post(login_url, data=self.params, headers=self.headers, cookies=self.cookies)
                responsedSoupLogin = BeautifulSoup(responsedLogin.text, 'html.parser')
                responsedSoupLoginzh = self.cc.convert(str(responsedSoupLogin))
                logging.debug(responsedSoupLoginzh)        
                if '賬號登入成功' in responsedSoupLoginzh:
                    logging.info('=== 賬號登入成功! ===')                    
                    return session
        logging.error('=== 賬號登入失敗! ===')
        return None
    # ------ 試圖讀取當天的結果資料檔 --------------------------    
    def getJustSequencedCaster(self):
        # ------ 定義起始序號及結束序號 --------------------------                
        def getStartAndStopNumbers():
            self.givenNo2Start = 0
            for i, j in enumerate(self.sequenceCaster):
                if not j['casterZip']:
                    # ------ 將找到的筆數號碼存入 givenNo2Stop 筆數, 往前固定 100 筆則為 givenNo2Start --------------------------
                    self.givenNo2Start = i - 100
                    self.givenNo2Stop = i 
                    break
        # ------ 讀取當天的結果資料檔 --------------------------                      
        self.sequenceCaster = None
        try:
            with open('%s/%s/%s' % (self.userbaseDir, self.storageData, self.sequenceCasterPickle), 'rb') as f:
                self.sequenceCaster = pickle.load(f)
        except Exception as e:
            logging.error('=== 讀取當天資料檔錯誤, 失敗原因: %s ===' % str(e))
            return False
        else:
            if self.sequenceCaster:  
                getStartAndStopNumbers()
                return True
            else:
                return False                   
    # ------ 試圖讀取前一天的結果資料檔 -------------------------- 
    def getLastSequencedCaster(self):
        # ------ 定義起始序號及結束序號 --------------------------
        def getStartAndStopNumbers():
            self.givenNo2Start = 0
            for i, j in enumerate(self.sequenceCaster):
                if not j['casterZip']:
                    # ------ 將找到的筆數號碼存入 givenNo2Start 筆數, 固定一天從 givenNo2Start 之後抓 100 筆的限制為 givenNo2Stop --------------------------
                    self.givenNo2Start = i
                    self.givenNo2Stop = i + 100
                    break
            logging.info('===[ 起始序號: %d, 結束序號: %d ]===' % (self.givenNo2Start, self.givenNo2Stop))         
        # ------ 讀取前一天的結果資料檔 --------------------------
        self.sequenceCaster = None
        try:
            with open('%s/%s/%s' % (self.userbaseDir, self.storageData, self.lastSequencedCaster), 'rb') as f:
                self.sequenceCaster = pickle.load(f) 
        except Exception as e:
            logging.error('=== 讀取前一天資料檔錯誤, 失敗原因: %s ===' % str(e))
            return False
        else:
            if self.sequenceCaster:    
                getStartAndStopNumbers()
                return True
            else:
                return False                 
    # ------ 定義擷取畫面上共18個圖影像並回傳結果函式 -------------------------- 
    def getPageItems(self, currentUrl):               
        responsedPage = self.session.get(currentUrl, headers=self.headers)
        responsedSoupPage = BeautifulSoup(responsedPage.text, 'html.parser')               
        pagebarItems = responsedSoupPage.select('.pagebar')
        barItems = pagebarItems[0].find_all('a')               
        lastestUrl = barItems[-1]['href']
        nextUrl = barItems[-2]['href']
        pageCounters = (self.casterIndexer//18) - (self.givenNo2Start)//18            
        logging.info('===[ 進行中的頁面: 第 %d 頁，網址: %s ]===' % (pageCounters, currentUrl))
        logging.debug('=== 下頁的頁面[%s] ===' % nextUrl)
        logging.debug('=== 最後的頁面[%s]===' % lastestUrl)                
        pageItems = responsedSoupPage.select('.col-25')
        return pageItems             
    # ------ 開始抓取資料 從 givenNo2Start 之後的固定一天為 100 筆限制 --------------------------
    def startCrawlerProcess(self):
        accumulateCounter = 0
        lastUrl = None
        notMatched = None
        for self.casterIndexer in range(self.givenNo2Start, self.givenNo2Stop):            
            forwardPages = self.casterIndexer // 18
            forwardItem = self.casterIndexer % 18
            logging.debug('===[ 擷取序號第: %d 號，跳過頁數: %d，跳過項目: %d ]===' % (self.casterIndexer, forwardPages, forwardItem))            
            currentUrl = '%s/%s_%s.html' % (self.appScheme, 'category-1', str(forwardPages + 1))
            if currentUrl != lastUrl:
                if lastUrl == None :
                    lastUrl = currentUrl
                else:
                    logging.info('===[ 此序號: %d 需跳轉頁面，試圖換頁中 ]===' % self.casterIndexer)
                pageItems = self.getPageItems(currentUrl)
                lastUrl = currentUrl
            i = pageItems[forwardItem]
            casterNameh3 = self.cc.convert(i.h3.text)
            casterNames, casterName, theCaster = None, None, None
            if '未閱讀' in casterNameh3 or '朕已閱' in casterNameh3:
                casterNames = casterNameh3.split(' ')
                if len(casterNames) > 1:
                    casterName = casterNames[1]
                else:
                    casterName = casterNameh3.strip()
            else:
                casterName = casterNameh3.strip()
            for j in range(len(casterName)):
                if casterName[j].isdigit():
                    theCaster = casterName[:j]
                    break
            if theCaster:
                pageUrl = i.a['href']
                responsedCasterPage = self.session.get(pageUrl, headers=self.headers)
                responsedCasterSoup = BeautifulSoup(responsedCasterPage.text, 'html.parser')  
                # ------ 抓取 casterThumbnail 的資料            
                casterItems_thumb = responsedCasterSoup.select('.img-box')
                casterThumbnail = casterItems_thumb[0].img['src']
                # ------ 抓取 casterThumbname 的資料
                casterThumbname = casterItems_thumb[0].img['alt']
                # ------ 抓取 casterUrl 的資料
                casterItems_url = responsedCasterSoup.select('.list-click')                
                casterUrl = casterItems_url[0].a['href']
                # ------ 抓取 casterImg 的資料
                casterItems_img = responsedCasterSoup.select('.pd15')
                # ------ 驗證是否已超過當天可下載的個數
                verifyForward = self.cc.convert(casterItems_img[0].span.text)
                # ------ 超過時會出現:今天已超出限制 ------
                if '今天已超出限制' in verifyForward:
                    logging.warning('Maximum item exceed: %s' % verifyForward)
                    break              
                else:     
                    casterImg = casterItems_img[0].p.img['src']
                # ------ 抓取 casterZip 的資料                
                casterItems_tab = responsedCasterSoup.select('.tab-bd')
                casterZip = ''
                if casterItems_tab:
                    casterZip = casterItems_tab[0].a['href']
                    if casterZip == '/2.html':
                        casterZip = ''
                # ------ 驗證當天抓取的資料和資料檔的資料是否符合 --------------------------                
                if self.sequenceCaster[self.casterIndexer]['casterZip'] == '':
                    if self.sequenceCaster[self.casterIndexer]['code'] == self.casterIndexer:
                        if self.sequenceCaster[self.casterIndexer]['referer'] == pageUrl:
                            if self.sequenceCaster[self.casterIndexer]['casterUrl'] == casterUrl:
                                if self.sequenceCaster[self.casterIndexer]['thumbnail'] == casterThumbnail:
                                    if self.sequenceCaster[self.casterIndexer]['name'] == casterThumbname:
                                        if self.sequenceCaster[self.casterIndexer]['casterImg'] == casterImg:
                                            if self.sequenceCaster[self.casterIndexer]['caster'] == theCaster:
                                                self.sequenceCaster[self.casterIndexer]['casterZip'] = casterZip
                                                # ------ 將當天抓取的資料 casterMatadata 每一筆儲存在 accumulatedCasterJson 檔案 --------------------------
                                                casterMatadata = {
                                                    'code':  self.casterIndexer,
                                                    'referer' : pageUrl,
                                                    'casterUrl' : casterUrl,
                                                    'thumbnail' : casterThumbnail,
                                                    'name' : casterThumbname,
                                                    'casterImg' : casterImg,
                                                    'casterZip' : casterZip,
                                                    'caster': theCaster }                                        
                                                self.accumulatedCaster.append(casterMatadata)
                                                accumulateCounter += 1
                                                logging.info('=== 第[%d]篇_序號[%d]_名稱[%s|%s]_擷取網址[%s] ===' % (accumulateCounter, self.casterIndexer, theCaster, self.cc.convert(casterThumbname), casterZip))
                                                with open('%s/%s/%s' % (self.userbaseDir, self.storageData, self.accumulatedCasterJson), 'a', encoding='utf-8') as f:
                                                    json.dump(casterMatadata, f, ensure_ascii=False, indent=2)
                                                    if (self.casterIndexer != (self.givenNo2Stop-1)):
                                                        f.write(',')
                                                sleep(1)
                                                continue
                                            else:
                                                notMatched = 'caster'
                                        else:
                                            notMatched = 'casterImg'
                                    else:
                                        notMatched = 'casterThumbname'
                                else:
                                    notMatched = 'casterThumbnail'
                            else:
                                notMatched = 'casterUrl'
                        else:
                            notMatched = 'referer'
                    else:
                        notMatched = 'code'
                else:
                    notMatched = 'casterZip'
                # ------ 如果驗證當天抓取的資料和資料檔的資料有任一項不符合 --------------------------
                if notMatched == None:
                    logging.warning('=== [%d] 驗證當天抓取的資料和資料檔的資料時發現有資料項不符合! 但資料項 [notMatched] 未填入! ===' % self.casterIndexer)                
                else:
                    logging.error('=== [%d] 驗證當天抓取的資料和資料檔的資料時發現 [%s] 項不符合! ===' % (self.casterIndexer, notMatched))
                    logging.error('=== [錯誤的資料為] %s: %s ===' % (notMatched, self.sequenceCaster[self.casterIndexer][notMatched]))
                    self.finilizeAccumulatedCasterJson()
                    self.dumpSequencedCasterUnfihishedPickle()
                return False
        self.dumpSequencedCasterPickle()
        self.dumpSequencedCasterJson()
        self.dumpAccumulatedCasterPickle()
        self.finilizeAccumulatedCasterJson()          
        return True    
    # ------ 啟始今天的 accumulatedCasterJson 檔案 --------------------------
    def initAccumulatedCasterJson(self):
        nameIndex = 0
        accumulatedCasterJson = self.accumulatedCasterJson
        if os.path.exists(accumulatedCasterJson) and os.path.isfile(accumulatedCasterJson):
            while os.path.exists(accumulatedCasterJson) and os.path.isfile(accumulatedCasterJson):
                nameIndex += 1
                accumulatedCasterJson = '%s_%d.json' % (self.accumulatedCasterJson.rstrip('.json'), nameIndex)
            shutil.move(self.accumulatedCasterJson, accumulatedCasterJson)
        with open('%s/%s/%s' % (self.userbaseDir, self.storageData, self.accumulatedCasterJson), 'w', encoding='utf-8') as f:
            f.write('[ ')
    # ------ 如果今天意外的中斷要從 accumulatedCasterJson 檔案回復資料 --------------------------
    def recoverfromAccumulatedCasterJson(self):
        # ------ 定義起始序號及結束序號 --------------------------        
        def getStartAndStopNumbers():
            # ------ 找到意外中斷的位置 --------------------------
            self.givenNo2Start = 0
            countCrawleredCaster = len(self.accumulatedCaster)
            for i, j in enumerate(self.sequenceCaster):
                if j['casterZip']:
                    continue
                else:
                    self.givenNo2Start = i
                    self.givenNo2Stop = self.givenNo2Start + countCrawleredCaster 
                    break            
            logging.info('=== 已蒐集的項目數[%d]_起始序號[%d]_預計結束序號[%d] ===' % (countCrawleredCaster, self.givenNo2Start, self.givenNo2Stop))
        def openaccumulatedCasterJson1():
            try:
                with open(accumulatedCasterJson, 'r', encoding='utf-8') as f:
                    self.accumulatedCaster = json.load(f)
            except Exception as e:
                logging.warning('=== 開啟 %s 檔案錯誤! 錯誤訊息: [%s] ===' % (accumulatedCasterJson, str(e)))
                self.accumulatedCaster = None
        def openaccumulatedCasterJson2():
            try:
                with open(accumulatedCasterJson, 'r', encoding='utf-8') as f:
                    readAsText = f.read()
                    convert2Dict = ast.literal_eval(readAsText)
                    self.accumulatedCaster = json.dumps(convert2Dict, ensure_ascii=False)
            except Exception as e:
                logging.warning('=== 使用方法2開啟 %s 檔案錯誤! 錯誤訊息: [%s] ===' % (accumulatedCasterJson, str(e)))
                self.accumulatedCaster = None            
        accumulatedCasterJson = '%s/%s/%s' % (self.userbaseDir, self.storageData, self.accumulatedCasterJson)
        if os.path.isfile(accumulatedCasterJson):
            openaccumulatedCasterJson1()
            if self.accumulatedCaster:
                getStartAndStopNumbers()
                flagValidation = False 
                accumulateCounter = 0                
                for self.casterIndexer in range(self.givenNo2Start, self.givenNo2Stop):
                    if self.sequenceCaster[self.casterIndexer]['code'] ==  self.accumulatedCaster[accumulateCounter]['code'] :
                        if not self.sequenceCaster[self.casterIndexer]['casterZip']:
                            self.sequenceCaster[self.casterIndexer]['casterZip'] = self.accumulatedCaster[accumulateCounter]['casterZip']
                            accumulateCounter += 1
                        else:
                            logging.warning('=== 驗證時發現序號[%d]_索引[%d]_的內容[%s]已包含值 ===' % (self.casterIndexer, accumulateCounter, self.sequenceCaster[self.casterIndexer]['casterZip']))
                            flagValidation = True
                            break                            
                    else:
                        logging.warning('=== 驗證時發現序號[%d]_索引[%d]_的內容[%d]和預期不同 ===' % (self.casterIndexer, accumulateCounter, self.sequenceCaster[self.casterIndexer]['code']))
                        flagValidation = True
                        break
                if accumulateCounter:
                    logging.info('=== 復原的項目數量[%d]_最後索引號[%d] ===' % (accumulateCounter, self.casterIndexer))
                    self.givenNo2Start = self.givenNo2Start + accumulateCounter
                    self.givenNo2Stop = self.givenNo2Start + 100 # 本來想 (100 - accumulateCounter) 但應該中間會自動停下
                    return True
                if flagValidation:
                    logging.error('=== 嘗試復原資料時發生驗證錯誤:[%d] ===' % self.casterIndexer)
                    return False
                else:
                    return True
            else:
                return False
        else:
            return False
    # ------ 把當天的結果寫入 json 的 dump 檔案 --------------------------            
    def finilizeAccumulatedCasterJson(self):
        with open('%s/%s/%s' % (self.userbaseDir, self.storageData, self.accumulatedCasterJson), 'a', encoding='utf-8') as f:            
            f.write(']')           
    # ------ 把加總的結果寫入 pickle 的 dump 檔案 --------------------------
    def dumpSequencedCasterPickle(self):
         with open('%s/%s/%s' % (self.userbaseDir, self.storageData, self.sequenceCasterPickle), 'wb') as f:
            pickle.dump(self.sequenceCaster, f)         
    # ------ 把加總的結果寫入 pickle 的 dump 檔案 --------------------------
    def dumpSequencedCasterUnfihishedPickle(self):
        with open('%s/%s/%s' % (self.userbaseDir, self.storageData, self.sequenceCasterUfPickle), 'wb') as f:
            pickle.dump(self.sequenceCaster, f)            
    # ------ 把加總的結果寫入 json 的 dump 檔案 --------------------------    
    def dumpSequencedCasterJson(self):
        with open('%s/%s/%s' % (self.userbaseDir, self.storageData, self.sequenceCasterJson), 'w', encoding='utf-8') as f:
            json.dump(self.sequenceCaster, f, ensure_ascii=False, indent=2)
    # ------ 把當天的結果寫入 pickle 的 dump 檔案 --------------------------
    def dumpAccumulatedCasterPickle(self):        
        with open('%s/%s/%s' % (self.userbaseDir, self.storageData, self.accumulatedCasterPickle), 'wb') as f:
            pickle.dump(self.accumulatedCaster, f)      
    # ------ 開始執行 --------------------------  
    def downloadProcess(self, ds214se):
        accumulateCounter = 0               
        for self.casterIndexer in range(self.givenNo2Start, self.givenNo2Stop):
            task = self.sequenceCaster[self.casterIndexer]            
            logging.info('=== 目前擷取第[%d]個_序號[%d] ===' % (accumulateCounter+1, self.casterIndexer))
            accumulateCounter += 1 
            # ------ 主播上層主資料夾 --------------------------       
            folder = 'ig_%s' % task['caster']  
            ds_folder = '%s/%s' % (self.storageDownload, folder)                
            os_folder = '%s/%s/%s' % (self.userbaseDir, self.storageDownload, folder)
            logging.debug('=== 檢查 ds folder 為 [%s] ===' % ds_folder)
            logging.debug('=== 檢查 os folder 為 [%s] ===' % os_folder)            
            if os.path.isdir(os_folder):  # ------ 資料夾已存在
                logging.debug('=== 資料夾 [%s] 已存在 ===' % ds_folder)
                ds214se.folder = ds_folder  
            else:  # ------ 資料夾不存在
                if ds214se.createFolder(ds_folder):
                    logging.debug('=== 建立資料夾 [%s] 成功 ===' % ds214se.folder)
                else:
                    logging.error('=== 建立資料夾 [%s] 失敗 ===' % ds214se.folder)
                    return False
            logging.info('=== 上層主資料夾位置: [%s] ===' % ds214se.folder)
            # ------ 找出主播序號 -----------------------------   
            for i in range(len(task['name'])-1, -1, -1):
                if not task['name'][i].isdigit():
                    folderNumberstr = task['name'][i+1:]
                    break
            # ------ 主播下層主資料夾為名字和序號做尾碼 -----------------------------  
            subFolder = '%s%s' % (task['caster'], folderNumberstr)
            ds_subFolder = '%s/%s' % (ds_folder, subFolder)
            os_subFolder = '%s/%s/%s/%s' % (self.userbaseDir, self.storageDownload, ds_folder, subFolder)
            if os.path.isdir(os_subFolder):  # ------ 資料夾已存在
                logging.debug('=== 資料夾 [%s] 已存在 ===' % ds_subFolder)
                ds214se.folder = ds_subFolder
            else:  # ------ 資料夾不存在
                if ds214se.createFolder(ds_subFolder):
                    logging.debug('=== [%s] 建立子資料夾 [%s] 成功 ===' % (task['name'], ds214se.folder))
                else:
                    logging.error('=== [%s] 建立子資料夾 [%s] 失敗 ===' % (task['name'], ds214se.folder))
                    return False
            logging.info('=== 下層子資料夾位置: [%s] ===' % ds214se.folder)   
            # ------ 主播_影像檔 -----------------------------
            casterZip = task['casterZip'].split('/')[-1].lower()
            if folderNumberstr != casterZip.rstrip('.zip'):
                logging.error('=== 錯誤 [%s] 資料夾名稱和號碼 [%s] 對應不起來 ===' % (task['name'], subFolder))
                return False
            if os.path.isfile('%s/%s' % (os_subFolder, casterZip)):  # ------ 檔案已存在
                logging.debug('=== 此 [%s] 影像檔 [%s] 已下載過 ===' % (task['name'], casterZip))
            else:  # ------ 檔案不存在
                if not urllib.parse.urlparse(task['casterZip']).scheme:
                    task['casterZip'] = self.appScheme + task['casterZip']                    
                if ds214se.createTask(task['casterZip'].replace(' ', r'%20')):
                    logging.info('=== 建立下載 [%s] 影像檔 [%s] 成功 ===' % (task['name'], task['casterZip']))           
                else:
                    logging.error('=== 建立下載 [%s] 影像檔 [%s] 失敗 ===' % (task['name'], task['casterZip']))
                    return False
            # ------ 主播_頭像檔 -----------------------------
            thumbnail = task['thumbnail'].split('/')[-1].lower()
            if os.path.isfile('%s/%s' % (os_subFolder, thumbnail)):
                logging.info('=== 此 [%s] 頭像檔 [%s] 已下載過 ===' % (task['name'], task['thumbnail']))
            else:
                if not urllib.parse.urlparse(task['thumbnail']).scheme:
                    task['thumbnail'] = self.appScheme + task['thumbnail']                               
                if ds214se.createTask(task['thumbnail'].replace(' ', r'%20')):
                    logging.info('=== 建立下載 [%s] 頭像檔 [%s] 成功 ===' % (task['name'], task['thumbnail']))
                else:
                    logging.error('=== 建立下載 [%s] 頭像檔 [%s] 失敗 ===' % (task['name'], task['thumbnail']))
                    return False
            # ------ 主播_圖像檔 -----------------------------
            casterImg = task['casterImg'].split('/')[-1].lower()
            if os.path.isfile('%s/%s' % (os_subFolder, casterImg)):
                logging.info('=== 此 [%s] 圖像檔 [%s] 已下載過 ===' % (task['name'], task['casterImg']))
            else:
                if not urllib.parse.urlparse(task['casterImg']).scheme:
                    task['casterImg'] = self.appScheme + task['casterImg']                
                if ds214se.createTask(task['casterImg'].replace(' ', r'%20')):
                    logging.info('=== 建立下載 [%s] 圖像檔 [%s] 成功 ===' % (task['name'], task['casterImg']))
                else:
                    logging.error('=== 建立下載 [%s] 圖像檔 [%s] 失敗 ===' % (task['name'], task['casterImg']))            
                    return False    
        return True
