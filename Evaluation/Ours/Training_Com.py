# -*- coding: UTF-8 -*- 


import os
import csv
import re
import codecs
import numpy as np
import jenkspy
import sqlite3
import collections
import pycrfsuite
import pickle
from itertools import chain
import time
from sklearn.neighbors import KernelDensity

import sklearn
import scipy.stats
from sklearn.metrics import make_scorer
from sklearn.cross_validation import cross_val_score
from sklearn.grid_search import RandomizedSearchCV

import sklearn_crfsuite
from sklearn_crfsuite import scorers
from sklearn_crfsuite import metrics
from scipy import stats

def dist_tags(b):
	ntag=[]
	dtag=[]
	ltag=[]
	atag=[]
	gtag=[]
	abv0=['FN','YR','AT','PG','SR','ED']
	b=[tmp for tmp in b if tmp in abv0]
	#wtag=1.0*sum([1 if tmp in b else 0 for tmp in abv0])/len(abv0)
	wtag=[1 if tmp in b else 0 for tmp in abv0]
	tmp=[b[j] for j in sorted(set([b.index(elem) for elem in b]))]
	bb=b[::-1]
	tmp2=[bb[j] for j in sorted(set([bb.index(elem) for elem in bb]))]
	for i in range (len(abv0)):
		if abv0[i] in b:
			#a=len(re.findall(r'('+abv0[i]+')+',''.join(b)))
			#ntag.extend([1.0*a/len(b)])
			#tmp = re.finditer(r'('+abv0[i]+')+',''.join(b))
			#dtag.extend([1.0*np.mean([(m.end(0)-m.start(0))/2 for m in tmp])/len(b)])
			#tmp=[0]*2
			#tmp[0]=b.index(abv0[i])
			#tmp[1]=len(b)-list(reversed(b)).index(abv0[i])
			#a=filter(lambda a: a != abv0[i], {i for i in b[tmp[0]:tmp[1]]})
			#ltag.extend([1.0*len(a)/len(b)])
			#tmp=[b[j] for j in sorted(set([b.index(elem) for elem in b]))]
			atag.extend([1.0*(tmp.index(abv0[i])+1)/len(tmp)])   #position of the tag in 
			ntag.extend([1.0*(tmp2.index(abv0[i])+1)/len(tmp2)])   #position of the tag in the reference string
		else:
			ntag.extend([2])
			#dtag.extend([-1])
			#ltag.extend([-1])
			atag.extend([2])
	gtag=np.concatenate((ltag,atag,wtag,ntag))    #best
	#gtag=np.concatenate((ntag,[wtag]))
	return ntag,dtag,ltag,atag,wtag,gtag



def findtag(w,l):    #w is the word and l is if the tag is still open 
	tag=['given-names','surname','year','title','editor','source','publisher','other','page','volume','page','issue','url','identifier']

	a=-1
	i=0
	v=True
	while (i<len(tag))&(v):
		tmp1=re.findall(r'<'+tag[i]+'>'.decode('utf-8'), w)
		tmp2=re.findall(r'</'+tag[i]+'>'.decode('utf-8'), w)
		if (bool(tmp1) & bool(tmp2)):
			v=False
			w=re.sub(r'<'+tag[i]+'>|</'+tag[i]+'>'.decode('utf-8'), '', w)
			a=abv[i]
			l=-1
		elif tmp2:	
			v=False
			w=re.sub(r'<'+tag[i]+'>|</'+tag[i]+'>'.decode('utf-8'), '', w)
			a=abv[i]
			l=-1
		elif tmp1:
			v=False
			w=re.sub(r'<'+tag[i]+'>|</'+tag[i]+'>'.decode('utf-8'), '', w)
			a=abv[i]
			l=i
		i+=1
	if ((v)&(l!=-1)):
		a=abv[l]
	elif ((v)&(l==-1)):
		a='XX'
	return w,a,l

def preproc(ln):
	#remove or replace strange character:
	ln=re.sub(r'–'.decode('utf-8'),'-',ln)
	ln=re.sub(r'<article-title>'.decode('utf-8'),'<title>',ln)
	ln=re.sub(r'</article-title>'.decode('utf-8'),'</title>',ln)
	
	
	# remove empty tags
	tag='given-names|surname|year|title|editor|source|publisher|other|page|volume|author|fpage|lpage|issue|url|identifier'
	tmp0=re.finditer('<('+tag+')>\s*</('+tag+')>',ln)
	tmp = [(m.start(0),m.end(0)) for m in tmp0]
	while tmp:
		ln=ln[0:tmp[0][0]]+' '+ln[tmp[0][1]:]
		tmp0=re.finditer('<('+tag+')>\s*</('+tag+')>',ln)
		tmp = [(m.start(0),m.end(0)) for m in tmp0]
	
	# add space before new tag 
	tmp0 = re.finditer(r'[^\s\(\[\{]<[^/]', ln)
	tmp = [m.start(0) for m in tmp0]
	while tmp:
		ln=ln[0:tmp[0]+1]+' '+ln[tmp[0]+1:]
		tmp0 = re.finditer(r'[^\s\(\[\{]<[^/]', ln)
		tmp = [m.start(0) for m in tmp0]
		
	# add space before new tag with parenthese
	tmp0 = re.finditer(r'[^\s][\(\[\{]<[^/]', ln)
	tmp = [m.start(0) for m in tmp0]
	while tmp:
		ln=ln[0:tmp[0]+1]+' '+ln[tmp[0]+1:]
		tmp0 = re.finditer(r'[^\s][\(\[\{]<[^/]', ln)
		tmp = [m.start(0) for m in tmp0]
	
	# remove space after beginning of new tag
	tmp0=re.finditer('<('+tag+')>\s',ln)
	tmp = [m.end(0) for m in tmp0]
	while tmp:
		ln=ln[0:tmp[0]-1]+ln[tmp[0]:]
		tmp0=re.finditer('<('+tag+')>\s',ln)
		tmp = [m.end(0) for m in tmp0]
	
	# remove space before end of tag	
	tmp=ln.find(' </')
	while tmp!=-1:
		ln=ln[0:tmp]+ln[tmp+1:]
		tmp=ln.find(' </')
	
	#separate tow tags	
	tmp=ln.find('><')
	while tmp!=-1:
		ln=ln[0:tmp+1]+' '+ln[tmp+1:]
		tmp=ln.find('><')
	
	return ln


#preparing training data
global abv
abv=['FN','LN','YR','AT','ED','SR','PB','OT','PG','VL','PG','IS','UR','ID']
dtag=[]
ltag=[]
ntag=[]
atag=[]
wtag=[]
gtag=[]   #general


#*****************************************************************************************************************************************************
# Choose the dataset:
dat_set='Ours_De'
#*****************************************************************************************************************************************************
#execfile('./src/Initial_Data.py')

trainingfolds=os.listdir("./Datasets/"+dat_set+"/CrossValidationFiles/Training/")

for tindex,trainFold in enumerate(trainingfolds):
	
	trainFile=open("./Datasets/"+dat_set+"/CrossValidationFiles/Training/"+trainFold,"r")
	inputTrainingFiles=trainFile.readlines()
	fdir=[]
	fdir2=[]
	for f in inputTrainingFiles:
		f=f.strip()
		filesplit=f.split(".")
		filename=filesplit[0].strip()
		f=filename+"."+"xml"
		fdir.append(f)
		fdir2.append(filename+"."+"csv")

	fold="./Datasets/"+dat_set+"/Seg"											
	print fdir
	train_label=[]
	for u in range (len(fdir)):
		fname=fold+"/"+fdir[u]
		file = open(fname, "rb")
		reader = csv.reader(file, delimiter='\t',quoting=csv.QUOTE_NONE)   #, quotechar='|'
		print 'File in prcossecing =  '+fdir[u]+'  . . .'
		for row in reader:
			ln=row[0].decode('utf-8')
			ln=re.sub(r'<author>|</author>', '', ln)     #remove author tag
			ln=re.sub(r'</fpage>|<lpage>', '', ln)     #change page tag
			ln=re.sub(r'<fpage>', '<page>', ln)     #change page tag
			ln=re.sub(r'</lpage>', '</page>', ln)     #change page tag
			ln=preproc(ln)
			ln=ln.split()
			l=-1          # no tag is open 
			w=ln[0]
			a,b,l=findtag(w,l)
			train_label.append([b])
			
			for i in range (1,len(ln)):
				#add the +2 word
				w=ln[i]
				a,b,l=findtag(w,l)
				train_label[len(train_label)-1].extend([b])
			tmpn,tmpd,tmpl,tmpa,tmpw,tmpg=dist_tags(train_label[len(train_label)-1])
			ntag.append(tmpn)
			dtag.append(tmpd)
			ltag.append(tmpl)
			atag.append(tmpa)
			wtag.append(tmpw)
			gtag.append(tmpg)
		file.close()

	llen=[]   #line length	
	tlen=[]	# length in terms of token 	
	fold="./Datasets/"+dat_set+"/RefLD"	
	fold2="./Datasets/"+dat_set+"/LYT"									#********************************************************************
	for u in range (len(fdir2)):	
		print 'File in prcossecing =  '+fdir2[u]+'  . . .'
		fname=fold+"/"+fdir2[u]
		file=open(fname,'rb')
		reader=file.read()
		file.close()
		reader=re.sub(r'\.[0]+e\+00[\r\n]+','',reader)
		x=re.findall('12*3*',reader)
		[llen.append([len(t)]) for t in x]
		
		fname=fold2+"/"+fdir2[u]
		file=open(fname,'rb')
		reader2=file.read()
		file.close()
		reader2=reader2.split('\r\n')
		tmp0=re.finditer('12*3*', reader)
		tmp = [(m.start(0),m.end(0)) for m in tmp0]
		for uu in tmp:
			tlen.append([sum([len((y.split('\t')[0]).split()) for y in reader2[uu[0]:uu[1]+1]])])    #number of token per ref
			if sum([len((y.split('\t')[0]).split()) for y in reader2[uu[0]:uu[1]+1]])==0:
				aaa=8
			
			
		

	#kde_ltag=KernelDensity(kernel='gaussian', bandwidth=1).fit(ltag)
	kde_ntag=KernelDensity(kernel='gaussian', bandwidth=1).fit(ntag)
	#kde_dtag=KernelDensity(kernel='gaussian', bandwidth=1).fit(dtag)
	kde_atag=KernelDensity(kernel='gaussian', bandwidth=1).fit(atag)
	kde_wtag=KernelDensity(kernel='gaussian', bandwidth=1).fit(wtag)
	#kde_gtag=KernelDensity(kernel='gaussian', bandwidth=1).fit(gtag)
	#kde_llen=KernelDensity(kernel='gaussian', bandwidth=1).fit(llen)
	#kde_tlen=KernelDensity(kernel='gaussian', bandwidth=1).fit(tlen)

	#with open('Utils/'+dat_set+'/kde_ltag_'+str(tindex)+'.pkl', 'wb') as fid:
		#pickle.dump(kde_ltag, fid) 
	with open('Utils/'+dat_set+'/kde_ntag_'+str(tindex)+'.pkl', 'wb') as fid:
		pickle.dump(kde_ntag, fid) 
	#with open('Utils/'+dat_set+'/kde_dtag_'+str(tindex)+'.pkl', 'wb') as fid:
		#pickle.dump(kde_dtag, fid) 
	with open('Utils/'+dat_set+'/kde_atag_'+str(tindex)+'.pkl', 'wb') as fid:
		pickle.dump(kde_atag, fid) 
	with open('Utils/'+dat_set+'/kde_wtag_'+str(tindex)+'.pkl', 'wb') as fid:
		pickle.dump(kde_wtag, fid) 
	#with open('Utils/'+dat_set+'/kde_gtag_'+str(tindex)+'.pkl', 'wb') as fid:
		#pickle.dump(kde_gtag, fid) 
	#with open('Utils/'+dat_set+'/kde_llen_'+str(tindex)+'.pkl', 'wb') as fid:
		#pickle.dump(kde_llen, fid) 
	#with open('Utils/'+dat_set+'/kde_tlen_'+str(tindex)+'.pkl', 'wb') as fid:
		#pickle.dump(kde_tlen, fid) 

#execfile('Training_Com.py')