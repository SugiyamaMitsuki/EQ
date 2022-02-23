import numpy as np
import pandas as pd
import cartopy.crs as ccrs
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
import os
from config import Config

"""
https://qiita.com/k_reiji/items/528d8eedaa2d6f92a4fe

https://www.mri-jma.go.jp/Dep/sei/fhirose/plate/PlateData.html
"""


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

    lon = station["経度[deg]"]
    lat = station["緯度[deg]"]
    c = station["最大速度水平"]
     
    fig = plt.figure(figsize=(5, 5), facecolor="white", tight_layout=True)
    ax = fig.add_subplot(111, projection=ccrs.Mercator(central_longitude=140.0), facecolor="white")
    ax.set_global()
    ax.coastlines()
    # ax.set_extent([138, 142, 34, 38], crs=ccrs.PlateCarree())
    ax.set_extent([130, 136, 30, 36], crs=ccrs.PlateCarree())
    gl = ax.gridlines(draw_labels=True)
    gl.xlocator = mticker.FixedLocator(np.arange(120, 150.1, 0.5))
    gl.ylocator = mticker.FixedLocator(np.arange(20, 50.1, 0.5))

    im = ax.scatter(lon, lat, c=c,s=10 ,vmin=0, vmax=max(c),transform=ccrs.PlateCarree(),cmap='viridis',alpha=1, edgecolor="black" , label  ="test") # viridis binary_r
    fig.colorbar(im,shrink=0.5,orientation='horizontal',label="clabel",pad=0.06)
    

    plt.show()

if __name__ == "__main__":
    main()     
        
        