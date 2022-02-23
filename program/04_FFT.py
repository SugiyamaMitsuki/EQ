import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

from config import Config
from calculus.calculus_class import Calculus

def main():
    
    ## 設定
    conf=Config()
    
    ## 出力先フォルダの作成　速度
    try:
        os.mkdir(conf.fft_file_dir)
    except:
        print("The folder exists.")
        print()
    ## 出力先フォルダの作成
    for organ in conf.organ_list: 
        try:
            print(f"{conf.fft_file_dir}/{organ}")
            os.mkdir(f"{conf.fft_file_dir}/{organ}")
        except:
            print("The folder exists.")
            print()




    for organ in conf.organ_list:
        acc_list = get_acc(f"{conf.acc_file_dir}/{organ}")
        
        for acc_path in acc_list:
            print(acc_path)
            
            acc_input_path = f"{conf.acc_file_dir}/{organ}/{acc_path}"
            acc_df = pd.read_csv(acc_input_path, encoding="shift_jis") 
            
            time = acc_df["time[s]"].values
            acc = acc_df["acc[gal]"].values
            
            freq,abs_fft,phase = make_ftt(time,acc)
            
            output_path = acc_input_path.replace("acc", "fft",2)
            save_fft(freq,abs_fft,phase,output_path)
            
            # df = freq[1]-freq[0]
            # num = int(10/df)
            # plt.plot(freq[:num],abs_fft[:num])
            # plt.show()
            # plt.plot(freq[:num],phase[:num])
            # plt.show()
            
            
            
def get_acc(input_path):
    files = []
    for file in os.listdir(input_path):
        base, ext = os.path.splitext(file)
        if ext == '.csv':
            files.append(file)
            # print(file,"このファイルを変換します")
    return files
    
def make_ftt(time,acc):
    conf=Config()
    #計算
    calculus=Calculus()
    
    freq,abs_fft,phase = calculus.fft(
                                        time=time,wave=acc,
                                        taper_on=conf.taper_on,
                                        left=conf.left,start=conf.start,
                                        end=conf.end,
                                        right=conf.right,
                                        parzen_on=conf.parzen_on,
                                        parzen_setting=conf.parzen_setting
                                    )
    
    return freq,abs_fft,phase

def save_fft(freq,abs_fft,phase,output_path):
    
    output = pd.DataFrame()
    output[1]=freq
    output[2]=abs_fft
    output.columns=["freq[Hz]", "Amp.[gal・sec]"]
    output_path = output_path.replace("fft.csv","abs.csv")
    output.to_csv(output_path, header=True, index=False, encoding="shift_jis")
    
    output = pd.DataFrame()
    output[1]=freq
    output[2]=phase
    output.columns=["freq[Hz]", "phase[-]"]
    output_path = output_path.replace("abs.csv","phase.csv")
    output.to_csv(output_path, header=True, index=False, encoding="shift_jis")
    

if __name__ == "__main__":
    main()     
        
        