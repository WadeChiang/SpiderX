from selenium import webdriver
import time
import pandas as pd
import json
import re
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import *
from pathlib import Path

from GlobalValue import *
from LoginAndLogout import *

def initSelenium():
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')  # 上面三行代码就是为了将Chrome不弹出界面，实现无界面爬取
        # browser = webdriver.Chrome(executable_path=r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",
        #                            options=chrome_options)
        browser = webdriver.Chrome(
            service=Service(driver_path), options=chrome_options)
        # browser = webdriver.Chrome(executable_path=r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe")
    except Exception as e:
        print("初始化Selenium失败！")
        return None
    else:
        return browser

def getBrowserList(num):
    browserList = []
    for i in range(num):
        browser = initSelenium()
        browserList.append(browser)
    print("初始化%i个浏览器对象" % num)

def getUserList(dic):
    file = csv.reader(open('oj_user.csv', 'r', encoding='utf-8'))
    cnt = 0
    for f in file:
        if cnt == 0:
            cnt = cnt + 1
            continue

        cnt = cnt + 1
        dic[f[1]] = f[2]
    return dic

def getSubmitStatus(brower, url, user_dict):
    # try:
    brower.get(url)
    print('111',url)
    nextpage = browser.find_element(by=By.LINK_TEXT, value='Next >')
    nextpage_href =nextpage.get_attribute('href')
    top = re.findall('&top=\d+', nextpage_href)[0]
    top = re.findall('\d+', top)[0]
    last_top = 0
    prevtop = re.findall('&prevtop=\d+', nextpage_href)[0]
    prevtop = re.findall('\d+', prevtop)[0]
    last_prevtop = 0
    # result = brower.find_element_by_id('result-tab')
    while top != last_top and prevtop != last_prevtop:
        result = browser.find_elements(by=By.TAG_NAME, value='tr')[1:]
        for entry in result:
            # submit_id = entry.find_element_by_xpath('.//td[1]').text
            # user_id = entry.find_element_by_xpath('.//td[2]').text
            # problem_id = entry.find_element_by_xpath('.//td[3]').text
            # score = entry.find_element_by_xpath('.//td[4]').text
            submit_id = entry.find_element(by=By.XPATH, value='.//td[1]').text
            user_id = entry.find_element(by=By.XPATH, value='.//td[2]').text
            problem_id = entry.find_element(by=By.XPATH, value='.//td[4]').text
            score = entry.find_element(by=By.XPATH, value='.//td[5]').text
            if score.find("Accepted") != -1:
                score = 100
            else:
                print(score)
                score = re.findall('\d+', score)[0]
            # if score > 100 or score < 0:
            #     print("{} 的成绩异常，提交记录为{}".format(user_id, submit_id))
            #     raise Exception(print("成绩异常"))
            score = int(score)
            submit_time = entry.find_element(by=By.XPATH, value='.//td[10]').text
            submit_time = int(time.mktime(time.strptime(submit_time,"%Y-%m-%d %H:%M:%S")))
            if user_id in user_dict.keys():
                problem_dict = user_dict[user_id]
                if problem_id in problem_dict.keys():
                    problem = problem_dict[problem_id]
                    if problem['score'] < score or (problem['score'] == score and problem['time'] < submit_time):
                        problem['submit_id'] = submit_id
                        problem['score'] = score
                        problem['time'] = submit_time
                else:
                    problem_dict[problem_id] = {}
                    dict = problem_dict[problem_id]
                    dict['submit_id'] = submit_id
                    dict['score'] = score
                    dict['time'] = submit_time

            else:
                user_dict[user_id] = {}
                user_dict[user_id][problem_id] = {}
                dict = user_dict[user_id][problem_id]
                dict['submit_id'] = submit_id
                dict['score'] = score
                dict['time'] = submit_time
        last_top = top
        last_prevtop = prevtop
        nextpage.click()
        nextpage = browser.find_element(by=By.LINK_TEXT, value='Next >')
        nextpage_href = nextpage.get_attribute('href')
        top = re.findall('&top=\d+', nextpage_href)[0]
        top = re.findall('\d+', top)[0]
        prevtop = re.findall('&prevtop=\d+', nextpage_href)[0]
        prevtop = re.findall('\d+', prevtop)[0]
# except Exception as e:
#     print(repr(e))
    print("top=%i prevtop=%i" % (int(top), int(prevtop)))
    print('获取提交状态完毕！')

def getSubmitCode(brower, url, problem):
    try:
        browser.get(url)
        code = browser.find_element(by=By.CLASS_NAME, value='code')
        # code_line = code.find_element(by=By.XPATH, value='.//div/div')
        code_line = code.find_elements(by=By.XPATH, value='.//div/div')
        code_text = ""
        for i in range(0, len(code_line)):
            code_text = code_text + code_line[i].text + '\n'
        problem['code'] = code_text
        print(problem['submit_id'])
    except Exception as e:
        print(repr(e))

def write2File(user_dict, code_path, score_path, problem_list, mode=3):
    result_dict = {}
    for user_id in user_dict.keys():
        problem_dict = user_dict[user_id]
        result_dict[user_id] = []
        sum_score = 0
        code_filename_1 = code_path + '/%s/%s.c'
        code_filename_2 = code_path + '/merge/%s-%s.c'
        sum_score = 0
        for problem_name in problem_list:
            if problem_name in problem_dict.keys():
                result_dict[user_id].append(problem_dict[problem_name]['score'])
                sum_score = sum_score + int(problem_dict[problem_name]['score'])
                if mode & 1:
                    codefile_name = code_filename_1 % (problem_name, teacherName + "_" + user_id)
                    codefile_dir = Path(codefile_name).parent
                    if not codefile_dir.exists():
                        codefile_dir.mkdir(exist_ok=True, parents=True)
                    f = open(codefile_name, 'w', encoding='utf8')
                    f.write(problem_dict[problem_name]['code'])
                    f.close()
                if mode & 2:
                    codefile_name = code_filename_2 % (teacherName + "_" + user_id, problem_name)
                    codefile_dir = Path(codefile_name).parent
                    if not codefile_dir.exists():
                        codefile_dir.mkdir(exist_ok=True, parents=True)
                    f = open(codefile_name, 'w', encoding='utf8')
                    f.write(problem_dict[problem_name]['code'])
                    f.close()
            else:
                result_dict[user_id].append(0)
        result_dict[user_id].append(sum_score)

    colunms = problem_list.append('sum')
    df = pd.DataFrame.from_dict(result_dict, orient='index', columns=colunms)
    df.index.name = 'ID'
    writer = pd.ExcelWriter(score_path)
    df.to_excel(writer)
    writer.save()
    print('写入文件完成！')

    '''
        if 'A' in problem_dict.keys():
            result_dict[user_id].append(problem_dict['A']['score'])
            sum_score = sum_score + int(problem_dict['A']['score'])
            codefile_name = code_filename % ('A', user_id)
            codefile_dir = Path(code_filename).parent
            if not codefile_dir.exists():
                codefile_dir.mkdir(exist_ok=True, parents=True)
            f = open(codefile_name, 'w', encoding='utf8')
            f.write(problem_dict['A']['code'])
            f.close()
        else:
            result_dict[user_id].append(0)
        if 'B' in problem_dict.keys():
            result_dict[user_id].append(problem_dict['B']['score'])
            sum_score = sum_score + int(problem_dict['B']['score'])
            f = open(code_filename % ('B', user_id), 'w', encoding='utf8')
            f.write(problem_dict['B']['code'])
            f.close()
        else:
            result_dict[user_id].append(0)
        if 'C' in problem_dict.keys():
            result_dict[user_id].append(problem_dict['C']['score'])
            sum_score = sum_score + int(problem_dict['C']['score'])
            f = open(code_filename % ('C', user_id), 'w', encoding='utf8')
            f.write(problem_dict['C']['code'])
            f.close()
        else:
            result_dict[user_id].append(0)
        if 'D' in problem_dict.keys():
            result_dict[user_id].append(problem_dict['D']['score'])
            sum_score = sum_score + int(problem_dict['D']['score'])
            f = open(code_filename % ('D', user_id), 'w', encoding='utf8')
            f.write(problem_dict['D']['code'])
            f.close()
        else:
            result_dict[user_id].append(0)
        result_dict[user_id].append(sum_score)
        
    colunms = ['A', 'B', 'C', 'D', 'sum']
    df = pd.DataFrame.from_dict(result_dict,  orient='index', columns=colunms)
    df.index.name = 'ID'
    writer = pd.ExcelWriter(score_path)
    df.to_excel(writer)
    writer.save()
    print('写入文件完成！')
    '''

def compute_scores(file_name_list, score_file_name):
    scores_dict = {}
    for file_name in file_name_list:
        df = pd.read_excel(file_name)
        ids = df["ID"]
        scores_1 = df["sum1"]
        scores_2 = df["sum2"]
        for (id, score_1, score_2) in zip(ids, scores_1, scores_2):
            if id not in scores_dict.keys():
                scores_dict[id] = score_1 * 0.07 + score_2 * 0.3
            else:
                scores_dict[id] += score_1 * 0.07 + score_2 * 0.3

    df = pd.DataFrame.from_dict(scores_dict, orient='index', columns=["score"])
    df.index.name = 'ID'
    writer = pd.ExcelWriter(score_file_name)
    df.to_excel(writer)
    writer.save()
    print('写入文件完成！')



if __name__ == "__main__":

    # compute_scores(["./链表1.xlsx", "./链表2.xlsx" , "./文件.xlsx"], "./总分.xlsx")

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    browser = initSelenium()
    status = loginHUSTOJ(browser, teacherId, teacherPwd, HUSTOJLoginUrl, HUSTOJIndexUrl)
    print("登录状态：" + str(status))
    if status != 0:
        exit(0)

    # contest_id = 1047 #需要修改
    user_dict = {}
    print('开始获取{}提交状态！'.format(contest_id))
    getSubmitStatus(browser, HUSTOJStatusUrl % (contest_id), user_dict)
    # user_dict['2019211318'] = {'B':{'submit_id':'15173', 'score':100}}
    for user_id in user_dict.keys():
        print(user_id)
        problem_dict = user_dict[user_id]
        for problem_id in problem_dict.keys():
            print(problem_id, end=' ')
            problem = problem_dict[problem_id]
            url = HUSTOJShowSourceUrl % (int(problem['submit_id']))
            getSubmitCode(browser, url, problem)

    print('获取代码完成！')
    # problem_list = ['A', 'B', 'C', 'D']
    # problem_list = ['A', 'B']
    os.makedirs(os.getcwd() + '\\' + teacherName + '\\' + contest_name + '\\')
    write2File(user_dict, teacherName + '\\' + contest_name + '\\code', teacherName + '\\' + contest_name + '\\score.xlsx', problem_list, 3)


    browser.close()
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print("Finished!")