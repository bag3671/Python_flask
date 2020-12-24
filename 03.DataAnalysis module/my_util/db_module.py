import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rc('font', family='Malgun Gothic')
mpl.rc('axes', unicode_minus=False)

def get_region_daily(date):
    conn = sqlite3.connect('./db/covid/test.db')
    cur = conn.cursor()

    sql = 'select * from region where stdDay=? order by incDec desc;'
    cur.execute(sql, (date,))
    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    return rows

def get_agender_daily(date):
    conn = sqlite3.connect('./db/covid/test.db')
    cur = conn.cursor()

    sql = 'select * from agender where stdDay=?;'
    cur.execute(sql, (date,))
    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    return rows

def select_covid_incDec():
    conn = sqlite3.connect('./db/covid/test.db')
    sql = 'select stdDay,gubun,incDec from region'
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    return rows
def saving_covid_plt(df,filename):
    df_result = df.pivot_table(index ='date',columns='region')['count']
    df_result = df_result[df_result.columns.difference(['합계','검역'])]
    df_result.loc['지역합계'] = df_result.sum()
    df_result[:].T.sort_values('지역합계',ascending=False).iloc[:5].T.iloc[:-1].plot(figsize = (12,8),grid=True,title="코로나확진자 증감지역 top5 의 3월부터 11까지의 추이")
    plt.savefig(filename)
def saving_covid_plt2(df,filename):
    df['count'] = df['count'].apply(int)
    df_result = df.pivot_table(index ='date',columns='region')['count']
    df_result = df_result[df_result.columns.difference(['검역'])]
    df_result.index = pd.to_datetime(df_result.index)
    df_result = df_result.resample('M').sum()
    df_result.index = df_result.index.strftime('%m월')
    df_result = df_result.apply(lambda x:round(x,0))
    df_result['합계'].plot(figsize=(12,8),grid=True,title="월별 확진자수 추이")
    plt.xticks(rotation = 0 )
    plt.savefig(filename)
def saving_covid_plt3(df,filename,month):
    df['count'] = df['count'].apply(int)
    df_result = df.pivot_table(index ='date',columns='region')['count']
    df_result = df_result[df_result.columns.difference(['검역'])]
    df_result.index = pd.to_datetime(df_result.index)
    df_result = df_result.resample('M').sum()
    df_result.index = df_result.index.strftime('%m월')
    df_result = df_result.apply(lambda x:round(x,0))
    df_result.T[f'{month}'].iloc[:-1].plot(figsize=(12,8),kind='bar',grid=True,title=f"{month} 전국 코로나 확진자수")
    plt.xticks(rotation = 0 )
    plt.savefig(filename)
    index_list = []
    for i in df_result.index:
        index_list.append(i)
    return index_list