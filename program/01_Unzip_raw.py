import os
import zipfile
import tarfile
import shutil
import wget

from config import Config


def main():
    
    conf=Config()
    
    raw_path = str(conf.folder).replace("program","wave/raw")

    ## 出力先フォルダの作成
    for organ in conf.organ_list:
        temp_path = f"{raw_path}/{organ}"
        print("Create the following folder")
        print(temp_path)
        try:
            os.mkdir(temp_path)
        except:
            print("The folder exists.")
            print()
    
    
    ## 解凍
    
    ## 気象庁の解凍
    if "JMA" in conf.organ_list:
        # ファイル名
        input_path = f"{raw_path}/{conf.jma_raw}"
        output_path = f"{raw_path}/JMA"
        ext = input_path.split(".")[-1] #拡張子

        # 解凍
        defrost(input_path,output_path,ext)
        print()

        ## 解凍するとoutput_pathの下のaccフォルダに保存されるため移動し不要ファイルを削除
        _dir = output_path+"/acc/"
        JMA_file=[]
        try:    
            for file in os.listdir(_dir):
                base, ext = os.path.splitext(file)
                if ext == '.csv':
                    JMA_file.append(file)
                    shutil.move(_dir+file, output_path)
        except Exception as e:
            print(str(e))
        try:
            shutil.rmtree(_dir)
            os.remove(output_path+"/level.csv")
        except Exception as e:
            print(str(e))

    ## K-NET　& KiK-netは一つのtarファイルに圧縮されている
    if "K-NET" and "KiK-net" in conf.organ_list:
        input_path = f"{raw_path}/{conf.kne_kik_raw}"
        output_path = raw_path 
        defrost(input_path,output_path,"tar")
        print()

    ## K-NETの解凍
    if "K-NET" in conf.organ_list:
        input_path =  f"{raw_path}/{conf.knet_raw}"
        output_path = f"{raw_path}/K-NET"
        defrost(input_path,output_path,"tar")
        remove_ps(output_path)
        print()
        
    ## KiK-netの解凍
    if "KiK-net" in conf.organ_list:
        input_path =  f"{raw_path}/{conf.kik_raw}"
        output_path = f"{raw_path}/KiK-net"
        defrost(input_path,output_path,"tar")
        remove_ps(output_path)
        print()
        
    
    ## 自治体のデータをwgetで取得
    if "LG" in conf.organ_list:

        output_path = f"{raw_path}/LG"
        
        # スクレイピング
        url = f'https://www.data.jma.go.jp/svd/eqev/data/kyoshin/jishin/{conf.LG_URL_key}/index.html'
        print(url)
        html = wget.download(url,out=raw_path) #ここまででraw_pathにディレクトリにindex.htmlがダウンロードされる
        with open(html,encoding="utf-8_sig") as f:
            for i,line in enumerate(f):
                if "csv" in line :
                    temp= [line for line in str(line).split('"') if 'csv' in line] 
                    key=temp[0].replace("data/","")
                    print(key)
                    stationdata_url = f"https://www.data.jma.go.jp/svd/eqev/data/kyoshin/jishin/{conf.LG_URL_key}/data/{key}"         
                    print(stationdata_url)
                    wget.download(stationdata_url, out=f"{output_path}/{key}")
                    print()

        # wget https://www.data.jma.go.jp/svd/eqev/data/kyoshin/jishin/1806180758_osakafu-hokubu/index.html
        # cat index.html | grep data |grep csv|cut -c22-45>LG_data.txt
        # cat LG_data.txt|while read line
        # do
        #     	word=($line)
        #     	data=${word[0]}
        # 	echo $data
        # 	wget https://www.data.jma.go.jp/svd/eqev/data/kyoshin/jishin/1806180758_osakafu-hokubu/data/$data>./LocalGovernment/$data
        # done


def defrost(input_path,output_path,option):
    print(f"{option}ファイルを解凍する")
    print(f"入力{input_path}\n出力{output_path}")
    
    if option == "zip":
        with zipfile.ZipFile(input_path) as existing_zip:
            print(existing_zip.filename) # zipファイル名の表示
            existing_zip.printdir()      # zipファイルに含まれているファイル名をsys.stdoutに出力
            existing_zip.extractall(output_path) #output_pathに解凍する
            
    elif option == "tar":
        with tarfile.open(input_path, 'r:*') as tar:
            tar.extractall(output_path)

def remove_ps(path):
    ## 余計なファイルの削除
    try:
        for file in os.listdir(path):
            base, ext = os.path.splitext(file)
            if ext == '.gz':
                os.remove(path+"/"+file)
    except Exception as e:
        print(str(e))



if __name__ == "__main__":
    main()
    
    