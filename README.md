# data-redash

## 使用方法 by docker

#### 建立 volume
    make create-postgres-volume
    make create-redis-redash-volume
    make create-db

#### 啟動
    make up-d

#### 關閉
    make down

#### package
    pip install sqlalchemy==1.4.20 pymysql==1.0.2 loguru==0.5.3 pandas==1.1.5 requests==2.25.1 tqdm wget


#### 明新科大
    https://docs.google.com/presentation/d/1WrWKvJ3e0JLluLK2z80vbagl3EijOK1mlSotZzMa3GI/edit?usp=sharing
