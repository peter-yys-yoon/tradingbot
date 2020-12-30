

# Financial Report Crawling

Downloads report from DART with official API. 


# Requirements
- pip install wcwidth, fss-dart, pandas, tqdm


# Usage
### Running
- Download report of corps belong to given stock market .
```angular2html
    python main.py -d -m kospi
    python main.py -d -m kosdaq
    python main.py -d -m konex
```

- List all corps who has earned profit in last three quarters in specific market.
-m Market: kospi, -s: Save in text, -v: Visualize in terminal, -cd1: conditioning

    `python main.py -e -m kospi -s -v -cd1`


- Count all files including downloaded and failed.
        
    `python main.py -t`
  
### Conditions
  - cd1: Earn profit in last three quarters.
  - cd2: No condition


### Debugging
  
  - Download test
 
    `python main.py -dt -m kospi -c 003490`

  - Evaluation test

    `python main.py -et -c 003490 -cd1`



  # Future Work






* 일부 보고서에는 분법기별 당기순이익이 공란임.
  * 예시) Q1: 3억, Q2: -, Q3: 5억 일시 3분기 연속 흑자로 판단함.

* 일부 보고서서는 당기순이익 라벨이 없어 직업 계산해야함.
  * 순이익 계산
    * 순이익 = 매출액 - 매출원가 - 판매관리비 + (금융수익 - 금육비용) + (영업외수익 -영업외비용) - 법인세비용
    * 순이익 = 영업이익                   +  금융손익           +  영업외손익            - 법인세비용


