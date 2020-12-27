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


def eval():
    fs_data_path = './fsdata'

    corp_dict = read_csv_dict(KOSPI)
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

        cis_profit_values = [corp_name, corp_code]
        for col_name in REPORT_COL_LIST:  # [ 2020Q3, 2020Q2,....]
            if col_name in cis_sheet_cols:  # if col_name is in the sheet
                if col_name in ANNUAL_REPORT_LIST:  # Q4 case
                    c9, c12 = get_cal(col_name)
                    cis_c12_vals = cis_sheet[c12]  # yearly-amount
                    cis_c9_vals = cis_sheet[c9]  # 3/4 amount
                    profit = cis_c12_vals[profit_idx] - cis_c9_vals[profit_idx]

                else:  # Q1, Q2, Q3 case
                    cis_vals = cis_sheet[col_name]
                    profit = cis_vals[profit_idx]

                cis_profit_values.append(vis_profit(profit))

            else:  # no data in sheet
                cis_profit_values.append('  ')

        results.append(cis_profit_values)
    name_desc.close()

    headers = [fmt('Name', 17, 'c'), fmt('Code', 17, 'c')] + [fmt(COL_NAME_DICT[aa], 17, 'c') for aa in REPORT_COL_LIST]
    print('|'.join(headers))
    for rec in results:
        rec2 = [fmt(rec[0], 17, 'l'), fmt(rec[1], 17, 'c')] + [fmt(a, 17, 'r') for a in rec[2:]]
        print('|'.join(rec2))


class fsDownloader:
    def __init__(self):
        api_key = 'd617ec8690f8cafd5d081e00a1501565e137f23e'
        dart.set_api_key(api_key=api_key)

        self.log_notfound = self.setup_logger('./logs/log1', 'notfound.log', empty_formatter)
        self.log_notmatch = self.setup_logger('./logs/log2', 'notmatch.log', empty_formatter)
        self.log_noprofit = self.setup_logger('./logs/log3', 'noprofit.log', empty_formatter)
        # self.log_success = self.setup_logger('log4','success.log')

    def get_ignore_list(self):

        ignore_list = []
        with open('./logs/notfound.log', 'r') as f:
            aa = f.readlines()
            ignore_list += [x.rstrip().split(',')[0] for x in aa]

        with open('./logs/notmatch.log', 'r') as f:
            aa = f.readlines()
            ignore_list += [x.rstrip().split(',')[0] for x in aa]

        with open('./logs/noprofit.log', 'r') as f:
            aa = f.readlines()
            ignore_list += [x.rstrip().split(',')[0] for x in aa]

        with open('./logs/ignore_list.txt', 'r') as f:
            aa = f.readlines()
            ignore_list += [x.rstrip().split(',')[0] for x in aa]

        for f in os.listdir('./fsdata'):
            ignore_list.append(f.split('_')[0])

        return ignore_list

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
        print(f'{market} has {len(list(market_corp_dict.keys()))} Corps ')
        ignore_list = self.get_ignore_list()

        for market_corp_code in market_corp_dict:
            market_corp_name = market_corp_dict[market_corp_code]

            if market_corp_code in ignore_list:
                print(market_corp_code, 'existed, pass')
                continue

            try:
                reports = dart.fs.extract(corp_code=market_corp_code,
                                          bgn_de=begin_date_str
                                          , report_tp='quarter'
                                          # ,report_tp='half'
                                          )

                print('corp code: ', market_corp_code, ' name:', market_corp_name)
                cis_report = reports['cis']
                report_cis_col_label = cis_report.to_dict().keys()
                report_cis_col_label = list(report_cis_col_label)

                first_labels = cis_report[report_cis_col_label[0]]  # concept_id
                eng_labels = cis_report[report_cis_col_label[2]]  # eng_label

                # if 'Profit (loss)' not in eng_labels:
                #     print('No Profit!!')

                no_label_flag = True
                target_idx = -1
                for idx, lab in enumerate(eng_labels):
                    if lab == 'Profit (loss)':
                        no_label_flag = False
                        target_idx = idx
                        # print(idx, first_labels[idx], eng_labels[idx])

                if no_label_flag:
                    print('No Profit!!')
                    self.log_noprofit.info(f'{market_corp_code},{market_corp_name}')
                else:
                    concept_id = first_labels[target_idx]
                    if concept_id != 'ifrs-full_ProfitLoss':
                        self.log_notmatch.info(f'{market_corp_code},{market_corp_name},{concept_id},{eng_labels}')

                reports.save()
            except (dart.errors.NoDataReceived,
                    dart.errors.NotFoundConsolidated,
                    dart.errors.InvalidField,
                    dart.errors.UnknownError,
                    RuntimeError) as e:

                self.log_notfound.info(f'{market_corp_code},{market_corp_name},{e}')


if args.d:
    dw = fsDownloader()
    dw.download(market=KOSPI, begin_date_str='20200101')

if args.e:
    eval()
