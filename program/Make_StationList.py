
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


from config import Config
from calculus.calculus_class import Calculus
from meshcode_lonlat.lonlat_to_meshcode import LatLon2Grid




def main():
    
    ## 設定
    conf=Config()
    
    stationlist=get_stationlist(conf.station_list_dir)
    
    station = pd.DataFrame()
    for path in stationlist:
        print(f"{conf.station_list_dir}/{path}")
        station_temp = pd.read_csv(f"{conf.station_list_dir}/{path}", encoding="shift_jis")
        # 地点コード	観測点名	緯度[deg]	経度[deg]	サンプリング周波数	収録開始時刻	震央距離[km]	震源距離[km]	機関
        print(station_temp)
        # http://sinhrks.hatenablog.com/entry/2015/01/28/073327
        station=pd.concat([station, station_temp], axis=0)
    station = station.reset_index()
    print(station)
    
    
    
    
    ## 加速度の最大値を取得する　各成分　水平2成分　3成分
    # for i,column_name, item in enumerate(station.itertuples()):
    cols = ['最大加速度EW','最大加速度NS','最大加速度UD','最大加速度水平','最大加速度3成分']
    acc_max = pd.DataFrame(index=[], columns=cols) 

    ## J-SHISの250mメッシュデータからAVS30と地盤増幅度を取得する
    # AVS = pd.read_csv(JSHIS_AVS_path, delimiter='\t',header=None)
    Mesh_data_250m = pd.read_csv(conf.JSHIS_AVS_path,header=None,skiprows=7)
    latlon2grid = LatLon2Grid()
    cols = ['地盤増幅度vs400m/s','AVS30','JCODE']
    ground = pd.DataFrame(index=[], columns=cols)
    
    ## 速度の最大値を取得する　各成分　水平2成分　3成分
    cols = ['最大速度EW','最大速度NS','最大速度UD','最大速度水平','最大速度3成分']
    vel_max = pd.DataFrame(index=[], columns=cols) 
    
    ## 変位の最大値を取得する　各成分　水平2成分　3成分
    cols = ['最大変位EW','最大変位NS','最大変位UD','最大変位水平','最大変位3成分']
    dis_max = pd.DataFrame(index=[], columns=cols) 
    
    ## 応答スペクトルの最大値とその周期を取得
    cols = ['最大加速度応答EW[cm/s/s]','最大加速度応答EW周期[s]',
            '最大速度応答EW[cm/s/s]','最大速度応答EW周期[s]',
            '最大変位応答EW[cm/s/s]','最大変位応答EW周期[s]',
            
            '最大加速度応答NS[cm/s/s]','最大加速度応答NS周期[s]',
            '最大速度応答NS[cm/s/s]','最大速度応答NS周期[s]',
            '最大変位応答NS[cm/s/s]','最大変位応答NS周期[s]',
            
            '最大加速度応答UD[cm/s/s]','最大加速度応答UD周期[s]',
            '最大速度応答UD[cm/s/s]','最大速度応答UD周期[s]',
            '最大変位応答UD[cm/s/s]','最大変位応答UD周期[s]'
            
            ]
    res_max = pd.DataFrame(index=[], columns=cols) 

    ## FFTの最大値とその周期を取得
    cols = ['FFTEW[gal・sec]','FFTEW周波数[Hz]',
            'FFTNS[gal・sec]','FFTNS周波数[Hz]',
            'FFTUD[gal・sec]','FFTUD周波数[Hz]',
            ]
    #freq[Hz]	Amp.[gal・sec]
    fft_max = pd.DataFrame(index=[], columns=cols) 

    


        
    for lat,lon,organ,code in zip(station["緯度[deg]"],station["経度[deg]"],station["機関"],station["地点コード"]):
        print(lat,lon,organ,code)

        if conf.add_AMP_AVS:
            JCODE,AVS,ARV=0,9999,9999
            if str(lon).replace('.', '').isdecimal() and lon > 0 and lat > 0:
                mesh = latlon2grid.grid250m(lon, lat)
                index=Mesh_data_250m[Mesh_data_250m[0]==int(mesh)].index
                if index > 1:
                    grep_data = Mesh_data_250m.loc[index]
                    JCODE=int(grep_data[1])
                    AVS=float(grep_data[2])
                    ARV=float(grep_data[3])
                print(lon,lat,mesh,"JCODE",JCODE,"AVS",AVS,"ARV",ARV)
            record = pd.Series([ARV,AVS,JCODE],
                           index=ground.columns)
            ground = ground.append(record,ignore_index=True)
        
    
    
        if conf.add_accMax:
            acc_path_EW=f"{conf.acc_file_dir}/{organ}/{code}.EW.acc.csv"
            acc_path_NS=f"{conf.acc_file_dir}/{organ}/{code}.NS.acc.csv"
            acc_path_UD=f"{conf.acc_file_dir}/{organ}/{code}.UD.acc.csv"
            
            acc_EW = pd.read_csv(acc_path_EW, encoding="shift_jis") 
            acc_NS = pd.read_csv(acc_path_NS, encoding="shift_jis") 
            acc_UD = pd.read_csv(acc_path_UD, encoding="shift_jis")
            
            # 3成分を一つのDFに結合
            acc=pd.concat([acc_EW, acc_NS["acc[gal]"], acc_UD["acc[gal]"]], axis=1)
            acc.columns=["time[s]", "EW", "NS", "UD"]
            # print(acc)
            # print(acc)
            acc['水平2成分'] = np.sqrt(acc["EW"]*acc["EW"]+acc["NS"]+acc["NS"])
            acc['3成分'] = np.sqrt(acc["EW"]*acc["EW"]+acc["NS"]+acc["NS"]+acc["UD"]+acc["UD"])
            
            max_EW=acc["EW"].max()
            max_NS=acc["NS"].max()
            max_UD=acc["UD"].max()
            max_horizon=acc["水平2成分"].max()
            max_3=acc["3成分"].max()
            
            record = pd.Series([max_EW,max_NS,max_UD,max_horizon,max_3],
                               index=acc_max.columns)
            acc_max = acc_max.append(record,ignore_index=True)
        
        
        
    
        if conf.add_velMax:
            vel_path_EW=f"{conf.vel_file_dir}/{organ}/{code}.EW.vel.csv"
            vel_path_NS=f"{conf.vel_file_dir}/{organ}/{code}.NS.vel.csv"
            vel_path_UD=f"{conf.vel_file_dir}/{organ}/{code}.UD.vel.csv"
            
            vel_EW = pd.read_csv(vel_path_EW, encoding="shift_jis") 
            vel_NS = pd.read_csv(vel_path_NS, encoding="shift_jis") 
            vel_UD = pd.read_csv(vel_path_UD, encoding="shift_jis")
            
            # 3成分を一つのDFに結合
            vel=pd.concat([vel_EW, vel_NS["vel[kine]"], vel_UD["vel[kine]"]], axis=1)
            vel.columns=["time[s]", "EW", "NS", "UD"]
            # print(vel)
            
            vel['水平2成分'] = np.sqrt(vel["EW"]*vel["EW"]+vel["NS"]+vel["NS"])
            vel['3成分'] = np.sqrt(vel["EW"]*vel["EW"]+vel["NS"]+vel["NS"]+vel["UD"]+vel["UD"])
            
            max_EW=vel["EW"].max()
            max_NS=vel["NS"].max()
            max_UD=vel["UD"].max()
            max_horizon=vel["水平2成分"].max()
            max_3=vel["3成分"].max()
            
            record = pd.Series([max_EW,max_NS,max_UD,max_horizon,max_3],
                               index=vel_max.columns)
            vel_max = vel_max.append(record,ignore_index=True)
        
       
        
        
        if conf.add_disMax:   
            dis_path_EW=f"{conf.dis_file_dir}/{organ}/{code}.EW.dis.csv"
            dis_path_NS=f"{conf.dis_file_dir}/{organ}/{code}.NS.dis.csv"
            dis_path_UD=f"{conf.dis_file_dir}/{organ}/{code}.UD.dis.csv"
            
            dis_EW = pd.read_csv(dis_path_EW, encoding="shift_jis") 
            dis_NS = pd.read_csv(dis_path_NS, encoding="shift_jis") 
            dis_UD = pd.read_csv(dis_path_UD, encoding="shift_jis")
            
            # 3成分を一つのDFに結合
            dis=pd.concat([dis_EW, dis_NS["dis[cm]"], dis_UD["dis[cm]"]], axis=1)
            dis.columns=["time[s]", "EW", "NS", "UD"]
            # print(dis)
            
            dis['水平2成分'] = np.sqrt(dis["EW"]*dis["EW"]+dis["NS"]+dis["NS"])
            dis['3成分'] = np.sqrt(dis["EW"]*dis["EW"]+dis["NS"]+dis["NS"]+dis["UD"]+dis["UD"])
            
            max_EW=dis["EW"].max()
            max_NS=dis["NS"].max()
            max_UD=dis["UD"].max()
            max_horizon=dis["水平2成分"].max()
            max_3=dis["3成分"].max()
            
            record = pd.Series([max_EW,max_NS,max_UD,max_horizon,max_3],
                               index=dis_max.columns)
            dis_max = dis_max.append(record,ignore_index=True)
        

    
    
        ## 応答スペクトルの最大値とその周期を取得
        if conf.add_res:
            respec_path_EW=f"{conf.respec_file_dir}/{organ}/{code}.EW.respec.csv"
            respec_path_NS=f"{conf.respec_file_dir}/{organ}/{code}.NS.respec.csv"
            respec_path_UD=f"{conf.respec_file_dir}/{organ}/{code}.UD.respec.csv"
            
            respec_EW = pd.read_csv(respec_path_EW, encoding="shift_jis") 
            respec_NS = pd.read_csv(respec_path_NS, encoding="shift_jis") 
            respec_UD = pd.read_csv(respec_path_UD, encoding="shift_jis")
            
            max_respec_acc_EW=respec_EW["acc[cm/s/s]"].max()
            max_respec_acc_T_EW=respec_EW.loc[respec_EW['acc[cm/s/s]'].idxmax()]["period[sec]"]
            max_respec_vel_EW=respec_EW["vel[cm/s]"].max()
            max_respec_vel_T_EW=respec_EW.loc[respec_EW["vel[cm/s]"].idxmax()]["period[sec]"]
            max_respec_dis_EW=respec_EW["dis[cm]"].max()
            max_respec_dis_T_EW=respec_EW.loc[respec_EW["dis[cm]"].idxmax()]["period[sec]"]
            
            max_respec_acc_NS=respec_NS["acc[cm/s/s]"].max()
            max_respec_acc_T_NS=respec_NS.loc[respec_NS['acc[cm/s/s]'].idxmax()]["period[sec]"]
            max_respec_vel_NS=respec_NS["vel[cm/s]"].max()
            max_respec_vel_T_NS=respec_NS.loc[respec_NS["vel[cm/s]"].idxmax()]["period[sec]"]
            max_respec_dis_NS=respec_NS["dis[cm]"].max()
            max_respec_dis_T_NS=respec_NS.loc[respec_NS["dis[cm]"].idxmax()]["period[sec]"]
            
            max_respec_acc_UD=respec_UD["acc[cm/s/s]"].max()
            max_respec_acc_T_UD=respec_UD.loc[respec_UD['acc[cm/s/s]'].idxmax()]["period[sec]"]
            max_respec_vel_UD=respec_UD["vel[cm/s]"].max()
            max_respec_vel_T_UD=respec_UD.loc[respec_UD["vel[cm/s]"].idxmax()]["period[sec]"]
            max_respec_dis_UD=respec_UD["dis[cm]"].max()
            max_respec_dis_T_UD=respec_UD.loc[respec_UD["dis[cm]"].idxmax()]["period[sec]"]
            
            record = pd.Series([max_respec_acc_EW, max_respec_acc_T_EW,
                                max_respec_vel_EW,max_respec_vel_T_EW,
                                max_respec_dis_EW,max_respec_dis_T_EW,
                                max_respec_acc_NS, max_respec_acc_T_NS,
                                max_respec_vel_NS, max_respec_vel_T_NS,
                                max_respec_dis_NS, max_respec_dis_T_NS,
                                max_respec_acc_UD, max_respec_acc_T_UD,
                                max_respec_vel_UD, max_respec_vel_T_UD,
                                max_respec_dis_UD, max_respec_dis_T_UD
                                ],
                                index=res_max.columns)
            res_max = res_max.append(record,ignore_index=True)
        
        
    
        if conf.add_FFT:
            fft_path_EW=f"{conf.fft_file_dir}/{organ}/{code}.EW.abs.csv"
            fft_path_NS=f"{conf.fft_file_dir}/{organ}/{code}.NS.abs.csv"
            fft_path_UD=f"{conf.fft_file_dir}/{organ}/{code}.UD.abs.csv"
            
            fft_EW = pd.read_csv(fft_path_EW, encoding="shift_jis") 
            fft_NS = pd.read_csv(fft_path_NS, encoding="shift_jis") 
            fft_UD = pd.read_csv(fft_path_UD, encoding="shift_jis")
            
            max_fft_EW=fft_EW["Amp.[gal・sec]"].max()
            max_fft_T_EW=fft_EW.loc[fft_EW['Amp.[gal・sec]'].idxmax()]["freq[Hz]"]
            
            max_fft_NS=fft_NS["Amp.[gal・sec]"].max()
            max_fft_T_NS=fft_NS.loc[fft_NS['Amp.[gal・sec]'].idxmax()]["freq[Hz]"]
            
            max_fft_UD=fft_UD["Amp.[gal・sec]"].max()
            max_fft_T_UD=fft_UD.loc[fft_UD['Amp.[gal・sec]'].idxmax()]["freq[Hz]"]
            
            record = pd.Series([max_fft_EW, max_fft_T_EW,
                                max_fft_NS, max_fft_T_NS,
                                max_fft_UD, max_fft_T_UD,
                                ],
                                index=fft_max.columns)
            fft_max = fft_max.append(record,ignore_index=True)

        print()
    
    
    station=pd.concat([station, ground], axis=1)
    station=pd.concat([station, acc_max], axis=1)
    station=pd.concat([station, vel_max], axis=1)
    station=pd.concat([station, dis_max], axis=1) 
    station=pd.concat([station, res_max], axis=1)
    station=pd.concat([station, fft_max], axis=1)
    
    
    ## 計測震度の追加
    if conf.add_I:
        sindo = pd.DataFrame()
        for organ in conf.organ_list:
            sindo_temp = pd.read_csv(f"{conf.station_list_dir}/計測震度リスト_{organ}.csv", encoding="shift_jis")
            sindo=pd.concat([sindo, sindo_temp], axis=0)
        sindo = sindo.reset_index()
        station=pd.concat([station, sindo["計測震度"]], axis=1)
    

    

    print(station)
    print(f"{conf.station_list_dir}/{conf.station_outputname}")
    station.to_csv(f"{conf.station_list_dir}/{conf.station_outputname}", header=True, index=False, encoding="shift_jis")
    
    
    
            
def get_stationlist(input_path):
    files = []
    for file in os.listdir(input_path):
        base, ext = os.path.splitext(file)
        if ext == '.csv' and "計測震度" not in base:
            files.append(file)
            # print(file,"このファイルを変換します")
    return files
   

if __name__ == "__main__":
    main()     
        
        