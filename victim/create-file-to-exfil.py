#!/usr/local/env python3

with open('an-ip-file.txt','w') as fh:
	for i in range(0,10000):
		fh.writelines("FooBar!")