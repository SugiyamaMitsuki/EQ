# EQ
2022/01 作成
杉山充樹

# 地震動観測記録
# 気象庁
気象庁｜長周期地震動に関する観測情報
http://www.data.jma.go.jp/svd/eew/data/ltpgm_explain/data/past/past_list.html

# 気象庁および地方公共団体 上記の気象庁データと重複あり
気象庁｜強震観測データ
https://www.data.jma.go.jp/svd/eqev/data/kyoshin/jishin/index.html

# 防災科研
防災科学技術研究所｜地震選択＆ダウンロード
https://www.kyoshin.bosai.go.jp/kyoshin/quake/

# 震源情報
F-net 地震のメカニズム情報
https://www.fnet.bosai.go.jp/event/joho.php?LANG=ja









# 地震動波形処理プログラムの説明
気象庁、K-NET、KiK-net、自治体の地震動データを
\地震動波形処理プログラム\（年_月日_時分）\raw\解凍前に置くことで
加速度や速度、応答スペクトルなどを計算する。
データの保存形式は基本的にcsv

必要モジュール
numpy
pandas
、、、、




# program

・config.py（パラメータ設定ファイル）
プログラムの実行時に書き換える必要あり。

・Unzip_raw.py
生データを解凍する。

・JMA_to_acc_csv.py
・K-NET_to_acc_csv.py
・KiK-NET_to_acc_csv.py
解凍したデータを時刻と地震動強さの二列データに変換する。

・Acc_to_VelorDis.py
加速度データを速度と変位に変換する。

・Nigam.py
応答スペクトルを計算する。

・Seismic_Intensity.py
計測震度を計算する。

・FFT.py
フーリエスペクトルを計算する。

・Make_StationList.py
観測点リストを作成する。
観測点名、緯度経度、地盤増幅度、最大加速度など

・Distance_attenuation_type.py
距離減衰式を作成する。

・Paste_up.py
ペーストアップを描写する。

・Draw_map_by_python.py
pythonのbasemapによって最大加速度の分布などを描写する。
basemapのインストールに苦労した。

・calculusパッケージ
計算時のもろもろの処理をするためのパッケージ
・meshcode_lonlatパッケージ
メッシュコードと緯度経度を変換するパッケージ
・for_basemapパッケージ
basemapの使用のために必要なパッケージ



# 使い方
①年_月日_時分のフォルダを作成する。（0000_0000_0000）をコピーして名称変更

②ダウンロードした気象庁、K-NET、KiK-netの生データを
　\地震動波形処理プログラム\（年_月日_時分）\raw\解凍前　に保存する。

③config.py
　を書き換える。
　self.eq_keyは①のフォルダ名（年_月日_時分）と同じにする。
　震源の緯度経度、深さ、マグニチュードを入力する。

