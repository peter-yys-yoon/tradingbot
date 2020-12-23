import dart_fss as dart
import time
import pdb

def get_time(given=0):
    current = time.time()
    return current , current-given

# Open DART API KEY 설정
api_key='d617ec8690f8cafd5d081e00a1501565e137f23e'
start_time = time.time()
dart.set_api_key(api_key=api_key)
set_api_ckpt, set_api_took = get_time(start_time)
print(set_api_took) # 1s
# DART 에 공시된 회사 리스트 불러오기
corp_list = dart.get_corp_list()
stock_list = dart.get_crp_list(market='Y') # KOSPI
stock_list = dart.get_crp_list(market='K') # KOSDAQ
stock_list = dart.get_crp_list(market='N') # KOSNEC
get_corp_list_ckpt, get_crop_list_took = get_time(set_api_ckpt)
print(get_crop_list_took) # 9s
# 삼성전자 검색
pdb.set_trace()
samsung = corp_list.find_by_corp_name('삼성전자', exactly=True)[0]
find_crop_name_ckpt, find_crop_name_took = get_time(get_corp_list_ckpt)
print(find_crop_name_took) # 0.02s
# 2012년부터 연간 연결재무제표 불러오기
fs = samsung.extract_fs(bgn_de='20200101')
_, extract_took = get_time(find_crop_name_ckpt)
print(extract_took) # 9s
# 재무제표 검색 결과를 엑셀파일로 저장 ( 기본저장위치: 실행폴더/fsdata )

fs.save()