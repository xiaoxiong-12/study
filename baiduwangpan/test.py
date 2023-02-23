#!/usr/bin/python
# author Yu
# 2023年02月19日
import os
from os import listdir

a=listdir(os.getcwd())
print(a)

print(os.stat(a[1]).st_size)