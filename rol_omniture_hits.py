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
from datetime import timedelta


#######data from ROL 
#datetime_object = datetime.datetime.strptime('2018/02/20', '%Y/%m/%d')
#
#end_date = datetime_object + datetime.timedelta(days=7)
#read cleaned data for omniture_hits and ps deta
parse_dates=['FIRST_PAID_DATE', 'EXPIRATION_DATE', 'RETAINED_ORDER_DATE' , 'ORDER_DATE', 'OPT_OUT_DATE', ]

customer_rol_df = pd.read_csv('/Users/razzak_lebbai/Desktop/customer_rol/data/customer_rol_us_clean.csv',  nrows=None, parse_dates=parse_dates)

##customer_rol_df = pd.read_csv('/Users/razzak_lebbai/Desktop/customer_rol/data/customer_rol_us_clean.csv',  nrows=None, parse_dates=parse_dates)
customer_rol_df['has_business'] = (customer_rol_df.RETAINED_ORDER_NUMBER.isnull()==False).astype(int)




customer_rol_df['RETAINED_CHANNEL'] = customer_rol_df.RETAINED_CHANNEL.replace('online (1st)', 'Online (1st)')
customer_rol_df['RETAINED_SUB_CHANNEL'] = customer_rol_df.RETAINED_SUB_CHANNEL.replace('online (1st)', 'Online (1st)')

customer_rol_df['ONLINE_SUB_CHANNEL'] = customer_rol_df.ONLINE_SUB_CHANNEL.replace('online (1st)', 'Online (1st)')
customer_rol_df['ONLINE_SUB_CHANNEL'] = customer_rol_df.ONLINE_SUB_CHANNEL.replace('Online 1st', 'Online (1st)')
customer_rol_df['ONLINE_SUB_CHANNEL'] = customer_rol_df.ONLINE_SUB_CHANNEL.replace('Returning Online', 'Online (Returning)')
customer_rol_df['ONLINE_SUB_CHANNEL'] = customer_rol_df.ONLINE_SUB_CHANNEL.replace('AR', 'AutoRenew')

##remove active customers 
##customer_rol_df = customer_rol_df[customer_rol_df.EXPIRATION_DATE<end_date]

###get customers with business

customer_rol_ret_df = customer_rol_df[customer_rol_df.has_business==1]
customer_rol_non_ret_df = customer_rol_df[customer_rol_df.has_business==0]



##create group with aggregation
def create_retGroups(df, ret_gpby='RETAINED_CHANNEL', deci=3):
    agg_ret_gp = df.groupby(ret_gpby)[['has_business']].count().unstack()
    agg_ret_gp = agg_ret_gp.fillna(0)
    agg_ret_gp = agg_ret_gp.reset_index(level=0)
    del agg_ret_gp['level_0']
    agg_ret_gp =  agg_ret_gp.rename(columns={0:ret_gpby+'_count'})
    
    agg_ret_gp[ret_gpby+'_percentage']= (100*agg_ret_gp[ret_gpby+'_count']/agg_ret_gp[ret_gpby+'_count'].sum()).round(deci)

    return agg_ret_gp




ret_list_columns=['RETAINED_CHANNEL', 'RETAINED_SUB_CHANNEL']
#

ret_list_df=[]


#
#
##create data frames after retention
for col in ret_list_columns:
    ret_list_df.append(create_retGroups(customer_rol_ret_df, ret_gpby=col, deci=2))
    
##now only take retention PSNs and calcuate the retentione percentage for each PSN]

for df in ret_list_df:
     
    render_mpl_table(df.reset_index(), header_columns=0, font_size=14, col_width=3.5,path='/Users/razzak_lebbai/Desktop/customer_rol/src/analysis/plots/after_ret/table_retention_distribution'+df.index.name+'.png')

  
        
    BarPlotWithGroup(df[df.columns[1]], title='Retention rate: distribustion on  '+df.index.name, \
                     path='/Users/razzak_lebbai/Desktop/customer_rol/src/analysis/plots/after_ret/retention_rate_distrubution_'+df.index.name+'.png')
    
    BarPlotWithGroupNoAnoSci(df[df.columns[0]], title='# Retention consumers: distribustionon '+df.index.name, \
                            path='/Users/razzak_lebbai/Desktop/customer_rol/src/analysis/plots/after_ret/retention_number_distrubution_'+df.index.name+'.png')
#    ##plottable(df, path='/Users/razzak_lebbai/Desktop/customer_rol/src/analysis/plots/after_ret/table_retention_distribution'+df.index.name+'.png')
##    render_mpl_table(df.reset_index(), header_columns=0, font_size=14, col_width=2.5,path='/Users/razzak_lebbai/Desktop/customer_rol/src/analysis/plots/after_ret/table_retention_distribution'+df.index.name+'.png')

  



###############data from omniture hits#######


#read cleaned data for omniture_hits and ps deta
parse_dates=['EXPIRATION_DATE', 'VISIT_STRT_DTTM_GMT' ]


omniture_rol_df = pd.read_csv('/Users/razzak_lebbai/Desktop/customer_rol/data/rol_omniture_hits_May02.csv', parse_dates=parse_dates, nrows=None)
##parse_dates=parse_dates

omniture_rol_df['Business_outcome']= (omniture_rol_df.PRCH_ID.isnull()==False).astype(int)

##now on non business psn, only take customers who actually expiration is already passed


outcome_df =omniture_rol_df.groupby('INCM_PSN_NUM').agg({'Business_outcome':'sum'})

outcome_psn_df = (outcome_df.Business_outcome>0).astype(int).reset_index()

pos_outcome = outcome_psn_df[outcome_psn_df.Business_outcome==1]
neg_outcome = outcome_psn_df[outcome_psn_df.Business_outcome==0]

def find_win_rate(df):
    outcome_df =df.groupby('INCM_PSN_NUM').agg({'Business_outcome':'sum'})
    outcome_psn_df = (outcome_df.Business_outcome>0).astype(int).reset_index()
    return outcome_psn_df.shape[0], outcome_psn_df[outcome_psn_df.Business_outcome==1].shape[0],outcome_psn_df[outcome_psn_df.Business_outcome==1].shape[0]/outcome_psn_df.shape[0] 
    
##conditional_df_list=[omniture_rol_df, omniture_rol_df[omniture_rol_df.EXPIRATION_DATE<=omniture_rol_df.VISIT_STRT_DTTM_GMT], omniture_rol_df[omniture_rol_df.EXPIRATION_DATE>omniture_rol_df.VISIT_STRT_DTTM_GMT]] 
    
conditional_df_dict={'E60plus': omniture_rol_df, 
                     'lessE':omniture_rol_df[omniture_rol_df.EXPIRATION_DATE<=pd.to_datetime(omniture_rol_df.VISIT_STRT_DTTM_GMT.dt.date)],
                     'moreE':omniture_rol_df[omniture_rol_df.EXPIRATION_DATE>pd.to_datetime(omniture_rol_df.VISIT_STRT_DTTM_GMT.dt.date)], 
                     'E7plus':omniture_rol_df[omniture_rol_df.EXPIRATION_DATE < (pd.to_datetime(omniture_rol_df.VISIT_STRT_DTTM_GMT.dt.date)+ pd.DateOffset(days=7))],
                     'E60minus':omniture_rol_df[omniture_rol_df.EXPIRATION_DATE >= (pd.to_datetime(omniture_rol_df.VISIT_STRT_DTTM_GMT.dt.date)+ pd.DateOffset(days=-60))]
                     }   

retention_list=[]
data_range_list=[]

for k,v in conditional_df_dict.items():
    print([k,find_win_rate(v)])
    data_range_list.append(k)
    retention_list.append(find_win_rate(v))
    
    
retention_df=pd.DataFrame(np.array(retention_list), columns=['total_customer', 'Nunmber_bussiness', 'Retention_ratio'])
    
retention_df['Visiting_datetime_range']=np.array(data_range_list)
retention_df['Retention' ]= 100*(retention_df.Retention_ratio.round(4))

retention_df=retention_df.loc[:,~retention_df.columns.duplicated()]
retention_df=retention_df.set_index('Visiting_datetime_range')



###plots
ag=retention_df.loc[:, 'Retention']
ag_total=retention_df.loc[:, 'total_customer']

heights=[]
ax=ag.plot(kind='bar', colormap=cm.Accent, width=0.95, title='Retention Rate')
for p in range(len(ax.patches)):
    ax.annotate(str(ax.patches[p].get_height())+'%', (ax.patches[p].get_x() * 1.01, ax.patches[p].get_height() * 1.01))
    ax.annotate(int(ag_total.loc[ag_total.index[p]]), (ax.patches[p].get_x() + 0.45*ax.patches[p].get_width(), ax.patches[p].get_height() * 0.5), rotation=90)
    heights.append(ax.patches[p].get_height())
handles, labels = ax.get_legend_handles_labels()
##lgd = ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(1.1,-0.05))
##ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2e'))
plt.ylim(0, max(heights)*1.08)
plt.tight_layout()
plt.savefig('/Users/razzak_lebbai/Desktop/customer_rol/src/plots/omniture_plots/retention_omni.png')
plt.show()



##now check non business customers in omniture hits tables are in ROL success table


##read estore order data


estore_ord_df_final_clean = pd.read_csv('/Users/razzak_lebbai/Desktop/customer_rol/data/estore_ord_rol_clean_v2.csv')

