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

CONCEPT_ID_COL_NAME = 'concept_id'
en_label_list = ['Profit (loss)', 'Profit']
concept_id_list = ['ifrs-full_ProfitLoss', 'ifrs_ProfitLoss']


def export_result(_results, no_profit_row_corp_list, no_concept_id_corp_list):
    filtered_results = []

    for res in _results:
        if check_condition(res):
            filtered_results.append(res)

    with open(f'result_{args.m}.txt', 'w') as f:
        headers = [fmt('NAME', 25, 'c'), fmt('CODE', 17, 'c')] + [fmt(COL_NAME_DICT[aa], 17, 'c') for aa in
                                                                  REPORT_COL_LIST]
        f.write('|'.join(headers) + '\n')
        print('|'.join(headers))
        for rec in filtered_results:
            rec2 = [fmt(rec[0], 25, 'l'), fmt(rec[1], 17, 'c')] + [fmt(vis_profit(a), 17, 'r') for a in rec[2:]]
            f.write('|'.join(rec2) + '\n')
            print('|'.join(rec2))

        for tmp in no_profit_row_corp_list:
            f.write(', '.join(tmp) + '\n')

        for tmp in no_concept_id_corp_list:
            f.write(', '.join(tmp) + '\n')


def check_condition(res_row):
    # res_row = [code, name, v1, v2,... ,vn ]
    vals = res_row[2:]
    cod = sum(n < 0 for n in vals)  # count negatives
    if cod:  # includes negatives
        return False
    else:  # all numbers are positive
        return True


def eval():
    fs_data_path = './fsdata'
    # fs_data_path = './tmp'
    no_concept_id_corp_list = []
    no_profit_row_corp_list = []

    corp_dict = read_csv_dict(args.m)
    xlsx_list = os.listdir(fs_data_path)
    results = []

    name_desc = tqdm(range(len(xlsx_list)))
    for ff in xlsx_list:
        name_desc.update(1)
        corp_code = ff.split('_')[0]
        if corp_code not in corp_dict.keys():  # specific market only
            continue

        corp_name = corp_dict[corp_code]
        fpath = f'{fs_data_path}/{ff}'
        xlsx = pd.read_excel(fpath, engine='openpyxl', sheet_name=None)
        cis_sheet = xlsx[DATA_CIS_SHEET]
        cis_sheet_cols = list(cis_sheet.keys())  # col names
        second_cols = [cis_sheet[key][0] for key in cis_sheet_cols]

        if CONCEPT_ID_COL_NAME in second_cols:
            en_col_idx = second_cols.index(CONCEPT_ID_COL_NAME)  # target_column_index
            en_col_vals = cis_sheet[cis_sheet_cols[en_col_idx]]  # target_column_values

            profit_row_idx = -1
            for en_col_val in en_col_vals:
                if type(en_col_val) == float:  # Some values are zero.
                    continue

                if en_col_val in concept_id_list:
                    profit_row_idx = list(en_col_vals).index(en_col_val)

            if profit_row_idx > 0:  # concept_id 'profit-loss' exists
                cis_profit_values = [corp_name, corp_code]
                for col_name in REPORT_COL_LIST:  # [ 2020Q3, 2020Q2,....]
                    if col_name in cis_sheet_cols:  # if col_name is in the sheet
                        if col_name in ANNUAL_REPORT_LIST:  # Q4 case
                            c9, c12 = get_cal(col_name)
                            cis_c12_vals = cis_sheet[c12]  # yearly-amount
                            cis_c9_vals = cis_sheet[c9]  # 3/4 amount
                            # print('c9', c9, 'c12', c12)
                            profit = cis_c12_vals[profit_row_idx] - cis_c9_vals[profit_row_idx]
                            # cis_profit_values.append(vis_profit(profit))
                            cis_profit_values.append(profit)

                        else:  # Q1, Q2, Q3 case
                            cis_vals = cis_sheet[col_name]
                            profit = cis_vals[profit_row_idx]
                            if math.isnan(profit):  # col exists but value is empty
                                cis_profit_values.append(0)
                            else:
                                cis_profit_values.append(profit)
                                # cis_profit_values.append(vis_profit(profit))

                    else:  # no column in the sheet
                        cis_profit_values.append(0)

                results.append(cis_profit_values)
            else:  # No 'profit-loss' label
                no_profit_row_corp_list.append([corp_name, corp_code, 'No profit-loss label'])
        else:
            no_concept_id_corp_list.append([corp_name, corp_code, 'No concept-id column'])

    name_desc.close()


    export_result(results, no_profit_row_corp_list, no_concept_id_corp_list)







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

    def download_corp(self, corp_code, corp_name, save_path='./tmp', begin_date_str='20200101', report_type='quarter'):
        try:
            reports = dart.fs.extract(corp_code=corp_code,
                                      bgn_de=begin_date_str
                                      , report_tp=report_type)

            print('corp code: ', corp_code, ' name:', corp_name)
            reports.save(f'{corp_code}_{report_type}.xlsx', save_path)
            # reports.save()

        except (dart.errors.NotFoundConsolidated,
                dart.errors.UnknownError,
                dart.errors.NoDataReceived) as e:
            print(f'{corp_code},{corp_name},{e}')
            self.log_noreport.info(f'{corp_code},{corp_name},{e}')

        except (dart.errors.InvalidField,
                AttributeError,
                KeyError,
                IndexError,
                ValueError,
                RuntimeError) as e:
            print(f'{corp_code},{corp_name},{e}')
            self.log_notfound.info(f'{corp_code},{corp_name},{e}')

    def download(self, market, begin_date_str):
        market_corp_dict = read_csv_dict(market)
        ignore_list = get_ignore_list()

        for market_corp_code in market_corp_dict:
            market_corp_name = market_corp_dict[market_corp_code]

            if market_corp_code in ignore_list:
                print(market_corp_code, 'existed, pass')
                continue
            self.download_corp(market_corp_code, market_corp_name,
                                        begin_date_str=begin_date_str,
                                        report_type='quarter',
                                        save_path='./fsdata')


if args.d:
    dw = fsDownloader()
    dw.download(market=args.m, begin_date_str='20200101')

if args.e:
    eval()

if args.t:
    print_files_status()

if args.dt:
    dw = fsDownloader()
    corp_dict = read_csv_dict(args.m)
    if args.c in corp_dict.keys():
        dw.download_corp(corp_code=args.c, corp_name= corp_dict[args.c])

