# --- The MIT License (MIT) Copyright (c) alvinconstantine(alvin.constantine@outlook.com), Sat Jun 20 00:10am 2020 ---
import stat
import os
import logging

# --- 移除唯讀資料夾 -----------------------------  
def remove_readonly(func, path):  # --- 定義回呼函數 ---
    os.chmod(path, stat.S_IWRITE)  # --- 刪除檔案的唯讀屬性 ---
    func(path)  # --- 再次呼叫剛剛失敗的函數 ---

# --- 刪除過期的資料 -----------------------------  
def del_dir(path, onerror=None):
    logging.debug('=== 檢查上層資料夾: %s ===' % path)
    for file in os.listdir(path):
        logging.debug('=== 檔案: %s ===' % file)
        file_or_dir = os.path.join(path, file)
        logging.debug('=== 檢查檔案或資料夾: %s ===' % file_or_dir)
        if os.path.isdir(file_or_dir) and not os.path.islink(file_or_dir):
            logging.debug('=== 進入資料夾再檢查: %s ===' % file_or_dir)
            del_dir(file_or_dir)  # --- 遞迴刪除子資料夾及其檔案 ---
        else:
            try:
                logging.debug('=== 正在嘗試刪除 %s ===' % file_or_dir)
                os.remove(file_or_dir)  # --- 嘗試刪除該檔 ---
            except:  #刪除失敗
                logging.debug('=== 刪除 %s 失敗 ===' % file_or_dir)
                if onerror and callable(onerror):
                    logging.debug('=== 呼叫回呼函數')
                    onerror(os.remove, file_or_dir)  # --- 自動呼叫回呼函數 ---
                else:
                    logging.error('刪除資料時發生未預期的錯誤')
                    return False
    try:
        logging.info('=== 移除 %s ===' % path)
        os.rmdir(path)  # --- 刪除資料夾 ---
    except Exception as e:
        logging.error('=== 移除資料夾 %s 時發生未預期的錯誤: %s ===' % (path, str(e)))
        return False
    else:
        return True

# --- 篩選要刪除的資料夾 ----------------------------- 
def webcamDataCleanUp():      
    removalTarget = '/volume1/homes/webcam'
    folderlistsinTarget = os.listdir(removalTarget)
    logging.debug('=== 檢查主資料夾 %s 清單: %s ===' % (removalTarget, folderlistsinTarget))
    additionalInfo = ''
    try:
        for i in folderlistsinTarget:
            logging.debug('=== 檢查上層資料夾: %s ===' % i)
            subfolder = os.path.join(removalTarget, i)
            logging.debug('=== 檢查下層資料夾: %s ===' % subfolder)
            getDirLists = os.listdir(subfolder)
            logging.debug('=== 檢查下層資料夾 %s 內的資料夾數量: %d ===' % (getDirLists, len(getDirLists)))
            if len(getDirLists) > 21:
                getDirLists.sort(reverse=True)
                folderCounts = len(getDirLists) - 21
                logging.debug('=== 有 %d 個資料夾需刪除 ===' % folderCounts)
                for j in range(folderCounts):
                    getPath = getDirLists.pop()
                    removalFolder = os.path.join(removalTarget, i, getPath)
                    logging.debug('=== 將被移除的資料夾為: %s ===' % removalFolder)
                    if del_dir(removalFolder, remove_readonly):  # --- 呼叫函數，並指定回呼函數 ---
                        logging.info('=== 已移除 %s 資料夾 ===' % removalFolder)
                    else:
                        logging.info('=== 執行移除資料夾作業未正確結束 ===')
                        return False
            else:
                additionalInfo = '沒有資料夾需要移除。'
    except Exception as e:
        logging.error('=== 刪除資料 %s 時發生未預期的錯誤: %s ===' % (removalTarget, str(e)))
        return False
    else:
        return '%s%s' % (additionalInfo, '清理作業完成')
