# %%
import numpy as np
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import time

# 搜尋頁面


def get_search_jobs(keyword, page=1):
    # api網址
    url = 'https://www.104.com.tw/jobs/search/api/jobs'

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'Referer': 'https://www.104.com.tw/jobs/search/?'
    }

    params = {'keyword': keyword,
              'page': page,
              'pagesize': 20,
              'order': 15,
              'area': '6001009000'
              }

    res = requests.get(url, headers=headers, params=params)
    print(res)
    data = res.json()
    return data

# request+bts


def job_requests(link):
    res = requests.get(link)
    bts = BeautifulSoup(res.text, 'lxml')
    # 抓每個網頁的工具(tools)
    tools = bts.select('.tools u')
    all_tools = [i.text for i in tools]

    # 抓每個網頁的技能(skill)
    skills = bts.select('.skills u')
    all_skill = [i.text for i in skills]

    # 抓每個網頁的工作經歷(work)
    exp = bts.select('.job-requirement-table .mb-2:nth-child(1) .mb-0')
    all_exp = [i.text for i in exp]
    return all_tools, all_skill, all_exp


keyword = 'python'  # 輸入職缺名稱
pages = 20  # 頁數

data_list = []

for p in range(1, pages+1):
    result = get_search_jobs(keyword, p)
    print(result['data'])
    print(f'=====第{p}頁=====')
    for job in result['data']:
        link = job['link']['job']
        jobname = job['jobName']
        salary = job['salaryLow']
        address = job['jobAddrNoDesc'][:3]
        industry = job['coIndustryDesc']
        major = ', '.join(job.get('major')) if job.get('major') else '不拘'
        tool_list, skill_list, exp_list = job_requests(link)
        tools = ', '.join(tool_list) if tool_list else ''
        skills = ', '.join(skill_list) if skill_list else '不拘'
        exps = ', '.join(exp_list) if exp_list else '不拘'

        # 避開時薪、年薪、面議
        if len(str(salary)) < 4 or salary > 100000 or salary == '':
            continue
        data_list.append(
            [jobname, salary, address, exps, industry, major, tools, skills, link])
        print(
            f"{jobname} | {salary} | {address}| {exps} | {industry} |科系: {major} | 工具:{tools} | 技能: {skills} | 網址: {link}")
        print()
job_df = pd.DataFrame(data_list, columns=[
                      '職稱', '薪資', '地區', '工作經歷', '行業類別', '科系', '工具', '技能', '網址'])

job_df.to_csv(f'{keyword}_職缺.csv', index=False, encoding='utf-8-sig')

# %%
# =====================視覺化=========================
plt.rcParams['font.family'] = 'Microsoft JhengHei'  # 微軟正黑體

# 工具文字雲
all_tools = ''.join(job_df['工具'].tolist())

wc = WordCloud(width=800, height=400,
               background_color='white').generate(all_tools)
plt.figure(figsize=(10, 5))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.title(f'{keyword}_工具文字雲', fontsize=20, pad=15)
plt.show()


# %% 各縣市薪資盒狀圖
job_df = job_df[job_df['地區'] != '日本']
job_df = job_df[job_df['地區'] != '越南']
salary_data = [job_df[job_df['地區'] == city]['薪資'].tolist()
               for city in job_df['地區'].unique()]
plt.figure(figsize=(10, 6))
plt.boxplot(  # Matplotlib 3.9之前的版本 須將 tick_labels 改為 labels
    salary_data, tick_labels=job_df['地區'].unique(), patch_artist=True)
plt.title(f'{keyword}_各縣市薪資分佈', fontsize=20)
plt.xlabel('地區', fontsize=15)
plt.ylabel('薪資', fontsize=15)
plt.yticks(range(30000, 100000, 5000),fontsize=12)
plt.xticks(fontsize=12)
plt.grid()
for i in range(len(salary_data)):
    q1 = round(np.percentile(salary_data[i], 25))
    median = round(np.median(salary_data[i]))
    q3 = round(np.percentile(salary_data[i], 75))
    min_salary = round(min(salary_data[i]))
    max_salary = round(max(salary_data[i]))

    x = i + 1  # 位置從 1 開始
    plt.text(x, min_salary - 1000, f'{min_salary}',
             ha='center', fontsize=9, color='black')
    plt.text(x, q1 - 1000, f'{q1}', ha='center',
             fontsize=9, color='blue')
    plt.text(x, median + 500, f'{median}',
             ha='center', fontsize=9, color='red')
    plt.text(x, q3 + 500, f'{q3}', ha='center', fontsize=9, color='blue')
    plt.text(x, max_salary + 1000, f'{max_salary}',
             ha='center', fontsize=9, color='black')
plt.tight_layout()
plt.show()

# %% 各縣市職缺bar圖
all_area = job_df.groupby('地區')['地區'].count()
all_area = all_area[all_area.index != '日本']
all_area = all_area[all_area.index != '越南']
plt.figure(figsize=(10, 6))
plt.bar(range(len(all_area.index)), all_area,
        color='orange')
plt.xticks(range(len(all_area.index)), all_area.index,fontsize=12)
plt.yticks(fontsize=12)
plt.title(f'{keyword}_各縣市職缺數量', fontsize=18)
plt.xlabel('地區', fontsize=15)
plt.ylabel('數量', fontsize=15)
plt.tick_params(axis='both', labelsize=10, color='red')

for i in range(len(all_area.index)):
    plt.text(i-0.1, all_area.iloc[i], all_area.iloc[i])
plt.show()
# %% 各縣市職缺pie圖
all_area = job_df.groupby('地區')['地區'].count()
total = all_area.sum()
all_area = all_area[(all_area/total)*100 >= 3]
plt.figure(figsize=(8, 8))
plt.pie(all_area, labels=all_area.index, autopct='%d%%',
        startangle=90, textprops={'fontsize': 15})
plt.title(f'{keyword}_各縣市職缺佔比', y=1.05, fontsize=20)
plt.axis('equal')
plt.tight_layout()
plt.show()

# %% 工作經歷pie圖
# all_work = job_df.groupby('工作經歷')['工作經歷'].count()
# all_work = all_work[all_work.index != '不拘']
# plt.figure(figsize=(8, 8))
# plt.pie(all_work, labels=all_work.index, autopct='%d%%',
#         startangle=90, textprops={'fontsize': 15})
# plt.title(f'{keyword}_工作經歷佔比', y=1, fontsize=20)
# plt.axis('equal')
# plt.show()

# %% 工作經歷vs薪資盒狀圖
exp_df = job_df.groupby('工作經歷')['工作經歷'].count()
# exp_df = exp_df[exp_df.index != '不拘 ']
sa_exp = [job_df[job_df['工作經歷'] == exp]['薪資'] for exp in exp_df.index]
plt.figure(figsize=(10,6))
plt.title(f'{keyword}_工作經歷與薪資分布',fontsize=20)
plt.boxplot(sa_exp, labels=exp_df.index,patch_artist=True)
plt.xlabel('工作經歷',fontsize=15)
plt.ylabel('薪資',fontsize=15)
plt.xticks(fontsize=12)
plt.yticks(range(30000,100000,5000),fontsize=12)
plt.grid()
plt.show()

# %% 職缺所需技能pie圖
all_skills = ','.join(job_df[job_df['技能'] != '不拘']['技能']).split(',')
df_skills = pd.DataFrame(all_skills, columns=['技能'])
all_skills = df_skills.groupby('技能')['技能'].count()
total = all_skills.sum()
all_skills = all_skills[(all_skills/total*100) > 3]

plt.figure(figsize=(8, 8))
plt.title(f'{keyword}_職缺所需技能占比', fontsize=20, y=1.05)
plt.pie(all_skills, labels=all_skills.index,
        autopct='%d%%', textprops={'fontsize': 15})
plt.axis('equal')
plt.show()

# %% 地區與行業pie圖
all_area = job_df.groupby('地區')['地區'].count()
all_area_total = all_area.sum()
all_area = all_area[(all_area/all_area_total*100) > 3]
all_type = job_df.groupby('行業類別')['行業類別'].count()
total = all_type.sum()
all_type = all_type[(all_type / total * 100) > 3]
plt.figure(figsize=(8, 8))
type_p = plt.pie(
    all_type,
    labels=all_type.index,
    autopct='%d%%',
    startangle=90,
    textprops={'fontsize': 12},
    pctdistance=0.9
)
for i in type_p[0]:
    i.set_edgecolor('w')

area_p = plt.pie(all_area, radius=0.8, labels=all_area.index,
                 autopct='%d%%', pctdistance=0.7, labeldistance=0.5)
for i in area_p[0]:
    i.set_edgecolor('w')

plt.title(f'{keyword}_地區與行業占比', fontsize=20, y=1.05)
plt.axis('equal')
plt.show()



# %%
