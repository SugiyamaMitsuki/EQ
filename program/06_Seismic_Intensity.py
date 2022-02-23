import os
import pandas as pd
import matplotlib.pyplot as plt
from config import Config
from calculus.sindo import Calculate_Intensity



def main():
    
    ## 設定
    conf=Config()
    
    ## 出力先フォルダの作成　速度
    try:
        os.mkdir(conf.sindo_file_dir)
    except:
        print("The folder exists.")
        print()
    ## 出力先フォルダの作成
    for organ in conf.organ_list: 
        try:
            print(f"{conf.sindo_file_dir}/{organ}")
            os.mkdir(f"{conf.sindo_file_dir}/{organ}")
        except:
            print("The folder exists.")
            print()
    
        
    
        
    
    
        
    for organ in conf.organ_list:
        acc_list = get_acc(f"{conf.acc_file_dir}/{organ}")
        acc_list = [s for s in acc_list if 'EW' in s]
        
        sindo_list=[]
        station_list=[]
        for acc_path in acc_list:
            print("観測点 ",acc_path.replace(".EW.acc.csv", ""))
            
            acc_input_path_EW = f"{conf.acc_file_dir}/{organ}/{acc_path}"
            acc_df_EW = pd.read_csv(acc_input_path_EW, encoding="shift_jis") 
            time = acc_df_EW["time[s]"].values
            Hertz=1/(time[1]-time[0])
            EW = acc_df_EW["acc[gal]"].values
            
            acc_input_path_NS = acc_input_path_EW.replace("EW", "NS")
            acc_df_NS = pd.read_csv(acc_input_path_NS, encoding="shift_jis") 
            NS = acc_df_NS["acc[gal]"].values
            
            acc_input_path_UD = acc_input_path_EW.replace("EW", "UD")
            acc_df_UD = pd.read_csv(acc_input_path_UD, encoding="shift_jis") 
            UD = acc_df_UD["acc[gal]"].values
            
            
            I = make_sindo(EW,NS,UD,Hertz)
            print("計測震度　",I)
            print()
            
            sindo_list.append(I)
            station_list.append(acc_path.replace(".EW.acc.csv", ""))
        
        
        output = pd.DataFrame()
        output[1]=station_list
        output[2]=sindo_list
        output.columns=["観測点コード", "計測震度"]
        output.to_csv(f"{conf.station_list_dir}/計測震度リスト_{organ}.csv", header=True, index=False, encoding="shift_jis")
            
            
            
def get_acc(input_path):
    files = []
    for file in os.listdir(input_path):
        base, ext = os.path.splitext(file)
        if ext == '.csv':
            files.append(file)
            print(file,"このファイルを変換します")
    return files
    
def make_sindo(EW,NS,UD,Hertz):
    
    sindo = Calculate_Intensity()    
    I = sindo.start_throw_data(EW,NS,UD,Hertz)
    return I


if __name__ == "__main__":
    main()     
        
        