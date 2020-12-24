import pandas as pd

xlsx = pd.read_excel('./fsdata/003280_quarter.xlsx'
                     , engine='openpyxl') # sheetname='시트명' 또는 숫자(1~), header=숫자, skiprow=숫자 실습

# 상위 데이터 확인
print(xlsx.head())
print()

# 데이터 확인
print(xlsx.tail())
print()

# 데이터 구조
print(xlsx.shape) # 행, 열