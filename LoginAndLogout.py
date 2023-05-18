from selenium import webdriver
import time
import threading
import requests
import csv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import *
def loginBOJ(browser,userId,userPwd,loginUrl):
    try:
        browser.get(loginUrl)
        if browser.title != 'BOJ-V4| 登录':
            print(userId+"：访问BOJ登陆地址失败")
            return 1
        else:
            browser.find_element_by_id("id_username").send_keys(userId)
            browser.find_element_by_id("id_password").send_keys(userPwd)
            btnLogin = browser.find_element_by_xpath('//*[@id="content_body"]/div/div/div[1]/form/button')
            btnLogin.click()
            try:
                alertDiv = browser.find_element_by_xpath('//*[@class="alert alert-danger"]')
                print(alertDiv.text)
            except NoSuchElementException as e:
                try:
                    userLogo = browser.find_element_by_xpath('//*[@class="container"]/div[2]/ul[2]/li[1]/a')
                    print(userLogo.text)
                except NoSuchElementException as e:
                    print(userId+":"+e.msg)
                    return 5
                else:
                    print(userId+":登陆成功！")
                    return 0
            else:
                print(userId+":用户名或密码错误！")
                return 6
    except NoSuchElementException as e:
        print(userId+":"+ e.msg)
        return 2
    except TimeoutException as e:
        print(userId + ":" + e.msg)
        return 3
    except Exception as e:
        print(userId + ":" + e.msg)
        return 4
    else:
        return 0

def loginHUSTOJ(browser,userId,userPwd,loginUrl, indexUrl):
    try:
        browser.get(loginUrl)
        if browser.title != 'Login':
            print(userId + "：访问HUSTOJ登陆地址失败")
            return 1
        else:
            browser.find_element("name","user_id").send_keys(userId)
            browser.find_element("name","password").send_keys(userPwd)
            btnLogin = browser.find_element("xpath",'//*[@id="login"]/div[3]/div[1]/button')
            btnLogin.click()
            try:
                alert = browser.switch_to.alert()
                if alert is not None:
                    alert.accept()
                    print(userId + ':用户名或密码错误！')
                    return 6
            except NoAlertPresentException as e:
                try:
                    browser.get(indexUrl)
                    userLogo = browser.find_element("xpath",'//*[@id="profile"]')
                    if userLogo.text == userId:
                        print(userId + ":登陆成功！")
                        return 0
                except NoSuchElementException as e:
                    print(userId + ":" + e.msg)
                    return 5
    except NoSuchElementException as e:
        print(userId+":"+ e.msg)
        return 2
    except TimeoutException as e:
        print(userId + ":" + e.msg)
        return 3
    except Exception as e:
        print(userId + ":" + e.msg)
        print(repr(e))
        return 4
    else:
        return 0
def logoutHUSTOj(browser,userId,indexurl):
    try:
        browser.get(indexurl)
        userLogo = browser.find_element("xpath",'//*[@id="profile"]')
        if userLogo.text == userId:
            userLogo.click()
            browser.find_element("xpath",'//*[@id="navbar"]/ul[2]/li/ul/li[5]/a').click()
    except Exception as e:
        print(repr(e))
        print(userId+"登出失败！！")
        return 1
    else:
        print(userId+"登出成功！")
        return 0

def getNumOfSubmissionPages(browser,SubmissionUrl):
    try:
        browser.get(SubmissionUrl)
        pages = browser.find_element("xpath",'//*[@id="wrapper"]/div/ul/li[1]').text.split(' ')[3]
        return int(pages)
    except Exception as e:
        print("获取提交记录页数失败！")
        return -1
    return 0