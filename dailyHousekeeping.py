from datetime import datetime
import myNASsynofuncs as nas
import logging
import os

logging.basicConfig(filename='%s/.log/dailyHousekeeping%s.log' % (os.path.expanduser('~'), datetime.now().strftime('%Y%m%d_%H%M%S')), level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
# ------ 主程式 ------------------------------------------------------------------
if __name__ == '__main__':
    # ------ 啟始並登入 ----------------------------- 
    ds214se = nas.nasDiskStation()
    if ds214se.login:      
        logging.info('=== 登入 %s 成功! === ' % ds214se.name)
        logging.debug('=== 工作階段 (Session ID) 為 %s ===' % ds214se.sid)             
        # ------ 主要功能 -----------------------------     
        classifiedTasks = ds214se.catagorizedTask()
        if classifiedTasks['finished']:
            allFinished = [i['id'] for i in classifiedTasks['finished']]
            if ds214se.deleteTask(allFinished[:]):
                logging.info('=== 已成功完成 %d 項清理工作 ===' % len(allFinished))
        # ------ 登出 ----------------------------- 
        if not ds214se.logout():
            logging.error('=== 登出 %s 失敗! == '  % ds214se.name)
        else:
            logging.info('=== 已成功登出 %s! == ' % ds214se.name)  
    else:
        logging.error('=== 登入 %s 失敗! === ' % ds214se.name)