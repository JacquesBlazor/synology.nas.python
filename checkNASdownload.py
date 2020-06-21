# --- The MIT License (MIT) Copyright (c) alvinconstantine(alvin.constantine@outlook.com), Tue Jun 20 15:19pm 2020 ---
import myNASsynofuncs as nas
import os, sys 

if __name__ == '__main__':
    ds214se = nas.nasDiskStation()
    if ds214se.login:
        print('登入 NAS [%s] 成功' % ds214se.name)    
    getfilteredTasks = ds214se.DownloadStation('filter')
    for i, j in getfilteredTasks.items():
        print(ds214se.staMapping[i], ':', len(j))
        if i == 'downloading':
            print('=== %s 的檔案清單 ===' % ds214se.staMapping[i])
            print('=== 編號, 目的地資料夾, 檔名, 檔案大小, 已下載大小, 已下載比率 ===')
            for x, y in enumerate(getfilteredTasks['downloading']):
                print(x+1, y['additional']['detail']['destination'], y['title'], y['sizeGB'], 'GB', y['downloadGB'], 'GB', y['percentage'])
    if not ds214se.logout():
        print('登出 NAS [%s] 失敗' % ds214se.name)
    else:
        print('已成功登出 NAS [%s]' % ds214se.name)
    check = input('請按任意鍵繼續...')
    
