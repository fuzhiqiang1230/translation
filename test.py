#!/usr/bin/python
# -*- coding: UTF-8 -*-
import tkinter as tk
#from ttk import *
#from ttk import *
import hashlib
import random
import urllib.parse
import requests
from concurrent import futures
from io import StringIO
import tkMessageBox
from tkinter import filedialog
import re
import os

from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams

def autherInf():
    tk.tkMessageBox.showinfo("作者信息", "作者：符克斯\r邮箱:704508652@qq.com")

def read_from_pdf(file_path):
    '''
    解析pdf文件
    '''
    with open(file_path, 'rb') as file:
        resource_manager = PDFResourceManager()
        return_str = StringIO()
        lap_params = LAParams()
        device = TextConverter(
            resource_manager, return_str, laparams=lap_params)
        process_pdf(resource_manager, device, file)
        device.close()
        content = return_str.getvalue()
        return_str.close()
        return content

def create_sign(q, appid, salt, key):
    '''
    制造签名
    '''
    sign = str(appid) + str(q) + str(salt) + str(key)
    md5 = hashlib.md5()
    md5.update(sign.encode('utf-8'))
    return md5.hexdigest()


def create_url(q, url):
    '''
    根据参数构造query字典
    '''
    fro = 'auto'
    to = 'zh'
    salt = random.randint(32768, 65536)
    sign = create_sign(q, appid, salt, key)
    url = url+'?appid='+str(appid)+'&q='+urllib.parse.quote(q)+'&from='+str(fro)+'&to='+str(to)+'&salt='+str(salt)+'&sign='+str(sign)
    return url


def translate(q):
    url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
    url = create_url(q, url)
    r = requests.get(url)
    txt = r.json()
    if txt.get('trans_result', -1) == -1:
        print('程序已经出错，请查看报错信息：\n{}'.format(txt))
        return '这一部分翻译错误\n'
    return txt['trans_result'][0]['dst']


def clean_data(data):
    '''
    将输入的data返回成为段落组成的列表
    '''
    data = data.replace('\n\n', '闲谈后')
    data = data.replace('\n', ' ')
    return data.split('闲谈后')


def _main(pdf_path, txt_path):
    # try:
    data = read_from_pdf(pdf_path)
    data_list = clean_data(data)
    with futures.ThreadPoolExecutor(20) as excuter:
        zh_txt = excuter.map(translate, data_list)
    # zh_txt = [translate(txt) for txt in data_list]
    zh_txt = list(zh_txt)
    article = '\n\n'.join(zh_txt)
    print(article)
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(article)
    # except Exception:
    #     return -1

def getFile():
    filename = tk.filedialog.askopenfilename(filetypes=[('PDF', 'pdf')])
    if filename != "":
        txtname = filename[1:-3] + 'txt'
        _main(filename, txtname)


root = tk.Tk()
root.wm_title("pdf自动翻译器V1.0")#主界面名字
root.geometry('1000x600+100+50')
root.resizable(width=0, height=0)
appid = 20181128000240769   #填入你的 appid ，为int类型
key = 'XBGQH_QXpl1PACYIivr3'      #填入你的 key ，为str类型
#_main('G:\\mycode\\translation\\1.pdf', 'G:\\mycode\\translation\\1.txt')  #填入 pdf 路径与翻译完毕之后的 txt 路径
menubar = tk.Menu(root)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="打开", command=getFile)
filemenu.add_separator()
filemenu.add_command(label="退出", command=root.quit)
menubar.add_cascade(label="文件", menu=filemenu)
root['menu'] = menubar
messagemenu = tk.Menu(menubar, tearoff=0)
messagemenu.add_command(label="说明")
messagemenu.add_command(label="作者", command=autherInf)
menubar.add_cascade(label="信息", menu=messagemenu)
root.mainloop()