import os
import re
from datetime import datetime
import json
from tqdm import tqdm

class TurnData():
    def __init__(self,path):
        self.path = path
    
    def load_data(self):
        with open(self.path,'r',encoding='utf-8') as f:
            raw = f.readlines()
            temp = []
            for line in raw:
                if line.startswith('\t'):
                    temp[-1] = temp[-1]+" "+line.strip()
                else:
                    temp.append(line.strip())
            raw = temp
            baisc_info = self.__getBasicInfo(raw)
            turn = self.__getTurnInfo(raw)
            data = {}
            data.update(baisc_info)
            data['turn'] = {}
            data['turn'].update(turn)
            self.data = data
            

    def __getBasicInfo(self,raw):
        basic_info = {}
        id_idx = 0
        for line in raw:
            line = line.strip()
            if re.search(r'@.+:.+',line):
                k = re.findall(r'@(.+?):[\t\s]+.+',line)[0]
                v = re.findall(r'@.+?:[\t\s]+(.+)',line)[0] 
                if re.search(r'@ID:.+',line):
                    v_dict = {}
                    for i,p in enumerate(v.split('|')):
                        v_dict[i] = p
                    basic_info['ID{}'.format(id_idx)] = v_dict
                    id_idx+=1
                elif re.search(r'@Date:.+',line) or re.search(r'@Birth of CHI:.+',line):
                    v = re.sub(r'\s','',v)
                    record_date = self.__convert_date(v)
                    basic_info['Date'] = {}
                    basic_info['Date']['y'] = record_date.split('/')[0]
                    basic_info['Date']['m'] = record_date.split('/')[1]
                    basic_info['Date']['d'] = record_date.split('/')[2]
                else:
                    basic_info[k] = v
        return basic_info
    
    def __convert_date(self,date_str):
        date_str = re.sub(r'\.','',date_str)
        try:
            input_format = '%d-%b-%Y'
            output_format = '%Y/%m/%d'
            
            date_obj = datetime.strptime(date_str, input_format)
            return date_obj.strftime(output_format)
        except:
            input_format = '%d-%B-%Y'
            output_format = '%Y/%m/%d'

            date_obj = datetime.strptime(date_str, input_format)
            return date_obj.strftime(output_format)
    
    def __getTurnInfo(self,raw):
        turn_info = {}
        temp = ''
        turn_idx = 0
        content_idx = 0
        for line in raw:
            if line.startswith('*') or line.startswith('%') or line.startswith('\t'):
                if line.startswith('*'):
                    line = line.replace(';',':')
                    role = re.findall(r'\*(.+):[\t\s]*.+',line)[0]
                    content = re.findall(r'\*.+:[\t\s]*(.+)',line)[0]
                    if (not role==temp) and (not 'act'==temp):
                        temp = ''
                        content_idx=0
                        turn_idx+=1
                        turn_info[turn_idx] = {}
                        turn_info[turn_idx]['role'] = role
                        turn_info[turn_idx]['content'] = [{'idx':content_idx,'text':content}]
                        temp = role
                        content_idx+=1
                    else:
                        turn_info[turn_idx]['content'].append({'idx':content_idx,'text':content})
                        content_idx+=1
                elif re.search(r'\%spa.+',line):
                    label = re.findall(r'\%spa:[\t\s]*?(.+)',line)[0]
                    turn_info[turn_idx]['content'][-1]['spa'] = {}
                    for spa_label in re.findall('\$([xi]:[a-z]+)',label):
                        spa = re.findall(r'(.+):.+',spa_label)[0]
                        act = re.findall(r'.+:(.+)',spa_label)[0]
                        turn_info[turn_idx]['content'][-1]['spa'][spa] = act

                else:
                    k = 'mor' if line.startswith('\t') else re.findall(r'\%(.+?):[\t\s]*.+',line)[0]
                    label = line.strip() if line.startswith('\t') else re.findall(r'\%.+?:[\t\s]*(.+)',line)[0]
                    if turn_idx:
                        turn_info[turn_idx]['content'][-1][k] = label
                    elif line.startswith("\t"):
                        turn_info[turn_idx]['content'][-1][k]+=label

                    else:
                        turn_idx+=1
                        turn_info[turn_idx] = {}
                        turn_info[turn_idx][k] = label
                        turn_info[turn_idx]['content'] = []
                        temp = "act"
        return turn_info

    
if __name__ == "__main__":
    #开始读取语料
    #更新脚本
    corpus = {}
    root_path = r'./添加了mor语料'
    for root,dirs,files in os.walk(root_path):
        for f in tqdm(files):
            if f.endswith('.cha'):
                child_age = {}
                child_age['age_y'] = int(f[:2])
                child_age['age_m'] = int(f[2:4])
                child_age['age_d'] = int(f[4:6])
                
                path = os.path.join(root,f)
                td = TurnData(path)
                td.load_data()
                data = td.data
                data.update(child_age)
                corpus[f] = data
    with open(r'child_corpus_python.json','w',encoding='utf-8') as fn:
        json.dump(corpus,fn,ensure_ascii=False,indent=4)




    


