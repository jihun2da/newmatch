# 🚀 Streamlit Cloud 배포 가이드

## 1단계: GitHub에 저장소 생성 및 업로드

### GitHub에 새 저장소 생성

1. [GitHub](https://github.com)에 로그인
2. 우측 상단의 "+" 버튼 클릭 → "New repository" 선택
3. 저장소 정보 입력:
   - **Repository name**: `newmatch` (또는 원하는 이름)
   - **Description**: "Brand matching system with Streamlit"
   - **Visibility**: Public (Streamlit Cloud는 Public 저장소만 지원)
   - **Initialize this repository with**: 체크하지 않음 (이미 파일이 있음)
4. "Create repository" 클릭

### 로컬 저장소를 GitHub에 연결

터미널에서 다음 명령어를 실행하세요:

```bash
cd newmatch

# GitHub 저장소 URL로 변경 (YOUR_USERNAME을 실제 GitHub 사용자명으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/newmatch.git

# main 브랜치로 변경
git branch -M main

# GitHub에 푸시
git push -u origin main
```

**예시:**
```bash
git remote add origin https://github.com/johndoe/newmatch.git
git branch -M main
git push -u origin main
```

## 2단계: Streamlit Cloud에서 배포

### Streamlit Cloud 접속

1. [Streamlit Cloud](https://streamlit.io/cloud)에 접속
2. "Sign in" 클릭 → GitHub 계정으로 로그인

### 새 앱 배포

1. 대시보드에서 "New app" 버튼 클릭
2. 배포 설정:
   - **Repository**: `YOUR_USERNAME/newmatch` 선택
   - **Branch**: `main` 선택
   - **Main file path**: `streamlit_app.py` 입력
3. "Deploy" 버튼 클릭

### 배포 완료!

배포가 완료되면 자동으로 URL이 생성됩니다:
```
https://YOUR_APP_NAME.streamlit.app
```

## 3단계: 앱 사용

1. 생성된 URL로 접속
2. Excel 파일 업로드
3. "매칭 시작" 버튼 클릭
4. 결과 다운로드

## 🔧 문제 해결

### 배포 실패 시

1. **의존성 문제**: `requirements.txt`에 모든 패키지가 포함되어 있는지 확인
2. **파일 경로 문제**: `streamlit_app.py`가 루트 디렉토리에 있는지 확인
3. **GitHub 연결 문제**: 저장소가 Public인지 확인

### 로컬에서 테스트

배포 전에 로컬에서 테스트하려면:

```bash
cd newmatch
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 📝 참고사항

- Streamlit Cloud는 무료로 제공됩니다
- Public 저장소만 지원합니다
- 자동 배포: GitHub에 푸시하면 자동으로 재배포됩니다
- 로그 확인: Streamlit Cloud 대시보드에서 앱 로그를 확인할 수 있습니다

