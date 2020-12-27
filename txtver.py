import csv
import pdb

CORP_NAME = 2
CORP_CODE = 'corp_code'
CORP_PROFIT_VAL_LIST = 'corp_profit_vals'
CORP_PROFIT_CHANGE_LIST = 'corp_profit_changes'
CORP_PROFIT_CULM_LIST = 'corp_culm_changes'
CORP_PROFIT_FLAG_LIST = 'corp_profit_flags'
KOSPI = 'kospi'
KOSDAQ = 'kosdaq'
KONEX = 'konex'


Y2019_Q1 = './datas/cis2019Q1.txt'
Y2019_Q2 = './datas/cis2019Q2.txt'
Y2019_Q3 = './datas/cis2019Q3.txt'
Y2019_Q4 = './datas/cis2019Q4.txt'

Y2020_Q1 = './datas/cis2020Q1.txt'
Y2020_Q2 = './datas/cis2020Q2.txt'
Y2020_Q3 = './datas/cis2020Q3.txt'

REVENUE1 = 'ifrs_Revenue'
REVENUE2 = 'ifrs-full_Revenue'
REVENUE3 = 'ifrs-full_ProfitLoss'

PROFITLOSS1 = 'ifrs-full_ProfitLoss'
PROFITLOSS2 = 'ifrs_ProfitLoss'

# DATA_LIST = [Y2019_Q1, Y2019_Q2, Y2019_Q3, Y2019_Q4, Y2020_Q1, Y2020_Q2, Y2020_Q3]
# DATA_LIST = [Y2019_Q3, Y2019_Q4, Y2020_Q1, Y2020_Q2, Y2020_Q3]
DATA_LIST = [Y2020_Q1, Y2020_Q2, Y2020_Q3]
DATA_LIST_TEST = [Y2019_Q1, Y2019_Q2, Y2019_Q3, Y2019_Q4]


def read_txt(txtfile):
    """
    재무제표종류(0)	종목코드(1)*	 회사명(2)*	시장구분(3) 업종(4)   업종명(5)	결산월(6)
    결산기준일(7)   보고서종류(8)	통화(9)	항목코드(10)	항목명(11)
    당기 1분기 3개월(12)*
    당기 1분기 누적(13)*
    전기 1분기 3개월(14)
    전기 1분기 누적(15)
    전기(16)
    전전기(17)


    :param txtfile:
    :return:
    """
    # a = open(txtfile, 'r') # window
    a = open(txtfile, 'r', encoding='cp949') # linux
    txtlines = a.readlines()
    txtlines = [txt.rstrip().split('\t') for txt in txtlines]

    return txtlines[1:]  # top line is col-name


def read_csv(datatype=KOSPI):
    """
    ['\ufeff', '종목코드', '기업명', '업종코드', '업종', '상장주식수(주)', '자본금(원)',
    '액면가(원)', '통화구분', '대표전화', '주소', '소속기업부', '지정자문인']

    :param datatype:
    :return:
    """
    corp_info_list = []
    # corp_code_list, corp_name_list = [], []
    if datatype == KOSPI:
        csv_file = './datas/kospi_list.csv'
    elif datatype == KOSDAQ:
        csv_file = './datas/kosdaq_list.csv'
    else:
        csv_file = './datas/konex_list.csv'

    with open(csv_file, 'r') as f:
        rdr = csv.reader(f)
        for line in rdr:
            corp_info_list.append([line[1], line[2]])
            # corp_code_list.append(line[1])
            # corp_name_list.append(line[2])

    # return [corp_code_list, corp_name_list]
    return corp_info_list


def str2int(given):
    if len(given):  # not empty
        return int(given.replace(',', ''))
    else:
        return 0


def extract_csv(rawlines):
    """
    code, name, revenue, amount, attribute

    :param rawlines:
    :return:
    """
    newline = []
    for line in rawlines:
        # if '030530' == line[1][1:-1]:
        #     pdb.set_trace()

        # if line[10] == REVENUE1 or line[10] == REVENUE2 or line[10] ==REVENUE3:
        if line[10] == PROFITLOSS1 or line[10] ==PROFITLOSS2:
            code = line[1][1:-1]
            name = line[2]
            attribute = line[11]

            if len(line) > 12:
                revenue = str2int(line[12])
                amount = str2int(line[13])
            else:
                revenue, amount = 0, 0

            newline.append([code, name, revenue, amount, attribute])
    return newline


def extract_cs_dict(rawlines):
    """
    code, name, revenue, amount, attribute

    :param rawlines:
    :return:
    """
    newline = {}
    for line in rawlines:
        # if '030530' == line[1][1:-1]:
        #     pdb.set_trace()

        # if line[10] == REVENUE1 or line[10] == REVENUE2 or line[10] ==REVENUE3:
        if line[10] == PROFITLOSS1 or line[10] ==PROFITLOSS2:
            code = line[1][1:-1]
            name = line[2]
            attribute = line[11]

            if len(line) > 12:
                revenue = str2int(line[12])
                amount = str2int(line[13])
            else:
                revenue, amount = 0, 0

            if code in newline.keys():
                print(newline[code])
                print(line)
            assert code not in newline.keys(), 'something is wrong'
            newline[code] = [code, name, revenue, amount, attribute]

            # newline.append([code, name, revenue, amount, attribute])
    return newline


class Trimmer:
    def __init__(self):
        self.corp_dict = {}

    def init_corp_dict(self):
        datatype = KOSDAQ
        corp_info_list = read_csv(datatype)

        ### create empty dict
        corp_dict = {}
        for corp_info in corp_info_list:
            code, name = corp_info
            corp_dict[code] = {
                CORP_NAME: name,
                CORP_PROFIT_CHANGE_LIST: [],
                CORP_PROFIT_VAL_LIST: [],
                CORP_PROFIT_CULM_LIST: [],
                CORP_PROFIT_FLAG_LIST: []
            }

        ### add
        for didx, report_txt in enumerate(DATA_LIST):
            print(didx, report_txt)
            raw_lines = read_txt(report_txt)
            ex_dict = extract_cs_dict(raw_lines)  # code:[code, name, revenue, amount, attribute]

            for code in list(ex_dict.keys()):
                if code not in corp_dict.keys():
                    continue

                _, name, revenue, amount, attribute = ex_dict[code]

                val_list = corp_dict[code][CORP_PROFIT_VAL_LIST]
                amount_list = corp_dict[code][CORP_PROFIT_CULM_LIST]
                flag_list = corp_dict[code][CORP_PROFIT_FLAG_LIST]

                val_list.append(revenue)
                amount_list.append(amount)
                flag_list.append(didx)

                corp_dict[code][CORP_PROFIT_VAL_LIST] = val_list
                corp_dict[code][CORP_PROFIT_CULM_LIST] = amount_list
                corp_dict[code][CORP_PROFIT_FLAG_LIST] = flag_list

        N = len(DATA_LIST)

        for code in list(corp_dict.keys()):
            flag_list = corp_dict[code][CORP_PROFIT_FLAG_LIST]
            if len(flag_list) != N:
                val_list = corp_dict[code][CORP_PROFIT_VAL_LIST]
                amount_list = corp_dict[code][CORP_PROFIT_CULM_LIST]
                flag_list = corp_dict[code][CORP_PROFIT_FLAG_LIST]
                name = corp_dict[code][CORP_NAME]
                print(len(flag_list) ,N)
                print(code, name)
                print('\t',flag_list)
                print('\t', val_list)

            # quit()

        return corp_dict

    def init_report(self):
        pass

    def get_jm_wants(self, datatype):
        pass

    def update(self, report):
        for line in report:
            corp_code = line[1][1:-1]
            profit_quarter = int(line[12])

            tmp = line[13]
            if len(tmp):  # non
                profit_culm = 0
            else:
                profit_culm = int(tmp)

            if corp_code in self.corp_dict.keys():

                profit_val_list = self.corp_dict[corp_code][CORP_PROFIT_VAL_LIST]
                profit_change_list = self.corp_dict[corp_code][CORP_PROFIT_CHANGE_LIST]

                if len(curr_culm_profit):  # not Q4 report

                    if len(profit_val_list) > 0:
                        change = profit_val_list - profit_val_list[-1]
                        profit_change_list.append(change)

                    profit_val_list.append(profit_val_list)

                else:  # Q4 report
                    pass


def check3():
    # corp_info_list = read_csv(KOSDAQ)
    corp_info_list = read_csv(KOSPI)
    corp_code_list = [xx[0] for xx in corp_info_list]


    txt_info_list = read_txt(Y2020_Q3)
    txt_code_list = [ll[1][1:-1] for ll in txt_info_list]

    c1set = set(corp_code_list)
    intersec = c1set.intersection(txt_code_list)

    corp_code_set = set(corp_code_list)
    txt_code_set = set(txt_code_list)
    print('raw text code: ', len(list(txt_code_set)))
    print('scv test code: ', len(list(c1set)))
    print('intersection: ', len(list(intersec)))


    listed_but_no_txtinfo = corp_code_set - txt_code_set
    for key in list(listed_but_no_txtinfo):

        for corp_info in corp_info_list:
            if key == corp_info[0]:
                print( corp_info)
                break




def check1():
    lines = read_txt(Y2020_Q1)
    lines2 = extract_csv(lines)
    tmp = []
    for ll in lines:
        code = ll[1][1:-1]
        tmp.append(code)

    print('original txt:', len(lines))
    print('extracted: ', len(lines2))
    print('unique code:', len(list(set(tmp))))

    for ucode in list(set(tmp)):
        flag = False
        for ex in lines2:
            c, _, _, _, _ = ex
            if c == ucode:
                flag = True
                break

        if flag == False:
            for ll in lines:
                if ll[1][1:-1] == ucode:
                    print(ll[1:4])
                    break

    # for ll in lines2:
    #     c,_,_,_ = ll
    #     if c not in tmp:
    #         print(c, type(c))


def check2():
    trim = Trimmer()
    trim.init_corp_dict()


# check1()
check2()
# check3()
# lines = read_txt('./2019_2Q_cis.txt')
# lines = read_txt('./2019_1Q_cis.txt')
