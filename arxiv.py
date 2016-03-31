from __future__ import print_function

import matplotlib
matplotlib.use('Agg')
matplotlib.rc('text', usetex=True)
matplotlib.rc('font', family='serif')
matplotlib.rc('font', serif='computer modern roman')
matplotlib.rc('font', **{'sans-serif': 'computer modern sans serif'})

from xml.dom import minidom, Node
import requests
import numpy as np
import pylab as plt
from collections import Counter
import datetime
import time
import os

# wget "http://export.arxiv.org/api/query?search_query=abs:optimal+AND+cat:astro-ph&max_results=2000" -O 4
#fn = '4'
# wget "http://export.arxiv.org/api/query?search_query=abs:optimal+AND+cat:astro-ph*&max_results=5000&sortBy=submittedDate&sortOrder=descending" -O 7
fn = '7'
if not os.path.exists(fn):
    cmd = 'wget "http://export.arxiv.org/api/query?search_query=abs:optimal+AND+cat:astro-ph*&max_results=5000&sortBy=submittedDate&sortOrder=descending" -O %s' % fn
    print(cmd)
    os.system(cmd)
# Parse query results   
dom1 = minidom.parse(fn)
#<published>2004-10-15T17:41:45Z</published>
pubs = dom1.getElementsByTagName('published')
print(len(pubs), 'published dates')
months = []
for p in pubs:
    datestring = p.firstChild.nodeValue
    # print('Date:', datestring)
    month = datestring[:7]
    months.append(month)

#print(Counter(months).most_common())
um = np.unique(months)
print('Months:', um)

monthnum = dict([(m, int(m[:4]) + (int(m[5:7],10) - 0.5)/12.) for m in months])
#dates = [datetime.date(int(m[:4]), int(m[5:7], 10), 1) for m in months]

yrs = [monthnum[m] for m in months]

plt.figure(figsize=(6,4))
plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.98)

# plt.clf()
# plt.hist(yrs, 50)
# plt.xlabel('Publication month')
# plt.ylabel('Number of "Optimals"')
# plt.savefig('monthly.png')



# http://arxiv.org/year/astro-ph/92 ... etc
# cat monthly | tr '|' ' ' | tr '!' ' ' | awk '{print $1, $2}'
monthly_totals = {
    199204: 6   , 199205: 6   , 199206: 5   , 199207: 2   , 199208: 7   ,
    199209: 6   , 199210: 7   , 199211: 14  , 199212: 6   , 199301: 12  ,
    199302: 18  , 199303: 20  , 199304: 29  , 199305: 38  , 199306: 30  ,
    199307: 40  , 199308: 48  , 199309: 59  , 199310: 52  , 199311: 77  ,
    199312: 66  , 199401: 51  , 199402: 71  , 199403: 67  , 199404: 80  ,
    199405: 75  , 199406: 75  , 199407: 99  , 199408: 104 , 199409: 95  ,
    199410: 98  , 199411: 117 , 199412: 97  , 199501: 116 , 199502: 105 ,
    199503: 124 , 199504: 101 , 199505: 148 , 199506: 148 , 199507: 118 ,
    199508: 159 , 199509: 158 , 199510: 161 , 199511: 150 , 199512: 171 ,
    199601: 197 , 199602: 158 , 199603: 161 , 199604: 185 , 199605: 204 ,
    199606: 182 , 199607: 176 , 199608: 202 , 199609: 204 , 199610: 270 ,
    199611: 234 , 199612: 245 , 199701: 246 , 199702: 242 , 199703: 201 ,
    199704: 300 , 199705: 259 , 199706: 303 , 199707: 354 , 199708: 275 ,
    199709: 306 , 199710: 374 , 199711: 356 , 199712: 360 , 199801: 322 ,
    199802: 364 , 199803: 346 , 199804: 340 , 199805: 372 , 199806: 401 ,
    199807: 350 , 199808: 360 , 199809: 412 , 199810: 510 , 199811: 481 ,
    199812: 487 , 199901: 425 , 199902: 386 , 199903: 492 , 199904: 429 ,
    199905: 395 , 199906: 504 , 199907: 447 , 199908: 364 , 199909: 518 ,
    199910: 574 , 199911: 535 , 199912: 569 , 200001: 546 , 200002: 531 ,
    200003: 486 , 200004: 413 , 200005: 607 , 200006: 458 , 200007: 478 ,
    200008: 526 , 200009: 506 , 200010: 659 , 200011: 582 , 200012: 549 ,
    200101: 573 , 200102: 506 , 200103: 522 , 200104: 490 , 200105: 567 ,
    200106: 575 , 200107: 605 , 200108: 523 , 200109: 559 , 200110: 708 ,
    200111: 607 , 200112: 571 , 200201: 551 , 200202: 526 , 200203: 524 ,
    200204: 529 , 200205: 557 , 200206: 512 , 200207: 673 , 200208: 590 ,
    200209: 632 , 200210: 697 , 200211: 655 , 200212: 581 , 200301: 656 ,
    200302: 612 , 200303: 669 , 200304: 565 , 200305: 608 , 200306: 632 ,
    200307: 566 , 200308: 548 , 200309: 836 , 200310: 917 , 200311: 633 ,
    200312: 657 , 200401: 644 , 200402: 677 , 200403: 717 , 200404: 612 ,
    200405: 637 , 200406: 685 , 200407: 649 , 200408: 590 , 200409: 769 ,
    200410: 749 , 200411: 805 , 200412: 708 , 200501: 679 , 200502: 591 ,
    200503: 715 , 200504: 673 , 200505: 630 , 200506: 769 , 200507: 720 ,
    200508: 693 , 200509: 914 , 200510: 862 , 200511: 842 , 200512: 658 ,
    200601: 718 , 200602: 633 , 200603: 860 , 200604: 619 , 200605: 752 ,
    200606: 763 , 200607: 674 , 200608: 715 , 200609: 832 , 200610: 962 ,
    200611: 952 , 200612: 791 , 200701: 925 , 200702: 755 , 200703: 810 ,
    200704: 796 , 200705: 807 , 200706: 818 , 200707: 784 , 200708: 785 ,
    200709: 940 , 200710: 993 , 200711: 921 , 200712: 807 , 200801: 1007,
    200802: 854 , 200803: 714 , 200804: 767 , 200805: 780 , 200806: 818 ,
    200807: 876 , 200808: 698 , 200809: 981 , 200810: 961 , 200811: 823 ,
    200812: 810 , 200901: 893 , 200902: 927 , 200903: 962 , 200904: 786 ,
    200905: 832 , 200906: 973 , 200907: 972 , 200908: 822 , 200909: 1089,
    200910: 1051, 200911: 957 , 200912: 1023, 201001: 936 , 201002: 858 ,
    201003: 975 , 201004: 883 , 201005: 998 , 201006: 917 , 201007: 894 ,
    201008: 900 , 201009: 1172, 201010: 1028, 201011: 1139, 201012: 916 ,
    201101: 1068, 201102: 907 , 201103: 980 , 201104: 874 , 201105: 929 ,
    201106: 974 , 201107: 917 , 201108: 924 , 201109: 1179, 201110: 1075,
    201111: 1180, 201112: 947 , 201201: 1018, 201202: 953 , 201203: 991 ,
    201204: 949 , 201205: 1030, 201206: 988 , 201207: 988 , 201208: 909 ,
    201209: 988 , 201210: 1346, 201211: 1115, 201212: 847 , 201301: 1030,
    201302: 971 , 201303: 1129, 201304: 1027, 201305: 982 , 201306: 983 ,
    201307: 1213, 201308: 974 , 201309: 1058, 201310: 1247, 201311: 957 ,
    201312: 904 , 201401: 1146, 201402: 900 , 201403: 1043, 201404: 941 ,
    201405: 1012, 201406: 1083, 201407: 1220, 201408: 930 , 201409: 1169,
    201410: 1154, 201411: 967 , 201412: 1020, 201501: 1052, 201502: 1000,
    201503: 1093, 201504: 1067, 201505: 1037, 201506: 1025, 201507: 1080,
    201508: 954 , 201509: 1216, 201510: 1182, 201511: 1173, 201512: 1019,
    201601: 1021, 201602: 989 , 201603: 1152,
}

#totals = dict([('%i-%02i' % (m/100, m%100), t) for m,t in
#               monthly_totals.items()])
#monthnum2 = dict([(m, int(m[:4]) + (int(m[5:7],10) - 0.5)/12.)
#                  for m in np.unique(totals.keys())])
#totalyrs = np.array([monthnum2[m] for m in totals.keys()])
#totalN = np.array(totals.values())

totalyrs = np.array(monthly_totals.keys())
totalyrs = (totalyrs - 0.5) / 100.
totalN = np.array(monthly_totals.values())

I = np.argsort(totalyrs)

# plt.plot(totalyrs[I], totalN[I], 'r-')
# plt.savefig('monthly2.png')

# fraction per month
count = Counter([int(m.replace('-',''),10) for m in months])
print('Monthly counts:', count)

noptimal = np.zeros_like(totalN)
for i,k in enumerate(monthly_totals.keys()):
    noptimal[i] = count[k]

fraction = noptimal / totalN.astype(float)
# plt.clf()
# plt.plot(totalyrs[I], fraction[I], 'b.')
# plt.xlabel('Month of publication')
# plt.ylabel('Fraction of article with "Optimal"')
# plt.savefig('monthly3.png')


yearly_totals = {}
for k,v in monthly_totals.items():
    yk = k / 100
    yearly_totals[yk] = yearly_totals.get(yk, 0) + v
    
totalyrs = np.array(yearly_totals.keys())
totalN = np.array(yearly_totals.values())
I = np.argsort(totalyrs)
# zero 'optimals' before 1993
I = I[totalyrs[I] > 1993]

yrcount = Counter([int(m[:4],10) for m in months])

noptimal = np.zeros_like(totalN)
for i,k in enumerate(yearly_totals.keys()):
    noptimal[i] = yrcount[k]

# plt.clf()
# plt.plot(totalyrs[I], totalN[I], 'b-')
# plt.plot(totalyrs[I], noptimal[I], 'r-')
# plt.savefig('yearly.png')

plt.clf()
plt.plot(totalyrs[I], 100. * noptimal[I] / totalN[I].astype(float), 'k.')
plt.xlabel('Year of publication')
plt.ylabel("Articles containing ``Optimal'' (\%)")
yt = [0,1,2,3]
plt.yticks(yt, ['   %i' % t for t in yt])

plt.errorbar(totalyrs[I], 100. * noptimal[I] / totalN[I].astype(float), 
            yerr=100. * np.sqrt(noptimal[I]) / totalN[I].astype(float),
             fmt='none', ecolor='k')
plt.axis([1992, 2017, 0, 3])
#plt.title('Use of the word "Optimal" in arXiv Astro-ph abstracts')
plt.savefig('yearly.png')
plt.savefig('yearly.pdf')

print('Total years:', totalyrs[I])



# cached = {
#     "1993-01": 0,
#     "1993-02": 0,
#     "1993-03": 0,
#     "1993-04": 0,
#     "1993-05": 0,
#     "1993-06": 0,
# 
#     "2014-12": 792,
#     "2014-11": 3335,
#     "2014-10": 1354,
#     "2014-09": 758,
#     "2014-08": 532,
#     "2014-07": 638,
#     "2014-06": 627,
#     "2014-05": 632,
#     "2014-04": 487,
#     "2014-03": 732,
#     "2014-02": 464,
#     "2014-01": 498,
#     "2013-12": 503,
#     "2013-11": 455,
#     "2013-10": 648,
#     "2013-09": 513,
#     "2013-08": 569,
#     "2013-07": 662,
#     "2013-06": 492,
#     "2013-05": 916,
#     }
# 
# # http://export.arxiv.org/oai2?verb=ListIdentifiers&metadataPrefix=arXiv&from=2016-01-01&until=2016-01-31&set=physics:astro-ph
# allmonths = range(1993*12, 2015*12)
# allmonths = list(reversed(allmonths))
# #for ym0,ym1 in zip(allmonths, allmonths[1:]):
# imonth = 0
# while imonth < len(allmonths)-1:
#     ym0 = allmonths[imonth]
#     ym1 = ym0 + 1
#     #ym1 = allmonths[imonth+1]
#     y0 = ym0 / 12
#     m0 = ym0 % 12 + 1
#     y1 = ym1 / 12
#     m1 = ym1 % 12 + 1
# 
#     ymstring = '%i-%02i' % (y0, m0)
#     if ymstring in cached:
#         print('Cached:', ymstring, cached[ymstring])
#         imonth += 1
#         continue
#     
#     url = ('http://export.arxiv.org/oai2?verb=ListIdentifiers&metadataPrefix=arXiv&from=%i-%02i-01&until=%i-%02i-01&set=physics:astro-ph' %
#            (y0,m0,y1,m1))
#     print(url)
#     
#     r = requests.get(url)
#     print(r.status_code)
#     if r.status_code == 503:
#         print(r.headers)
#         sleep = int(r.headers.get('retry-after', '5'))
#         print('Sleeping for', sleep)
#         time.sleep(sleep)
#         continue
#         
#     xml = r.text
#     dom1 = minidom.parseString(xml)
#     #<header>
#     headers = dom1.getElementsByTagName('header')
#     print('"%i-%02i": %i,' % (y0, m0, len(headers)))
#     time.sleep(3)
#     imonth += 1