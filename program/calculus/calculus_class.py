import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
import sys
import math
from scipy import signal
import warnings
warnings.simplefilter('ignore')

# from calculete_intensity import Calculate_Intensity
# from nigam_method import AnalysisCondition
# from nigam_method import Calculus

class Calculus(object):

    def __init__(self):
        None
        
    
    def calculus(self,time=None,wave=None,
                 differentiation_or_integration=0,times=0,taper_on=True,left=0.05,start=0.1,end=20,right=30):
        """
        t:
            時刻(DF)
        wave:
            地震動強さ(DF)
        differentiation_or_integration:
            0 なら微分　1　なら積分
        times:
            何階微積か
        
        return:
            計算後のデータ
        """
        
        data_length = len(wave)
        
        dt=time[1]-time[0]
        
        #基線補正した元データ(時間領域)
        wave = wave - wave.mean()  
        
        #FFTのために後続の0を付ける データの倍の長さの0を付けた後2の累乗にする
        flag = math.floor(math.log2(2*len(time)))  #切り捨て
        N=int(math.pow(2,flag+1))               #flagに1追加する
        t = np.arange(0, N*dt, dt)
        add_zeros = np.zeros(len(t)-len(wave))
        
        freq = np.linspace(0, 1.0/dt, N)  # 周波数軸
        
        wave=np.append(wave, add_zeros)
        
        
        
        # 高速フーリエ変換        
        fft = np.fft.fft(wave)/(N/2)   
        
        if taper_on != False:
            #周波数フィルターの配列番号
            f_left,f_start,f_end,f_right = int(left/(1/(N*dt))),int(start/(1/(N*dt))),int(end/(1/(N*dt))),int(right/(1/(N*dt)))
            #コサインテーパー作成     
            cos_taper = np.zeros(len(freq))        
            cos_taper[f_left:f_start] = [1/2*(1+math.cos( 2*math.pi/(2*(f_start-f_left))*(x*N*dt - f_start))) for x in freq[f_left:f_start] ]
            cos_taper[f_start:f_end] = 1
            cos_taper[f_end:f_right] = [1/2*(1+math.cos( 2*math.pi/(2*(f_right-f_end))*(x*N*dt -  f_end ))) for x in freq[f_end:f_right] ]
            
            #costaper
            fft=fft*cos_taper
        
        
        #周波数領域のデータから積分
        k=times
        if differentiation_or_integration == 1:
            k=k*(-1)
        
        # w=0の扱いは適当
        freq[0]=1     #0で割るとおかしくなっちゃう
        calculus_array = np.zeros(len(t))
        calculus_array = (1j*2*np.pi*freq)**k * fft 
        calculus_array[0]=0
        calculus_array[N//2+1:] = 0
        wave_out = np.fft.ifft(calculus_array.real)*(N/2)*4 
        wave_out=wave_out.real
        wave_out[N//2+1:]=0
        
        return t[:data_length],wave_out[:data_length]
    
    
    
    
    
    def fft(self,time,wave,taper_on=True,left=0.05,start=0.1,end=20,right=30,parzen_on=True,parzen_setting=0.1):
        
        dt=time[1]-time[0]
        
        #基線補正した元データ(時間領域)
        wave = wave - wave.mean()  
        
        #FFTのために後続の0を付ける データの倍の長さの0を付けた後2の累乗にする
        flag = math.floor(math.log2(2*len(time)))  #切り捨て
        N=int(math.pow(2,flag+1))               #flagに1追加する
        t = np.arange(0, N*dt, dt)
        add_zeros = np.zeros(len(t)-len(wave))
        
        freq = np.linspace(0, 1.0/dt, N)  # 周波数軸
        
        wave=np.append(wave, add_zeros)
        
        # 高速フーリエ変換
        # fft_data = np.fft.fft(acc)/(N/2)*(1/dt)    #逆変換するときは周期注意      
        fft = np.fft.fft(wave)/(N/2)
        
        phase=np.angle(fft)
        
        if taper_on:
            #周波数フィルターの配列番号
            f_left,f_start,f_end,f_right = int(left/(1/(N*dt))),int(start/(1/(N*dt))),int(end/(1/(N*dt))),int(right/(1/(N*dt)))
            #コサインテーパー作成     
            cos_taper = np.zeros(len(freq))        
            cos_taper[f_left:f_start] = [1/2*(1+math.cos( 2*math.pi/(2*(f_start-f_left))*(x*N*dt - f_start))) for x in freq[f_left:f_start] ]
            cos_taper[f_start:f_end] = 1
            cos_taper[f_end:f_right] = [1/2*(1+math.cos( 2*math.pi/(2*(f_right-f_end))*(x*N*dt -  f_end ))) for x in freq[f_end:f_right] ]
            #costaper
            fft=fft*cos_taper
        
        
        abs_fft=""
        #parzen window
        if parzen_setting:
            parzen_num=int(parzen_setting/(freq[1]-freq[0]))
            if parzen_num % 2 != 0:
                parzen_num+=1
            #奇数点のparzen
            w_parzen = signal.parzen(parzen_num)*parzen_setting
            abs_fft=np.convolve(w_parzen,np.abs(fft) , mode ='same') # valid same full  
        else:
            abs_fft=np.abs(fft)
            
        return freq[:N//2],abs_fft[:N//2],phase[:N//2]
    
        
        
        
        
        # wave=acc
        # EW_fft = np.fft.fft(EW_acc)/(N/2)
    
        # EW_fft=EW_fft*cos_taper
        
        # #周波数領域のデータから積分
        # # k=k
        # freq[0]=1     #0で割るとおかしくなっちゃう
        # calculus_array = np.zeros(len(t))
        # k=-1
        # calculus_array = (1j*2*np.pi*freq)**k * EW_fft 
        # calculus_array[0]=0
        #後ろ半分0にして実部だけにしてfftの時に割った大きさをかけて4倍
        # calculus_array[N//2+1:] = 0 
        # EW_vel = np.fft.ifft(calculus_array.real)*(N/2)*4 
        # EW_vel=EW_vel.real
        # EW_vel[N//2+1:]=0
            
       
        # output_EW = pd.DataFrame()
        # output_EW[1]=freq[:N//2]
        # output_EW[2]=np.abs(EW_fft)[:N//2]
        # output_EW.columns=["freq[Hz]", "abs[gal・sec]"]
            
        
            
        
            
            
            
    
    def add_AMP(DF,ampdata):
        
        cols = ['AMP']    
        df_add = pd.DataFrame(index=[], columns=cols)
    
        for df in DF.itertuples():
            Lon ,Lat = df[1],df[2]
            distance = np.empty(len(ampdata))
            distance = pow(ampdata[:,0]-float(Lon),2) + pow(ampdata[:,1]-float(Lat),2)
            min_arg = np.argmin(distance)
            amp = ampdata[min_arg][2]
        
            record = pd.Series([amp], index=df_add.columns)
            df_add = df_add.append(record, ignore_index=True)
            
        new_df = pd.concat([DF, df_add], axis=1)
        return new_df
    
  
    
        
if __name__ == '__main__':
    None
    
    
    
    
    
    
    
    
    
    
    