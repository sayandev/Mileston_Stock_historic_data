from flask import Flask, render_template, request, redirect
import requests
import numpy as np
import json
from bokeh.plotting import figure, output_notebook, show
from bokeh import embed

#Using pandas
import pandas as pd
from pandas import *


app = Flask(__name__)



@app.route('/')
#def hello_world():
        #return '<h1>Bokeh plot embeded With Flask Webapp. Data fetched from QUANDL API; moving average convergence-divergence analysis is also shown in plot. </h1><a href=/plot>Go to plot page</a>'
def index():
        return render_template('index.html')
def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n
def make_my_plot(col):
        company_name=col
        mystrr='http://d.yimg.com/autoc.finance.yahoo.com/autoc?query='+company_name+'&callback=YAHOO.Finance.SymbolSuggest.ssCallback'
        tick_raw=requests.get(mystrr)#("http://d.yimg.com/autoc.finance.yahoo.com/autoc?query=yahoo&callback=YAHOO.Finance.SymbolSuggest.ssCallback")
        abc=tick_raw.text
        abc1=abc.split('(')
        abc2=abc1[1].split(')')
        tickr_obj=json.loads(abc2[0])
        intrm1=tickr_obj.get('ResultSet')
        intrm2=intrm1.get('Result')
        intrm3=intrm2[0]
        final_tickr=intrm3.get('symbol')
        a1="https://www.quandl.com/api/v3/datasets/WIKI/"
        a2=".json?api_key=TA-Y6ZXfBRY4cJiJBqHE"
        mystr=a1+final_tickr+a2

        rfb_auth=requests.get(mystr)#("https://www.quandl.com/api/v3/datasets/WIKI/AAPL.json?api_key=TA-Y6ZXfBRY4cJiJBqHE")
        rqst_data1 = rfb_auth.json()
        rqst_data=rqst_data1 .get('dataset')
        raw_data=rqst_data.get('data')

        date=[]
        closing=[]
        for i in range (0,len(raw_data)):
                date.append(raw_data[i][0])
                closing.append(raw_data[i][4])

        # prepare some data
        aapl = np.array(closing)
        aapl_dates = np.array(date, dtype=np.datetime64)

        aapl_avg=moving_average(aapl,n=7);
        aapl_avg1=moving_average(aapl,n=19);

        #Create a dataframe
        my_dict = {'closing_val' : aapl ,'date' : aapl_dates}
        df=DataFrame(my_dict)
        abc1=pd.rolling_mean(df.loc[:,'closing_val'], 7)
        for i in range (0,7):
                abc1[i]=abc1[7]
        df['shrt_mv_avrg']=abc1
        abc2=pd.rolling_mean(df.loc[:,'closing_val'], 19)
        for i in range (0,19):
                abc2[i]=abc2[19]
        df['lng_mv_avrg']=abc2
        shtr_avg=np.array(df.loc[:,'shrt_mv_avrg'])
        lng_avg=np.array(df.loc[:,'lng_mv_avrg'])
		
		# output to static HTML file
        #output_file("QUANDL_AAPL_stocks.html", title="QUANDL_stocks.py example")

        # create a new plot with a a datetime axis type
        p = figure(width=800, height=350, x_axis_type="datetime")

        # add renderers
        p.circle(aapl_dates, aapl, size=4, color='darkgrey', alpha=0.2, legend='close')
        p.line(aapl_dates, shtr_avg, color='navy', legend='short_avg')#aapl_avg
        p.line(aapl_dates, lng_avg, color='blue', legend='long_avg')#aapl_avg1

        # NEW: customize by setting attributes
        p.title = "QUANDL data for=>"+col+':'+final_tickr
        p.legend.orientation = "top_left"
        p.grid.grid_line_alpha=0
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'Price'
        p.ygrid.band_fill_color="olive"
        p.ygrid.band_fill_alpha = 0.1
        # show the results
        return p

@app.route('/plot/', methods=['GET', 'POST'])
#@app.route('/plot/<color>', methods=['GET', 'POST'])
def hello(color='Google'):
        if request.method == 'POST' and 'name' in request.form:
                color = request.form['name']
        try:
                plot = make_my_plot(color)
        except Exception as e:
            return render_template('error.html')

        script, div = embed.components(plot)
        return render_template(
                'bokeh.html',
                script=script,
                div=div
                )

if __name__ == '__main__':
  app.run(port=33507)
