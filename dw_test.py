import dart_fss as dart

# Open DART API KEY 설정
api_key = 'd617ec8690f8cafd5d081e00a1501565e137f23e'
dart.set_api_key(api_key=api_key)

# DART 에 공시된 회사 리스트 불러오기

begin_date_str='20200101'
# code = '005930'  # samsung
code = '115530'  #
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
else:
    concept_id = first_labels[target_idx]
    if concept_id != 'ifrs-full_ProfitLoss':
        print('not match')



reports.save(f'{code}_quarter.xlsx', './tmp/')


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