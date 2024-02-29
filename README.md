# PandashAI
---
분석가 입장에서 어려운 작업은 아니지만 반복적으로 수행해야 하는 귀찮은 작업들이 있습니다. 저의 경우 데이터 탐색 과정에서 다양한 통계 검정을 수행거나, 시각화하는 등의 작업이 그랬습니다. 이러한 귀찮음을 대화하듯이 텍스트로 작성하고 결과를 바로 확인하며 사용된 코드를 가져와 내 마음대로 수정할 수 있다면, 데이터 분석 과정의 효율이 올라갈 것이라 생각하여 제작했습니다.

Description
---
Step1. API key를 입력합니다.
<img width="959" alt="image" src="https://github.com/haesung-j/pandashAI/assets/47179168/aade8b48-ab16-4f8e-85fa-e5548d7b8bf3">

Step2. 분석 대상 csv 데이터를 선택합니다. 2개 이상의 데이터도 선택 가능하며 Select CSV File 버튼을 클릭하여 업로드하거나, 스크립트와 동일 폴더 내 data folder가 존재한다면 해당 폴더 내에서 파일 목록을 읽어와 보여줍니다.
<img width="958" alt="image" src="https://github.com/haesung-j/pandashAI/assets/47179168/47ef0c8d-d178-4332-8ccc-cd5a4b253566">

Step3. 대화형으로 데이터를 분석해보세요!
<img width="946" alt="image" src="https://github.com/haesung-j/pandashAI/assets/47179168/8d03f07e-2e17-407b-abd2-f7f97e27819e">

- Show Code 버튼을 누르면, 해당 답변을 생성하는데 사용한 코드를 확인할 수 있습니다.
  <img width="927" alt="image" src="https://github.com/haesung-j/pandashAI/assets/47179168/6885b43f-4cee-44e7-8ba2-7d2172c8473a">

- Download Result 버튼을 누르면, 해당 답변을 다운로드 받을 수 있습니다. 파일의 형태는 png, csv, txt 3가지 중 하나로 다운로드 됩니다.
  
  <img width="370" alt="image" src="https://github.com/haesung-j/pandashAI/assets/47179168/3161bf1b-96aa-4cad-93a9-6d888f4c3551">

How to run the app
---
1. 레포지토리를 클론합니다.
2. 클론한 디렉토리로 이동합니다.
3. 필요한 라이브러리를 다운받습니다.
```
pip install -r requirements.txt
```
4. 아래 명령어를 사용해 실행합니다.
```
python app_run.py
```




