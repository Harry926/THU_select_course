from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route("/index", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        cb1 = request.form.getlist('cb1')
        cb2 = request.form.getlist('cb2')
        cb3 = request.form.getlist('cb3')
        cb4 = request.form.getlist('cb4')
        cb5 = request.form.getlist('cb5')
        cb = cb1 + cb2 +cb3 + cb4 + cb5
        coll = request.form.get('college')
        sele = request.form.get('sector')
        if sele != '0':
            data = get_course(cb, int(coll), int(sele)-1)
        else:
            data = get_muti_course(cb, int(coll))
        return render_template('test.html', data=data)

global dep_list
dep_list = [['文學院','中國文學系' ,'外國語文學系' ,'歷史學系' ,'華語文教學國際碩士學位學程' ,'日本語言文化學系','哲學系' ,'哲學系碩士在職專班'],
            ['理學院','應用物理學系','化學系','生命科學系','應用數學系','生醫暨材料科學國際博士學位學程','生物多樣性國際研究生博士學位學程'],
            ['工學院','化學工程與材料工程學系','工業工程與經營資訊學系','工業工程與經營資訊碩士專班','環境科學與工程學系','資訊工程學系','資訊工程學系在職專班','電機工程學系','數位創新碩士學位學程'],
            ['管理學院','企業管理學系','國際經營與貿易學系','會計學系','財務金融學系', '高階經營管理專班', '國際企業管理碩士學位學程', '統計學系', '資訊管理學系'],
            ['社會科學院','經濟學系','政治學系','行政管理暨政策學系','社會學系','社會工作學系','教育研究所','教育研究所碩士在職專班','公共事務在職專班'],
            ['農學院','畜產與生物科技學系','食品科學系','餐旅管理學系','餐旅管理學系在職專班','運動休閒與健康管理學位學程','高齡健康與運動科學學士學位學程'],
            ['創意設計暨藝術學院','美術學系','美術系碩士在職專班','音樂學系','建築學系','工業設計學系','工業設計學系碩士在職專班','景觀學系','景觀系碩士班在職專班','表演藝術與創作碩士學位學程'],
            ['法律學系'],
            ['國際學院','國際經營管理學位學程','永續科學與工程學士學位學程','國際學院不分系英語學士班'],
            ['通識課程:人文領域','通識課程:自然領域','通識課程:社會領域','通識課程:文明與經典','通識課程:領導與倫理','AI思維與程式設計','通識課程:議題導向'],
            ['多元學習課程(共同選修)'],
            ['第二外國語','日文課程','中文課程','大一英文','選修英文','大二英文'],
            ['軍訓一','軍護二','體育課程(進修部)','大一大二體育'],
            ['師資培育中心課程']]

def get_course(time_cb, college, department):
    kk = "一二三四五"
    all_course = get_all_course_url()
    url = all_course[dep_list[college][department]]
    cb = {}
    for i in time_cb:
        temp = i.split(",")
        if(temp[0] in cb.keys()):
            cb[temp[0]].append(int(temp[1]))
        else:
            cb[temp[0]] = [int(temp[1])]

    resp = requests.get(url)
    page = BeautifulSoup(resp.text, "html.parser")
    table = page.find_all("tr")
    table2 = page.find_all('td')

    course = {"course":[]}
    if(url.find('-dept') != -1):
        z = 3
        q = 7
        r = 9
    else:
        z = 1
        q = 4
        r = 6
    for i in range(z, len(table)):
        tds = table[i].find_all("td")
        tmp = tds[0].text.replace("\n", "")
        tmp2 = tds[3].text.strip().replace("星期", "")
        tmp2 = tmp2.replace("\n","")
        if(tmp2.find("[") != -1):
            tmp2 = tmp2[:tmp2.find("[")]
        tmp2 = re.split('/|,', tmp2)
        for j in range(len(tmp2)):  #白癡應物
            if len(tmp2[j]) >= 2:
                if tmp2[j][1] in kk:
                    tmp2[j] = tmp2[j][0]
        time_re = {}
        for j in range(len(tmp2)):
            if tmp2[j] in kk:
                time_re[tmp2[j]] = []
                for k in range(j+1, len(tmp2)):
                    if tmp2[k] in kk:
                        break
                    else:
                        time_re[tmp2[j]].append(tmp2[k])
        time_res = {}
        for j in time_re:
            time_res[j] = []
            for k in time_re[j]:
                try: #白癡外文
                    time_res[j].append(int(k))
                except:
                    print(time_res[j])
        boo = True
        for j in time_res:
            if j not in cb.keys() or set(time_res[j]) & set(cb[j]) != set(time_res[j]):
                boo = False
                break
        if(boo):
            course["course"].append({"id": tmp.replace(" ", ""), "name":tds[1].text.strip(), "credit": tds[2].text.strip(), "time": tds[3].text.strip().replace("\n",""), "teacher":table2[q].text.strip(), "note": table2[r].text.strip().split("/")[1].strip(), "url":"https://course.thu.edu.tw"+tds[0].find("a").get("href")})
        r+=7
        q+=7
    return course

def get_all_course_url():
    url = "https://course.thu.edu.tw/view-dept/111/1/everything"
    resp = requests.get(url)
    page = BeautifulSoup(resp.text, "html.parser")
    table = page.find_all('tr')
    all_course = {}

    for i in range(1, len(table)):
        tds = table[i].find_all('td')
        all_course[tds[0].text.strip()] = "https://course.thu.edu.tw" + tds[2].find('a').get('href')
    return all_course

def get_muti_course(time_cb, college):
    dep = len(dep_list[college])
    muti_course = {"course":[]}
    for i in range(dep):
        muti_course['course'] += (get_course(time_cb, college, i)['course'])
    return muti_course

if __name__ == '__main__':
    app.run(debug=True)
