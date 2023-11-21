from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
import time
import jieba
import re
import os
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

driver = None

def init_driver():#初始化浏览器driver
    global driver
    if not driver == None:
        return
    optn = webdriver.Edge
    svc = Service(r'C:/Program Files (x86)/Microsoft/Edge/Application/msedgedriver.exe')
    optn = webdriver.EdgeOptions()
    optn.add_argument('--headless')
    driver = webdriver.Edge(service=svc,options=optn)

def get_elems(xpath_pattern):#枚举对应XPATH路径下的指定标签
    cnt = 1
    global driver
    ret = []
    while True:
        try:
            tmp = driver.find_element(By.XPATH,xpath_pattern+f'[{cnt}]')
            cnt+=1
            ret.append(tmp)
        except:
            break
    return ret

def get_dramasummary():#爬取分集剧情
    global driver
    page_buttons = get_elems(f'//*[@id="dramaSeries"]/div[1]/div/a')

    eposide_XPATH = r'//*[@id="dramaSerialList"]/dl'

    eposide_segments = get_elems(eposide_XPATH)
    print(f'found {len(eposide_segments)} segments')

    try:#定位剧集展开按钮（如果有），并展开
        unfold=driver.find_element(By.XPATH,'//*[@id="dramaSeries"]/div[1]/a')
        driver.execute_script("arguments[0].click()", unfold)
    except Exception as e:
        print(f'没有找到点击按钮或点击按钮失败 err:{e}')

    drama_list = open('drama_summary.txt','w',encoding='utf-8')

    for segment_index in range(len(eposide_segments)):#通过XPAH逐层遍历分集剧情
        page_buttons[segment_index].click()

        titles = get_elems(f'//*[@id="dramaSerialList"]/dl[{segment_index+1}]/dt')

        for x in range(len(titles)):
            drama_list.write((titles[x].text)+'\n')

            eposide = get_elems(f'//*[@id="dramaSerialList"]/dl[{segment_index+1}]/dd[{x+1}]/p')

            for t in eposide:
                drama_list.write((t.text)+'\n')
    drama_list.close()

def get_roles():#爬取角色
    global driver
    role_output = open('roles.txt','w',encoding='utf-8')
    role_list = driver.find_elements(By.CLASS_NAME,'info')
    print(len(role_list))
    for x in range(len(role_list)):
        try:
            rela = role_list[x].get_attribute("innerText").splitlines()[0].split('\xa0')[2]
            role_output.write(rela+'\n')
            x+=1
        except Exception as e:
            #driver.execute_script("arguments[0].click()", driver.find_element(By.XPATH,'/html/body/div[3]/div[4]/div/div[1]/div/div[21]/div[2]/div/a[2]'))
            print(e)

def split_with_jieba():#分词处理summary
    if not os.path.exists('roles.txt'):
        get_roles()
    
    if not os.path.exists('drama_summary.txt'):
        get_dramasummary()

    jieba.load_userdict('roles.txt')

    summary = open('drama_summary.txt','r',encoding='utf-8')
    summary_text = summary.read()
    with open('content.txt','w',encoding='utf-8') as f:
        sentences = summary_text.split('。')
        for sentence in sentences:
            s = re.sub(r'，|。|？|：|“|”|！', '',sentence.strip())
            words = list(jieba.cut(s))
            outstr = ' '.join(words)
            f.write(outstr+'\n')
    
def gen_plot():#生成人物出场率图表
    #if not os.path.exists('content.txt'):
        #split_with_jieba()
    plot_font = fm.FontProperties(fname='c:/windows/Fonts/simsun.ttc')
    with open('content.txt','r',encoding='utf-8') as f:
        summary_data = f.read()
    with open('roles.txt','r',encoding='utf-8') as f:
        names = [line.strip('\n') for line in f.readlines()]
    
    count_summary = []
    for name in names:
        count_summary.append([name,summary_data.count(name)])
    count_summary.sort(key=lambda x :x[1],reverse=True)
    _,ax = plt.subplots()
    nms = [x[0] for x in count_summary[:10]]
    count = [x[1] for x in count_summary[:10]]
    ax.barh(range(10),count, color=['peru','coral'],align='center')
    ax.set_title('人物出场次数',fontsize=14,fontproperties=plot_font)
    ax.set_yticks(range(10))
    ax.set_yticklabels(nms,fontsize=14, fontproperties=plot_font)
    plt.show()

if __name__ == '__main__':
    init_driver()
    url = r'https://baike.baidu.com/item/%E4%BA%BA%E6%B0%91%E7%9A%84%E5%90%8D%E4%B9%89/17545218'
    driver.get(url)
    #get_roles()
    #get_dramalist()
    #split_with_jieba()
    gen_plot()
    driver.quit()