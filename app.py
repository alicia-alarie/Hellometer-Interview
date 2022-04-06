from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import numpy as np

import pandas as pd
from bokeh.plotting import figure, show
from bokeh.resources import CDN
from bokeh.embed import file_html
from bokeh.layouts import gridplot
from bokeh.models import Range1d




app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    if request.method == 'POST':
        print('post')
        f = request.files['file']
        f.save(secure_filename(f.filename))
    return render_template('index.html',methods=['POST'])



@app.route('/display', methods = ['GET', 'POST'])
def display():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        print('file uploaded successfully')
        
        
        #filename='/Volumes/GoogleDrive/My Drive/Interviews/Hellometer_Interview/flask-framework-master/'+secure_filename(f.filename)
        #print(filename)
        filename1=secure_filename(f.filename)
        
        df = pd.read_csv (filename1)
        num_hist_bins=10
        bins_pre=np.linspace(df.pre_orderboard.min(),df.pre_orderboard.max()/60,num_hist_bins)
        bins_order=np.linspace(df.orderboard.min(),df.orderboard.max()/60,num_hist_bins)
        bins_pickup=np.linspace(df.pickup.min(),df.pickup.max()/60,num_hist_bins)
        max_counts=[df.pre_orderboard.div(60).value_counts(bins=bins_pre).max(),df.orderboard.div(60).value_counts(bins=bins_order).max(),df.pickup.div(60).value_counts(bins=bins_pickup).max()]
        max_values=[df.pre_orderboard.div(60).max(),df.orderboard.div(60).max(),df.pickup.div(60).max()]
        x_axismax=max(max_values) 
        y_axismax=(max(max_counts)+100) #add 100 to pad with extra white space to see the bar fully
        bin_width=(x_axismax/2)/num_hist_bins
        
        #time spent waiting to order vs getting order complete vs pickup- wheich part is the bottleneck?
        #plot 1 - pre-orderboard times over 1 week
        p1 = figure(title="pre-orderboard time over one week", x_axis_label='pre-orderboard times (minutes)', y_axis_label='frequency')
        p1.x_range = Range1d(0, x_axismax)
        p1.y_range = Range1d(0, y_axismax)
        bins = bins_pre
        heights=df.pre_orderboard.div(60).value_counts(bins=bins).sort_index()
        p1.vbar(x=bins[1::],width=bin_width, bottom=0,top=heights, color="#CAB2D6", alpha=0.5)
        
        
        #plot 2 - orderboard times over 1 week
        p2 = figure(title="orderboard time over one week", x_axis_label='orderboard times (minutes)', y_axis_label='frequency ')
        p2.x_range = Range1d(0, x_axismax)
        p2.y_range = Range1d(0, y_axismax)
        bins = bins_order
        heights=df.orderboard.div(60).value_counts(bins=bins).sort_index()
        p2.vbar(x=bins[1::],width=bin_width, bottom=0,top=heights, color="#CAB2D6", alpha=0.5)
        
        # plot 3 - pickup times over 1 week
        p3 = figure(title="pickup times over one week", x_axis_label='pickup times (minutes)', y_axis_label='frequency')
        p3.x_range = Range1d(0, x_axismax)
        p3.y_range = Range1d(0, y_axismax)
        bins = bins_pickup
        heights=df.pickup.div(60).value_counts(bins=bins).sort_index()
        p3.vbar(x=bins[1::],width=bin_width, bottom=0,top=heights, color="#CAB2D6", alpha=0.5)
        
        #does long orderboard time correlate to time of day, how busy it is?
        #simulating google busy times graph by time of day
        timestamps=pd.to_datetime(df.arrival_time)
        hour_of_day=timestamps.dt.hour
        df['hour']=hour_of_day
        hour_plot=df.groupby('hour').mean()
        
        # plot 4 - average pre-orderboard times by hour of day
        p4 = figure(title="Avg pre-orderboard time by business hour", x_axis_label='time of day', y_axis_label='favg pre-orderboard time (seconds)')
        p4.y_range = Range1d(0, 200)
        bins = np.linspace(df.hour.min(),df.hour.max(),df.hour.max()-df.hour.min()+1)
        heights=hour_plot.pre_orderboard
        p4.vbar(x=bins,width=0.5, bottom=0,top=heights, color="navy", alpha=0.5)
        
        
        # plot 5 - average pre-orderboard times by hour of day
        p5 = figure(title="Avg orderboard time by business hour", x_axis_label='time of day', y_axis_label='avg orderboard time (seconds)')
        p5.y_range = Range1d(0, 200)
        heights=hour_plot.orderboard
        p5.vbar(x=bins,width=0.5, bottom=0,top=heights, color="navy", alpha=0.5)
        
        
        # plot 6 - average pre-orderboard times by hour of day
        p6 = figure(title="Avg pickup time by business hour", x_axis_label='time of day', y_axis_label='avg pickup time (seconds)')
        p6.y_range = Range1d(0, 200)
        heights=hour_plot.pickup
        p6.vbar(x=bins,width=0.5, bottom=0,top=heights, color="navy", alpha=0.5)
        
        
        # make a grid to display all the graphs
        grid = gridplot([p1, p2, p3, p4 ,p5, p6], ncols=3, sizing_mode="stretch_both")
        show(grid)
        html = file_html(grid, CDN, "display.html")
        
        
        return render_template('display.html',user_image=filename1)


@app.route('/about')
def about():
  return render_template('about.html')

if __name__ == '__main__':
  app.run()#ort=33508
