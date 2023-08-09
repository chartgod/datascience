# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8

@author: 이승헌

"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# Set Korean font for matplotlib
plt.rcParams['font.family'] = 'Malgun Gothic'

# 데이터 파일 경로
file_path = r'C:\Users\ust21\Desktop\2023_이승헌\2023\Project\2023_특화해양예보_code_figure\base_file\해양기상부이\해양기상부이_거제도.csv'

# 데이터 불러오기 (encoding을 'cp949'로 설정)
df = pd.read_csv(file_path, encoding='cp949')

# 일시를 날짜형으로 변환
df['일시'] = pd.to_datetime(df['일시'])

df['풍속(m/s)'] = df['풍속(m/s)'].replace('-', float('nan'))
df['현지기압(hPa)'] = df['현지기압(hPa)'].replace('-', float('nan'))
df['유의파고(m)'] = df['유의파고(m)'].replace('-', float('nan'))
df['파주기(sec)'] = df['파주기(sec)'].replace('-', float('nan'))

# 기압, 풍속, 유의파고, 파주기 자료 가져오기
data_columns = ['현지기압(hPa)', '풍속(m/s)', '유의파고(m)', '파주기(sec)']
data_labels = ['현지기압(hPa)', '풍속(m/s)', '유의파고(m)', '파주기(sec)']

df[data_columns] = df[data_columns].apply(pd.to_numeric, errors='coerce')

# 생성한 reference time series
ref_time = pd.date_range('2013-01-01', '2022-12-31', freq='1H')
ref_data = pd.Series(np.nan, index=ref_time)
ref_data = pd.DataFrame(ref_data)
ref_data.columns = ['sample_time']

# DataFrame에 merge
merged_data = pd.merge(ref_data, df, left_index=True, right_on='일시', how='left')
merged_data = merged_data.sort_values(by='일시')

# '현지기압(hPa)' 열의 연속된 값들 간의 차이 계산
df['pressure_diff'] = df['현지기압(hPa)'].diff()

# 갑작스러운 하강을 식별하기 위한 임계값 정의
threshold = -10  # 필요에 따라 조절 가능.

# 압력 차이가 임계값 아래인 곳에서 값을 NaN으로 대체
df['현지기압(hPa)'] = df.apply(lambda row: np.nan if row['pressure_diff'] < threshold else row['현지기압(hPa)'], axis=1)

# 임시로 추가한 'pressure_diff' 열 삭제
df.drop(columns=['pressure_diff'], inplace=True)

# 원래 데이터프레임에 수정된 '현지기압(hPa)' 값을 반영
merged_data['현지기압(hPa)'] = df['현지기압(hPa)']

# 그래프를 저장할 폴더 경로
result_folder = r'C:\Users\ust21\Desktop\2023_이승헌\2023\Project\2023_특화해양예보_code_figure\base_file\해양기상부이\해양기상부이_거제도'
os.makedirs(result_folder, exist_ok=True)

# 월별 차트 그리기
for year_month, group in merged_data.groupby(merged_data['일시'].dt.to_period('M'), dropna=False):
    group = group.sort_values(by='일시')
    fig, axes = plt.subplots(nrows=4, ncols=1, figsize=(20, 24), sharex=True)
    plt.subplots_adjust(hspace=0.2)
        
    for ax, col, label in zip(axes, data_columns, data_labels):
        ax.plot(group['일시'], group[col])
        ax.set_ylabel(label, fontsize=20)
        ax.set_title(f'{label} ({year_month})', fontsize=25)
        fig.suptitle(f'{year_month}  해양기상부이_거제도', fontsize=40, fontweight='bold')
        # 5일 간격으로 날짜 표시
        ax.xaxis.set_major_locator(plt.MaxNLocator(6))
        ax.tick_params(axis='x', rotation=45)
        ax.xaxis.set_major_locator(plt.MultipleLocator(5))  # 5일 간격으로 나누기
        ax.xaxis.set_minor_locator(plt.MultipleLocator(1))  # 1일 간격으로 나누기
    
    # x축 라벨 설정
    axes[-1].set_xlabel('일시')
    
    # 그래프 저장
    save_path = os.path.join(result_folder, f'{year_month}_chart.png')
    plt.savefig(save_path, bbox_inches='tight')
    
    plt.close()

print("차트가 생성되었습니다.")
