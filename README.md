## synology.nas.python
### Synology DiskStation (NAS) 的 Python 應用
 
 所有的程式是設計跑在 Synology NAS 的控制台裡的自訂排程。新增自訂排程後，選定時間，然後放入自訂的 .sh 檔案，讓程式自動依時間由 NAS 執行。
 
#### 目前有二個主程式
主要程式為 `dailyCrawlerCleansing.py`，另一個比較小為 `dailyHousekeeping.py`。

##### 1.`dailyCrawlerCleansing.py` 
> 主要是用來爬資料和下載資料。從主程式的說明應該很容易理解。runDailyCrawler.sh 是對應的排程自訂程式 
> 程式中匯入了多個不同的 module 模組，分別說明如下:
>1. `myNASlinefuncs.py` 
>     同時運用了 Line Notify 和 Python 的 Logging 來做為記錄與通知 module 模組用
>2. `myNASkoreafuncs.py`
>     用來下載 korea 網址的資料
>3. `myNASbeautyfuncs.py` 
>     用來下載 ptt 表特板 Beauty 的資料
>4. `myNAScleanfuncs.py`
>     主要用來定期清理特定旳資料夾下超過21天的資料並計算剩餘可用的儲存空間容量。
>5. `myNASsynofuncs.py` 用來下載資料
>     這個 myNASsynofuncs.py 模組的功能是為提供使用 Synology DiskStation (NAS) 的使用者一個由 Python 程式 語言
>     透過 Synology 官方提供的應用程式界面 (API) 來自動在 Synology DiskStation (NAS) 上完成新增資料夾、 下載檔案等作業。    
>6. 其中主要有三個功能:
1. Storage: 提供 NAS 系統儲存空間的 (load_info)/(get_usage) 作業
>-  主要用來取得目前可用的空間及空間使用率
2. FileStation: 檔案資料夾的新增 (create) 作業
>-  主要用來新增資料夾
3. DownloadStation: 網站資料的下載作業等包含:
>-  1.新增(Create)
>-  2.修改(Edit)
>-  3.列出(List)
>-  4.刪除(Delete)
>-  5.資訊(GetInfo)
>-  6.暫停(Pause)
>-  7.繼續(Resume)
>-  8.移除(remove)
>-  9.篩選(filter)

##### 2. `dailyHousekeeping.py`
  > 主要是用來定期清理已完成的下載清單。程式很短也應該很容易理解。runDailyHousekeeping.sh 是對應的排程自訂程式

#### 畫面示例
`爬蟲與下載`
![程式示例](https://github.com/spectreConstantine/synology.nas.python/blob/master/2020-06-16_234131.png)

`checkNASdownload.py`
![程式示例](https://github.com/spectreConstantine/synology.nas.python/blob/master/2020-06-18_131617.png)

`檢查空間並移除舊的檔案`
![程式示例](https://github.com/spectreConstantine/synology.nas.python/blob/master/2020-06-18_141805.png)

#### 執行環境需求 

>- 此程式需有一個自己客製的文字檔名稱為 nasconfig 的設定檔, 放在 ~/.nas/ 目錄下, 包含帳號密碼  
>- 使用 Line Module 要有一個 token file, 放在 ~/.line/ 目錄下, 包含 line token
>- 使用 Korea Module 要有一個`帳號密碼`檔案, 放在 ~/.korea/ 目錄下, 包含帳號密碼的 pickle
>- 在 ~/.log/ 目錄用來放所有的記錄檔
>- 在 ~/.scheduler/ 目錄用來放所抓的資料, 每個 module 有一個子資料夾對應 module 的 .name
>- Synology 的 NAS 要安裝 Python3 的套件和 Download Station 的套件。目前的 Python 版本是 3.5, 請參考 Synology 的說明.
>- 也能跑在 Windows 下。則上述 ~ 在 Windows 就會自動對應到 %userprofile% 目錄。我用的版本版為 Python 3.7.7, 其他版本沒實測過.

#### 執行流程控制設定檔

>- 由於程式執行過程難免因各種原因中斷，如程式錯誤，網路斷線，網站意外關機等。因此程式改用`dailyCrawlClean.config`的檔案來控制哪一段程式需不需要執行。
>- 這樣可以只修改設定檔而避免因修改更改程式導致其他未知的問題，同時可以保留多個不同的設定檔案以因應不同的狀況。
>- 以下是預設值。尾碼為 Just 的兩項只用在資料已抓取完畢時使用。所以除兩項為0外其餘為1表示會執行。請參考程式以瞭解詳細流程。
```
 { 
   "myKoreaCrawler": 1, 
   "myKoreaCrawlerSession": 1, 
   "myKoreaCrawlerGetJust": 0,
   "myKoreaCrawlerGetLast": 1, 
   "myKoreaCrawlerRecovery": 1,
   "myKoreaCrawlerInitialize": 1,
   "myKoreaCrawlerStartStop": 1,
   "myKoreaCrawlerStartCrawl": 1,  
   "pttBeautyCrawler": 1, 
   "pttBeautyCrawlerGetJust": 0,
   "pttBeautyCrawlerInitialize": 1,
   "pttBeautyCrawlerStartCrawl": 1,      
   "ds214se": 1, 
   "ds214seDownloaMyKorea": 1, 
   "ds214seDownloaPttBeauty": 1,
   "ds214seWebcamDataCleanup": 1,
   "ds214seUsageStastistics": 1
 }        
```

#### 撰寫心得

>- 這整套程式雖然只是運用 Python 下載一些資料，從第一個版本由網站上下載 (感謝 scku深紅/scku208@gmail.com) 的原始碼，從中學習瞭解別人的程式 )，
>- 到自己研究如何運用 Synology 的 WebAPI，到優化整個模組間的相互運作，到完全能自己掌握程式的風格、調性、模組間的協同合作、類別的建立與使用，
>- 程式除錯等等，實值上算是我在學習 Python 過程中一個練習。中間反覆改了大概有20幾個版本，每天都在嘗試做不同的優化。是個很累但很有收獲的過程。
>- 另一個值得參考的套件也提供大家參考 <https://github.com/N4S4/synology-api>。雖然他的套件很完整，但我自己的已經寫完了，沒有再使用他的。
