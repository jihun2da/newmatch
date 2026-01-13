# 🔗 브랜드 매칭 시스템 (Streamlit)

Excel 파일을 업로드하여 브랜드 상품을 자동으로 매칭하는 Streamlit 웹 애플리케이션입니다.

## ✨ 주요 기능

- 📁 **다중 파일 업로드**: 여러 엑셀 파일을 동시에 업로드 가능
- 🔄 **Sheet1 → Sheet2 변환**: 업로드된 파일을 Sheet2 형식으로 자동 변환
- 🎯 **브랜드 매칭**: 브랜드, 상품명, 사이즈 기반 정확한 매칭
- 🔍 **유사도 매칭**: 정확 매칭 실패 시 유사도 기반 매칭 제공
- 📊 **실시간 통계**: 매칭 성공률과 처리 현황을 실시간으로 확인
- 📥 **결과 다운로드**: 매칭 완료된 데이터를 Excel 파일로 다운로드
- 🔧 **키워드 관리**: 상품명에서 제거할 키워드를 관리

## 🚀 Streamlit Cloud 배포

### 1. GitHub에 저장소 업로드

```bash
cd newmatch
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/newmatch.git
git push -u origin main
```

### 2. Streamlit Cloud에서 배포

1. [Streamlit Cloud](https://streamlit.io/cloud)에 접속
2. "New app" 클릭
3. GitHub 저장소 선택: `YOUR_USERNAME/newmatch`
4. Main file path: `streamlit_app.py`
5. "Deploy" 클릭

### 3. 배포 완료!

배포가 완료되면 자동으로 URL이 생성됩니다:
```
https://YOUR_APP_NAME.streamlit.app
```

## 📋 로컬 실행

### 1. 필수 조건
- Python 3.8 이상
- pip (Python 패키지 관리자)

### 2. 설치
```bash
# 의존성 패키지 설치
pip install -r requirements.txt
```

### 3. 실행
```bash
# Streamlit 앱 실행
streamlit run streamlit_app.py
```

### 4. 접속
브라우저에서 다음 주소로 접속:
```
http://localhost:8501
```

## 📖 사용 방법

### 1️⃣ 파일 업로드
- **지원 형식**: `.xlsx`, `.xls` (Sheet1 형식)
- **업로드 방법**: 
  - 클릭하여 파일 선택
  - 드래그 앤 드롭으로 업로드
- **다중 업로드**: 여러 파일을 한 번에 선택 가능

### 2️⃣ 데이터 변환
- 업로드된 Sheet1 형식 파일들이 자동으로 Sheet2 형식으로 변환
- 23개 컬럼 구조로 매핑

### 3️⃣ 브랜드 매칭
- **매칭 기준**:
  - **브랜드**: 정확히 일치
  - **상품명**: 유사도 85% 이상
  - **사이즈**: 정확 매칭 (주니어 사이즈 차단)
  - **색상**: 유사도 매칭
- **매칭 소스**: [브랜드매칭시트](https://docs.google.com/spreadsheets/d/14Pmz5-bFVPSPbfoKi5BfQWa8qVMVNDqxEQVmhT9wyuU/edit?gid=1834709463#gid=1834709463)

### 4️⃣ 결과 확인 및 다운로드
- 정확 매칭 결과와 유사도 매칭 결과를 별도로 다운로드 가능
- 통합 결과 파일도 제공

## 🎯 매칭 로직

### 정확 매칭
- 브랜드명 정확히 일치
- 상품명 유사도 85% 이상
- 사이즈 정확 매칭 (주니어 사이즈 차단)
- 종합 유사도 60% 이상

### 유사도 매칭
- 정확 매칭 실패한 상품에 대해 수행
- 상품명, 색상, 사이즈 유사도 종합 평가
- 종합 유사도 30% 이상인 경우 제시

## 📂 파일 구조

```
newmatch/
├── streamlit_app.py          # Streamlit 메인 앱
├── brand_matching_system.py  # 매칭 로직
├── brand_sheets_api.py      # 구글 시트 API 연동
├── file_processor.py         # 파일 처리
├── requirements.txt          # 패키지 의존성
├── keywords.xlsx            # 키워드 파일
├── README.md                # 사용 설명서
├── uploads/                 # 업로드된 파일 저장소 (자동 생성)
└── results/                 # 처리 결과 파일 저장소 (자동 생성)
```

## 🛠 기술 스택

- **프론트엔드**: Streamlit
- **백엔드**: Python
- **데이터 처리**: Pandas, OpenPyXL
- **API 연동**: Requests (구글 시트)

## ⚡ 성능 최적화

- **브랜드 인덱스**: 브랜드별 상품 인덱싱으로 빠른 검색
- **캐싱**: 상품명 정규화, 유사도 계산 결과 캐싱
- **배치 처리**: 결과를 리스트에 모았다가 한 번에 할당
- **조기 종료**: 높은 유사도 발견 시 즉시 반환

## 🔒 보안 기능

- **파일 검증**: 허용된 확장자만 업로드 가능
- **안전한 파일명**: 타임스탬프 기반 파일명 생성
- **크기 제한**: 50MB 파일 크기 제한
- **경로 보안**: 안전한 경로 처리

## 🐛 문제 해결

### 일반적인 문제들

1. **매칭률이 낮은 경우**
   - 브랜드명이 정확히 일치하는지 확인
   - 사이즈 정보가 올바른 형식인지 확인
   - 브랜드 데이터 새로고침 시도

2. **파일 업로드 실패**
   - 파일 형식이 `.xlsx` 또는 `.xls`인지 확인
   - 파일 크기가 50MB 이하인지 확인
   - 파일이 손상되지 않았는지 확인

3. **처리 시간이 오래 걸리는 경우**
   - 파일 크기와 데이터 양에 따라 처리 시간 증가
   - 큰 파일은 여러 개로 나누어 처리 권장

## 📞 지원

문제가 발생하거나 개선 사항이 있으시면 이슈를 등록해주세요.



