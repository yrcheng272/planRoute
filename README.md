# 簡易路線規劃

用Python Django的架構建置一個簡易的前端介面，串接[everystreet演算法](https://github.com/matejker/everystreet)，提供簡易的路線規劃。

另外提供gpx檔案下載。


### **注意事項**
由於地圖資料是從[OpenStreetMap](https://www.openstreetmap.org/)取得的，<mark>有可能與實際道路不符合</mark>，僅供參考！


## 安裝

請先確認已安裝好Python和pip，再開始下面步驟。

1. 安裝所需的libs
```
pip install -r requirements.txt
```

2. 移動到planRoute目錄底下，啟動Django Server
```
python manage.py runserver
```