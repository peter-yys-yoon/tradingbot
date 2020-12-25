import pandas as pd
import pdb
from math import isnan
# xlsx = pd.read_excel('./fsdata/003280_quarter.xlsx'
xlsx = pd.read_excel('./fsdata/000990_quarter.xlsx'
                     , engine='openpyxl', sheet_name=None)  # sheetname='시트명' 또는 숫자(1~), header=숫자, skiprow=숫자 실습

# 상위 데이터 확인
# print(xlsx.head())
# print()

# 데이터 확인
# print(xlsx.tail())
# print()

# 데이터 구조
# print(xlsx.shape) # 행, 열

COL_2020Q3 = '20200701-20200930'
COL_2020Q2 = '20200401-20200630'
COL_2020Q1 = '20200101-20200331'
COL_2020C3 = '20200101-20200930' # = Q1 + Q2 + Q3
DATA_CIS_SHEET = 'Data_cis'
CONCEPT_PROFIT_LOSS = 'ifrs-full_ProfitLoss'
LABEL_EN_PROFIT_LOSS ='Profit (loss)'


# print('xlsx sheets:' )
# print(xlsx.keys())
cis_sheet = xlsx[DATA_CIS_SHEET]
cis_sheet_cols = cis_sheet.keys() # col names
# print('cis_sheet_cols: ', cis_sheet_cols)


concept_id_list = cis_sheet[cis_sheet_cols[1]]
label_en_list = cis_sheet[cis_sheet_cols[3]]

# print(concept_id_list)
# print(label_en_list)

for idx, label in enumerate(label_en_list):
    print(type(label), label)



    # if LABEL_EN_PROFIT_LOSS in label:
    #     print('idx: ',idx)



# print(cis_sheet_cols[0])
# print(cis_sheet_cols[1])
# print(cis_sheet_cols[2])


# cis_Q1 = cis_sheet[COL_2020Q1]

# print()
# print()
# print()
# print()
# print(cis_Q1)


