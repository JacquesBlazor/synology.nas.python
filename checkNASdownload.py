# --- The MIT License (MIT) Copyright (c) alvinconstantine(alvin.constantine@outlook.com), Tue Jun 18 08:54:00am 2020 ---
import myNASsynofuncs as nas
import os, sys 

if __name__ == '__main__':
    ds214se = nas.nasDiskStation()
    if ds214se.login:
        print('登入 NAS [%s] 成功' % ds214se.name)    
    getfilteredTasks = ds214se.DownloadStation('filter')
    for i, j in getfilteredTasks.items():
        print(ds214se.staMapping[i], ':', len(j))
    if not ds214se.logout():
        print('登出 NAS [%s] 失敗' % ds214se.name)
    else:
        print('已成功登出 NAS [%s]' % ds214se.name)        
