#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 15:20:26 2018

@author: razzak_lebbai
"""


import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.ticker as mtick
from pandas.tools.plotting import table

train_cust = pd.read_csv('/Users/razzak_lebbai/Desktop/msc/test/data/train.csv',  nrows=None)


members_df = pd.read_csv('/Users/razzak_lebbai/Desktop/msc/test/data/members.csv',  nrows=None)

##join with members
train_cust_mem = train_cust.merge(members_df, on='msno', how='inner')
