from flask.helpers import url_for
from flask import redirect
from flask_login.utils import login_required
import pandas as pd
from bs4 import BeautifulSoup as bs
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import numpy as np
import time
from selenium import webdriver
import selenium
import sys
from flask import Blueprint, flash
from selenium.webdriver.common.by import By
from selenium.webdriver.edge import options
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from numpy.core.records import array
from os import name
from flask import Blueprint, render_template
from flask.globals import request
from .models import Note
from flask_login import current_user
from . import db

product = Blueprint('product', __name__)

prd_name = ''

def driverForscraping(Path):
    option = webdriver.EdgeOptions()
    option.add_argument('headless')
    driver = webdriver.Edge(Path,options=option)
    return driver

def plotChartOLX(olxdata):
    y = olxdata['Location'].value_counts().values
    mylabels = list(set(olxdata['Location'].values))
    plt.pie(y, labels = mylabels)
    #plt.savefig("piChart.png")
    print("abbbbbbbcccccccc")
    plt.savefig("website/static/piChart.png")

def plotHistOfStats(data):
    try:
        mean1 = data['Price(Rs)'].mean()
        median1 = data['Price(Rs)'].median()
        mode1 = data['Price(Rs)'].mode()
    except KeyError:
        mean1 = data['Discounted Price(Rs)'].mean()
        median1 = data['Discounted Price(Rs)'].median()
        mode1 = data['Discounted Price(Rs)'].mode()

    hist = plt.hist([mean1, median1, mode1])
    plt.savefig("website/static/histogram.png")

def dftotuples(datafr,platform):
    if platform == 'olx':
        records = datafr.to_records(index=False)
        resultdata = list(records)
        headingdata = ("Discounted Price(Rs)","Actual Price(Rs)","Item Description","Already Sold")
        return headingdata,resultdata
    if platform == 'daraz':
        records = datafr.to_records(index=False)
        resultdata = list(records)
        headingdata = ("Price(Rs)","specs()","Item Description","Location")
        print(headingdata, resultdata)
        return headingdata,resultdata

def daraz(driver, prod_name, location = "Pakistan"):
    Page_link = 'https://www.daraz.pk/catalog/?q='
    driver.get(Page_link+prod_name)
#     if(location == "Pakistan"):
#         WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div[1]/div/div[2]/div/div[4]/div[2]/div/div/label[2]/span[1]/input'))).click()
#     if(location == "China"):
#         WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div[1]/div/div[2]/div/div[4]/div[2]/div/div/label[1]/span[1]/input'))).click()
#     driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
    dictOfData = []
    for i in range(1,41):
        data_point = (WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,'//*[@id="root"]/div/div[2]/div[1]/div/div[1]/div[2]/div[{}]'.format(i)))).text)
        if("Rs" in data_point):
            data = data_point.split('\n')
            if(data[0] == "FEATURED"):
                data = data[1:]
            if("Rs" not in data[2]):
                dictOfData.append({"Discounted Price(Rs)": data[1].split()[1].replace(',',''),
                                   "Actual Price(Rs-%dis)": data[1],
                           "Item Description":data[0],
                           "Already Sold": data[-2:][0].strip('()')
                          })
            else:
                dictOfData.append({"Discounted Price(Rs)": data[1].split()[1].replace(',',''),
                           "Actual Price(Rs-%dis)": data[2],
                           "Item Description":data[0],
                           "Already Sold": data[-2:][0].strip('()')
                          })
    # Some Pre Processing on data
    darazdata = pd.DataFrame(dictOfData)
    darazdata["Discounted Price(Rs)"] = pd.to_numeric(darazdata["Discounted Price(Rs)"])
    darazdata = darazdata[darazdata["Discounted Price(Rs)"] > darazdata["Discounted Price(Rs)"].mean()/2]

    darazdata['Already Sold'] = (
    pd.to_numeric(darazdata['Already Sold'],
                  errors='coerce')
      .fillna(0)

    )
    return darazdata
def olx(driver, prod_name):
    Page_link = 'https://www.olx.com.pk/items/q-'
    driver.get(Page_link+prod_name)
    dictOfData = []
    for i in range(1,22):
        data_point = (WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,'//*[@id="body-wrapper"]/div/div[3]/div[2]/div[2]/div/ul/li[{}]'.format(i)))).text)
        if("Rs" in data_point):
            data = data_point.split('\n')
            if(data[0] == "FEATURED"):
                data = data[1:]
            dictOfData.append({"Price(Rs)": data[0].split()[1].replace(',',''),
                       "specs()":data[1],
                       "Item Description": data[2],
                       "Location": data[-2:][0].split(',')[-1:][0]
                      })
    olxdata = pd.DataFrame(dictOfData)
    # Some Pre Processing on data
    olxdata["Price(Rs)"] = pd.to_numeric(olxdata["Price(Rs)"])
    olxdata = olxdata[olxdata["Price(Rs)"] > olxdata["Price(Rs)"].mean()/2]
    return olxdata
@product.route('/Product-analysis', methods=['GET', 'POST'])
@login_required
def product_an():
    if request.method == 'POST':
        product_name = request.form.get('productName')
        new_note = Note(data=product_name,user_id=current_user.id)
        db.session.add(new_note)
        db.session.commit()
        product_url = request.form.get('producturl')
        #Location = request.form.get('Location')
        source = request.form.get('Source')
        prd_name = product_name
        if (product_name == "" and product_url == ""):
            flash('Please enter a product_name or valid url.', category='error')
            return render_template("analysis.html")
        PATH = r'C:\Users\adeel\Downloads\Compressed\edgedriver_win64\msedgedriver.exe'
        driver = driverForscraping(PATH)

        if("daraz" in product_url.lower()):
            dataOnDaraz = daraz(driver, product_url.split('=')[1])
            headingdaraz, datadaraz = dftotuples(dataOnDaraz,'daraz')
            plotHistOfStats(dataOnDaraz)
            return render_template("res.html",heading=headingdaraz,data = datadaraz)
            #return redirect(url_for('results.results',heading=headingdaraz))
        elif("olx" in product_url.lower()):
            dataOnOlx = olx(driver, product_url.split('-')[1])
            headingolx, dataolx = dftotuples(dataOnOlx,'olx')
            plotHistOfStats(dataOnOlx)
            return render_template("res.html",heading=headingolx, data = dataolx)
            #return redirect(url_for('results.results',heading=headingolx))
        elif(source.lower() == "olx"):
            dataOnOlx = olx(driver, prd_name)
            headingolx, dataolx = dftotuples(dataOnOlx,'olx')
            plotHistOfStats(dataOnOlx)
            return render_template("res.html",heading=headingolx, data = dataolx)
            #return redirect(url_for('results.results',heading=headingolx))
        elif(source.lower() == "daraz"):
            dataOnDaraz = daraz(driver, prd_name)
            headingdaraz, datadaraz = dftotuples(dataOnDaraz,'daraz')
            plotHistOfStats(dataOnDaraz)
            return render_template("res.html",heading=headingdaraz, data = datadaraz,user=current_user)
            #return redirect(url_for('results.results',heading=headingdaraz))
    return render_template("analysis.html", text="")
