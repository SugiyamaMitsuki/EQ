import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime,timedelta
from sympy import dirichlet_eta
 
from config import Config
from calculus.calculus_class import Calculus
from meshcode_lonlat.lonlat_to_meshcode import LatLon2Grid


def main():
    ## 設定
    conf=Config()
    
   
    ## 出力先フォルダの作成　速度
    try:
        os.mkdir(conf.drawwave_dir)
    except:
        print("The folder exists.")
        print()
    
    station = pd.read_csv(f"{conf.station_list_dir}/{conf.station_outputname}", encoding="shift_jis")
    station = station.sort_values(conf.ascending_key, ascending=conf.ascending)
    station=station[:conf.head_num]
    
    
    ## 加速度波形　速度波形　変位波形
    for direction in ["EW","NS","UD"]:
        for organ,code in zip(station["機関"],station["地点コード"]):
            #print(f"{organ} {code} {direction}")
            

            acc_path=f"{conf.wave_path}/acc/{organ}/{code}.{direction}.acc.csv"
            acc = pd.read_csv(acc_path, encoding="shift_jis") 
            # acc=acc[acc["time[s]"]<60]
            plt_acc = draw_wave_graph(xlabel="時間 [s]",
                                    ylabel="加速度 [gal]")
            plt_acc.plot(acc["time[s]"],acc["acc[gal]"],linewidth=1,color='black')
            plt_acc.savefig(f"{conf.drawwave_dir}/acc_{organ}_{code}_{direction}.png",bbox_inches='tight',color='black')
            plt_acc.clf()
            plt_acc.close()
            

            vel_path=f"{conf.wave_path}/vel/{organ}/{code}.{direction}.vel.csv"
            vel = pd.read_csv(vel_path, encoding="shift_jis") 
            # vel=vel[vel["time[s]"]<60]
            plt_vel = draw_wave_graph(xlabel="時間 [s]",
                    ylabel="速度 [kine]")
            plt_vel.plot(vel["time[s]"],vel["vel[kine]"],linewidth=1,color='black')
            plt_vel.savefig(f"{conf.drawwave_dir}/vel_{organ}_{code}_{direction}.png".format(organ,code,direction),bbox_inches='tight',color='black')
            plt_vel.clf()
            plt_vel.close()
            

            dis_path=f"{conf.wave_path}/dis/{organ}/{code}.{direction}.dis.csv"
            dis = pd.read_csv(dis_path, encoding="shift_jis") 
            # dis=dis[dis["time[s]"]<60]
            plt_dis = draw_wave_graph(xlabel="時間 [s]",
                    ylabel="変位 [gal]")
            plt_dis.plot(dis["time[s]"],dis["dis[cm]"],linewidth=1,color='black')
            plt_dis.savefig(f"{conf.drawwave_dir}/dis_{organ}_{code}_{direction}.png".format(organ,code,direction),bbox_inches='tight',color='black')
            plt_dis.clf()
            plt_dis.close()
            
            
    ## FFT
    for organ,code in zip(station["機関"],station["地点コード"]):
        
        print(f"{organ} {code} ")

        freq_max = 10
        
        fft_abs_EW_path = f"{conf.wave_path}/fft/{organ}/{code}.EW.abs.csv"
        fft_EW = pd.read_csv(fft_abs_EW_path, encoding="shift_jis")
        fft_EW = fft_EW[fft_EW["freq[Hz]"]<freq_max]
        fft_freq_EW = fft_EW["freq[Hz]"]
        fft_abs_EW = fft_EW["Amp.[gal・sec]"]
        
        fft_abs_NS_path = f"{conf.wave_path}/fft/{organ}/{code}.NS.abs.csv"
        fft_NS = pd.read_csv(fft_abs_NS_path, encoding="shift_jis")
        fft_NS = fft_NS[fft_NS["freq[Hz]"]<freq_max]
        fft_freq_NS = fft_NS["freq[Hz]"]
        fft_abs_NS = fft_NS["Amp.[gal・sec]"]
        
        fft_abs_UD_path = f"{conf.wave_path}/fft/{organ}/{code}.UD.abs.csv"
        fft_UD = pd.read_csv(fft_abs_UD_path, encoding="shift_jis")
        fft_UD = fft_UD[fft_UD["freq[Hz]"]<freq_max]
        fft_freq_UD = fft_UD["freq[Hz]"]
        fft_abs_UD = fft_UD["Amp.[gal・sec]"]
        
        plt_fft_abs = draw_fft_graph(xlabel="周波数 [Hz]",
                                  ylabel="加速度フーリエスペクトル [gal・sec]")
        
        plt_fft_abs.plot(fft_freq_EW,fft_abs_EW,linewidth=1,label="EW",color='red')
        plt_fft_abs.plot(fft_freq_NS,fft_abs_NS,linewidth=1,label="NS",color='blue')
        plt_fft_abs.plot(fft_freq_UD,fft_abs_UD,linewidth=1,label="UD",color='black')
        plt_fft_abs.legend(bbox_to_anchor=(1, 1), loc='upper right', borderaxespad=0.8, fontsize=10)   
        
        # plt_fft_abs.yscale('log')

        plt_fft_abs.savefig(f"{conf.drawwave_dir}/FFT_abs_{organ}_{code}.png",bbox_inches='tight',color='black')
        plt_fft_abs.clf()
        plt_fft_abs.close()
            
        
            
            
            
            
            
            
            
            
        
def draw_wave_graph(xlabel,ylabel):
    
    plt.figure(figsize=(15,5),dpi=300,facecolor='w',edgecolor='k')
    # plt.axes().set_aspect('equal')
    plt.rcParams['font.size'] = 12
    plt.rcParams['font.family']= 'sans-serif'
    plt.rcParams['font.family'] = 'Hiragino Sans' #日本語使用可
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

def draw_fft_graph(xlabel,ylabel):
    plt.figure(figsize=(8,4),dpi=300,facecolor='w',edgecolor='k')
    # plt.axes().set_aspect('equal')
    plt.rcParams['font.size'] = 12
    plt.rcParams['font.family']= 'sans-serif'
    plt.rcParams['font.family'] = 'Hiragino Sans' #日本語使用可
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
    
    # plt.xscale('log')
    # plt.yscale('log')
    
    
    return plt
    
   
    
if __name__ == "__main__":
    main()     
        
        