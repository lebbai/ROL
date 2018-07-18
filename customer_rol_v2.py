#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 12:36:37 2018
@author: razzak_lebbai
"""
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.ticker as mtick
from pandas.tools.plotting import table

from plottings import *
import datetime




datetime_object = datetime.datetime.strptime('2018/02/20', '%Y/%m/%d')

end_date = datetime_object + datetime.timedelta(days=7)
#read cleaned data for omniture_hits and ps deta
parse_dates=['FIRST_PAID_DATE', 'EXPIRATION_DATE', 'RETAINED_ORDER_DATE' , 'ORDER_DATE', 'OPT_OUT_DATE', ]


customer_rol_df = pd.read_csv('/Users/razzak_lebbai/Desktop/customer_rol/data/customer_rol_us_clean.csv',  nrows=None, parse_dates=parse_dates)
customer_rol_df['has_business'] = (customer_rol_df.RETAINED_ORDER_NUMBER.isnull()==False).astype(int)

##remove active customers 
customer_rol_df = customer_rol_df[customer_rol_df.EXPIRATION_DATE<end_date]


#
###read cleaned data for omniture_hits and ps deta
#parse_dates=['START_DATE', 'B_EXPIRATION_DATE', 'B_ACTIVATION_DATE' , 'B_ORDER_DATE', 'B_ORDER_DATE_modified', 'B_OPT_OUT_DATE', 'Session_Start_Time','FST_HIT_DTTM_GMT', 'HIT_DTTM_GMT', 'VISIT_STRT_DTTM_GMT']
#omniture_hits_df = pd.read_csv('/Users/razzak_lebbai/Desktop/omniture/data/OneYear_omniture_hits_sample_with_before_psn_dtl.csv', error_bad_lines=False, nrows=None, parse_dates=parse_dates)


##Retention_rate = customer_rol_df[customer_rol_df.RETAINED_ORDER_NUMBER.isnull()==False].shape[0]/customer_rol_df.shape[0]
totalretention = customer_rol_df.groupby(['has_business'])[['has_business']].count()
totalretention['Ratio'] = totalretention.has_business/totalretention.has_business.sum()
##retention
BarPlotWithGroup(totalretention['Ratio'], path='/Users/razzak_lebbai/Desktop/customer_rol/src/analysis/plots/retention_ratio.png')
BarPlotWithGroup(totalretention['has_business'], path='/Users/razzak_lebbai/Desktop/customer_rol/src/analysis/plots/success_numbers.png')



customer_rol_df['RETAINED_CHANNEL'] = customer_rol_df.RETAINED_CHANNEL.replace('online (1st)', 'Online (1st)')
customer_rol_df['RETAINED_SUB_CHANNEL'] = customer_rol_df.RETAINED_SUB_CHANNEL.replace('online (1st)', 'Online (1st)')

customer_rol_df['ONLINE_SUB_CHANNEL'] = customer_rol_df.ONLINE_SUB_CHANNEL.replace('online (1st)', 'Online (1st)')
customer_rol_df['ONLINE_SUB_CHANNEL'] = customer_rol_df.ONLINE_SUB_CHANNEL.replace('Online 1st', 'Online (1st)')
customer_rol_df['ONLINE_SUB_CHANNEL'] = customer_rol_df.ONLINE_SUB_CHANNEL.replace('Returning Online', 'Online (Returning)')
customer_rol_df['ONLINE_SUB_CHANNEL'] = customer_rol_df.ONLINE_SUB_CHANNEL.replace('AR', 'AutoRenew')
customer_rol_df['PSN_START_MONTH']  = pd.to_datetime(customer_rol_df.PSN_START_DATE).dt.month
customer_rol_df['EXPIRATION_DATE_MONTH']  = pd.to_datetime(customer_rol_df.EXPIRATION_DATE).dt.month
customer_rol_df['EXPIRATION_DATE_YEAR']  = pd.to_datetime(customer_rol_df.EXPIRATION_DATE).dt.year

customer_rol_df['ORDER_DATE_YEAR']  = pd.to_datetime(customer_rol_df.ORDER_DATE).dt.year


##remove 2013 and 2014
"""
2016    3132081
2017    2379517
2018     351226
2015       8685
2014         88
2013          3
"""
customer_rol_df = customer_rol_df[customer_rol_df.EXPIRATION_DATE_YEAR>2014]

labels = ["{0} - {1}".format(i, i + 50) for i in range(0, 500, 50)]
labels.append(np.nan)

##catogarize the new sales
customer_rol_df['netsales_range'] = pd.cut(customer_rol_df.NET_SALES, range(0, 550, 50), right=False)
customer_rol_df['netsales_range'] = customer_rol_df.netsales_range.astype(str)
##bins2 = np.array([-1, 50, 100,150, 200, 250,300,350,400, 450, 500,np.nan])
#
#np.digitize(bins2, bins2, right=True)
#Out[122]: array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11])

##customer_rol_df['netsales_range']=np.digitize(customer_rol_df.NET_SALES, bins2, right=True)

##import seaborn
##seaborn.set() #make the plots look pretty


##plot bar plots for number of business with OPT_OUT_Value (active abd passiv)
##for out out
agg_opt = customer_rol_df.groupby(['EXPIRATION_DATE_YEAR', 'OPT_OUT_VALUE', 'has_business'])[['has_business']].count().unstack()
agg_opt.columns = agg_opt.columns.droplevel()
agg_opt['ratio_0'] , agg_opt['ratio_1']= (agg_opt[0]/agg_opt[0].sum()).round(4), (agg_opt[1]/agg_opt[1].sum()).round(4)
agg_opt['total_customer']= agg_opt.loc[:,[0,1]].sum(axis=1)
agg_opt['Ret_Rate']= (agg_opt.loc[:,1].div(agg_opt.loc[:,[0,1]].sum(axis=1), axis=0)*100).round(2)

##ag_opt[['No', 'Yes']]= (ag_opt[['No', 'Yes']]*100).astype(str)+'%'

   

##create aggregated features
list_columns=['OPT_OUT_VALUE', 'ONLINE_SUB_CHANNEL', 'PROD_FMLY_GRP','PURCHASE_AR_FLAG', 'netsales_range']
list_df=[]
for col in list_columns:
    temp_df='agg_'+col
    temp_df = customer_rol_df.groupby(['EXPIRATION_DATE_YEAR', col, 'has_business'])[['has_business']].count().unstack()
    temp_df.columns = temp_df.columns.droplevel() 
    temp_df['ratio_0'] , temp_df['ratio_1']= (temp_df[0]/temp_df[0].sum()).round(4), (temp_df[1]/temp_df[1].sum()).round(4)
    temp_df['total_customer']= (temp_df.loc[:,[0,1]].sum(axis=1)).astype(int)
    temp_df['Ret_Rate']= (temp_df.loc[:,1].div(temp_df.loc[:,[0,1]].sum(axis=1), axis=0)*100).round(2)
    ##del temp_df['ratio_0']
    list_df.append(temp_df)

 
##plot cpomparision retention plots for each relavent features
  
count=0
for sdf in list_df:
    render_mpl_table(sdf.reset_index(), header_columns=0, font_size=14, col_width=2.5, path='/Users/razzak_lebbai/Desktop/customer_rol/src/analysis/plots/before_ret_yearly/table_year_'+sdf.index.names[1]+'.png')
    ##plottable(sdf, path='/Users/razzak_lebbai/Desktop/customer_rol/src/analysis/plots/before_ret_yearly/table_'+df.index.name+'.png')
##    
    
    for le in sdf.index.levels[0]:
        df= sdf.loc[[le], :]
    ##number of success and failure 
    ##print(df.loc[:,[0,1]])
#    BarPlotWithGroupNoAnoSci(df.loc[:,[1,0]], title='# success/failure based on '+df.index.name,\
#                             path='/Users/razzak_lebbai/Desktop/customer_rol/src/analysis/plots/before_ret/success_num_year'+df.index.name+'.png')
#    
#    ##success and failure rates
#   ## print(df.loc[:,['ratio_0','ratio_1']])
#    BarPlotWithGroupNoAnoNosci(df.loc[:,['ratio_1','ratio_0']], title='success/failure ratio based on '+df.index.name, \
#                             path='/Users/razzak_lebbai/Desktop/customer_rol/src/analysis/plots/before_ret/success_rate_year'+df.index.name+'.png')
# 
#    ##get retention 
        BarPlotWithGroupAnoNosci(df.loc[:,['Ret_Rate']], title='Retention rate based for '+df.index.names[1]+' Year: '+str(df.index[0][0]), colormap=cm.summer,\
                             path='/Users/razzak_lebbai/Desktop/customer_rol/src/analysis/plots/before_ret_yearly/retention_year_'+str(df.index[0][0])+'_'+df.index.names[1]+'.png')
#   
#    BarPlotWithGroupAnoNosci2(df.loc[:,['Ret_Rate']], df.loc[:,['total_customer']],title='Retention rate based on '+df.index.name, colormap=cm.summer,\
##                              path='/Users/razzak_lebbai/Desktop/customer_rol/src/analysis/plots/before_ret/retention_v2_year'+df.index.name+'.png')
##    plottable(df, path='/Users/razzak_lebbai/Desktop/customer_rol/src/analysis/plots/before_ret/table_'+df.index.name+'.png')
##    render_mpl_table(sdf.reset_index(), header_columns=0, font_size=14, col_width=2.5, path='/Users/razzak_lebbai/Desktop/customer_rol/src/analysis/plots/before_ret_yearly/table_year_'+sdf.index.names[0]+'.png')
#  
