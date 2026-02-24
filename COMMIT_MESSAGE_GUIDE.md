# 커밋 메시지 가이드 (Conventional Commits)

프로젝트에서 쓰는 커밋 형식을 하나씩 정리한 문서입니다.

---

## 기본 형식

```
<타입>: <한 줄 요약>
```

- **타입**: 변경 성격 (feat, fix, docs, refactor 등)
- **한 줄 요약**: 50자 내외, 마침표 생략, 명령형으로 작성 (예: "추가한다" O / "추가함" △)

---

## 사용하는 타입 정리

### 1. `init` — 최초 설정 / 프로젝트 시작

**언제 쓰나요:** 저장소를 처음 만들었을 때, EDA·모델링 파이프라인·폴더 구조 등 **뼈대**를 올릴 때.

**예시**
```
init: EDA, modeling pipeline 및 프로젝트 구조 설정
init: 프로젝트 초기 설정 및 데이터 파이프라인 구축
```

---

### 2. `feat` — 새 기능

**언제 쓰나요:** 사용자 입장에서 **새로 생기는 동작**을 넣었을 때.

**예시**
```
feat: 교통사고 위험 예측 서비스 API 및 대시보드 추가
feat: 모델 API 서빙 및 Streamlit 대시보드 연동
feat: 지도 클릭으로 위·경도 입력 기능 추가
feat: 500m 반경 사고다발 구역 여부 표시
```

---

### 3. `fix` — 버그 수정

**언제 쓰나요:** 잘못된 동작을 **고쳤을 때**.

**예시**
```
fix: 배포 시 API 연결 실패(Connection refused) 해결
fix: 전처리 시 반경500m사고건수 컬럼 누락 수정
fix: 한글 인코딩으로 CSV 로드 오류 해결
```

---

### 4. `refactor` — 리팩터링 (동작은 유지, 코드만 정리)

**언제 쓰나요:** 기능은 그대로인데 **구조·이름·중복**만 바꿨을 때.

**예시**
```
refactor: 프로젝트 루트 기준 경로 처리로 통일
refactor: 예측 로직을 Streamlit 앱 내부로 통합
refactor: app 모듈 import 경로 정리
```

---

### 5. `docs` — 문서만 수정

**언제 쓰나요:** **코드가 아닌 문서**만 바꿨을 때 (README, DEPLOY, 주석 등).

**예시**
```
docs: README.md 수정 및 실행 방법 보완
docs: DEPLOY.md 배포 가이드 추가
docs: 커밋 메시지 가이드(COMMIT_MESSAGE_GUIDE.md) 추가
```

---

### 6. (선택) 다른 자주 쓰는 타입

| 타입       | 의미           | 예시 |
|------------|----------------|------|
| `style`    | 포맷/들여쓰기 등 (동작 변경 없음) | `style: Black 적용, 따옴표 통일` |
| `test`     | 테스트 추가/수정 | `test: predict API 단위 테스트 추가` |
| `chore`    | 빌드·설정·의존성 등 | `chore: requirements.txt에 streamlit-folium 추가` |

---

## 작성 시 유의사항

1. **타입은 소문자**, 콜론 뒤 **띄어쓰기 한 칸**.
2. **한 커밋 = 한 가지 목적**. 여러 기능을 한 번에 넣었다면 `feat: A 추가 및 B 수정`처럼 요약하거나, 가능하면 커밋을 나누기.
3. **이미 push한 커밋 메시지는** 히스토리를 바꾸지 않는 한 보통 수정하지 않는 것이 좋음.

---

## 이 프로젝트에서 쓸 만한 예시 (복사해서 사용)

```text
init: EDA, modeling pipeline 및 프로젝트 구조 설정
feat: 모델 API 서빙 및 Streamlit 대시보드 연동
feat: 교통사고 위험 예측 서비스 API 및 대시보드 추가
docs: README.md 수정 및 실행 방법 보완
refactor: 예측 로직 Streamlit 내부 통합 및 API 의존성 제거
docs: DEPLOY.md 배포 가이드 및 COMMIT_MESSAGE_GUIDE.md 추가
chore: requirements.txt에 streamlit, folium, streamlit-folium 추가
```

이 형식을 따라서 커밋하면, 나중에 `git log`나 GitHub에서 변경 이력을 타입별로 보기 좋습니다.
