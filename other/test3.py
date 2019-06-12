# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 11:59:19 2018

@author: whj
"""

import matplotlib.pyplot as plt
import numpy as np

x=range(1,10)
y=[2*v for v in x]
print(x, y)
plt.plot(x, y)
pos=plt.ginput(1)
print(pos)