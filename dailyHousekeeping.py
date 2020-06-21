# --- The MIT License (MIT) Copyright (c) alvinconstantine(alvin.constantine@outlook.com), Sat Jun 20 00:10am 2020 ---
from datetime import datetime
import myNASsynofuncs as nas
import logging
import os
from pprint import pprint
logging.basicConfig(filename='%s/.scheduler/.log/.dailyHousekeeping/%s.log' % (os.path.expanduser('~'), datetime.now().strftime('%Y%m%d_%H%M%S')), level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
# ------ 主程式 ------------------------------------------------------------------
if __name__ == '__main__':
    # ------ 啟始並登入 ----------------------------- 
    ds214se = nas.nasDiskStation()
    if not ds214se.login:
        logging.error('=== 登入 %s 失敗! === ' % ds214se.name)
    else:                
        logging.info('=== 登入 %s 成功! === ' % ds214se.name)
        logging.debug('=== 工作階段 (Session ID) 為 %s ===' % ds214se.sid)             
        # ------ 主要功能 -----------------------------
        if ds214se.DownloadStation('remove'):              
            if not ds214se.logout():
                logging.error('=== 登出 %s 失敗! == '  % ds214se.name)
            else:
                logging.info('=== 已成功登出 %s! == ' % ds214se.name)

