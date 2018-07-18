#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 13:28:44 2018

@author: razzak_lebbai
"""

import pandas as pd
import numpy as np

estore_ord_df= pd.read_csv('/Users/razzak_lebbai/Desktop/customer_rol/data/estore_rol_v1.csv',  nrows=None)

#get the duplicate order and PSN
dup_order = estore_ord_df.groupby(['ORDER_NUMBER', 'PSN', 'PRODUCT_FAMILY']).size()

dup_order = dup_order.reset_index(name='nrows')


dup_order_test = estore_ord_df.groupby(['ORDER_NUMBER', 'PSN', 'PRODUCT_FAMILY']).agg({'PSN':'count', 'NET_SALES':'sum','RETURN_SALES':'sum'})


dup_order_test.columns=['nrows', 'NET_SALES', 'RETURN_SALES' ]

dup_order_test = dup_order_test.reset_index()

##get duplicate row orders and PSN
dup_order_psn = dup_order_test[dup_order_test.nrows>1]
##make numpy sum problem due to size (for 0 values)
dup_order_psn.loc[(dup_order_psn.NET_SALES>-0.01) & (dup_order_psn.NET_SALES<0.01), 'NET_SALES'] = 0.0

##find negative 
##net sales and remove thmem
neg_return_df = dup_order_psn[dup_order_psn.NET_SALES<0.0]
neg_return_order_num = neg_return_df.ORDER_NUMBER.unique().tolist()
neg_return_order_psn = neg_return_df.PSN.unique().tolist()




##find out full return ######################
full_return_df = dup_order_psn[dup_order_psn.NET_SALES==0.00]

full_return_order_num = full_return_df.ORDER_NUMBER.unique().tolist()
full_return_order_psn =full_return_df.PSN.unique().tolist()

##get full return orders
full_return_all_order = estore_ord_df[(estore_ord_df.ORDER_NUMBER.isin(full_return_order_num)==True) & (estore_ord_df.PSN.isin(full_return_order_psn)==True)]

##remove zoro demand sales rows
full_return_all_order_clean = full_return_all_order[full_return_all_order.DEMAND_SALES!=0]

full_return_all_order_clean['RETURN_SALES']=full_return_all_order_clean['DEMAND_SALES']*-1
full_return_all_order_clean['NET_SALES']=0.0
full_return_all_order_clean['Refund_type']='F'
full_return_all_order_clean =full_return_all_order_clean.drop_duplicates(subset='PSN')
##there is still some returns with multople rpducts families
##just removed duplicates 


#########Full return END

####Partial Return##########################################

partial_return_df = dup_order_psn[dup_order_psn.NET_SALES>0.00]


partial_return_order_num = partial_return_df.ORDER_NUMBER.unique().tolist()
partial_return_order_psn = partial_return_df.PSN.unique().tolist()

##get full return orders
partial_return_all_order = estore_ord_df[(estore_ord_df.ORDER_NUMBER.isin(partial_return_order_num)==True) & (estore_ord_df.PSN.isin(partial_return_order_psn)==True)]

##remove zoro demand sales rows
partial_return_all_order_clean = partial_return_all_order[partial_return_all_order.DEMAND_SALES!=0]

##drop net sales and return sales 
partial_return_all_order_clean =   partial_return_all_order_clean.drop(['NET_SALES','RETURN_SALES'], axis=1)

partial_return_all_order_clean_final =  partial_return_df.loc[:, ['ORDER_NUMBER', 'PSN','NET_SALES','RETURN_SALES']].merge(partial_return_all_order_clean, on=['ORDER_NUMBER','PSN'], how='inner')
partial_return_all_order_clean_final['Refund_type']='P'
##remove some duplicates
partial_return_all_order_clean_final= partial_return_all_order_clean_final.drop_duplicates(subset=['PSN','NET_SALES'])
##organise the remaining duplicates
##find duplicate psn in partial return
partial_dup_psn=partial_return_all_order_clean_final.PSN.value_counts().reset_index()[partial_return_all_order_clean_final.PSN.value_counts().reset_index()['PSN']>1]['index'].tolist()

##get non duplicate dataframe
partial_return_all_order_clean_no_dup = partial_return_all_order_clean_final[partial_return_all_order_clean_final.PSN.isin(partial_dup_psn)==False]

##get duplicates datafram
partial_return_all_order_dup = partial_return_all_order_clean_final[partial_return_all_order_clean_final.PSN.isin(partial_dup_psn)==True]

partial_dup_df = partial_return_all_order_dup.groupby('PSN').agg({'NET_SALES':'sum', 'RETURN_SALES':'sum','DEMAND_SALES':'sum','LIST_PRICE_LOCAL':'sum','DISCOUNT_AMOUNT':'sum'}).reset_index()
##drop duplicates of PSN
partial_return_all_order_dup_drop = partial_return_all_order_dup.drop_duplicates(subset='PSN')

##remove the aggregated columns values from original 
partial_return_all_order_dup_drop =  partial_return_all_order_dup_drop.drop(labels=['NET_SALES', 'RETURN_SALES','DEMAND_SALES','LIST_PRICE_LOCAL','DISCOUNT_AMOUNT'], axis=1)

##now combined aggregated values
partial_return_all_order_dup_drop_final = partial_return_all_order_dup_drop.merge(partial_dup_df, on='PSN', how='inner')

##finaly join non duplicate and cleane duplicates
partial_return_final = pd.concat([partial_return_all_order_clean_no_dup,partial_return_all_order_dup_drop_final])
#################################################################################################


####Non Refund ######################
##now remove partial and full return data from original data sets#############################

##remove full return orders
remove_full_return_all_order = estore_ord_df[(estore_ord_df.ORDER_NUMBER.isin(full_return_order_num)==False) | (estore_ord_df.PSN.isin(full_return_order_psn)==False)]

##now remove partial  returen orders############
remove_full_and_partial_return_all_order = remove_full_return_all_order[(remove_full_return_all_order.ORDER_NUMBER.isin(partial_return_order_num)==False) | (remove_full_return_all_order.PSN.isin(partial_return_order_psn)==False)]
remove_full_and_partial_return_all_order['Refund_type']='N'
##this one has duplicates too due to legacy product 
##aggregate them and readjust the table

no_return_dup_psn =remove_full_and_partial_return_all_order.PSN.value_counts().reset_index()[remove_full_and_partial_return_all_order.PSN.value_counts().reset_index()['PSN']>1]['index'].tolist()

##get non duplicate dataframe
remove_full_and_partial_return_all_order_no_dup = remove_full_and_partial_return_all_order[remove_full_and_partial_return_all_order.PSN.isin(no_return_dup_psn)==False]

##get duplicates datafram
remove_full_and_partial_return_all_order_dup = remove_full_and_partial_return_all_order[remove_full_and_partial_return_all_order.PSN.isin(no_return_dup_psn)==True]

##aggregate some uncommon values 
no_return_dup_df = remove_full_and_partial_return_all_order_dup.groupby('PSN').agg({'NET_SALES':'sum', 'RETURN_SALES':'sum','DEMAND_SALES':'sum','LIST_PRICE_LOCAL':'sum','DISCOUNT_AMOUNT':'sum'}).reset_index()

##drop duplicates of PSN
remove_full_and_partial_return_all_order_dup_drop = remove_full_and_partial_return_all_order_dup.drop_duplicates(subset='PSN')

##remove the aggregated columns values from original 
remove_full_and_partial_return_all_order_dup_drop =  remove_full_and_partial_return_all_order_dup_drop.drop(labels=['NET_SALES', 'RETURN_SALES','DEMAND_SALES','LIST_PRICE_LOCAL','DISCOUNT_AMOUNT'], axis=1)

##now combined aggregated values
no_return_dup_order_final = remove_full_and_partial_return_all_order_dup_drop.merge(no_return_dup_df, on='PSN', how='inner')




##finaly join non duplicate and cleane duplicates
no_return_final = pd.concat([remove_full_and_partial_return_all_order_no_dup,no_return_dup_order_final])

#######


estore_ord_df_final = pd.concat([full_return_all_order_clean,partial_return_final,no_return_final])
##remove negative net sales orders

estore_ord_df_final_clean = estore_ord_df_final[(estore_ord_df_final.ORDER_NUMBER.isin(neg_return_order_num)==False) | (estore_ord_df_final.PSN.isin(neg_return_order_psn)==False)]




estore_ord_df_final_clean.to_csv('/Users/razzak_lebbai/Desktop/customer_rol/data/estore_ord_rol_clean.csv', index=False)

