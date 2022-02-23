import matplotlib.pyplot as plt
import pandas as pd
import os
import sys
import numpy as np
import sympy
import math
import cmath
import time
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN


class Calculate_Intensity(object):

    def __init__(self):
        None    
    

    def input_wave_for_FFT(self,data,Hertz):   
        
        dt = 1/Hertz
        input_wave = data[:] - data.mean()
        
        # FFTのために後続の0を付ける データの倍の長さの0を付けた後2の累乗にする
        flag = math.floor(math.log2(2*len(data))) #切り捨て
        N=int(math.pow(2,flag+1)) #flagに1追加する
        t = np.arange(0, N*dt, dt)
        add_zeros = np.zeros(len(t)-len(input_wave))
        input_wave=np.append(input_wave, add_zeros)
        
        
        # 計算に使用する周波数軸
        data_length = len(t) 
        df = (1/dt)/data_length 
        freq = np.linspace(0, 1.0/dt, data_length) #numpy.linspace(a, b, n)メソッドでa以上b以下で個数nの等差数列（配列）を作成ができます 
        #freq = np.arange(0, 1.0/dt, df)            #numpy.arrange(a, b, d)メソッドでa以上b未満で間隔dの等差数列を作ることができます。   
        
        return input_wave,t,dt,freq,df,N


    
    def start_throw_data(self,EW,NS,UD,Hertz): 
        """
        EW,NS,UDは一列データ
        """
    
        
        #入力地震動 gnu
        EW,t,dt,freq,df,N= self.input_wave_for_FFT(EW,Hertz)
        NS,t,dt,freq,df,N= self.input_wave_for_FFT(NS,Hertz)
        UD,t,dt,freq,df,N= self.input_wave_for_FFT(UD,Hertz)
        
        FFT_EW = np.fft.fft(EW)/(N/2)
        FFT_NS = np.fft.fft(NS)/(N/2)
        FFT_UD = np.fft.fft(UD)/(N/2)
        
        
        #周波数フィルターを用意
        X = freq/10.0
        FH = 1.0/np.sqrt(1.0 + 0.694*X**2 + 0.241*X**4+ 0.0557*X**6+ 0.009664*X**8+ 0.00134*X**10+ 0.000155*X**12) #ハイカット
        f0 = 0.5
        FL = np.sqrt(1.0 - np.exp(-(freq/f0)**3))                                                                  #ローカット
        freq[0]=1
        FC = np.sqrt(1.0/freq)                                                                                     #周波数特性
        freq[0]=0
        window = FH * FL * FC
        
        
        FFT_EW_output = FFT_EW * window
        FFT_EW_output[N//2+1:] = 0
        ew_ifft = np.fft.ifft(FFT_EW_output.real)*(N/2)*4 
        ew_ifft=ew_ifft.real
        ew_ifft[N//2+1:]=0
        
        FFT_NS_output = FFT_NS * window
        FFT_NS_output[N//2+1:] = 0
        ns_ifft = np.fft.ifft(FFT_NS_output.real)*(N/2)*4 
        ns_ifft=ns_ifft.real
        ns_ifft[N//2+1:]=0
        
        FFT_UD_output = FFT_UD * window
        FFT_UD_output[N//2+1:] = 0
        ud_ifft = np.fft.ifft(FFT_UD_output.real)*(N/2)*4 
        ud_ifft=ud_ifft.real
        ud_ifft[N//2+1:]=0
        
        Synthesis = np.sqrt(ew_ifft*ew_ifft + ns_ifft*ns_ifft + ud_ifft*ud_ifft)
        Synthesis_sort = sorted(Synthesis, reverse=True)
        a = Synthesis_sort[int(0.3/dt)]
        if a == 0:
            return 0
        I = 2 * np.log10( a )+ 0.94
        
        # I=Decimal(str(I)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        # I = str(I)[:3]
        
        return I
           
    
    def start_throw_data_2_ingredients(self,EW,NS,Hertz): 
        """
        EW,NS,UDは一列データ
        """
    
        self.file = [EW,NS]
        self.Hertz= Hertz
        
        #入力地震動 gnu
        EW,t,dt,freq,df,N= self.input_wave_for_FFT(self.file[0],self.Hertz)
        NS,t,dt,freq,df,N= self.input_wave_for_FFT(self.file[1],self.Hertz)
        
        FFT_EW = np.fft.fft(EW)/(N/2) 
        FFT_NS = np.fft.fft(NS)/(N/2) 
        
        #周波数フィルターを用意
        X = freq/10.0
        FH = 1.0/np.sqrt(1.0 + 0.694*X**2 + 0.241*X**4+ 0.0557*X**6+ 0.009664*X**8+ 0.00134*X**10+ 0.000155*X**12) #ハイカット
        f0 = 0.5
        FL = np.sqrt(1.0 - np.exp(-(freq/f0)**3))                                                                  #ローカット
        freq[0]=1
        FC = np.sqrt(1.0/freq)                                                                                     #周波数特性
        freq[0]=0
        window = FH * FL * FC
        
        FFT_EW_output = FFT_EW * window
        FFT_EW_output[N//2+1:] = 0
        ew_ifft = np.fft.ifft(FFT_EW_output.real)*(N/2)*4 
        ew_ifft=ew_ifft.real
        ew_ifft[N//2+1:]=0
        
        FFT_NS_output = FFT_NS * window
        FFT_NS_output[N//2+1:] = 0
        ns_ifft = np.fft.ifft(FFT_NS_output.real)*(N/2)*4 
        ns_ifft=ns_ifft.real
        ns_ifft[N//2+1:]=0
        
        
        Synthesis = np.sqrt(ew_ifft*ew_ifft + ns_ifft*ns_ifft)
        Synthesis_sort = sorted(Synthesis, reverse=True)
        a = Synthesis_sort[int(0.3/dt)]
        if a == 0:
            return 0
        I = 2 * np.log10( a )+ 0.94
        
        # I=Decimal(str(I)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        # I = str(I)[:3]
        
        return I
           
    
    def start_throw_data_1_ingredients(self,EW,Hertz): 
        """
        EW,NS,UDは一列データ
        """
    
        self.file = [EW]
        self.Hertz= Hertz
        
        #入力地震動 gnu
        EW,t,dt,freq,df,N= self.input_wave_for_FFT(self.file[0],self.Hertz)
        
        FFT_EW = np.fft.fft(EW)/(N/2) 
        
        #周波数フィルターを用意
        X = freq/10.0
        FH = 1.0/np.sqrt(1.0 + 0.694*X**2 + 0.241*X**4+ 0.0557*X**6+ 0.009664*X**8+ 0.00134*X**10+ 0.000155*X**12) #ハイカット
        f0 = 0.5
        FL = np.sqrt(1.0 - np.exp(-(freq/f0)**3))                                                                  #ローカット
        freq[0]=1
        FC = np.sqrt(1.0/freq)                                                                                     #周波数特性
        freq[0]=0
        window = FH * FL * FC
        
        FFT_EW_output = FFT_EW * window
        FFT_EW_output[N//2+1:] = 0
        ew_ifft = np.fft.ifft(FFT_EW_output.real)*(N/2)*4 
        ew_ifft=ew_ifft.real
        ew_ifft[N//2+1:]=0
        
        
        Synthesis = np.sqrt(ew_ifft*ew_ifft)
        Synthesis_sort = sorted(Synthesis, reverse=True)
        a = Synthesis_sort[int(0.3/dt)]
        if a == 0:
            return 0
        I = 2 * np.log10( a )+ 0.94
        
        # I=Decimal(str(I)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        # I = str(I)[:3]
        
        return I
           
    
    
    
    
    
    
    
if __name__ == '__main__': 
    file_list = ["SZO012.EW.acc","SZO012.NS.acc","SZO012.UD.acc"]