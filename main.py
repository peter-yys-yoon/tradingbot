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
from tools import *


def export_result(results):
    with open(f'result_{args.m}.txt', 'w') as f:
        headers = [fmt('NAME', 25, 'c'), fmt('CODE', 17, 'c')] + [fmt(COL_NAME_DICT[aa], 17, 'c') for aa in
                                                                  REPORT_COL_LIST]
        f.write('|'.join(headers) + '\n')
        print('|'.join(headers))
        for rec in results:
            rec2 = [fmt(rec[0], 25, 'l'), fmt(rec[1], 17, 'c')] + [fmt(vis_profit(a), 17, 'r') for a in rec[2:]]
            f.write('|'.join(rec2) + '\n')
            print('|'.join(rec2))


def check_condition(res_row):
    # res_row = [code, name, v1, v2,... ,vn ]
    vals = res_row[2:]
    cod = sum(n < 0 for n in vals)  # count negatives
    if cod:  # includes negatives
        return False
    else:  # all numbers are positive
        return True


def eval():
    # fs_data_path = './fsdata'
    fs_data_path = './tmp'

    corp_dict = read_csv_dict(args.m)
    xlsx_list = os.listdir(fs_data_path)
    results = []

    name_desc = tqdm(range(len(xlsx_list)))
    for ff in xlsx_list:
        name_desc.update(1)

        fpath = f'{fs_data_path}/{ff}'
        xlsx = pd.read_excel(fpath, engine='openpyxl', sheet_name=None)
        cis_sheet = xlsx[DATA_CIS_SHEET]
        cis_sheet_cols = list(cis_sheet.keys())  # col names

        corp_code = ff.split('_')[0]

        if corp_code not in corp_dict.keys(): # specific market only
            continue
        corp_name = corp_dict[corp_code]

        profit_idx = -1
        label_en_list = cis_sheet[cis_sheet_cols[3]]
        for idx, label in enumerate(label_en_list):
            if type(label) == str:
                if LABEL_EN_PROFIT_LOSS == label:
                    profit_idx = idx
                    # print(type(label), idx, label)

        if profit_idx < 0:  # No Profit row in table
            continue
        # print(corp_code, corp_name)
        cis_profit_values = [corp_name, corp_code]
        for col_name in REPORT_COL_LIST:  # [ 2020Q3, 2020Q2,....]
            if col_name in cis_sheet_cols:  # if col_name is in the sheet
                if col_name in ANNUAL_REPORT_LIST:  # Q4 case
                    c9, c12 = get_cal(col_name)
                    cis_c12_vals = cis_sheet[c12]  # yearly-amount
                    cis_c9_vals = cis_sheet[c9]  # 3/4 amount
                    # print('c9', c9, 'c12', c12)
                    profit = cis_c12_vals[profit_idx] - cis_c9_vals[profit_idx]
                    # cis_profit_values.append(vis_profit(profit))
                    cis_profit_values.append(profit)

                else:  # Q1, Q2, Q3 case
                    cis_vals = cis_sheet[col_name]
                    profit = cis_vals[profit_idx]
                    if math.isnan(profit):  # col exists but value is empty
                        cis_profit_values.append(0)
                    else:
                        cis_profit_values.append(profit)
                        # cis_profit_values.append(vis_profit(profit))

            else:  # no column in the sheet
                cis_profit_values.append(0)

        # if check_condition(cis_profit_values):
        if True:
            results.append(cis_profit_values)
    name_desc.close()
    export_result(results)


class fsDownloader:
    def __init__(self):
        api_key = 'd617ec8690f8cafd5d081e00a1501565e137f23e'
        dart.set_api_key(api_key=api_key)

        self.log_notfound = self.setup_logger('log1', './logs/notfound.log', empty_formatter)
        self.log_noreport = self.setup_logger('log4', './logs/noreport.log', empty_formatter)
        # self.log_success = self.setup_logger('log4','success.log')

    def setup_logger(self, name, log_file, formatt, level=logging.INFO):
        """To setup as many loggers as you want"""

        handler = logging.FileHandler(log_file)
        handler.setFormatter(formatt)

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)

        return logger

    def download(self, market, begin_date_str):
        market_corp_dict = read_csv_dict(market)
        ignore_list = get_ignore_list()

        for market_corp_code in market_corp_dict:
            market_corp_name = market_corp_dict[market_corp_code]

            if market_corp_code in ignore_list:
                print(market_corp_code, 'existed, pass')
                continue

            try:
                reports = dart.fs.extract(corp_code=market_corp_code,
                                          bgn_de=begin_date_str
                                          , report_tp='quarter')

                print('corp code: ', market_corp_code, ' name:', market_corp_name)
                reports.save()

            except (dart.errors.NotFoundConsolidated,
                    dart.errors.UnknownError,
                    dart.errors.NoDataReceived) as e:
                print(f'{market_corp_code},{market_corp_name},{e}')
                self.log_noreport.info(f'{market_corp_code},{market_corp_name},{e}')

            except (dart.errors.InvalidField,
                    AttributeError,
                    KeyError,
                    ValueError,
                    RuntimeError) as e:
                print(f'{market_corp_code},{market_corp_name},{e}')
                self.log_notfound.info(f'{market_corp_code},{market_corp_name},{e}')


if args.d:
    dw = fsDownloader()
    dw.download(market=args.m, begin_date_str='20200101')

if args.e:
    eval()

if args.t:
    print_files_status()
