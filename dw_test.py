import dart_fss as dart

# Open DART API KEY 설정
api_key = 'd617ec8690f8cafd5d081e00a1501565e137f23e'
dart.set_api_key(api_key=api_key)

# DART 에 공시된 회사 리스트 불러오기

begin_date_str='20200101'
# code = '005930'  # samsung
code = '091810'  # tay air
reports = dart.fs.extract(corp_code=code,
                          bgn_de=begin_date_str
                          , report_tp='quarter'
                          # ,report_tp='half'
                          )

cis_report = reports['cis']
report_cis_col_label = cis_report.to_dict().keys()
report_cis_col_label = list(report_cis_col_label)
# print(report_cis_col_label)
# 2012년부터 연간 연결재무제표 불러오기
reports.save('tway.xlsx', './tmp/')


# 004690
# 029780
# 244920
# 003470
# 033780
# 007630
# 005430
# 180640
# 044180
# 043260