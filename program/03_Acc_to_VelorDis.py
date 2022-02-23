import os
import pandas as pd
import matplotlib.pyplot as plt

from config import Config
from calculus.calculus_class import Calculus




def main():
    
    ## 設定
    conf=Config()
    
    
    ## 出力先フォルダの作成　速度
    try:
        os.mkdir(conf.vel_file_dir)
    except:
        print("The folder exists.")
        print()
    ## 出力先フォルダの作成
    for organ in conf.organ_list: 
        try:
            print(f"{conf.vel_file_dir}/{organ}")
            os.mkdir(f"{conf.vel_file_dir}/{organ}")
        except:
            print("The folder exists.")
            print()

    ## 出力先フォルダの作成 変位
    try:
        os.mkdir(conf.dis_file_dir)
    except:
        print("The folder exists.")
        print()
    ## 出力先フォルダの作成
    for organ in conf.organ_list: 
        try:
            print(f"{conf.dis_file_dir}/{organ}")
            os.mkdir(f"{conf.dis_file_dir}/{organ}")
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
            
            if conf.make_vel:
                t,vel = acc_to_vel(time=time,
                                   acc=acc)
                output_vel_path = acc_input_path.replace("acc", "vel",2)
                print(f"速度 {output_vel_path}")
                save_vel(t,vel,output_vel_path)

            if conf.make_dis:
                t,dis = acc_to_dis(time=time,
                                   acc=acc)
                output_dis_path = acc_input_path.replace("acc", "dis",2)
                print(f"変位 {output_dis_path}")
                save_dis(t,dis,output_dis_path)


            
            # plt.plot(acc_df["time[s]"].values,acc_df["acc[gal]"].values)
            # plt.show()
            # plt.plot(t,vel)
            # plt.show()
            # plt.plot(t,dis)
            # plt.show()
            
            
def get_acc(input_path):
    files = []
    for file in os.listdir(input_path):
        base, ext = os.path.splitext(file)
        if ext == '.csv':
            files.append(file)
            #print(file,"このファイルを変換します")
    return files
    
    
def acc_to_vel(time,acc):
    calc = Calculus()
    conf=Config()
    t,vel = calc.calculus(time=time,wave=acc,
                          differentiation_or_integration=1, #微分=0or積分=1
                          times=1, # 微分　積分の階数
                          taper_on=conf.taper_on,
                          left=conf.left,start=conf.start,end=conf.end,right=conf.right,
                          )
    return t,vel

def acc_to_dis(time,acc):
    calc = Calculus()
    conf=Config()
    t,dis = calc.calculus(time=time,wave=acc,
                          differentiation_or_integration=1, #微分=0or積分=1
                          times=2, # 微分　積分の階数
                          taper_on=conf.taper_on,
                          left=conf.left,start=conf.start,end=conf.end,right=conf.right,
                          )
    return t,dis


def save_vel(t,vel,output_vel_path):
    output = pd.DataFrame()
    output[1]=t
    output[2]=vel
    output.columns=["time[s]", "vel[kine]"]
    output.to_csv(output_vel_path, header=True, index=False)
    
def save_dis(t,dis,output_dis_path):
    output = pd.DataFrame()
    output[1]=t
    output[2]=dis
    output.columns=["time[s]", "dis[cm]"]
    output.to_csv(output_dis_path, header=True, index=False)

if __name__ == "__main__":
    main()     
        
        