import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pyproj

from config import Config


def main():
    grs80 = pyproj.Geod(ellps='GRS80') 
    
    ## 設定
    conf=Config()
    epi_lon,epi_lat,depth = conf.epi_lon,conf.epi_lat,conf.depth
    
    organ="K-NET"
    _input_path = f"{conf.wave_path}/raw/{organ}"
    output_folder_path = f"{conf.acc_file_dir}/{organ}"
    output_df_dir = conf.station_list_dir
    
    
    try:
        ## 出力先フォルダの作成
        print(conf.acc_file_dir)
        os.mkdir(conf.acc_file_dir)
    except:
        print("The folder exists.")
        print()

    try:
        ## 出力先フォルダの作成
        print(output_folder_path)
        os.mkdir(output_folder_path)
    except:
        print("The folder exists.")
        print()

    try:
        ## 観測点リスト置き場
        print(output_df_dir)
        os.mkdir(output_df_dir)
    except:
        print("The folder exists.")
        print()

    
    ## 観測点リストのデータフレーム
    cols = ['地点コード','観測点名','緯度[deg]','経度[deg]','サンプリング周波数','収録開始時刻','震央距離[km]','震源距離[km]','機関']    
    df_table = pd.DataFrame(index=[], columns=cols)
    
    
    
    files = []
    for file in os.listdir(_input_path):
        base, ext = os.path.splitext(file)
        if ext == '.EW' or ext == '.NS' or ext == '.UD':
            files.append(file)
            print(file,"このファイルを変換します")
    print("K-NETの元データをcsv形式の二列データで出力します。")
    
    for filename in files:
        input_path = f"{_input_path}/{filename}"
        print(input_path)
        header_length = 17
        
        with open(input_path) as f:
            lines = f.readlines()
        
        #ヘッダーの読み込み
        ymd_origin=lines[0].split()[2] if len(lines[0].split()) > 2 else np.nan
        OriginTime = lines[0].split()[3] if len(lines[0].split()) > 3 else np.nan
        Lat=lines[1].split()[1] if len(lines[1].split()) > 2 else np.nan
        Lon=lines[2].split()[1] if len(lines[2].split()) > 2 else np.nan
        # depth=lines[3].split()[1]
        M=lines[4].split()[1] if len(lines[4].split()) > 1 else np.nan
        
        station_code=lines[5].split()[2] if len(lines[5].split()) > 2 else np.nan
        statoin_lat=lines[6].split()[2] if len(lines[6].split()) > 2 else np.nan
        station_lon=lines[7].split()[2] if len(lines[7].split()) > 2 else np.nan
        station_hight=lines[8].split()[2] if len(lines[8].split()) > 2 else np.nan
        
        ymd_record=lines[9].split()[2] if len(lines[9].split()) > 2 else np.nan
        RecordTime=lines[9].split()[3] if len(lines[9].split()) > 3 else np.nan
        samplingFreq_temp=lines[10].split()[2] if len(lines[10].split()) > 2 else np.nan
        dir=lines[12].split()[1] if len(lines[12].split()) > 1 else np.nan
        print(station_code)
        print(dir)
        output_path = "{0}/{1}".format(output_folder_path,station_code+"."+dir[0]+dir[2]+".acc.csv")
        
        ScaleFactor_temp=lines[13].split()[2] if len(lines[13].split()) > 2 else np.nan
        
        samplingFreq=samplingFreq_temp[0:3]
        scaleFactor=float(ScaleFactor_temp[0:4])/float(ScaleFactor_temp[10:17])
        
        
        ## 地震発生時刻からの記録にするためにデータの前に0をつける 場合の処理
        # OriginTime=datetime.datetime.strptime(OriginTime, '%H:%M:%S') 
        # RecordTime=datetime.datetime.strptime(RecordTime, '%H:%M:%S')
        # print("OriginTime",OriginTime,"RecordTime",RecordTime)
        
        # td = RecordTime - OriginTime
        # print(td.seconds,"秒遅らせる")
        # add_step = int(td.seconds) * int(samplingFreq)
        
        add_step = 0 #今回は0を追加しないでおく
        add_zero = [0] * add_step

        with open(input_path) as f:
            data_list = [s.strip() for s in f.read().split()]
        #print(data_list[48])
        data = pd.Series(data_list[49:], dtype='float')
        data_adj = data - data.mean()
        add_data = data_adj.values.tolist()
        
        data = pd.Series(add_zero+add_data, dtype='float')
        
        acc = data * scaleFactor
        
        #print(len(acc))
        time_temp = pd.Series(list(range(len(acc))), dtype='float')
        time = time_temp /float(samplingFreq)    
        #print(len(time))
        
        output = pd.DataFrame()
        output[1]=time
        output[2]=acc
        output.columns=["time[s]", "acc[gal]"]
        
        print(output)
        
        output.to_csv(output_path, header=True, index=False)
        print("END")
        
        if dir[0]+dir[2] == "EW":
            station_code=lines[5].split()[2]
            station_name=lines[5].split()[2]
            
            lat=lines[6].split()[2]
            lon=lines[7].split()[2]
    
            sampling_line=lines[10].split()[2]
            samplingFreq=sampling_line[:-2]
            
            # initialtime_line=lines[9].split()
            # initialtime=initialtime_line[2]+" "+initialtime_line[3]
            # print(initialtime_line)
            # print(_list)
            # print(_list[0])azimuth, bkw_azimuth, hyp_distance = grs80.inv(epi_lon,epi_lat, lon,lat)
            
            azimuth, bkw_azimuth, hyp_distance = grs80.inv(epi_lon,epi_lat, lon,lat)
            epi_distance = pow(hyp_distance**2 + depth**2,0.5)
            
            hyp_distance=round(hyp_distance/1000,4)
            epi_distance=round(epi_distance/1000,4)
            
            # print(station_code,station_name,lat,lon,samplingFreq,initialtime,hyp_distance,epi_distance)
            
            #cols = ['地点コード','観測点名','緯度[deg]','経度[deg]','サンプリング周波数','収録開始時刻']     
            record = pd.Series([station_code,station_name,lat,lon,samplingFreq,RecordTime,hyp_distance,epi_distance,organ], index=df_table.columns)
            df_table = df_table.append(record, ignore_index=True)
            
    ## 観測点リストの保存    
    df_table.to_csv(f"{output_df_dir}/{organ}_station_list.csv",encoding="shift_jis",index=False)  
    print(df_table)
    

    
if __name__ == "__main__":
    main()     
        
        
        
        
        
        
        