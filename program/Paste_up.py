# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 18:50:05 2021

@author: sugiy

ペーストアップを作成するプログラム
"""

from logging import getLogger, DEBUG
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime,timedelta

from config import Config
from calculus.calculus_class import Calculus
from meshcode_lonlat.lonlat_to_meshcode import LatLon2Grid


# ログの設定
logger = getLogger(__name__)
logger.setLevel(DEBUG)


def main():
    logger.debug("mainの開始")
    
    ## 設定
    conf=Config()
    
    input_path = input_path = conf.station_list_dir+conf.station_outputfile
    paste_up_path = conf.paste_up_path
    
    
    ## 出力先フォルダの作成
    try:
        os.mkdir(paste_up_path)
    except:
        print("フォルダあるよ")
    
    
    station = pd.read_csv(input_path, encoding="shift_jis")
    print(station)
    print(station["地盤増幅度vs400m/s"])

    # index	地点コード	観測点名	緯度[deg]	経度[deg]	サンプリング周波数	収録開始時刻	震央距離[km]	震源距離[km]	機関	地盤増幅度vs400m/s	AVS30	JCODE
    # 	最大加速度EW	最大加速度NS	最大加速度UD	最大加速度水平	最大加速度3成分	
    # 最大速度EW	最大速度NS	最大速度UD	最大速度水平	最大速度3成分	
    # 最大変位EW	最大変位NS	最大変位UD	最大変位水平	最大変位3成分	
    # 計測震度	最大加速度応答EW[cm/s/s]	最大加速度応答EW周期[s]	最大速度応答EW[cm/s/s]	最大速度応答EW周期[s]	最大変位応答EW[cm/s/s]	最大変位応答EW周期[s]	最大加速度応答NS[cm/s/s]	最大加速度応答NS周期[s]	最大速度応答NS[cm/s/s]	最大速度応答NS周期[s]	最大変位応答NS[cm/s/s]	最大変位応答NS周期[s]	最大加速度応答UD[cm/s/s]	最大加速度応答UD周期[s]	最大速度応答UD[cm/s/s]	最大速度応答UD周期[s]	最大変位応答UD[cm/s/s]	最大変位応答UD周期[s]	FFTEW[gal・sec]	FFTEW周波数[Hz]	FFTNS[gal・sec]	FFTNS周波数[Hz]	FFTUD[gal・sec]	FFTUD周波数[Hz]
    
    
    station=station[station["震央距離[km]"]<conf.max_dis]
    station = station.sort_values('最大加速度3成分', ascending=True)
    station=station[:conf.top]
    
    
    max_acc=abs(station["最大加速度3成分"]).max()
    
    i=-1
    ## 加速度　
    start_time=datetime.strptime(conf.start_time, '%Y/%m/%d %H:%M:%S')
    for direction in ["EW","NS","UD"]:
        i+=1
        plt_direction = draw_paste_up(xlabel="時間 [s]",
                        ylabel="震源距離 [km]"
                        )
        plt_direction.plot(0,0,linewidth=0.3,color='black')
        plt_direction.text(0,-conf.max_dis*1,start_time,fontsize=15,color="red",ha="center")
        # station=station[station["機関"]!="LG"]
        for organ,code,distance,recording in zip(station["機関"],station["地点コード"],station["震源距離[km]"],station["収録開始時刻"]):
                
            acc_path_EW=f"{conf.acc_file_dir}{organ}/{code}.EW.acc.csv"
            acc_path_NS=f"{conf.acc_file_dir}{organ}/{code}.NS.acc.csv"
            acc_path_UD=f"{conf.acc_file_dir}{organ}/{code}.UD.acc.csv"
            
            acc_EW = pd.read_csv(acc_path_EW, encoding="shift_jis") 
            acc_NS = pd.read_csv(acc_path_NS, encoding="shift_jis") 
            acc_UD = pd.read_csv(acc_path_UD, encoding="shift_jis")
            
            # 3成分を一つのDFに結合
            acc=pd.concat([acc_EW, acc_NS["acc[gal]"], acc_UD["acc[gal]"]], axis=1)
            acc.columns=["time[s]", "EW", "NS", "UD"]
            # acc=acc[acc["time[s]"]<conf.data_sec]
            
            print(code,organ,recording,start_time,distance)
            RecordTime=None
            td=9999
            print(organ)
            RecordTime=datetime.strptime(recording,  '%H:%M:%S')
            td = RecordTime - start_time
            # if organ =="JMA" or organ == "LG":
            #     RecordTime=datetime.strptime(recording,  '%Y/%m/%d %H:%M:%S') #+ timedelta(seconds=30)
            #     # RecordTime = datetime(hour=RecordTime.hour,minute=RecordTime.minute,second=RecordTime.second)
            #     # print(organ,RecordTime)
            #     td = RecordTime - start_time
            # elif organ == "K-NET":
            #     RecordTime=datetime.strptime(recording,  '%H:%M:%S')
            #     td = RecordTime - start_time
            # elif organ == "KiK-net":
            #     RecordTime=datetime.strptime(recording,  '%H:%M:%S')#+ timedelta(seconds=30)
            #     td = RecordTime - start_time
            
            if td != 9999:
                print(f"{td.seconds}秒遅らせる")
                samplingFreq=1/(acc["time[s]"][1] - acc["time[s]"][0])
                add_step = int(td.seconds) * int(samplingFreq)
                print(f"追加ステップ {add_step}")
                add_zero = [0] * add_step
                add_data_direction = acc[direction].values.tolist()
                data_direction = pd.Series(add_zero+add_data_direction, dtype='float')[:int(conf.max_time*samplingFreq)]
                time = np.arange(0,len(data_direction)*(1/samplingFreq), 1/samplingFreq)            #numpy.arrange(a, b, d)メソッドでa以上b未満で間隔dの等差数列を作ることができます。   
                # if organ =="K-NET":
                plt_direction.plot(time,data_direction/max_acc-distance,linewidth=0.3,color='black')
                plt_direction.text(-conf.max_time*0.2,-distance,f"{code} {round(max(abs(data_direction)),3)} cm/s/s",fontsize=5,va="center")
            
                
            else:
                print("スルー")    
                
            print()
        
        
        plt_direction.savefig(paste_up_path+"走時_加速度{}.png".format(direction),bbox_inches='tight',color='black')
        plt_direction.show()
        
        
        
    max_vel=abs(station["最大速度3成分"]).max()    
    ## 速度　
    start_time=datetime.strptime(conf.start_time, '%Y/%m/%d %H:%M:%S')
    for direction in ["EW","NS","UD"]:
        plt_direction = draw_paste_up(xlabel="時間 [s]",
                        ylabel="震源距離 [km]"
                        )
        plt_direction.plot(0,0,linewidth=0.3,color='black')
        plt_direction.text(0,-conf.max_dis*1,start_time,fontsize=15,color="red",ha="center")
        
        for organ,code,distance,recording in zip(station["機関"],station["地点コード"],station["震源距離[km]"],station["収録開始時刻"]):
                
            vel_path_EW=f"{conf.vel_file_dir}{organ}/{code}.EW.vel.csv"
            vel_path_NS=f"{conf.vel_file_dir}{organ}/{code}.NS.vel.csv"
            vel_path_UD=f"{conf.vel_file_dir}{organ}/{code}.UD.vel.csv"
            
            vel_EW = pd.read_csv(vel_path_EW, encoding="shift_jis") 
            vel_NS = pd.read_csv(vel_path_NS, encoding="shift_jis") 
            vel_UD = pd.read_csv(vel_path_UD, encoding="shift_jis")
            
            # 3成分を一つのDFに結合
            vel=pd.concat([vel_EW, vel_NS["vel[kine]"], vel_UD["vel[kine]"]], axis=1)
            vel.columns=["time[s]", "EW", "NS", "UD"]
            # vel=vel[vel["time[s]"]<conf.data_sec]
            
            print(code,organ,recording,start_time)
            RecordTime=None
            td=9999
            print(organ)
            RecordTime=datetime.strptime(recording,  '%H:%M:%S')
            td = RecordTime - start_time
            # if organ =="JMA":
            #     RecordTime=datetime.strptime(recording,  '%Y/%m/%d %H:%M:%S') #+ timedelta(seconds=30)
            #     # RecordTime = datetime(hour=RecordTime.hour,minute=RecordTime.minute,second=RecordTime.second)
            #     # print(organ,RecordTime)
            #     td = RecordTime - start_time
            # elif organ == "K-NET":
            #     RecordTime=datetime.strptime(recording,  '%H:%M:%S')
            #     td = RecordTime - start_time
            # elif organ == "KiK-net":
            #     RecordTime=datetime.strptime(recording,  '%H:%M:%S')#+ timedelta(seconds=30)
            #     td = RecordTime - start_time
            if td != 9999:
                print(f"{td.seconds}秒遅らせる")
                samplingFreq=1/(acc["time[s]"][1] - acc["time[s]"][0])
                add_step = int(td.seconds) * int(samplingFreq)
                print(f"追加ステップ {add_step}")
                add_zero = [0] * add_step
                add_data_direction = acc[direction].values.tolist()
                data_direction = pd.Series(add_zero+add_data_direction, dtype='float')[:int(conf.max_time*samplingFreq)]
                time = np.arange(0,len(data_direction)*(1/samplingFreq), 1/samplingFreq)            #numpy.arrange(a, b, d)メソッドでa以上b未満で間隔dの等差数列を作ることができます。   
                # if organ =="K-NET":
                plt_direction.plot(time,data_direction/max_vel-distance,linewidth=0.3,color='black')
                plt_direction.text(-conf.max_time*0.2,-distance,f"{code} {round(max(abs(data_direction)),3)} cm/s",fontsize=5,va="center")
            
                
            else:
                print("スルー")    
                
            print()
        plt_direction.savefig(paste_up_path+"走時_速度{}.png".format(direction),bbox_inches='tight')
        plt_direction.show()   
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
def draw_paste_up(xlabel,ylabel):
    
    plt.figure(figsize=(10,20),dpi=300,facecolor='w',edgecolor='k')
    # plt.axes().set_aspect('equal')
    plt.rcParams['font.size'] = 12
    plt.rcParams['font.family']= 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['MS Gothic'] #日本語使用可
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['xtick.major.width'] = 1.2
    plt.rcParams['ytick.major.width'] = 1.2
    plt.rcParams['axes.linewidth'] = 1.2
    plt.rcParams['axes.grid']=True
    plt.rcParams['grid.linestyle']='--'
    plt.rcParams['grid.linewidth'] = 0.3
    
    plt.rcParams["legend.markerscale"] = 1.2
    plt.rcParams["legend.fancybox"] = False
    plt.rcParams["legend.framealpha"] = 1
    plt.rcParams["legend.edgecolor"] = 'black'
    
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    # plt.xlim(xmin,xmax)
    # plt.ylim(ymin,ymax)
    
    # plt.grid(True),plt.locator_params(axis='x',nbins=10),plt.locator_params(axis='y',nbins=10)
    # plt.grid(axis='x', which='major',color='black',linestyle='-')
    # plt.grid(axis='y', which='major',color='black',linestyle='-')
    
    # plt.scatter(x, y,c=c,cmap='coolwarm',label=label, alpha=1, edgecolor="black", s=20) # viridis
    # plt.clim(0,3)
    
    # plt.legend(bbox_to_anchor=(1, 1), loc='upper right', borderaxespad=0.8, fontsize=10)    
    # plt.colorbar(shrink=0.5,orientation='horizontal',label=clabel)
    # label = label.replace('\n', '')
    
    return plt
    
   
    
    
    # if conf.add_accMax:
    #     ## 加速度の最大値を取得する　各成分　水平2成分　3成分
    #     # for i,column_name, item in enumerate(station.itertuples()):
    #     cols = ['最大加速度EW','最大加速度NS','最大加速度UD','最大加速度水平','最大加速度3成分']
    #     acc_max = pd.DataFrame(index=[], columns=cols) 
    #     for organ,code in zip(station["機関"],station["地点コード"]):
            
    #         acc_path_EW=f"{conf.acc_file_dir}{organ}/{code}.EW.acc.csv"
    #         acc_path_NS=f"{conf.acc_file_dir}{organ}/{code}.NS.acc.csv"
    #         acc_path_UD=f"{conf.acc_file_dir}{organ}/{code}.UD.acc.csv"
            
    #         acc_EW = pd.read_csv(acc_path_EW, encoding="shift_jis") 
    #         acc_NS = pd.read_csv(acc_path_NS, encoding="shift_jis") 
    #         acc_UD = pd.read_csv(acc_path_UD, encoding="shift_jis")
            
    #         # 3成分を一つのDFに結合
    #         acc=pd.concat([acc_EW, acc_NS["acc[gal]"], acc_UD["acc[gal]"]], axis=1)
    #         acc.columns=["time[s]", "EW", "NS", "UD"]
    #         # print(acc)
            
    #         acc['水平2成分'] = np.sqrt(acc["EW"]*acc["EW"]+acc["NS"]+acc["NS"])
    #         acc['3成分'] = np.sqrt(acc["EW"]*acc["EW"]+acc["NS"]+acc["NS"]+acc["UD"]+acc["UD"])
            
    #         max_EW=acc["EW"].max()
    #         max_NS=acc["NS"].max()
    #         max_UD=acc["UD"].max()
    #         max_horizon=acc["水平2成分"].max()
    #         max_3=acc["3成分"].max()
            
    #         record = pd.Series([max_EW,max_NS,max_UD,max_horizon,max_3],
    #                            index=acc_max.columns)
    #         acc_max = acc_max.append(record,ignore_index=True)
        
    #     station=pd.concat([station, acc_max], axis=1)
        
    
    # if conf.add_velMax:
    #     ## 速度の最大値を取得する　各成分　水平2成分　3成分
    #     cols = ['最大速度EW','最大速度NS','最大速度UD','最大速度水平','最大速度3成分']
    #     vel_max = pd.DataFrame(index=[], columns=cols) 
    #     for organ,code in zip(station["機関"],station["地点コード"]):
            
    #         vel_path_EW=f"{conf.vel_file_dir}{organ}/{code}.EW.vel.csv"
    #         vel_path_NS=f"{conf.vel_file_dir}{organ}/{code}.NS.vel.csv"
    #         vel_path_UD=f"{conf.vel_file_dir}{organ}/{code}.UD.vel.csv"
            
    #         vel_EW = pd.read_csv(vel_path_EW, encoding="shift_jis") 
    #         vel_NS = pd.read_csv(vel_path_NS, encoding="shift_jis") 
    #         vel_UD = pd.read_csv(vel_path_UD, encoding="shift_jis")
            
    #         # 3成分を一つのDFに結合
    #         vel=pd.concat([vel_EW, vel_NS["vel[kine]"], vel_UD["vel[kine]"]], axis=1)
    #         vel.columns=["time[s]", "EW", "NS", "UD"]
    #         # print(vel)
            
    #         vel['水平2成分'] = np.sqrt(vel["EW"]*vel["EW"]+vel["NS"]+vel["NS"])
    #         vel['3成分'] = np.sqrt(vel["EW"]*vel["EW"]+vel["NS"]+vel["NS"]+vel["UD"]+vel["UD"])
            
    #         max_EW=vel["EW"].max()
    #         max_NS=vel["NS"].max()
    #         max_UD=vel["UD"].max()
    #         max_horizon=vel["水平2成分"].max()
    #         max_3=vel["3成分"].max()
            
    #         record = pd.Series([max_EW,max_NS,max_UD,max_horizon,max_3],
    #                            index=vel_max.columns)
    #         vel_max = vel_max.append(record,ignore_index=True)
        
    #     station=pd.concat([station, vel_max], axis=1)
        
        
    # if conf.add_disMax:    
    #     ## 変位の最大値を取得する　各成分　水平2成分　3成分
    #     cols = ['最大変位EW','最大変位NS','最大変位UD','最大変位水平','最大変位3成分']
    #     dis_max = pd.DataFrame(index=[], columns=cols) 
    #     for organ,code in zip(station["機関"],station["地点コード"]):
            
    #         dis_path_EW=f"{conf.dis_file_dir}{organ}/{code}.EW.dis.csv"
    #         dis_path_NS=f"{conf.dis_file_dir}{organ}/{code}.NS.dis.csv"
    #         dis_path_UD=f"{conf.dis_file_dir}{organ}/{code}.UD.dis.csv"
            
    #         dis_EW = pd.read_csv(dis_path_EW, encoding="shift_jis") 
    #         dis_NS = pd.read_csv(dis_path_NS, encoding="shift_jis") 
    #         dis_UD = pd.read_csv(dis_path_UD, encoding="shift_jis")
            
    #         # 3成分を一つのDFに結合
    #         dis=pd.concat([dis_EW, dis_NS["dis[cm]"], dis_UD["dis[cm]"]], axis=1)
    #         dis.columns=["time[s]", "EW", "NS", "UD"]
    #         # print(dis)
            
    #         dis['水平2成分'] = np.sqrt(dis["EW"]*dis["EW"]+dis["NS"]+dis["NS"])
    #         dis['3成分'] = np.sqrt(dis["EW"]*dis["EW"]+dis["NS"]+dis["NS"]+dis["UD"]+dis["UD"])
            
    #         max_EW=dis["EW"].max()
    #         max_NS=dis["NS"].max()
    #         max_UD=dis["UD"].max()
    #         max_horizon=dis["水平2成分"].max()
    #         max_3=dis["3成分"].max()
            
    #         record = pd.Series([max_EW,max_NS,max_UD,max_horizon,max_3],
    #                            index=dis_max.columns)
    #         dis_max = dis_max.append(record,ignore_index=True)
        
    #     station=pd.concat([station, dis_max], axis=1)
        

    # ## 計測震度の追加
    # if conf.add_I:
    #     sindo = pd.DataFrame()
    #     for organ in conf.organ_list:
    #         sindo_temp = pd.read_csv(f"{conf.sindo_file_dir}{organ}/計測震度リスト_{organ}.csv", encoding="shift_jis")
    #         print(sindo_temp)
    #         sindo=pd.concat([sindo, sindo_temp], axis=0)
    #     sindo = sindo.reset_index()
    #     station=pd.concat([station, sindo["計測震度"]], axis=1)
        
        
    #     ## 応答スペクトルの最大値とその周期を取得
    #     cols = ['最大加速度応答EW[cm/s/s]','最大加速度応答EW周期[s]',
    #             '最大速度応答EW[cm/s/s]','最大速度応答EW周期[s]',
    #             '最大変位応答EW[cm/s/s]','最大変位応答EW周期[s]',
                
    #             '最大加速度応答NS[cm/s/s]','最大加速度応答NS周期[s]',
    #             '最大速度応答NS[cm/s/s]','最大速度応答NS周期[s]',
    #             '最大変位応答NS[cm/s/s]','最大変位応答NS周期[s]',
                
    #             '最大加速度応答UD[cm/s/s]','最大加速度応答UD周期[s]',
    #             '最大速度応答UD[cm/s/s]','最大速度応答UD周期[s]',
    #             '最大変位応答UD[cm/s/s]','最大変位応答UD周期[s]'
                
    #             ]
    #     res_max = pd.DataFrame(index=[], columns=cols) 
    #     for organ,code in zip(station["機関"],station["地点コード"]):
            
    #         respec_path_EW=f"{conf.respec_file_dir}{organ}/{code}.EW.respec.csv"
    #         respec_path_NS=f"{conf.respec_file_dir}{organ}/{code}.NS.respec.csv"
    #         respec_path_UD=f"{conf.respec_file_dir}{organ}/{code}.UD.respec.csv"
            
    #         respec_EW = pd.read_csv(respec_path_EW, encoding="shift_jis") 
    #         respec_NS = pd.read_csv(respec_path_NS, encoding="shift_jis") 
    #         respec_UD = pd.read_csv(respec_path_UD, encoding="shift_jis")
            
    #         max_respec_acc_EW=respec_EW["acc[cm/s/s]"].max()
    #         max_respec_acc_T_EW=respec_EW.loc[respec_EW['acc[cm/s/s]'].idxmax()]["period[sec]"]
    #         max_respec_vel_EW=respec_EW["vel[cm/s]"].max()
    #         max_respec_vel_T_EW=respec_EW.loc[respec_EW["vel[cm/s]"].idxmax()]["period[sec]"]
    #         max_respec_dis_EW=respec_EW["dis[cm]"].max()
    #         max_respec_dis_T_EW=respec_EW.loc[respec_EW["dis[cm]"].idxmax()]["period[sec]"]
            
    #         max_respec_acc_NS=respec_NS["acc[cm/s/s]"].max()
    #         max_respec_acc_T_NS=respec_NS.loc[respec_NS['acc[cm/s/s]'].idxmax()]["period[sec]"]
    #         max_respec_vel_NS=respec_NS["vel[cm/s]"].max()
    #         max_respec_vel_T_NS=respec_NS.loc[respec_NS["vel[cm/s]"].idxmax()]["period[sec]"]
    #         max_respec_dis_NS=respec_NS["dis[cm]"].max()
    #         max_respec_dis_T_NS=respec_NS.loc[respec_NS["dis[cm]"].idxmax()]["period[sec]"]
            
    #         max_respec_acc_UD=respec_UD["acc[cm/s/s]"].max()
    #         max_respec_acc_T_UD=respec_UD.loc[respec_UD['acc[cm/s/s]'].idxmax()]["period[sec]"]
    #         max_respec_vel_UD=respec_UD["vel[cm/s]"].max()
    #         max_respec_vel_T_UD=respec_UD.loc[respec_UD["vel[cm/s]"].idxmax()]["period[sec]"]
    #         max_respec_dis_UD=respec_UD["dis[cm]"].max()
    #         max_respec_dis_T_UD=respec_UD.loc[respec_UD["dis[cm]"].idxmax()]["period[sec]"]
            
    #         record = pd.Series([max_respec_acc_EW, max_respec_acc_T_EW,
    #                             max_respec_vel_EW,max_respec_vel_T_EW,
    #                             max_respec_dis_EW,max_respec_dis_T_EW,
    #                             max_respec_acc_NS, max_respec_acc_T_NS,
    #                             max_respec_vel_NS, max_respec_vel_T_NS,
    #                             max_respec_dis_NS, max_respec_dis_T_NS,
    #                             max_respec_acc_UD, max_respec_acc_T_UD,
    #                             max_respec_vel_UD, max_respec_vel_T_UD,
    #                             max_respec_dis_UD, max_respec_dis_T_UD
    #                             ],
    #                             index=res_max.columns)
    #         res_max = res_max.append(record,ignore_index=True)
        
    #     station=pd.concat([station, res_max], axis=1)
    
    # if conf.add_FFT:
    #     ## FFTの最大値とその周期を取得
    #     cols = ['FFTEW[gal・sec]','FFTEW周波数[Hz]',
    #             'FFTNS[gal・sec]','FFTNS周波数[Hz]',
    #             'FFTUD[gal・sec]','FFTUD周波数[Hz]',
    #             ]
    #     #freq[Hz]	Amp.[gal・sec]
    #     fft_max = pd.DataFrame(index=[], columns=cols) 
    #     for organ,code in zip(station["機関"],station["地点コード"]):
            
    #         fft_path_EW=f"{conf.fft_file_dir}{organ}/{code}.EW.abs.csv"
    #         fft_path_NS=f"{conf.fft_file_dir}{organ}/{code}.NS.abs.csv"
    #         fft_path_UD=f"{conf.fft_file_dir}{organ}/{code}.UD.abs.csv"
            
    #         fft_EW = pd.read_csv(fft_path_EW, encoding="shift_jis") 
    #         fft_NS = pd.read_csv(fft_path_NS, encoding="shift_jis") 
    #         fft_UD = pd.read_csv(fft_path_UD, encoding="shift_jis")
            
    #         max_fft_EW=fft_EW["Amp.[gal・sec]"].max()
    #         max_fft_T_EW=fft_EW.loc[fft_EW['Amp.[gal・sec]'].idxmax()]["freq[Hz]"]
            
    #         max_fft_NS=fft_NS["Amp.[gal・sec]"].max()
    #         max_fft_T_NS=fft_NS.loc[fft_NS['Amp.[gal・sec]'].idxmax()]["freq[Hz]"]
            
    #         max_fft_UD=fft_UD["Amp.[gal・sec]"].max()
    #         max_fft_T_UD=fft_UD.loc[fft_UD['Amp.[gal・sec]'].idxmax()]["freq[Hz]"]
            
    #         record = pd.Series([max_fft_EW, max_fft_T_EW,
    #                             max_fft_NS, max_fft_T_NS,
    #                             max_fft_UD, max_fft_T_UD,
    #                             ],
    #                             index=fft_max.columns)
    #         fft_max = fft_max.append(record,ignore_index=True)
        
    #     station=pd.concat([station, fft_max], axis=1)
        
    
    
    # print(station)
    # station.to_csv(output_path, header=True, index=False, encoding="shift_jis")
    
    
if __name__ == "__main__":
    main()     
        
        