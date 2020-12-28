import csv
import pdb
import dart_fss as dart
import logging
import time
import os
import pandas as pd
import argparse
from tqdm import tqdm
import math
import calendar
from wcwidth import wcswidth




CORP_NAME = 2
CORP_CODE = 'corp_code'
CORP_PROFIT_VAL_LIST = 'corp_profit_vals'
CORP_PROFIT_CHANGE_LIST = 'corp_profit_changes'
CORP_PROFIT_CULM_LIST = 'corp_culm_changes'
CORP_PROFIT_FLAG_LIST = 'corp_profit_flags'
KOSPI = 'kospi'
KOSDAQ = 'kosdaq'
KONEX = 'konex'

COL_2020Q4 = '20200101-20201231'
COL_2020Q3 = '20200701-20200930'
COL_2020Q2 = '20200401-20200630'
COL_2020Q1 = '20200101-20200331'
COL_2019Q4 = '20190101-20191231'

COL_NAME_DICT = {
    COL_2019Q4: '2019 Q4',
    COL_2020Q1: '2020 Q1',
    COL_2020Q2: '2020 Q2',
    COL_2020Q3: '2020 Q3',
    COL_2020Q4: '2020 Q4'
}

# Anual:	    yearly amount
# Half:	    2Q, half-year amount
# Quarter:	3Q, 2Q,       1~9	1~6	1Q
# Quarter:   3Q, 2Q	1~12  1~9	1~6	1Q

# REPORT_COL_LIST = [COL_2020Q3, COL_2020Q2, COL_2020Q1, COL_2019Q4]
REPORT_COL_LIST = [COL_2020Q3, COL_2020Q2, COL_2020Q1]
ANNUAL_REPORT_LIST = [COL_2020Q4, COL_2019Q4]  # includes only Q4-cols.

DATA_CIS_SHEET = 'Data_cis'
CONCEPT_PROFIT_LOSS = 'ifrs-full_ProfitLoss'
LABEL_EN_PROFIT_LOSS = 'Profit (loss)'
PROFITLOSS1 = 'ifrs-full_ProfitLoss'
PROFITLOSS2 = 'ifrs_ProfitLoss'

default_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
empty_formatter = logging.Formatter('')
MARKET_TP = {
    KOSPI: 'Y',
    KOSDAQ: 'K',
    KONEX: 'N'
}

parser = argparse.ArgumentParser(description='wowwowwowwow')
parser.add_argument('-d', action='store_true')
parser.add_argument('-e', action='store_true')
parser.add_argument('-t', action='store_true')
parser.add_argument('-m', type=str, default='kospi', action='store')
args = parser.parse_args()




def print_files_status():
    failed_corp_list = read_all_logs()
    fsdata_list = get_fsdata_list()

    for market_key in MARKET_TP.keys():
        market_corp_dict = read_csv_dict(market_key)
        total_count = len(market_corp_dict)
        dw_count, fail_count, rest  = 0,0, 0

        for t in market_corp_dict.keys():
            if t in fsdata_list:
                dw_count +=1
            elif t in failed_corp_list:
                fail_count +=1
            else:
                rest += 1
        print(market_key, 'total:', total_count, 'fsdata:',dw_count, 'failed:',fail_count,'rest:',rest)





def read_all_logs():
    flist = []
    with open('./logs/notfound.log', 'r') as f:
        aa = f.readlines()
        flist += [x.rstrip().split(',')[0] for x in aa]

    with open('./logs/notmatch.log', 'r') as f:
        aa = f.readlines()
        flist += [x.rstrip().split(',')[0] for x in aa]

    with open('./logs/noprofit.log', 'r') as f:
        aa = f.readlines()
        flist += [x.rstrip().split(',')[0] for x in aa]

    with open('./logs/ignore_list.txt', 'r') as f:
        aa = f.readlines()
        flist += [x.rstrip().split(',')[0] for x in aa]

    return flist

def get_fsdata_list():
    flist = []

    for f in os.listdir('./fsdata'):
        flist.append(f.split('_')[0])
    return flist

def get_ignore_list():
    return get_fsdata_list() + read_all_logs()


def read_csv_dict(datatype=KOSPI):
    """
    List all corps in given market from csv file.

    ['\ufeff', '종목코드', '기업명', '업종코드', '업종', '상장주식수(주)', '자본금(원)',
    '액면가(원)', '통화구분', '대표전화', '주소', '소속기업부', '지정자문인']

    :param datatype:
    :return:
    """
    corp_dict = {}
    if datatype == KOSPI:
        csv_file = './datas/kospi_list.csv'
    elif datatype == KOSDAQ:
        csv_file = './datas/kosdaq_list.csv'
    else:
        csv_file = './datas/konex_list.csv'

    with open(csv_file, 'r', encoding='UTF-8') as f:
        # with open(csv_file, 'r') as f:
        rdr = csv.reader(f)
        for line in rdr:
            if line[2] == '기업명':  # excludes first line in the csv
                continue
            corp_dict[line[1]] = line[2]  # dict['code'] ='name'

    return corp_dict


def vis_profit(_given):
    """
    Visualize profit human-readable

    :param given:
    :return:
    """

    base = 1
    if _given < 0:
        base = -1

    given = _given * base

    danwi1 = math.pow(10, 8)  # 억단위
    danwi2 = math.pow(10, 12)  # 조단위

    a, b = divmod(given, danwi2)
    # print('_given', '    ', given, 'a:', a, 'b: ', b)
    if a:  # a is not zero :
        return f'{int(a) * base:,}조 {int(b / danwi1):,}억원'
    else:
        return f'{int(b * base / danwi1):,}억원'


def fmt(x, w, align='r'):
    """
    formatting and spacing on both english and korean

    :param x: given string
    :param w:  width size
    :param align: c|r|l
    :return:
    """
    x = str(x)
    l = wcswidth(x)
    s = w - l

    if s <= 0:
        return x
    if align == 'l':
        return x + ' ' * s
    if align == 'c':
        sl = s // 2
        sr = s - sl
        return ' ' * sl + x + ' ' * sr

    return ' ' * s + x


def get_cal(given):
    """
    get 8-digit date of C9 and C12
    :param given:
    :return:
    """
    year = int(given[:4])
    last_day_Sep = calendar.monthrange(year, 9)[1]
    c9 = f'{year}0101-{year}09{last_day_Sep}'
    c12 = f'{year}0101-{year}1231'

    return c9, c12
