import sys, os, json
import math
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, Future, wait
import matplotlib.pyplot as plt

# 解析条件クラス
class AnalysisCondition:
    def __init__(self, period_begin, period_end, period_step_num, damp_factor_h, dt):
        self.period_begin = float(period_begin)
        self.period_end = float(period_end)
        self.period_step_num = int(period_step_num)
        self.damp_factor_h = float(damp_factor_h)
        self.dt = float(dt)

#計算クラス
class Calculus:
    def __init__(self):
        None
    # Nigam・Jennings法による応答計算
    def nigam_jennings(self,period, g_acc, dt, h):
        if period == 0:
            _period, acc_max, vel_max, dis_max= 0.0, np.max(np.abs(g_acc)), 0, 0 
            return _period, acc_max, vel_max, dis_max
        
        period=round(period,2)
        # print("period",period,"dt", dt,"h", h)
        w = 2.0 * np.pi / period
        h_ = np.sqrt(1.0 - h * h)
        w_ = h_ * w
        ehw = np.exp(-h * w * dt);
        hh_ = h / h_
        sinw_ = np.sin(w_*dt)
        cosw_ = np.cos(w_ * dt)
        hw1 = (2.0 * h * h - 1.0) / (w * w * dt)
        hw2 = h / w
        hw3 = (2.0 * h) / (w * w * w * dt)
        ww = 1.0 / (w * w)
        a11 = ehw * (hh_ * sinw_ + cosw_)
        a12 = ehw / w_ * sinw_
        a21 = -w / h_ * ehw * sinw_
        a22 = ehw * (cosw_ - hh_ * sinw_)
        b11 = ehw * ((hw1 + hw2) * sinw_ / w_ + (hw3 + ww) * cosw_) - hw3
        b12 = -ehw * (hw1 * sinw_ / w_ + hw3 * cosw_) - ww + hw3
        b21 = ehw * ((hw1 + hw2) * (cosw_ - hh_ * sinw_) - (hw3 + ww) * (w_ * sinw_ + h * w * cosw_)) + ww / dt
        b22 = -ehw * (hw1 * (cosw_ - hh_ * sinw_) - hw3 * (w_ * sinw_ + h * w * cosw_)) - ww / dt
        
        b_acc=np.zeros_like(g_acc)
        b_vel=np.zeros_like(g_acc)
        b_dis=np.zeros_like(g_acc)
        b_acc_abs=np.zeros_like(g_acc)
        
        b_acc[0] = -g_acc[0]
        length=len(g_acc)
        for i  in range(1,length):
            # print(i)
            b_dis[i] = a11 * b_dis[i - 1] + a12 * b_vel[i - 1] + b11 * g_acc[i - 1] + b12 * g_acc[i]
            b_vel[i] = a21 * b_dis[i - 1] + a22 * b_vel[i - 1] + b21 * g_acc[i - 1] + b22 * g_acc[i]
            b_acc[i] = -g_acc[i] - 2.0 * h * w * b_vel[i] - w * w * b_dis[i]
            b_acc_abs[i] = b_acc[i] + g_acc[i]
        
        dis_max, vel_max, acc_max = np.max(np.abs(b_dis)),np.max(np.abs(b_vel)),np.max(np.abs(b_acc_abs))
        # print(dis_max, vel_max, acc_max)
        return period, acc_max, vel_max, dis_max
    
    
    # 応答スペクトル計算
    def spectrum(self,condition, g_acc):
        # 初期化
        df = pd.DataFrame([], columns=['period[sec]', 'acc[cm/s/s]', 'vel[cm/s]', 'dis[cm]'])
        periods = np.linspace(condition.period_begin,condition.period_end,num=condition.period_step_num)
        h = condition.damp_factor_h
        dt = condition.dt
        # result = [nigam_jennings(period, g_acc, dt, h) for period in periods]
            
        # for period in periods[1:]:
        #     _period, _acc, _vel, _dis= Calculus.nigam_jennings(self,period, g_acc, dt, h)        
        #     record = pd.Series([_period, _acc, _vel, _dis], index=df.columns)
        #     df = df.append(record, ignore_index=True)
        
        with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
            print("nigam法の計算をします",'並列計算：CPU', os.cpu_count())
            futures = [executor.submit(Calculus.nigam_jennings,self, period, g_acc, dt, h) for period in periods]
            df['period[sec]'] = [future.result()[0] for future in futures]
            df['acc[cm/s/s]'] = [future.result()[1] for future in futures]
            df['vel[cm/s]'] = [future.result()[2] for future in futures]
            df['dis[cm]'] = [future.result()[3] for future in futures]    
        # print(df)
        return df
    

if __name__ == "__main__":
    organ="JMA"
    filename="41332"
    EW_acc=pd.read_csv("../acc/{}/{}.EW.acc.csv".format(organ,filename))
    dt=EW_acc["time"][1]-EW_acc["time"][0]
    inputacc=EW_acc["acc[cm/s/s]"]
    
    EW = pd.read_table("test.txt", skiprows=1)
    print(EW)
    t=EW.iloc[:,0]
    EW_acc=EW.iloc[:,1]
    print(EW_acc)
    inputacc=EW_acc
    
    # print(acc)
    
    #初期設定
    condition = AnalysisCondition(period_begin=0, period_end=10, period_step_num=101, damp_factor_h=0.05, dt=dt)
    #計算
    calculus=Calculus()
    df_spectrum = calculus.spectrum(condition, inputacc)
    
    print(df_spectrum)
    
    plt.plot(df_spectrum['period[sec]'],df_spectrum['acc[cm/s/s]'])
    plt.show()
    plt.plot(df_spectrum['period[sec]'],df_spectrum['vel[cm/s]'])
    plt.show()
    plt.plot(df_spectrum['period[sec]'],df_spectrum['dis[cm]'])
    plt.show()