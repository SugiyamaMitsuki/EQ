import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

from config import Config
from calculus.nigam_method import AnalysisCondition
from calculus.nigam_method import Calculus



def main():
    ## 設定
    conf=Config()
    if conf.nigam==False:
        sys.exit()
        
    ## 出力先フォルダの作成　速度
    try:
        os.mkdir(conf.respec_file_dir)
    except:
        print("The folder exists.")
        print()
    ## 出力先フォルダの作成
    for organ in conf.organ_list: 
        try:
            print(f"{conf.respec_file_dir}/{organ}")
            os.mkdir(f"{conf.respec_file_dir}/{organ}")
        except:
            print("The folder exists.")
            print()
    
        
    for organ in conf.organ_list:
        acc_list = get_acc(f"{conf.acc_file_dir}/{organ}")
        
        for acc_path in acc_list:
            
            acc_input_path = f"{conf.acc_file_dir}/{organ}/{acc_path}"
            print(f"{acc_input_path}")
            acc_df = pd.read_csv(acc_input_path, encoding="shift_jis") 
            
            time = acc_df["time[s]"].values
            acc = acc_df["acc[gal]"].values
            
            
            df_spectrum = make_respec(acc,time[1]-time[0])
            
            print(df_spectrum)
            
            output_path = acc_input_path.replace("acc", "respec",2)
            
            save_spectrum(df_spectrum,output_path)
            # plt.plot(df_spectrum['period[sec]'],df_spectrum['acc[cm/s/s]'])
            # plt.show()
            # plt.plot(df_spectrum['period[sec]'],df_spectrum['vel[cm/s]'])
            # plt.show()
            # plt.plot(df_spectrum['period[sec]'],df_spectrum['dis[cm]'])
            # plt.show()
            
            
            
def get_acc(input_path):
    files = []
    for file in os.listdir(input_path):
        base, ext = os.path.splitext(file)
        if ext == '.csv':
            files.append(file)
            print(file,"このファイルを変換します")
    return files
    
def make_respec(inputacc,dt):
    conf=Config()
    #初期設定
    condition = AnalysisCondition(period_begin=conf.period_begin, period_end=conf.period_end,
                                  period_step_num=conf.period_step_num, damp_factor_h=conf.damp_factor_h, dt=dt)
    #計算
    calculus=Calculus()
    df_spectrum = calculus.spectrum(condition, inputacc)
    
    return df_spectrum

def save_spectrum(spectrum,output_path):
    spectrum.to_csv(output_path, header=True, index=False)


if __name__ == "__main__":
    main()     
        
        