import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from config import Config



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
    print(station)
    # index	地点コード	観測点名	緯度[deg]	経度[deg]	サンプリング周波数	収録開始時刻	震央距離[km]	震源距離[km]	機関	地盤増幅度vs400m/s	AVS30	JCODE
    # 	最大加速度EW	最大加速度NS	最大加速度UD	最大加速度水平	最大加速度3成分	
    # 最大速度EW	最大速度NS	最大速度UD	最大速度水平	最大速度3成分	
    # 最大変位EW	最大変位NS	最大変位UD	最大変位水平	最大変位3成分	
    # 計測震度	最大加速度応答EW[cm/s/s]	最大加速度応答EW周期[s]	最大速度応答EW[cm/s/s]	最大速度応答EW周期[s]	最大変位応答EW[cm/s/s]	最大変位応答EW周期[s]	最大加速度応答NS[cm/s/s]	最大加速度応答NS周期[s]	最大速度応答NS[cm/s/s]	最大速度応答NS周期[s]	最大変位応答NS[cm/s/s]	最大変位応答NS周期[s]	最大加速度応答UD[cm/s/s]	最大加速度応答UD周期[s]	最大速度応答UD[cm/s/s]	最大速度応答UD周期[s]	最大変位応答UD[cm/s/s]	最大変位応答UD周期[s]	FFTEW[gal・sec]	FFTEW周波数[Hz]	FFTNS[gal・sec]	FFTNS周波数[Hz]	FFTUD[gal・sec]	FFTUD周波数[Hz]
    
    station=station[station["地盤増幅度vs400m/s"]<5]
    # station=station[station["最大加速度水平"]>1]
    station = station.sort_values('地盤増幅度vs400m/s', ascending=True)

    fig = draw_distance_attenuation_linear(xlabel="震源距離 [$km$]",
                            ylabel="計測震度",
                            clabel="地盤増幅度",
                            x=station["震源距離[km]"],
                            y=station["計測震度"],
                            c=station["地盤増幅度vs400m/s"],
                            label="計測震度",
                            xmin=10**1,
                            xmax=10**3,
                            ymin=0,
                            ymax=7,
                            Vel_or_Acc=False
                            )
    
    fig.savefig(f"{conf.drawwave_dir}/距離減衰_計測震度.png",bbox_inches='tight')
    fig.clf()
    fig.close()


    
    fig = draw_distance_attenuation(xlabel="震源距離 [$km$]",
                            ylabel="最大加速度水平 [$cm/s^{2}$]",
                            clabel="地盤増幅度",
                            x=station["震源距離[km]"],
                            y=station["最大加速度水平"],
                            c=station["地盤増幅度vs400m/s"],
                            label="距離減衰(地表)",
                            xmin=10**1,
                            xmax=10**3,
                            ymin=10**0,
                            ymax=10**3,
                            Vel_or_Acc="Acc"
                            )
    fig.savefig(f"{conf.drawwave_dir}/距離減衰_最大加速度水平.png",bbox_inches='tight')
    fig.clf()
    fig.close()
    
    fig = draw_distance_attenuation(xlabel="震源距離 [$km$]",
                            ylabel="最大速度水平 [$cm/s$]",
                            clabel="地盤増幅度",
                            x=station["震源距離[km]"],
                            y=station["最大速度水平"],
                            c=station["地盤増幅度vs400m/s"],
                            label="距離減衰(地表)",
                            xmin=10**1,
                            xmax=10**3,
                            ymin=10**-1,
                            ymax=10**2,
                            Vel_or_Acc="Vel"
                            )
    
    fig.savefig(f"{conf.drawwave_dir}/距離減衰_最大速度水平.png",bbox_inches='tight')
    fig.clf()
    fig.close()
    
    print()
    print(f"{conf.drawwave_dir}")
    
    
    
    
    
    
        
        
def draw_distance_attenuation(xlabel,ylabel,clabel,x,y,c,label,xmin,xmax,ymin,ymax,Vel_or_Acc):
    
    plt.figure(figsize=(10,10),dpi=300,facecolor='w',edgecolor='k')
    plt.axes().set_aspect('equal')
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
    
    plt.xscale('log'),plt.yscale('log') 
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    plt.xlim(xmin,xmax)
    plt.ylim(ymin,ymax)
    
    # plt.grid(True),plt.locator_params(axis='x',nbins=10),plt.locator_params(axis='y',nbins=10)
    plt.grid(axis='x', which='major',color='black',linestyle='-')
    plt.grid(axis='y', which='major',color='black',linestyle='-')
    
    conf=Config()
    ## 距離減衰式 作成
    PV_list=[]
    PA_list=[]
    dx,distance_max=0.2,1000
    distance = np.arange(1, distance_max, dx)
    for i in distance:
        Xeq=i
        PV=0
        PA=0
        # 等価震源距離
        if conf.Distance_attenuation_type=="Using_Equivalent_hypocentral_distance":
            PV = 10**(conf.a*conf.Mw + conf.h*conf.D + conf.d +conf.e -np.log10(Xeq) -0.002*Xeq)
            PA = 10**(conf.a_PA*conf.Mw + conf.h_PA*conf.D + conf.d_PA +conf.e_PA -np.log10(Xeq) -0.002*Xeq)
        # 断層最短震源距離
        elif conf.Distance_attenuation_type=="Shortest_fault_distance":
            PV = 10**(conf.a*conf.Mw + conf.h*conf.D + conf.d +conf.e -np.log10(Xeq+0.0028*10**(0.50*conf.Mw)) -0.002*Xeq)
            PA = 10**(conf.a_PA*conf.Mw + conf.h_PA*conf.D + conf.d_PA +conf.e_PA -np.log10(Xeq+0.0028*10**(0.50*conf.Mw)) -0.002*Xeq)
        PV_list.append(PV)
        PA_list.append(PA)
        # print(Xeq,PA)
    
    if Vel_or_Acc == "Vel":        
        plt.plot(distance, PV_list, label=f"司・翠川 距離減衰式Vs=600m/s\nMw{conf.Mw} 深さ{int(conf.depth)}km {conf.Fault_type}", c="black")
    elif Vel_or_Acc == "Acc": 
        plt.plot(distance, PA_list, label=f"司・翠川 距離減衰式Vs=600m/s\nMw{conf.Mw} 深さ{int(conf.depth)}km {conf.Fault_type}", c="black")
    plt.scatter(x, y,c=c,cmap='binary_r',label=label, alpha=1, edgecolor="black", s=15) # viridis
    plt.clim(0,3)
    
    plt.legend(bbox_to_anchor=(1, 1), loc='upper right', borderaxespad=0.8, fontsize=10)    
    plt.colorbar(shrink=0.5,orientation='horizontal',label=clabel,pad=0.06)
    
    
    return plt
    
        
def draw_distance_attenuation_linear(xlabel,ylabel,clabel,x,y,c,label,xmin,xmax,ymin,ymax,Vel_or_Acc):
    
    plt.figure(figsize=(10,10),dpi=300,facecolor='w',edgecolor='k')
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
    
    plt.xscale('log')#,plt.yscale('log') 
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    plt.xlim(xmin,xmax)
    plt.ylim(ymin,ymax)
    
    # plt.grid(True),plt.locator_params(axis='x',nbins=10),plt.locator_params(axis='y',nbins=10)
    plt.grid(axis='x', which='major',color='black',linestyle='-')
    plt.grid(axis='y', which='major',color='black',linestyle='-')
    
    conf=Config()
    ## 距離減衰式 作成
    PV_list=[]
    PA_list=[]
    dx,distance_max=0.2,1000
    distance = np.arange(1, distance_max, dx)
    for i in distance:
        Xeq=i
        PV=0
        PA=0
        # 等価震源距離
        if conf.Distance_attenuation_type=="Using_Equivalent_hypocentral_distance":
            PV = 10**(conf.a*conf.Mw + conf.h*conf.D + conf.d +conf.e -np.log10(Xeq) -0.002*Xeq)
            PA = 10**(conf.a_PA*conf.Mw + conf.h_PA*conf.D + conf.d_PA +conf.e_PA -np.log10(Xeq) -0.002*Xeq)
        # 断層最短震源距離
        elif conf.Distance_attenuation_type=="Shortest_fault_distance":
            PV = 10**(conf.a*conf.Mw + conf.h*conf.D + conf.d +conf.e -np.log10(Xeq+0.0028*10**(0.50*conf.Mw)) -0.002*Xeq)
            PA = 10**(conf.a_PA*conf.Mw + conf.h_PA*conf.D + conf.d_PA +conf.e_PA -np.log10(Xeq+0.0028*10**(0.50*conf.Mw)) -0.002*Xeq)
        PV_list.append(PV)
        PA_list.append(PA)
        # print(Xeq,PA)
    
    if Vel_or_Acc == "Vel":        
        plt.plot(distance, PV_list, label=f"司・翠川 距離減衰式Vs=600m/s\nMw{conf.Mw} 深さ{int(conf.depth)}km {conf.Fault_type}", c="black")
    elif Vel_or_Acc == "Acc": 
        plt.plot(distance, PA_list, label=f"司・翠川 距離減衰式Vs=600m/s\nMw{conf.Mw} 深さ{int(conf.depth)}km {conf.Fault_type}", c="black")
    plt.scatter(x, y,c=c,cmap='binary_r',label=label, alpha=1, edgecolor="black", s=15) # viridis
    plt.clim(0,3)
    
    plt.legend(bbox_to_anchor=(1, 1), loc='upper right', borderaxespad=0.8, fontsize=10)    
    plt.colorbar(shrink=0.5,orientation='horizontal',label=clabel,pad=0.06)
    label = label.replace('\n', '')
    
    return plt
        
        
        
        
    

if __name__ == "__main__":
    main()   
        
        