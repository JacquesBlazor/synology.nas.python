# synology.nas.python
This simple tool was made to automate the folder creating and image/urls downloading for your synology NAS.
It referred to someone who's name is scku and posted on the web:
https://www.mobile01.com/topicdetail.php?f=494&t=5546291 

You can refer to the .png screenshot for reference. 
To use it, you have to create a 'account' file under your ~/.nas/ folder either on your Windows or NAS/Linux depends on where you'd prefer to run it. And then you need to replace the url variable for what you'd like to download. The folder where the file to be downloaded will be automatically generated by the time when you run it but you can change it. 

That's it. Have fun using it.

## synology.nas.python
**Synology DiskStation (NAS) API function implementations by python**

- [x] --- 繁體中文版 ---

    此程的功能為提供使用 Synology DiskStation (NAS) 的使用者一個由 Python 程式語言所實作
    出來的應用程式界面 (API), 讓你可以執行在你的個人電腦 Windows 10 上, 或直接執行在你自己
    的 Synology DiskStation (NAS) 上. 目前有實作了下列功能: 1.登入(Initialize&Login)
    2.新增(Create)下載, 3.修改(Edit), 4.列出(List), 5.刪除(Delete), 6.資訊(GetInfo),
    7.暫停(Pause), 8.繼續(Resume), 9.登出(Logout) 等. 還在持續修改中.
    
    實作裡也包含了能夠建立新的資料夾以便可以利用上述功能來將下載的工作存在新的資料夾裡.
    範例也展示了一個簡單的功能把目前下載的清單列出, 並依據下載的效率做出評比, 以利後續
    程式可以依據評比來自動調整新增進來的工作, 例如暫停目前下載效率不佳的工作一陣子, 讓
    其他工作可以下載, 以增進下載的整體效率. 

- [x] --- English Version ---

    The program is intended to provide users who are using Synology DiskStation (NAS)
    with a application programming interface (API) by using Python Language either 
    running on your own Windows 10 computer or running on the DS NAS itself. The 
    current implementation of the API includes the functionality of: 1. Initilization
    & Login. 2. CreateTask, 3. EditTask, 4. ListTask, 5. DeleteTask, 6. GetInfo.
    7. PauseTask, 8. ResumeTask, 9. Logout. etc. It will keep improving overtime.
    
    It also implements a function to allow users to create a new folder on the NAS
    for above downloadStation functions to work with.

    ![程式示例](https://github.com/spectreConstantine/synology.nas.python/blob/master/2020-05-02_032250.png)

- [x] --- 摘要說明 ---

    * 此程式需有一個自己客製的文字檔的設定檔, 放在 %userprofile%\.nas\ 目錄下, 包含帳號密碼

- [x] --- 執行環境需求 ---

    * 跑在 Windows 裡電腦裡要安裝 Python 3.7.7 (這是我用的版本, 其他版本也許可以跑但沒實測過).
    * 跑在 DS NAS 要安裝 Python 3.x (目前應該是 3.5, 請參考 Synology 的說明). 
