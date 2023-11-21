import json
from pprint import pprint
import re
from functools import reduce
from collections import Counter
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

def list2pair(data_list):
    pair_list = []
    for i in range(1,len(data_list)):
        if data_list[i]:
            pair_list.append((data_list[i-1],data_list[i]))
        else:
            padding = {'role':'sep','content':[{'idx':0,'text':''}]}
            pair_list.append((data_list[i-1],padding))
    return pair_list

def extract_pos(pos_value):
    pos_value = re.sub(r'[?.!。，,？]$','',pos_value)
    pos_list = pos_value.strip().split(' ')
    pos = [re.findall(r'(.+?)[\|\:].+',p)[0] for p in pos_list]
    return pos

#找出成人儿童问答对
# with open(r'child_corpus_python.json','r',encoding='utf-8') as f:
#     data = json.load(f)
#     file_list = data.keys()
#     filter_data = [data[k]['turn'] for k in file_list if data[k]['age_y']==3 and data[k]['age_m'] in [0,1,2,3]]
#     turn_list = [data[k] for data in filter_data for k in data.keys()]
#     turn_pair = [(tp[0]['content'][-1],tp[1]['content'][0]) for tp in list2pair(turn_list) if not tp[0]['role']=='CHI'
#                  and tp[1]['role']=='CHI'
#                  and tp[0]['content'][-1]['text'][-1]=='?' and len(tp[0]['content'][-1]['text'])>3]
#     pprint(turn_pair)

#找出儿童应答语
with open(r'child_corpus_python.json','r',encoding='utf-8') as f:
    data = json.load(f)
    file_list = data.keys()
    for i in [2,3]:
        for j in [0,1,2,3,4,5,6,7,8,9,10,11]:
            filter_data = [data[k]['turn'] for k in file_list if (data[k]['age_y']==i and data[k]['age_m']==j)]

            turn_list = [data[k] for data in filter_data for k in data.keys()]
            turn_pair = [(tp[0]['content'][-1],tp[1]['content'][0]) for tp in list2pair(turn_list) if not tp[0]['role']=='CHI'
                         and tp[1]['role']=='CHI' and (len(tp[1]['content'])>1)]

            chi_pos = []
            for tp in turn_pair:
                try:
                    chi_pos += extract_pos(tp[1]['mor'])
                except:
                    pass

            adult_sent = [d['content'] for d in turn_list if not d['role']=='CHI']
            merge_adult = reduce(lambda x,y:x+y,adult_sent)
            adult_pos = []
            for d in merge_adult:
                if 'mor' in d.keys():
                    adult_pos+=extract_pos(d['mor'])

            turn_pair2 = [(tp[0]['content'][-1],tp[1]['content'][0]) for tp in list2pair(turn_list) if (tp[0]['role']=='CHI')
                         and (not tp[1]['role']=='CHI') and (len(tp[0]['content'])>1)]
            chi_sent = [tp[0] for tp in turn_pair2]

            all_chi_pos = []
            for d in chi_sent:
                if 'mor' in d.keys():
                    all_chi_pos+=extract_pos(d['mor'])


            count_chi = Counter(chi_pos)
            count_adult = Counter(adult_pos)
            count_all_chi = Counter(all_chi_pos)

            chi_df = pd.DataFrame(count_chi.most_common(),columns=['pos','count'])
            adult_df = pd.DataFrame(count_adult.most_common(),columns=['pos','count'])
            all_chi_df = pd.DataFrame(count_all_chi.most_common(), columns=['pos', 'count'])

            chi_df['freq'] = chi_df['count']/chi_df['count'].sum()
            adult_df['freq'] = adult_df['count'] / adult_df['count'].sum()
            all_chi_df['freq'] = all_chi_df['count'] / all_chi_df['count'].sum()

            chi_df.drop('count',inplace=True,axis=1)
            adult_df.drop('count', inplace=True,axis=1)
            all_chi_df.drop('count', inplace=True,axis=1)
            diff_df = reduce(lambda x,y:pd.merge(x,y,how='left',on='pos'),[adult_df,chi_df,all_chi_df])
            diff_df.fillna(0,inplace=True)
            diff_df.columns = ['pos','adult','chi_response','chi_other']
            diff_df['pos_freq_diff(adult&child_response)'] = abs(diff_df['chi_response']-diff_df['adult'])
            diff_df['pos_freq_diff(adult&child_other)'] = abs(diff_df['chi_other'] - diff_df['adult'])
            diff_df['response_diff < other_diff'] = diff_df.iloc[:,-2] < diff_df.iloc[:,-1]
            cols = ['pos','pos_freq_diff(adult&child_response)','pos_freq_diff(adult&child_other)']
            out = diff_df[cols]
            res = out[[c for c in out.columns if not c == 'pos']].sum()
            print(i,j,res.values)
    # out.to_excel('儿童与成人词性频率之差对比_0818.xlsx',index=False,encoding='utf_8_sig')
    #
    # chi_df.loc[:,'role'] = 'chi(response)'
    # adult_df.loc[:, 'role'] = 'adult'
    # all_chi_df.loc[:, 'role'] = 'chi(other)'
    #
    # all_df = pd.concat([chi_df,all_chi_df,adult_df],axis=0)
    #
    # fig = sns.barplot(data=all_df,x='pos',y='freq',hue='role')
    # plt.xticks(rotation=-45)
    # plt.show()
