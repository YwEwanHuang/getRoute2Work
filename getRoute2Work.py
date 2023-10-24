# -*- coding: utf-8 -*-
import urllib.request 
from urllib import parse 
import json 
import webbrowser
from datetime import datetime, timedelta


# 使用高德地图API的路径规划功能
# 分别计算从<输入地址>分别到上班地方
# 使用公共交通/驾车通勤的时间

# 通过 https://lbs.amap.com/tools/picker
# 查询工作地点经纬度坐标
work_place_info = [
                    ['Latitude and longitude', 'name', 'tag'],
                ]


# API key
key = ''

# For routing
bus_url   = 'https://restapi.amap.com/v3/direction/transit/integrated?' 
drive_url = 'https://restapi.amap.com/v3/direction/driving/integrated?' 

next_workday = datetime.today()
while next_workday.weekday() > 4: #[0,1,2,3,4] means Monday to Friday
    next_workday += timedelta(days=1)
next_workday = next_workday.strftime('%Y-%m-%d') + "%7C07-00"


#%%
def formatTime(sec)->int:
    '''
    transfer seconds to Hours:Minutes
    '''
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    return f'{h}小时{m}分钟'


def addr2Geocode(addr)->str:
    '''
    Parameters
    ----------
    addr : string, actually address in plain text, better to be specific

    Returns
    -------
    formatted_address: address formatted and shown on Gaode
    geoCodes: the longitude and altitude of the input address

    '''
    encoded_addr = parse.quote(addr) # or use safe="/:=&?#+!$,;'@()*[]" to encode the whole url
    url = f'https://restapi.amap.com/v3/geocode/geo?address={encoded_addr}&output=json&key={key}&city=010'
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    
    formatted_address = data['geocodes'][0]['formatted_address']
    geoCodes = data['geocodes'][0]['location']
    return formatted_address, geoCodes

# Strategt可选模式 
# 0：最快捷模式
# 1：最经济模式
# 2：最少换乘模式
# 3：最少步行模式
# 5：不乘地铁模式
def getTransitTime(base_url, 
                   dep_geoCodes, 
                   dst_geoCodes, 
                   tag): # dep_geoCodes obtained from other function
    url = base_url + f'key={key}&output=json&origin={dep_geoCodes}&destination={dst_geoCodes}&city=010&strategy=0'
    data = json.loads(urllib.request.urlopen(url).read())

    if data['status'] != '1': # means transit route found
        print(f'无法找到去***{tag}***上班地方的公交路径.')
        return
    
    dis = data['route']['distance'] # in meters    
    fast_route = data['route']['transits'][0]
    duration = int(fast_route['duration'])
    format_duration = formatTime(duration)
    print(f'去{tag}上班地方{format_duration}.')
    return data


#%%

while True:
    dep_addr = input('出发地点(输入0退出程序):').strip()
    if dep_addr == '0':
        break
    formatted_address, dep_geoCodes = addr2Geocode(dep_addr)
    
    print('-'*66)
    print()
    print(f'从<--{formatted_address}-->出发:')
    
    for dst_geoCodes, _, tag in work_place_info:
        # (导航方式:公交/驾车, 出发地经纬度, 目的地经纬度, 给谁导航)
        data = getTransitTime(bus_url, dep_geoCodes, dst_geoCodes, tag) 
    
    print()
    print('-'*66)
    
    while True:
        open_url = input('是否打开地图导航?(Y/N):').strip().lower()
        if open_url == 'y':
            for dst_geoCodes, dst_name, _ in work_place_info:
                show_nav_url =  'https://ditu.amap.com/dir?'\
                               f'&from%5Blnglat%5D={parse.quote(dep_geoCodes)}'\
                               f'&from%5Bname%5D={parse.quote(formatted_address)}'\
                               f'&to%5Blnglat%5D={parse.quote(dst_geoCodes)}'\
                               f'&to%5Bname%5D={parse.quote(dst_name)}'\
                               f'&type=bus&policy=0&dateTime={next_workday}'
            
                    
                webbrowser.open(show_nav_url, new=0, autoraise=True)
            break
        elif open_url == 'n':
            break
        else:
            print('未知命令, 请输入Y/N.')
    print()
    print('-'*66)
