## synology.nas.python
**Synology DiskStation (NAS) API function implementations by python**

- [x] --- 繁體中文版 ---
 
    * 所有的程式是設計跑在 Synology NAS 的控制台裡的自訂排程。新增自訂排程後，選定時間，然後放入自訂的 .sh 檔案，讓程式自動依時間由 NAS 執行。
    * 目前有三個主程式。一個為 dailyCrawler.py，一個為 dailyHousekeeping.py，最後一個為 dailyMaintainance.py。
    * 同時也運用了 Line Notify 的 module 模組 myNASlinefuncs.py 來做為通知用。
    1. dailyCrawler.py 
        * 主要是用來爬資料和下載資料。從主程式的說明應該很容易理解。runDailyCrawler.sh 是對應的排程自訂程式
        * 程式中匯入了多個不同的 module 模組，主要的兩個 module 模組為 myNASkoreafuncs.py 及 myNASbeautyfuncs.py。
    2. dailyHousekeeping.py 
        * 主要是用來定期清理已完成的下載清單。程式很短也應該很容易理解。runDailyHousekeeping.sh 是對應的排程自訂程式
    3. dailyMaintainance.py 
        *  主要是用來計算目前可用的儲存空間的容量。程式很短也應該很容易理解。runDailyMaintainance.sh 是對應的排程自訂程式
    * 
    * 上述的程式可能會呼叫另一個 myNASsynofuncs.py 模組的功能。這個模組是為提供使用 Synology DiskStation (NAS) 的使用者一個
    * 由 Python 程式語言透過 Synology 官方提供的應用程式界面 (API) 來自動在 Synology DiskStation (NAS) 上完成新增資料夾、
    * 下載檔案等作業。其中主要有兩個功能:
    * (1) FileStation: 檔案資料夾的新增 (create) 作業 
    * (2) DownloadStation: 網站資料的下載 (create) 作業以及其他如:
    *     1.新增(Create)下載
    *     2.修改(Edit)
    *     3.列出(List)
    *     4.刪除(Delete)
    *     5.資訊(GetInfo)
    *     6.暫停(Pause)
    *     7.繼續(Resume)
    *     8.移除(remove)
    *     9.篩選(filter)

    ![程式示例](https://github.com/spectreConstantine/synology.nas.python/blob/master/2020-05-02_032250.png)

- [x] --- 執行環境需求 ---

    * 此程式需有一個自己客製的文字檔名稱為 nasconfig 的設定檔, 放在 ~/.nas/ 目錄下, 包含帳號密碼  
    * 使用 Line Module 要有一個 token file, 放在 ~/.line/ 目錄下, 包含 line token
    * 使用 Korea Module 要有一個 帳號密碼 檔案, 放在 ~/.korea/ 目錄下, 包含帳號密碼的 pickle
    * 在 ~/.log/ 目錄用來放所有的記錄檔
    * 在 ~/.scheduler/ 目錄用來放所抓的資料, 每個 module 有一個子資料夾對應 module 的 .name
    * Synology 的 NAS 要安裝 Python3 的套件和 Download Station 的套件。目前的 Python 版本是 3.5, 請參考 Synology 的說明.
    * 也能跑在 Windows 下。則上述 ~ 就自動對應到 %userprofile% 目錄。我用的版本版為 Python 3.7.7, 其他版本沒實測過.
