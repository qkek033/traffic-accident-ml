# GitHub 푸시 → Streamlit 배포까지 전체 가이드

처음부터 끝까지 순서대로 따라 하면 됩니다.

---

## 0. 준비

- **Git 설치**: 터미널에서 `git --version` 입력 후 버전이 나오면 OK.
- **GitHub 계정**: [github.com](https://github.com) 에서 가입/로그인.
- **프로젝트 위치**: `c:\Users\Hyeonseong\Desktop\project_final` 에서 진행한다고 가정합니다.

---

## 1단계: GitHub에 새 저장소 만들기

1. 브라우저에서 [github.com](https://github.com) 접속 후 로그인.
2. 오른쪽 상단 **+** → **New repository** 클릭.
3. 아래처럼 입력:
   - **Repository name**: 예) `traffic-accident-dashboard` (원하는 이름으로)
   - **Description**: (선택) 예) 교통사고 위험 분석 Streamlit 대시보드
   - **Public** 선택.
   - **"Add a README file"** 는 체크하지 않음 (이미 로컬에 코드가 있으므로).
4. **Create repository** 클릭.
5. 생성된 페이지에 나오는 **저장소 주소**를 복사해 둡니다.  
   예: `https://github.com/본인아이디/traffic-accident-dashboard`

---

## 2단계: 모델·데이터가 올라가도록 설정하기

이 프로젝트는 `.gitignore`에 `*.pkl`과 `data/`가 있어서, **그대로면 모델·데이터가 GitHub에 안 올라갑니다.**  
배포하려면 아래 중 하나를 해야 합니다.

### 방법 A: 강제로 추가 (추천, 빠름)

터미널에서 프로젝트 폴더로 간 뒤, **일반 파일 먼저** 커밋하고, **그다음** 모델·데이터를 강제 추가합니다.

```powershell
cd c:\Users\Hyeonseong\Desktop\project_final

# 1) 일반 코드·문서만 먼저 추가
git add streamlit_app.py app/ requirements.txt DEPLOY.md COMMIT_MESSAGE_GUIDE.md README.md .gitignore
git add notebooks/
git status
git commit -m "docs: 배포 가이드 및 커밋 메시지 가이드 추가"

# 2) 모델·데이터 강제 추가 (.gitignore 무시)
git add -f models/lgbm_model.pkl models/feature_columns.pkl
git add -f data/
git status
git commit -m "chore: 배포용 모델 및 데이터 파일 추가"
```

- `data/` 안에 파일이 너무 크면(예: 한 파일이 100MB 넘음) GitHub에서 push가 막힐 수 있습니다. 그때는 [Git LFS](https://git-lfs.com/) 사용을 검토하세요.

### 방법 B: .gitignore 수정 후 추가

1. `.gitignore` 파일을 열고, 아래 두 줄을 **맨 앞에 `#`** 를 붙여 주석 처리합니다.
   ```text
   # *.pkl
   # data/
   ```
2. 저장한 뒤 터미널에서:
   ```powershell
   cd c:\Users\Hyeonseong\Desktop\project_final
   git add .
   git status
   git commit -m "chore: 배포를 위해 모델·데이터 포함 및 .gitignore 수정"
   ```
3. **주의**: 이렇게 하면 `models/`, `data/`가 계속 Git에 포함됩니다. 나중에 다시 빼려면 `.gitignore`에서 `#`를 제거하고 `git rm -r --cached models/ data/` 후 커밋하면 됩니다.

---

## 3단계: GitHub에 푸시하기

1. **저장소를 방금 만든 경우** (아직 `origin`이 없을 때):

   ```powershell
   cd c:\Users\Hyeonseong\Desktop\project_final
   git remote add origin https://github.com/본인아이디/저장소이름.git
   git branch -M main
   git push -u origin main
   ```

   - `본인아이디/저장소이름`은 1단계에서 만든 저장소 주소에 맞게 바꿉니다.  
     예: `https://github.com/hong/traffic-accident-dashboard.git`

2. **이미 `origin`을 추가해 둔 경우** (예전에 연결한 적 있으면):

   ```powershell
   cd c:\Users\Hyeonseong\Desktop\project_final
   git push -u origin main
   ```

3. GitHub 로그인 창이 뜨면 로그인하거나, **Personal access token**을 비밀번호 대신 입력할 수 있습니다.  
   (토큰 생성: GitHub → Settings → Developer settings → Personal access tokens)

4. 푸시가 끝나면 브라우저에서 해당 저장소를 열어 **파일 목록**에 `streamlit_app.py`, `app/`, `models/`, `data/`, `requirements.txt` 등이 보이는지 확인합니다.

---

## 4단계: Streamlit Cloud에서 배포하기

1. [share.streamlit.io](https://share.streamlit.io) 접속.
2. **Sign in with GitHub** 클릭 → GitHub 권한 허용.
3. **New app** 버튼 클릭.
4. 다음을 입력/선택:
   - **Repository**: 방금 푸시한 저장소 선택 (예: `본인아이디/traffic-accident-dashboard`).
   - **Branch**: `main`.
   - **Main file path**: `streamlit_app.py` (그대로 입력).
5. **Deploy!** 클릭.
6. 빌드가 시작됩니다. 로그가 나오며, 처음에는 2~5분 정도 걸릴 수 있습니다.
7. 완료되면 상단에 **Your app is live!** 와 함께 URL이 표시됩니다.  
   예: `https://traffic-accident-dashboard-xxx.streamlit.app`
8. 해당 URL을 클릭하면 배포된 대시보드가 열립니다.

---

## 5단계: 배포 후 확인

- 브라우저에서 앱 URL로 접속.
- 위도·경도 입력 후 **분석 시작** 버튼을 눌러 예측이 되는지 확인.
- 에러가 나면 6단계(문제 해결)를 참고합니다.

---

## 6단계: 나중에 코드 수정했을 때 (재배포)

1. 로컬에서 수정 후:
   ```powershell
   cd c:\Users\Hyeonseong\Desktop\project_final
   git add .
   git commit -m "feat: OOO 기능 추가"
   git push
   ```
2. Streamlit Cloud는 **해당 저장소의 main 브랜치**를 보고 있으므로, `git push`만 하면 자동으로 다시 빌드·배포됩니다.
3. share.streamlit.io 대시보드에서 앱을 클릭하면 **Reboot app** 버튼으로 수동 재시작도 할 수 있습니다.

---

## 체크리스트 (배포 전)

- [ ] Git 설치됨 (`git --version`)
- [ ] GitHub 저장소 생성됨
- [ ] `streamlit_app.py`, `app/`, `requirements.txt` 포함해서 커밋함
- [ ] `models/lgbm_model.pkl`, `models/feature_columns.pkl` 포함 (방법 A 또는 B)
- [ ] `data/` 폴더(또는 필요한 CSV) 포함
- [ ] `git push` 로 GitHub에 올라간 것 확인
- [ ] share.streamlit.io에서 Repository, Branch, Main file path 설정 후 Deploy 완료

---

## 자주 나오는 오류와 해결

| 증상 | 대처 |
|------|------|
| **"모델 또는 데이터 파일을 찾을 수 없습니다"** | GitHub 저장소에 `models/`, `data/`가 올라가 있는지 확인. 없으면 2단계(강제 추가 또는 .gitignore 수정) 다시 진행 후 `git push`. |
| **"ModuleNotFoundError: No module named 'app'"** | Streamlit Cloud는 **저장소 루트**를 기준으로 실행합니다. `streamlit_app.py`와 `app/` 폴더가 같은 루트에 있어야 합니다. |
| **Push 시 "file too large" / 100MB 오류** | 큰 파일은 [Git LFS](https://git-lfs.com/)로 올리거나, 데이터를 일부만 쓰거나 샘플만 올리도록 정리. |
| **빌드는 되는데 앱이 안 뜸** | share.streamlit.io 해당 앱 페이지에서 **Logs** 탭을 열어 에러 메시지 확인. `requirements.txt`에 `streamlit`, `folium`, `streamlit-folium`이 있는지 확인. |

---

## 요약 순서

1. GitHub에서 **New repository** 로 저장소 생성 → 주소 복사  
2. 로컬에서 **모델·데이터 포함** (강제 추가 또는 .gitignore 수정)  
3. `git add` → `git commit` → `git remote add origin ...` (최초 1회) → **`git push`**  
4. **share.streamlit.io** → Sign in with GitHub → **New app** → 저장소·Branch·Main file path 입력 → **Deploy!**  
5. 나오는 URL로 접속해서 동작 확인  
6. 이후 수정 시: `git add` → `git commit` → `git push` 하면 자동 재배포

이 순서대로 하면 GitHub 푸시부터 Streamlit 배포까지 한 번에 진행할 수 있습니다.
