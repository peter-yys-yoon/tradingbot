import csv
import pdb
import dart_fss as dart
import logging
import time
import os
import pandas as pd
import argparse

CORP_NAME = 2
CORP_CODE = 'corp_code'
CORP_PROFIT_VAL_LIST = 'corp_profit_vals'
CORP_PROFIT_CHANGE_LIST = 'corp_profit_changes'
CORP_PROFIT_CULM_LIST = 'corp_culm_changes'
CORP_PROFIT_FLAG_LIST = 'corp_profit_flags'
KOSPI = 'kospi'
KOSDAQ = 'kosdaq'
KONEX = 'konex'

COL_2020Q3 = '20200701-20200930'
COL_2020Q2 = '20200401-20200630'
COL_2020Q1 = '20200101-20200331'
COL_2020C3 = '20200101-20200930'  # = Q1 + Q2 + Q3
DATA_CIS_SHEET = 'Data_cis'
CONCEPT_PROFIT_LOSS = 'ifrs-full_ProfitLoss'
LABEL_EN_PROFIT_LOSS = 'Profit (loss)'

default_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
empty_formatter = logging.Formatter('')
MARKET_TP = {
    KOSPI: 'Y',
    KOSDAQ: 'K',
    KONEX: 'N'
}

PROFITLOSS1 = 'ifrs-full_ProfitLoss'
PROFITLOSS2 = 'ifrs_ProfitLoss'

parser = argparse.ArgumentParser(description='wowwowwowwow')

parser.add_argument('-d', action='store_true')
parser.add_argument('-e', action='store_true')
parser.add_argument('-m', type=str ,action='store')

args = parser.parse_args()


def read_csv_dict(datatype=KOSPI):
    """
    ['\ufeff', '종목코드', '기업명', '업종코드', '업종', '상장주식수(주)', '자본금(원)',
    '액면가(원)', '통화구분', '대표전화', '주소', '소속기업부', '지정자문인']

    :param datatype:
    :return:
    """
    corp_dict = {}
    # corp_code_list, corp_name_list = [], []
    if datatype == KOSPI:
        csv_file = './datas/kospi_list.csv'
    elif datatype == KOSDAQ:
        csv_file = './datas/kosdaq_list.csv'
    elif datatype== KONEX:
        csv_file = './datas/konex_list.csv'
    else:
        quit('no market')

    with open(csv_file, 'r', encoding='UTF-8') as f:
        # with open(csv_file, 'r') as f:
        rdr = csv.reader(f)
        for line in rdr:
            if line[2] == '기업명':
                continue
            corp_dict[line[1]] = line[2]

    return corp_dict


def run():
    fs_data_path = './fsdata'

    corp_dict = read_csv_dict(KOSPI)

    for ff in os.listdir(fs_data_path):

        fpath = f'{fs_data_path}/{ff}'
        xlsx = pd.read_excel(fpath, engine='openpyxl', sheet_name=None)
        cis_sheet = xlsx[DATA_CIS_SHEET]
        cis_sheet_cols = cis_sheet.keys()  # col names
        # print(cis_sheet_cols)
        concept_id_list = cis_sheet[cis_sheet_cols[1]]
        label_en_list = cis_sheet[cis_sheet_cols[3]]

        Q1_VALS = cis_sheet[COL_2020Q1]
        Q2_VALS = cis_sheet[COL_2020Q2]
        Q3_VALS = cis_sheet[COL_2020Q3]

        profit_idx = -1
        for idx, label in enumerate(label_en_list):
            if type(label) == str:
                if LABEL_EN_PROFIT_LOSS == label:
                    profit_idx = idx
                    # print(type(label), idx, label)

        if profit_idx > 0:
            corp_code = ff.split('_')[0]
            print(corp_dict[corp_code], Q1_VALS[profit_idx], Q2_VALS[profit_idx], Q3_VALS[profit_idx])


class Trimmer:
    def __init__(self):
        api_key = 'd617ec8690f8cafd5d081e00a1501565e137f23e'
        dart.set_api_key(api_key=api_key)

        self.log_notfound = self.setup_logger('log1', 'notfound.log', empty_formatter)
        self.log_notmatch = self.setup_logger('log2', 'notmatch.log', empty_formatter)
        self.log_noprofit = self.setup_logger('log3', 'noprofit.log', empty_formatter)
        # self.log_success = self.setup_logger('log4','success.log')

    def get_ignore_list(self):

        ignore_list = []
        with open('notfound.log', 'r') as f:
            aa = f.readlines()
            ignore_list += [x.rstrip().split(',')[0] for x in aa]

        with open('notmatch.log', 'r') as f:
            aa = f.readlines()
            ignore_list += [x.rstrip().split(',')[0] for x in aa]

        with open('noprofit.log', 'r') as f:
            aa = f.readlines()
            ignore_list += [x.rstrip().split(',')[0] for x in aa]

        with open('custom_ignore.txt', 'r') as f:
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

    def jm_want(self, market, begin_date_str):
        market_corp_dict = read_csv_dict(market)
        print(f'{market} has {len(list(market_corp_dict.keys()))} Corps ')
        ignore_list = self.get_ignore_list()
        # dart_corp_list = dart.get_corp_list()

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

                first_labels = cis_report[report_cis_col_label[0]]  # eng_label
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
            except dart.errors.NoDataReceived as e:
                self.log_notfound.info(f'{market_corp_code},{market_corp_name},NoDataReceived')
            except dart.errors.NotFoundConsolidated as e:
                self.log_notfound.info(f'{market_corp_code},{market_corp_name},NotFoundConsolidated')
            except dart.errors.InvalidField as e:
                self.log_notfound.info(f'{market_corp_code},{market_corp_name},InvalidField')
            except dart.errors.UnknownError as e:
                self.log_notfound.info(f'{market_corp_code},{market_corp_name},UnknownError')
            except IndexError as e:
                self.log_notfound.info(f'{market_corp_code},{market_corp_name},IndexError')
            except AttributeError as e:
                self.log_notfound.info(f'{market_corp_code},{market_corp_name},AttributeError')
            except ValueError as e:
                self.log_notfound.info(f'{market_corp_code},{market_corp_name},ValueError')
            except RuntimeError as e:
                print('Runtime Errorrrrrrrrrrrrrrrrrrrrrrrrrrrr')
                self.log_notfound.info(f'{market_corp_code},{market_corp_name}')



def ignore_test():
    trim = Trimmer()
    ignore_list = trim.get_ignore_list()
    print(ignore_list)

#ignore_test()


if args.d:
    trim = Trimmer()
    trim.jm_want(market=args.m, begin_date_str='20200101')
    #trim.jm_want(market=KOSPI, begin_date_str='20200101')

if args.e:
    run()
