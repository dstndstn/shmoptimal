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

def retrieve_page(query, max_results, offset):
    '''
    Retrieves one page of the given query to the ArXiv API, with N per page
    of *max_results*, starting from offset *offset*.  Returns the XML text.
    '''
    url = 'http://export.arxiv.org/api/query?'
    params = dict(search_query=query,
                  max_results=max_results,
                  start=offset)
    #r = requests.get(url, params=params)
    url = url + '&'.join('%s=%s' % (k,v) for k,v in params.items())
    print('Requesting', url)
    r = requests.get(url)
    #print('Requesting', r.url)
    if r.status_code != 200:
        raise RuntimeError('Arxiv API returned status code %i: %s' % (r.status_code, r.text))
    return r.text

def find_published_dates(xml):
    '''
    Parses the given XML string, searching for the tags giving the total
    number of search results, and the publication dates.

    Returns: (int *ntotal*, list of strings *dates*)
    
    '''
    # Parse query results   
    dom1 = minidom.parseString(xml)
    # How many total search results were found?
    #<opensearch:totalResults xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">3159</opensearch:totalResults>
    ntotals = dom1.getElementsByTagName('opensearch:totalResults')
    assert(len(ntotals) == 1)
    ntotal = int(ntotals[0].firstChild.nodeValue)
    print('Total of', ntotal, 'results')

    # <published>2004-10-15T17:41:45Z</published>
    pubs = dom1.getElementsByTagName('published')
    print(len(pubs), 'published dates')
    dates = [p.firstChild.nodeValue for p in pubs]
    return ntotal,dates

def count_word_use(word, cat='astro-ph*', where='abs', cachefn=None,
                   max_results = 5000):
    '''
    Counts how often the given *word* is used in arxiv papers.

    *cat*: which arxiv category to search.
    *where*: "abs" for the abstract
           "ti" for the title
    *cachefn*: filename to cache results in
    *max_results*: number of results per page

    Returns:
    (list of strings *months* like "2016-03", list of integer years)
    '''

    words = word.split()
    query = '+AND+'.join(['%s:%s' % (where,word) for word in words]) + '+AND+cat:%s' % (cat)

    #query='%s:%s+AND+cat:%s' % (where, word, cat)
    if cachefn is None or not os.path.exists(cachefn):
        txt = retrieve_page(query, max_results, 0)
        if cachefn is not None:
            f = open(cachefn,'wb')
            txt = txt.encode('ascii', 'ignore')
            f.write(txt)
            f.close()
    else:
        print('Reading cached', cachefn)
        txt = open(cachefn).read()

    ntotal,dates = find_published_dates(txt)
    
    # If total > max_results, retrieve additional pages...
    for page in range(ntotal / max_results):
        txt = None
        if cachefn is not None:
            cfn = cachefn + '-page%i' % (page+1)
            if os.path.exists(cfn):
                print('Reading cached', cfn)
                txt = open(cfn).read()
        if txt is None:
            txt = retrieve_page(query, max_results, (page+1)*max_results)
            if cachefn is not None:
                f = open(cfn, 'w')
                txt = txt.encode('ascii', 'ignore')
                f.write(txt)
                f.close()
        nt,moredates = find_published_dates(txt)
        dates.extend(moredates)
                
    months = []
    years = []
    for d in dates:
        # '2016-04'
        months.append(d[:7])
        # 2016
        years.append(int(d[:4]))
    return months,years

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Use ArXiv API to count articles containing terms')
    parser.add_argument('word', nargs=1, help='Word to search for')
    parser.add_argument('--plot', default='yearly.png',
                        help='Output filename for plot')
    parser.add_argument(
        '--cache', default=None,
        help='Cache filename prefix, default WORD-cache.txt; "no" for no cache')
    parser.add_argument('--perpage', default=1000,
                        help='Number of results per page, default 1000')
    parser.add_argument('--title', action='store_true', default=False,
                        help='Search in title, not in abstract')
    parser.add_argument('--number', action='store_true', default=False,
                        help='Plot raw number, not fraction')
    opt = parser.parse_args()
    word = opt.word[0]

    if opt.cache is None:
        cachefn = '%s-cache.txt' % word
    elif opt.cache == 'no':
        cachefn = None
    else:
        cachefn = opt.cache

    where = 'abs'
    wherestring = 'abstract'
    if opt.title:
        where = 'ti'
        wherestring = 'title'
        
    wordmonths,wordyears = count_word_use(word, cachefn=cachefn, where=where,
                                          max_results=opt.perpage)
    plotfn = opt.plot

    plt.figure(figsize=(6,4))
    plt.subplots_adjust(left=0.1, bottom=0.11, right=0.98, top=0.92)

    if opt.number:
        plt.clf()
        yrcount = Counter(wordyears).most_common()
        print('year count', yrcount)
        years = [y for y,n in yrcount]
        num = np.array([n for y,n in yrcount])
        plt.plot(years, num, 'k.')
        plt.xlabel('Year of publication')
        plt.ylabel('Number of articles')
        plt.errorbar(years, num,
                     yerr = np.sqrt(num),
                     fmt='none', ecolor='k')
        plt.xlim(1992, 2017)
        plt.title("Arxiv astro-ph %ss containing the term ``%s''" % (wherestring, word))
        plt.savefig(plotfn)
        return

    
    # http://arxiv.org/year/astro-ph/92 ... etc
    # cat monthly | tr '|' ' ' | tr '!' ' ' | awk '{print $1, $2}'
    astroph_monthly_totals = {
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

    yearly_totals = {}
    for k,v in astroph_monthly_totals.items():
        yk = k / 100
        yearly_totals[yk] = yearly_totals.get(yk, 0) + v
    

    totalyrs = np.array(yearly_totals.keys())
    totalN = np.array(yearly_totals.values())
    I = np.argsort(totalyrs)
    print('Total of', np.sum(totalN), 'articles')

    yrcount = Counter(wordyears)

    nword = np.zeros_like(totalN)
    for i,k in enumerate(yearly_totals.keys()):
        nword[i] = yrcount[k]

    # plt.clf()
    # plt.plot(totalyrs[I], totalN[I], 'b-')
    # plt.plot(totalyrs[I], noptimal[I], 'r-')
    # plt.savefig('yearly.png')

    plt.clf()
    plt.plot(totalyrs[I], 100. * nword[I] / totalN[I].astype(float), 'k.')
    plt.xlabel('Year of publication')
    plt.ylabel("Articles containing ``%s'' (\%%)" % word)
    #yt = [0,1,2,3]
    #plt.yticks(yt, ['   %i' % t for t in yt])

    plt.errorbar(totalyrs[I], 100. * nword[I] / totalN[I].astype(float), 
                 yerr=100. * np.sqrt(nword[I]) / totalN[I].astype(float),
                 fmt='none', ecolor='k')
    plt.xlim(1992, 2017)
    plt.title("Arxiv astro-ph %ss containing the term ``%s''" % (wherestring, word))
    plt.savefig(plotfn)

# I also tried the Open Archives version...
# url = ('http://export.arxiv.org/oai2?verb=ListIdentifiers&metadataPrefix=arXiv&from=%i-%02i-01&until=%i-%02i-01&set=physics:astro-ph' %
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


if __name__ == '__main__':
    import sys
    sys.exit(main())

