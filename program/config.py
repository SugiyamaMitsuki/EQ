"""
2022年01月22日 01時08分ころ地震がありました。
震源地は、日向灘（北緯32.7度、東経132.1度）で、震源の深さは約40km、地震の規模（マグニチュード）は6.4と推定されます。

【長周期地震動階級１以上が観測された地域】
長周期地震動階級２　　熊本県熊本　　　熊本県球磨　　　大分県中部　　　大分県南部　　　宮崎県北部平野部　　　
　　　　　　　　　　　　　　宮崎県北部山沿い　　　
長周期地震動階級１　　大阪府南部　　　鳥取県西部　　　徳島県北部　　　愛媛県南予　　　高知県西部　　　
　　　　　　　　　　　　　　福岡県筑後　　　佐賀県南部　　　長崎県北部　　　長崎県島原半島　　　熊本県阿蘇　　　
　　　　　　　　　　　　　　熊本県天草・芦北　　　大分県北部　　　大分県西部　　　宮崎県南部山沿い　　　鹿児島県薩摩　

https://www.jma.go.jp/bosai/map.html#6/33.626/134.095/&elem=int&contents=earthquake_map
http://www.data.jma.go.jp/eew/data/ltpgm/20220122132100/index.html
https://www.data.jma.go.jp/svd/eqev/data/kyoshin/jishin/index.html
https://www.kyoshin.bosai.go.jp/kyoshin/quake/
"""


import os

class Config(object):
    def __init__(self):
        
        ## このconfig.pyの絶対パス
        self.folder = os.path.dirname(os.path.abspath(__file__)) #os.path.abspath(__file__)
        self.wave_path = str(self.folder).replace("program","wave")
        
        ###
        ## 地震情報を入力する
        ###

        ## 地震を区別するための名前 年_月日_時分 （フォルダ名）
        self.eq_key = "EQ_20220122" 
        
        ## 地震情報 
        # https://www.fnet.bosai.go.jp/event/tdmt.php?_id=20220121160700&LANG=ja
        self.epi_lon,self.epi_lat,self.depth = 132.1,32.7,55.41
        self.Mw = 6.4
        
        ## 地震データをダウンロードした機関 
        self.organ_list =["JMA", "K-NET"]
        #self.organ_list =["JMA", "K-NET", "KiK-net", "LG"]


        ###
        ## 生データの解凍 01_Unzip_raw.py
        ###

        ## ファイル名
        #　JMA
        self.jma_raw = "acc.zip"
        #　K-NET　& KiK-net 20220122010830.knt.tar.gz
        key ="20220122010830"
        self.kne_kik_raw = f"{key}.tar"
        #　K-NET
        self.knet_raw = f"{key}.knt.tar.gz"
        #　KiK-net
        self.kik_raw = f"{key}.kik.tar.gz"
        #LG 
        # インターネット経由で直接ダウンロードする(規模の大きな地震でのみ公表される)
        # https://www.data.jma.go.jp/svd/eqev/data/kyoshin/jishin/ 気象庁の観測点も含まれる
        # self.LG_URL_key = "2102132307_fukushima-oki"
        

        ###
        ## 加速度ファイルをcsvデータに変更 JMA_to_acc_csv.py
        ###
        self.acc_file_dir = f"{self.wave_path}/acc"
        self.station_list_dir = f"{self.wave_path}/station"
        

        ###
        ## 加速度を速度、変位に変更 03_Acc_to_VelorDis.py
        ###
        
        ## 加速度から速度に変換
        self.make_vel = True
        self.vel_file_dir = f"{self.wave_path}/vel"
        self.taper_on=True
        
        ## 加速度から変位に変換
        self.make_dis = True
        self.dis_file_dir = f"{self.wave_path}/dis"
        self.taper_on=True

        self.left=0.05
        self.start=0.1
        self.end=20
        self.right=30
        
        ###
        ## フーリエスペクトルを計算 04_FFT.py
        ###
        ## FFT
        self.fft_file_dir = f"{self.wave_path}/fft/"
        self.taper_on=True
        self.left=0.05
        self.start=0.1
        self.end=20
        self.right=30
        self.parzen_on=True
        self.parzen_setting=0.1



        ###
        ## nigam方による応答スペクトルの計算 05_nigam.py
        ###
        self.nigam=True
        self.respec_file_dir = f"{self.wave_path}/respec"
        self.period_begin=0
        self.period_end=10
        self.period_step_num=101
        self.damp_factor_h=0.05
        
        ###
        ## 計測震度の計算 06_Seismic_Intensity.py
        ###
        self.sindo_file_dir = f"{self.wave_path}/sindo"
        
        

        ###
        ## 観測記録の整理 Make_StationList.py
        ###

        ## 観測点表
        self.station_outputname=f"観測点リスト_{self.eq_key}.csv"
        self.add_AMP_AVS=True
        
        self.JSHIS_AVS_path = f'{str(self.folder).replace(f"{self.eq_key}/program","")}/J-SHIS250mMesh/Z-V3-JAPAN-AMP-VS400_M250.csv'   #lon_lat_AVS30.txt#
        self.add_FFT=True
        self.add_I=True
        self.add_res=False
        self.add_disMax=True
        self.add_velMax=True
        self.add_accMax=True
        
        
        ###
        ## 波形を保存する Draw_wave.py
        ###
        ## 波形の出力
        self.drawwave_dir = f"{self.wave_path}/graph"
        self.ascending_key = "震源距離[km]" #['最大加速度EW','最大加速度NS','最大加速度UD','最大加速度水平','最大加速度3成分']震央距離[km]	震源距離[km] 
        self.ascending =  False #降順ならTrue
        self.head_num = 2






        ###
        ## 距離減衰 Distance_attenuation_type.py
        ###
        ## 距離減衰グラフの作成　Distance attenuation type
        
        self.distance_attenuation_path = f"{self.wave_path}/graph"
        
        # 距離減衰式 司・翠川(1999) https://www.jstage.jst.go.jp/article/aijs/64/523/64_KJ00004087596/_pdf/-char/ja
        self.Fault_type = "境界" #"内陸" "境界" "プレート内"
        self.Distance_attenuation_type = "Using_Equivalent_hypocentral_distance"
        
        ## 距離減衰式のパラメータ
        self.a,self.h,self.D,self.d,self.e=0,0,0,0,0
        self.a_PA,self.h_PA,self.e_PA=0,0,0
        if self.Distance_attenuation_type=="Using_Equivalent_hypocentral_distance":# 等価震源距離
            if self.Fault_type == "内陸":
                self.d = 0.00
                self.d_PA = 0.00
            elif self.Fault_type == "境界":
                self.d_PA = 0.06
                self.d_PA = 0.09
            elif self.Fault_type == "プレート内":
                self.d = 0.16
                self.d_PA = 0.28
            self.a,self.h,self.D,self.e=0.58, 0.0031, self.depth/1000, -1.25
            self.a_PA,self.h_PA,self.D,self.e_PA=0.5, 0.0036, self.depth/1000, 0.60
       
        elif self.Distance_attenuation_type=="Using_fault_distance": # 断層最短震源距離
            if self.Fault_type == "内陸":
                self.d = 0.00
                self.d_PA = 0.00
            elif self.Fault_type == "境界":
                self.d = -0.02
                self.d_PA = 0.01
            elif self.Fault_type == "プレート内":
                self.d = 0.12
                self.d_PA = 0.22
            self.a,self.h,self.D,self.e=0.58, 0.0038, self.depth/1000, -1.29
            self.a_PA,self.h_PA,self.D,self.e_PA=0.5, 0.0043, self.depth/1000, 0.61
            
        
        
        
        # ペーストアップ走時の作成 波形の出力
        self.top = 500 # 最大加速度の大きな順に指定した観測点数
        
        ## ペーストアップ 走時の作成
        self.paste_up_path = f"../{self.eq_key}/graph/"
        self.start_time = "2021/3/20 18:09:00"
        self.max_dis = 800
        self.max_time = 500
        #機関が違うと時間がずれてるときがある
        
        
        
        
        
        
        ## 地震動継続時間
        
        



        
        ## 最大加速度　最大速度　最大変位　の分布
        
        ## 最大加速度　最大速度　最大変位　の分布
        # GMTで地図を書く際のパラメータ
        self.gmt_path = f"../{self.eq_key}/gmt_input/"
        self.center_lon,self.center_lat = self.epi_lon,self.epi_lat
        self.distance_from_center = 1000 # km
        
        