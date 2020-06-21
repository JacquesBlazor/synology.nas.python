# --- The MIT License (MIT) Copyright (c) alvinconstantine(alvin.constantine@outlook.com), Sat Jun 21 10:00am 2020 ---
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
import re

# ------ 定義 korea crawler 類別 -------------------------- 
class crawlerKorea():
    def __init__(self):
        # ------ 常變數設定 --------------------------
        self.name = 'korea'
        self.appScheme = 'https://www.korea.com'             
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
        self.timeFreeze = datetime.now()   
        self.timeFreezeNow = self.timeFreeze.strftime('%Y%m%d')
        self.timeYesterday = (self.timeFreeze - timedelta(days=1)).strftime('%Y%m%d')                     
        self.userbaseDir = os.path.expanduser('~')        
        self.storageData = '%s/%s/%s' % ('.scheduler', self.name, 'crawlerdata')
        self.storageDownload = '%s/%s/%s' % ('.scheduler', self.name, 'downloads')
        self.lastSequencedCaster = '%s/%s/sequenceCaster_%s.pickle' % (self.userbaseDir, self.storageData, self.timeYesterday)  
        self.sequenceCasterPickle = '%s/%s/sequenceCaster_%s.pickle' % (self.userbaseDir, self.storageData, self.timeFreezeNow)
        self.sequenceCasterJson = '%s/%s/sequenceCaster_%s.json' % (self.userbaseDir, self.storageData, self.timeFreezeNow)
        self.sequenceCasterUfPickle = '%s/%s/sequenceCaster_%s_unfinished.pickle' % (self.userbaseDir, self.storageData, self.timeFreezeNow)
        self.accumulatedCasterPickle = '%s/%s/accumulatedCaster_%s.pickle' % (self.userbaseDir, self.storageData, self.timeFreezeNow)
        self.accumulatedCasterJson = '%s/%s/accumulatedCaster_%s.json' % (self.userbaseDir, self.storageData, self.timeFreezeNow)
        self.cc = OpenCC('s2twp')  # opencc.Converter(from_variant='cn', to_variant='twp')
        self.accumulatedCaster = []
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
                logging.error('=== 讀取網站帳號密碼設定檔時發生錯誤。錯誤訊息: %s ===' % str(e))
        # ------ 定義登入圖影像網站函式 --------------------------          
        with requests.Session() as session:  
            login_url = 'https://www.korea.com/zb_users/plugin/tx_reg/login.php'
            getLoginCredential()  # 讀取網站帳號密碼設定檔
            if self.params:
                responsedLogin = session.post(login_url, data=self.params, headers=self.headers, cookies=self.cookies)
                responsedSoupLogin = BeautifulSoup(responsedLogin.text, 'html.parser')
                responsedSoupLoginzh = self.cc.convert(str(responsedSoupLogin))
                logging.debug('=== 使用帳號密碼自動登入網站時網站回應: %s ===' % responsedSoupLoginzh)
                if '登入成功' in responsedSoupLoginzh:
                    logging.info('=== 成功使用帳號密碼自動登入網站 ===')                    
                    return session
        logging.error('=== 使用帳號密碼登入失敗! ===')
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
            with open(self.sequenceCasterPickle, 'rb') as f:
                self.sequenceCaster = pickle.load(f)
        except Exception as e:
            logging.error('=== 讀取當天資料檔錯誤。錯誤訊息: %s ===' % str(e))
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
            logging.info('===[ 起始序號: %d，結束序號: %d ]===' % (self.givenNo2Start, self.givenNo2Stop))         
        # ------ 讀取前一天的結果資料檔 --------------------------
        self.sequenceCaster = None
        try:
            with open(self.lastSequencedCaster, 'rb') as f:
                self.sequenceCaster = pickle.load(f) 
        except Exception as e:
            logging.error('=== 讀取前一天資料檔錯誤。錯誤訊息: %s ===' % str(e))
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
        logging.info('===[ 進行中的頁面 | 第 %d 頁 | 網址 %s ]===' % (pageCounters, currentUrl))
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
                    logging.debug('===[ 此序號: %d 需跳轉頁面，試圖換頁中 ]===' % self.casterIndexer)
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
                # ------ 超過時會出現: ['親，你每天可以瀏覽下載100部作品，今天已超出限制，請明天再來哦^_^'] ------
                if '今天已超出限制' in verifyForward:
                    logging.warning('Maximum item exceed: %s' % verifyForward)
                    break              
                else:
                    if casterItems_img[0].p.text:      
                        casterImg = casterItems_img[0].p.img['src']
                    else:
                        casterImg = None
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
                                        if not casterImg or self.sequenceCaster[self.casterIndexer]['casterImg'] == casterImg:
                                            if self.sequenceCaster[self.casterIndexer]['caster'] == theCaster:
                                                self.sequenceCaster[self.casterIndexer]['casterZip'] = casterZip
                                                # ------ 將當天抓取的資料 casterMatadata 每一筆儲存在 accumulatedCasterJson 檔案 --------------------------
                                                casterMatadata = {
                                                    'code':  self.casterIndexer,
                                                    'referer' : pageUrl,
                                                    'casterUrl' : casterUrl,
                                                    'thumbnail' : casterThumbnail,
                                                    'name' : casterThumbname,
                                                    'casterImg' : casterImg if casterImg else '',
                                                    'casterZip' : casterZip,
                                                    'caster': theCaster }                                        
                                                self.accumulatedCaster.append(casterMatadata)
                                                accumulateCounter += 1
                                                logging.info('=== 第[%d]篇_序號[%d]_名稱[%s|%s]_擷取網址[%s] ===' % (accumulateCounter, self.casterIndexer, theCaster, self.cc.convert(casterThumbname), casterZip))
                                                with open(self.accumulatedCasterJson, 'a', encoding='utf-8') as f:
                                                    json.dump(casterMatadata, f, ensure_ascii=False, indent=2)
                                                    if (self.casterIndexer != (self.givenNo2Stop-1)):
                                                        f.write(',')
                                                    else:
                                                        f.write('\n]')
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
                    self.finalizeAccumulatedCasterJson()
                    self.dumpSequencedCasterUnfihishedPickle()
                return False
        self.dumpSequencedCasterPickle()
        self.dumpSequencedCasterJson()
        self.dumpAccumulatedCasterPickle()       
        return True    
    # ------ 啟始今天的 accumulatedCasterJson 檔案 --------------------------
    def initAccumulatedCasterJson(self):
        existingFile = False
        nameIndex = 0
        accumulatedCasterJson = self.accumulatedCasterJson
        if os.path.exists(accumulatedCasterJson) and os.path.isfile(accumulatedCasterJson):
            while os.path.exists(accumulatedCasterJson) and os.path.isfile(accumulatedCasterJson):
                nameIndex += 1
                accumulatedCasterJson = '%s_%d.json' % (self.accumulatedCasterJson.rstrip('.json'), nameIndex)
            try:
                shutil.move(self.accumulatedCasterJson, accumulatedCasterJson)
            except Exception as e:
                logging.error('=== 在更改資料檔 %s 為 %s 時失敗。錯誤訊息: %s ===' % (self.accumulatedCasterJson, accumulatedCasterJson, str(e)))
            else:    
                logging.info('=== 已將已存在的[%s]檔案更改名稱為[%s] ===' % (self.accumulatedCasterJson, accumulatedCasterJson))
                existingFile = True
        try:                
            with open(self.accumulatedCasterJson, 'w', encoding='utf-8') as f:
                f.write('[\n')
        except Exception as e:
            logging.error('=== 儲存當天資料檔 %s 錯誤。錯誤訊息: %s ===' % (self.accumulatedCasterJson, str(e)))
        else:            
            return existingFile
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
        def openAccumulatedCasterJson():
            self.accumulatedCaster = None
            try:
                with open(self.accumulatedCasterJson, 'r', encoding='utf-8') as f:
                    self.accumulatedCaster = json.load(f)
            except json.decoder.JSONDecodeError:
                try:
                    self.finalizeAccumulatedCasterJson()
                    with open(self.accumulatedCasterJson, 'r', encoding='utf-8') as f:
                        self.accumulatedCaster = json.load(f)
                except Exception as e:
                    logging.warning('=== 在開啟檔案 %s 時發生 [json.decoder.JSONDecodeError] 錯誤，但已試圖修復檔案。仍有下列錯誤發生: [%s] ===' % (self.accumulatedCasterJson, str(e)))
                else:
                    if self.accumulatedCaster:
                        return True
            except Exception as e:
                logging.warning('=== 試圖開啟 %s 檔案時發生未預期的錯誤。錯誤訊息: [%s] ===' % (self.accumulatedCasterJson, str(e)))
                return False
            else:
                if self.accumulatedCaster:
                    return True         
        if os.path.isfile(self.accumulatedCasterJson):
            if openAccumulatedCasterJson():
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
                    self.givenNo2Stop = self.givenNo2Start + (100 - accumulateCounter)
                    return True
                if flagValidation:
                    logging.error('=== 嘗試復原資料時發生驗證錯誤。參考的索引號: [%d] ===' % self.casterIndexer)
                    return False
                else:
                    logging.info('=== 復原的項目數量[%d]_最後索引號[%d] ===' % (accumulateCounter, self.casterIndexer))
                    return True
        else:
            logging.warning('=== 沒有可復原資料的檔案可以復原: [%s] ===' % self.accumulatedCasterJson)
            return False
    # ------ 把當天的結果寫入 json 的 dump 檔案 --------------------------            
    def finalizeAccumulatedCasterJson(self):
        try:
            with open(self.accumulatedCasterJson, 'r+b') as f:
                f.seek(-2, os.SEEK_END)
                removeComma = f.read()
                if removeComma == b'},':
                    repsquareBracket = removeComma.replace(b'},', b'}]')
                    f.seek(-2, os.SEEK_END)
                    f.write(repsquareBracket)
                else:
                    logging.warning('=== 沒有將 accumulatedCasterJson 正確結尾: %s ===' % removeComma)
        except Exception as e:
            logging.error('=== 儲存當天資料檔 %s 錯誤。錯誤訊息: %s ===' % (self.accumulatedCasterJson, str(e)))             
    # ------ 把加總的結果寫入 pickle 的 dump 檔案 --------------------------
    def dumpSequencedCasterPickle(self):
         with open(self.sequenceCasterPickle, 'wb') as f:
            pickle.dump(self.sequenceCaster, f)         
    # ------ 把加總的結果寫入 pickle 的 dump 檔案 --------------------------
    def dumpSequencedCasterUnfihishedPickle(self):
        with open(self.sequenceCasterUfPickle, 'wb') as f:
            pickle.dump(self.sequenceCaster, f)            
    # ------ 把加總的結果寫入 json 的 dump 檔案 --------------------------    
    def dumpSequencedCasterJson(self):
        with open(self.sequenceCasterJson, 'w', encoding='utf-8') as f:
            json.dump(self.sequenceCaster, f, ensure_ascii=False, indent=2)
    # ------ 把當天的結果寫入 pickle 的 dump 檔案 --------------------------
    def dumpAccumulatedCasterPickle(self):        
        with open(self.accumulatedCasterPickle, 'wb') as f:
            pickle.dump(self.accumulatedCaster, f)      
    # ------ 開始執行 --------------------------  
    def downloadProcess(self, diskStation, **kwargs):
        if kwargs and 'target' in kwargs:
            if 'start' in kwargs:
                self.start = kwargs['start']
            if 'stop' in kwargs:
                self.stop = kwargs['stop']
            try:
                target = '%s/%s/%s' % (self.userbaseDir, self.storageData, kwargs['target'])
                with open(target, 'rb') as f:
                        self.sequenceCaster = pickle.load(f)
            except Exception as e:
                logging.error('=== 讀取指定的下載檔案 %s 時發生錯誤。錯誤訊息: %s ===' % (target, str(e)))
                return False
        accumulateCounter = 0
        contentKeys = ('casterZip', 'casterImg', 'thumbnail')
        for self.casterIndexer in range(self.givenNo2Start, self.givenNo2Stop):
            accumulateCounter += 1            
            task = self.sequenceCaster[self.casterIndexer]
            caster = self.cc.convert(task['name'])        
            logging.debug('=== 第 %d 位 | 序號 %d ===' % (accumulateCounter, self.casterIndexer))
            # ------ 主播上層主資料夾 --------------------------
            folderExists = None        
            folder = 'ig_%s' % task['caster']  
            ds_folder = '%s/%s' % (self.storageDownload, folder)                
            logging.debug('=== 檢查資料夾為 [%s] ===' % ds_folder)
            diskStation.folder = ds_folder
            if os.path.isdir('%s/%s' % (self.userbaseDir, ds_folder)):  # ------ 資料夾已存在
                folderExists = True
                logging.debug('=== 資料夾 [%s] 已存在 ===' % ds_folder)                  
            else:  # ------ 資料夾不存在
                folderExists = False
                logging.debug('=== 資料夾 [%s] 不存在 ===' % ds_folder)
            logging.debug('===[ 上層資料夾位置 | %s/%s ]===' % (self.userbaseDir, diskStation.folder)) 
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
            if os.path.isdir('%s/%s' % (self.userbaseDir, ds_subFolder)):  # ------ 資料夾已存在
                subFolderExists = True
                logging.debug('=== 子資料夾 [%s] 已存在 ===' % ds_subFolder) 
            else:  # ------ 資料夾不存在
                subFolderExists = False
                logging.debug('=== 子資料夾 [%s] 不存在 ===' % ds_subFolder)
            logging.debug('===[ 子資料夾位置 | %s/%s ]===' % (self.userbaseDir, diskStation.folder))                                  
            # ------ 主播_檔案s -----------------------------
            logging.info('===[ 第 %d 位_%s | 序號 %d | 資料夾 %s/%s ]===' % (accumulateCounter, caster, self.casterIndexer, self.userbaseDir, ds_subFolder))             
            downloadUris = []
            for contentKey in contentKeys: 
                contentValue = os.path.basename(task[contentKey])
                if contentValue:
                    if os.path.isfile('%s/%s' % (ds_subFolder, contentValue)):  # ------ 檔案已存在
                        logging.debug('=== 此 [%s] %s [%s] 已下載過 ===' % (caster, contentKey, task[contentKey]))
                    else:  # ------ 檔案不存在
                        if not urllib.parse.urlparse(task[contentKey]).scheme:
                            task[contentKey] = self.appScheme + task[contentKey]
                        logging.info('=== 新增 [%s] 檔案 [%s] ===' % (contentKey, task[contentKey]))
                        downloadUris.append(task[contentKey].replace(' ', r'%20'))
                else:
                    logging.warning('=== 注意 | 第 [%d] 筆資料內容 [%s] 似乎有問題 ===' % (self.casterIndexer, contentKey))                       
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
                logging.debug('===[ 主播 %s | 共有 %s 個影像檔 | 嘗試建立下載清單 ]===' % (caster, len(downloadUris)))
                if diskStation.DownloadStation('create', data=downloadUris):
                    logging.info('===%s[ 已成功建立 %d 個影像檔到下載清單 ]%s===' % ('='*33, len(downloadUris), '='*6))
                else:
                    logging.error('===%s[ 建立 %d 個影像檔到下載清單時失敗 ]%s===' % ('='*33, len(downloadUris), '='*6))
                    return False
            else:
                logging.info('===%s[ 第 %d 位_%s | 序號 %d | 沒有檔案需要下載 ]%s===' % ('='*33, accumulateCounter, caster, self.casterIndexer, '='*6))
        return True
