# Guild

## 建立環境
1. python3 -m venv unlimited_tree    
2. sourece unlimited_tree/bin/activate    
3. pip install -r requirements.txt    

## db setting
1. 先在mysql底下建一個schema    
2. 把你mysql database uri 補上 app.config['SQLALCHEMY_DATABASE_URI']    

## 開跑
1. 執行腳本: python app.py    
2. 初始化db: http://127.0.0.1:6666/init ，會幫你建立最基本的樹架構。如果測試搞壞了想重來就直接把table刪了，再跑一次api    
3. 新增: [POST] http://127.0.0.1:6666/agent , payload: {"parent": "B","agent": "F"}    
4. 刪除: [DELTE] http://127.0.0.1:6666/agent?agent=D    
5. 查詢子樹: [GET] http://127.0.0.1:6666/agent/child?parent=F    
6. 查詢林老北: [GET] http://127.0.0.1:6666/agent/parent?child=E    
