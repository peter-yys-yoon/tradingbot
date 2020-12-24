import dart_fss as dart
import time
import pdb
from datetime import datetime, timedelta

def get_time(given=0):
    current = time.time()
    return current , current-given

# Open DART API KEY 설정
api_key='d617ec8690f8cafd5d081e00a1501565e137f23e'
start_time = time.time()
dart.set_api_key(api_key=api_key)
set_api_ckpt, set_api_took = get_time(start_time)
print('Setting API:', set_api_took) # 1s



def check_corp_count():
    corp_list = dart.get_corp_list()
    pdb.set_trace()
    print(type(corp_list))

def date_test():
    now = datetime.now()


    begin_date =now - timedelta(days=365)
    begin_date_str = begin_date.strftime("%Y%m%d")
    return begin_date_str




def test1():
    corp_list = dart.get_corp_list()
    # corp_name_list = []
    corp_name_list = ['SK하이닉스']
    # corp_name_list = ['SK하이닉스', '삼성전자']
    begin_date_str = date_test()

    for corp_name in corp_name_list:
        #(Y: 코스피, K: 코스닥, N:코넥스, E:기타)

        """
        corpname and market='YK' cannot be used at the same time
        """
        res_corp_list = corp_list.find_by_corp_name(corp_name, exactly=True)
        res_corp = res_corp_list[0]
        print(res_corp_list)

        """
        report_tp='quarter' and fs_tp='is', can not be used at the same time.
        """
        reports = res_corp.extract_fs(bgn_de=begin_date_str,
                                      report_tp='quarter'
                                      )
        # pdb.set_trace()

        report_cis_col_list = list(reports.to_dict().keys())
        report_is = reports['cis']
        # report_is_keys = reports.labels['cis'].to_dict().keys()
        report_is_keys = list(reports.labels['cis'].to_dict().keys())
        for kk in report_is_keys:
            print(kk)
        pdb.set_trace()
        print(report_is)
        print(begin_date_str)
        print(report_is_keys)










def saumsung_test1():
    # DART 에 공시된 회사 리스트 불러오기
    corp_list = dart.get_corp_list()
    get_corp_list_ckpt, get_crop_list_took = get_time(set_api_ckpt)
    print('Get Corp list: ', get_crop_list_took)  # 9s , #상장된 회사 83226개



    samsung = corp_list.find_by_corp_name('삼성전자', exactly=True)[0]
    find_crop_name_ckpt, find_crop_name_took = get_time(get_corp_list_ckpt)
    print('Find corp name: ', find_crop_name_took) # 0.02s
    # 2012년부터 연간 연결재무제표 불러오기
    fs = samsung.extract_fs(bgn_de='20170101')

    _, extract_took = get_time(find_crop_name_ckpt)
    print('Extracing fs: ', extract_took) # 9s
    # 재무제표 검색 결과를 엑셀파일로 저장 ( 기본저장위치: 실행폴더/fsdata )

    fs.save()



# reports = dart.filings.search(bgn_de='20170101')
# check_corp_count()
test1()



