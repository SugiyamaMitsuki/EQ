# -*- coding: utf-8 -*-
import math as mt
import pandas as pd
import sys

# https://qiita.com/yuusei/items/549402a80efd7e7192ef
class LatLon2Grid:
    def __init__(self):
        None
    
    def grid1st(self, lon, lat):  # 1次メッシュ(4桁) 分割なし
        return int(mt.floor(lat*1.5)) * 100 + int(mt.floor(lon-100))

    def grid2nd(self, lon, lat):  # 2次メッシュ(6桁) 8分割
       return (int(mt.floor(lat*12       / 8))   * 10000 + int(mt.floor((lon-100)*8         / 8))  * 100   +   
               int(mt.floor(lat*12 %  8     ))   * 10    + int(mt.floor((lon-100)*8))  %  8               )  

    def grid3rd(self, lon, lat):  # 3次メッシュ(8桁) 8分割x10分割=80分割
        return (int(mt.floor(lat*120      / 80)) * 1000000 + int(mt.floor((lon-100))             ) * 10000 +  # 1次メッシュ
                int(mt.floor(lat*120 % 80 / 10)) * 1000    + int(mt.floor((lon-100)*80 % 80 / 10)) * 100 +    # 2次メッシュ
                int(mt.floor(lat*120 % 10))      * 10      + int(mt.floor((lon-100)*80)) % 10               ) 

    def grid4th(self, lon, lat):  # 4次メッシュ(9桁) 8分割x10分割x2分割=160分割
        return (int(mt.floor(lat*240       / 160)) * 10000000 + int(mt.floor((lon-100)*160       / 160)) * 100000 +    # 1次メッシュ
                int(mt.floor(lat*240 % 160 / 20))  * 10000    + int(mt.floor((lon-100)*160 % 160 / 20))  * 1000   +    # 2次メッシュ
                int(mt.floor(lat*240 % 20  / 2))   * 100      + int(mt.floor((lon-100)*160 % 20  / 2))   * 10     +    # 3次メッシュ
                int(mt.floor(lat*240)) % 2         * 2        + int(mt.floor((lon-100)*160)) % 2                  + 1) # 4次メッシュ
    
    def grid250m(self, lon, lat):
        # https://www.stat.go.jp/data/mesh/pdf/gaiyo1.pdf
        p=int(lat*60/40)
        a=(lat*60)%40
        
        q=int(a/5)
        b=a%5
        
        r=int(b*60/30)
        c=(b*60)%30
        
        s=int(c/15)
        d=c%15
        
        t=int(d/7.5)
        f=d%7.5
        
        # あ=int(f/3.75)
        
        u=int(lon-100)
        f=lon-100-u
        
        v=int(f*60/7.5)
        g=f*60%7.5
        
        w=int(g*60/45)
        h=g*60%45
        
        x=int(h/22.5)
        i=h%22.5
        
        y=int(i/11.25)
        # j=i%11.25
        # い=int(j/5.625)
        
        m=s*2+x+1
        n=t*2+y+1
        # o=あ*2+い+1
        return( str(p)+str(u)+str(q)+str(v)+str(r)+str(w)+str(m)+str(n))
    
    def get_latlon(self,meshCode):

        # 文字列に変換
        meshCode = str(meshCode)
    
        # １次メッシュ用計算
        code_first_two = meshCode[0:2]
        code_last_two = meshCode[2:4]
        code_first_two = int(code_first_two)
        code_last_two = int(code_last_two)
        lat  = code_first_two * 2 / 3
        lon = code_last_two + 100
    
        if len(meshCode) > 4:
            # ２次メッシュ用計算
            if len(meshCode) >= 6:
                code_fifth = meshCode[4:5]
                code_sixth = meshCode[5:6]
                code_fifth = int(code_fifth)
                code_sixth = int(code_sixth)
                lat += code_fifth * 2 / 3 / 8
                lon += code_sixth / 8
    
            # ３次メッシュ用計算
            if len(meshCode) == 8:
                code_seventh = meshCode[6:7]
                code_eighth = meshCode[7:8]
                code_seventh = int(code_seventh)
                code_eighth = int(code_eighth)
                lat += code_seventh * 2 / 3 / 8 / 10
                lon += code_eighth / 8 / 10
    
        return lon, lat
            

if __name__ == "__main__":

    # lon = 141.3157
    # lat = 43.1714
    # print('1次メッシュ： ', latlon2grid.grid1st(lon, lat))  
    # print('2次メッシュ： ', latlon2grid.grid2nd(lon, lat))  
    # print('基準地域メッシュ： ', latlon2grid.grid3rd(lon, lat))  
    # print('4次メッシュ： ', latlon2grid.grid4th(lon, lat))  
    # print('10桁 ', latlon2grid.grid25m(lon, lat)) 
    
    # 観測点temp.csv に エクセルからlon lat name　をコピー
    # Z-V3-JAPAN-AMP-VS400_M250.csvはJ-SHISからダウンロードした
    # Q-GISのpointssamplingtoosと同じ操作であることを確認済
    
    stations = pd.read_csv('KiK-net観測点.csv',header = 0,encoding="shift_jis")
    Mesh_data_250m = pd.read_csv('Z-V3-JAPAN-AMP-VS400_M250.csv',header=None,skiprows=7)
    
    print(stations)
    print(Mesh_data_250m)
    
    cols = ['経度','緯度','メッシュコード','JCODE','AVS','ARV','観測点名']
    output = pd.DataFrame(index=[], columns=cols) 
    
    for i,A in enumerate(stations.itertuples()):
        # print(A)
        name=A[1]
        lon = A[4]
        lat = A[3]
        JCODE,AVS,ARV=0,0,0
        # print(lon,lat)
        if str(lon).replace('.', '').isdecimal() and lon > 0 and lat > 0:
            mesh = latlon2grid.grid250m(lon, lat)
            index=Mesh_data_250m[Mesh_data_250m[0]==int(mesh)].index
            # print(index)
            if index > 1:
                grep_data = Mesh_data_250m.loc[index]
                # print(grep_data)
                # print(grep_data.columns)
                # print(grep_data.index)
                JCODE=int(grep_data[1])
                AVS=float(grep_data[2])
                ARV=float(grep_data[3])
        else:
            lon,lat=0,0
            mesh = 0
            
        print(i,name,lon,lat,mesh,"JCODE",JCODE,"AVS",AVS,"ARV",ARV)
        
        record = pd.Series([lon,lat,mesh,JCODE,AVS,ARV,name] ,  index=output.columns)
        output = output.append(record,ignore_index=True)
        
    
    print(output)
    output.to_csv("KiK-net250mメッシュの表層地盤情報割り当て後.csv",encoding="shift_jis")
    
    
    
    
    
    
    