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
    
    
    organ="LG"
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
    
    
    ## 波形ファイル名を取得
    files = []
    for file in os.listdir(_input_path):
        base, ext = os.path.splitext(file)
        if ext == '.csv' and "(" not in file:
            files.append(file)
            print(file,"この波形ファイルを変換します")
    
    ## 自治体波形群に含まれる気象庁データをのぞく
    #JMA_df = 
    
    
    print("自治体の元データをcsv形式の二列データで出力します。")
    
    
    
    
    
    
    
    for filename in files:
        input_path = f"{_input_path}/{filename}"
        print(input_path)
        header= pd.read_csv(input_path, nrows=6, header=None, encoding="shift_jis")
        sampling_line=str(header.iloc[3])
        samplingFreq=sampling_line.split()[3][:-2]
        acc = pd.read_csv(input_path,header=6, encoding="shift_jis")
        # print(acc)
        print(acc.columns)
        if organ == "JMA":
            EW=acc[" EW"]
            NS=acc["NS"]
            UD=acc[" UD"]
        else:#"LocalGovernment"
            EW=acc["EW"]
            NS=acc[" NS"]
            UD=acc["UD"]
        
        station_code_line=str(header.iloc[0])
        station_code=station_code_line.split()[3][:5]
        
    
        time_temp = pd.Series(list(range(len(acc))), dtype='float')
        time = time_temp /float(samplingFreq)
         
        outputEW_path = "{0}/{1}".format(output_folder_path,station_code+"."+"EW"+".acc.csv")
        output = pd.DataFrame()
        output[1]=time
        output[2]=EW
        output.columns=["time[s]", "acc[gal]"]
        print(output)
        output.to_csv(outputEW_path, header=True, index=False)
        
        outputNS_path = "{0}/{1}".format(output_folder_path,station_code+"."+"NS"+".acc.csv")
        output = pd.DataFrame()
        output[1]=time
        output[2]=NS
        output.columns=["time[s]", "acc[gal]"]
        print(output)
        output.to_csv(outputNS_path, header=True, index=False)
        
        outputUD_path = "{0}/{1}".format(output_folder_path,station_code+"."+"UD"+".acc.csv")
        output = pd.DataFrame()
        output[1]=time
        output[2]=UD
        output.columns=["time[s]", "acc[gal]"]
        print(output)
        output.to_csv(outputUD_path, header=True, index=False)
        
        print("END")
        
        station_code_line=str(header.iloc[0])
        station_code=station_code_line.split()[3][:5]
                
        station_name_line=str(header.iloc[0])
        station_name=station_name_line.split()[3][5:]
        
        lat_line=str(header.iloc[1])
        lat=lat_line.split()[2]
        
        lon_line=str(header.iloc[2])
        lon=lon_line.split()[2]

        sampling_line=str(header.iloc[3])
        samplingFreq=sampling_line.split()[3][:-2]
        
        initialtime_line=str(header.iloc[5])
        _list=initialtime_line.split()[4:10]
        # initialtime=_list[0]+"/"+_list[1]+"/"+_list[2]+" "+_list[3]+":"+_list[4]+":"+_list[5]
        # OriginTime=datetime.datetime.strptime(initialtime, '%H:%M:%S') 
        initialtime=_list[3]+":"+_list[4]+":"+_list[5]
        
        
        azimuth, bkw_azimuth, hyp_distance = grs80.inv(epi_lon,epi_lat, lon,lat)
        epi_distance = pow(hyp_distance**2 + depth**2,0.5)
        
        hyp_distance=round(hyp_distance/1000,4)
        epi_distance=round(epi_distance/1000,4)
        
        print(station_code,station_name,lat,lon,samplingFreq,initialtime,hyp_distance,epi_distance)
        
        #cols = ['地点コード','観測点名','緯度[deg]','経度[deg]','サンプリング周波数','収録開始時刻']     
        record = pd.Series([station_code,station_name,lat,lon,samplingFreq,initialtime,hyp_distance,epi_distance,organ], index=df_table.columns)
        df_table = df_table.append(record, ignore_index=True)
    
    
    ## 観測点リストの保存    
    df_table.to_csv(f"{output_df_dir}/{organ}_station_list.csv",encoding="shift_jis",index=False)  
    print(df_table)
        
        
    
        
        
    
    
    
    
if __name__ == "__main__":
    main()
    
        
    