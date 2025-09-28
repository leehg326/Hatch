# Hatch - 부동산 중개업자용 계약서 자동화 SaaS

**Hatch**는 부동산 중개업자를 위한 원클릭 계약서 자동화 서비스입니다. 입력 → DB 저장 → PDF 생성 → 서명 → 미리보기/다운로드 → 검색 가능한 계약서 목록까지 모든 과정을 자동화합니다.

## 🚀 주요 기능

### 1. 계약서 작성 폼
- 고객 정보 입력 (이름, 연락처, 부동산 주소, 임대료, 계약 기간, 메모)
- 마우스/터치 서명 기능 (react-signature-canvas)
- 실시간 폼 검증 (Zod + React Hook Form)

### 2. 계약서 목록 및 검색
- 최신 계약서 목록 표시
- 고객명, 전화번호, 주소로 실시간 검색
- 계약 상태 표시 (계약 예정, 진행 중, 종료)
- 페이지네이션 지원

### 3. 표준계약서 PDF 생성
- 한국공인중개사협회 표준계약서 형식 준용
- 매매/전세/월세/반전세 계약서 자동 생성
- 법적/실무 필수 항목 모두 포함
- QR 코드 및 문서 해시를 통한 증빙력 확보
- 전자서명 지원 (목업)

### 4. 계약서 미리보기 및 다운로드
- 계약서 상세 정보 표시
- PDF 미리보기/다운로드/인쇄 기능
- 계약서 상태 관리 (초안/서명완료/보관)

### 5. 대시보드
- 계약서 통계 (총 계약서 수, 진행 중인 계약)
- 최근 활동 내역
- 월별 계약 건수 차트

## 🛠 기술 스택

### Frontend
- **React 19** + **TypeScript** + **Vite**
- **React Router DOM** (라우팅)
- **React Hook Form** + **Zod** (폼 관리 및 검증)
- **React Signature Canvas** (서명 기능)
- **Tailwind CSS** (스타일링)
- **Radix UI** (UI 컴포넌트)
- **Lucide React** (아이콘)
- **Recharts** (차트)

### Backend
- **Flask 3.0** + **SQLAlchemy** + **Flask-Migrate**
- **PyMySQL** (MariaDB 드라이버)
- **ReportLab** (PDF 생성)
- **Pillow** (이미지 처리)
- **Authlib** (OAuth 인증)
- **Flask-Limiter** (Rate Limiting)
- **Flask-CORS** (CORS 처리)

### Database
- **SQLite** (개발 환경)
- **MariaDB** (프로덕션 환경)

## 📁 프로젝트 구조

```
realestate-saas/
├── src/
│   ├── components/          # 재사용 가능한 UI 컴포넌트
│   │   ├── ui/             # 기본 UI 컴포넌트 (Radix UI 기반)
│   │   └── Sidebar.tsx     # 사이드바 네비게이션
│   ├── views/              # 페이지 컴포넌트
│   │   ├── Dashboard.tsx   # 대시보드
│   │   ├── Contracts.tsx   # 계약서 목록
│   │   ├── ContractForm.tsx # 계약서 작성 폼
│   │   └── ContractPreview.tsx # 계약서 미리보기
│   ├── pages/              # 인증 관련 페이지
│   ├── lib/                # 유틸리티 라이브러리
│   │   ├── api.ts          # API 클라이언트
│   │   └── utils.ts        # 공통 유틸리티
│   ├── stores/             # 상태 관리
│   └── routes/             # 라우팅 설정
├── app.py                  # Flask 메인 애플리케이션
├── models.py               # SQLAlchemy 모델
├── pdf_generator.py        # PDF 생성 모듈
├── requirements.txt        # Python 의존성
└── package.json           # Node.js 의존성
```

## 🚀 시작하기

### 사전 요구사항

- **Node.js 18+**
- **Python 3.8+**
- **MariaDB** (프로덕션) 또는 **SQLite** (개발)

### 설치 및 실행

1. **저장소 클론**
   ```bash
   git clone <repository-url>
   cd realestate-saas
   ```

2. **Python 의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

3. **Node.js 의존성 설치**
   ```bash
   npm install
   ```

4. **데이터베이스 초기화**
   ```bash
   python init_db.py
   ```

5. **환경 변수 설정**
   ```bash
   # .env 파일 생성 (env.example 참고)
   cp env.example .env
   # .env 파일에서 JWT_SECRET 등 설정
   ```

6. **개발 서버 시작**

   **백엔드 (Flask)**
   ```bash
   python app.py
   ```
   - http://localhost:5000 에서 실행

   **프론트엔드 (Vite)**
   ```bash
   npm run dev
   ```
   - http://localhost:5173 에서 실행

## 🔐 인증 시스템 사용법

### 이메일/패스워드 인증 (새로 추가)
1. **회원가입**: http://localhost:5173/signup
2. **로그인**: http://localhost:5173/login
3. **자동 토큰 갱신**: 액세스 토큰 만료 시 자동으로 리프레시 토큰으로 갱신
4. **로그아웃**: 브라우저에서 토큰 자동 삭제

### 기존 소셜 로그인
- 카카오, 구글, 페이스북 로그인은 기존과 동일하게 작동
- http://localhost:5173/auth 에서 사용 가능

### 라우트 보호 (선택사항)
```javascript
// 나중에 라우트 보호를 활성화하려면:
window.__HATCH_PROTECT__ = true;
```

## 📋 API 엔드포인트

### 인증
- `POST /auth/email/register` - 이메일 회원가입
- `POST /auth/email/login` - 이메일 로그인
- `POST /auth/email/verify` - 이메일 인증
- `GET /auth/<provider>` - 소셜 로그인 (카카오, 구글, 페이스북)

### 이메일/패스워드 인증 (새로 추가)
- `POST /api/auth/signup` - 이메일/패스워드 회원가입
- `POST /api/auth/login` - 이메일/패스워드 로그인
- `POST /api/auth/refresh` - 토큰 갱신
- `GET /api/auth/me` - 현재 사용자 정보
- `POST /api/auth/logout` - 로그아웃

### 계약서
- `POST /api/contracts` - 계약서 생성
- `GET /api/contracts` - 계약서 목록 (검색, 페이지네이션)
- `GET /api/contracts/<id>` - 계약서 상세
- `GET /api/contracts/<id>/pdf` - 계약서 PDF 다운로드

## 🎨 UI/UX 특징

### Toss 스타일 디자인
- **깔끔하고 미니멀한 디자인**
- **큰 폰트와 간단한 버튼**
- **A4 인쇄 최적화**
- **반응형 디자인** (모바일/데스크톱)

### 사용자 경험
- **원클릭 계약서 생성**
- **실시간 검색 및 필터링**
- **직관적인 네비게이션**
- **빠른 PDF 생성 및 다운로드**

## 🔒 보안

- **JWT 토큰 기반 인증**
- **Rate Limiting** (API 호출 제한)
- **CORS 설정**
- **개인정보 최소 수집**
- **안전한 서명 데이터 처리**

## 📱 지원 기능

- **반응형 웹 디자인**
- **터치/마우스 서명 지원**
- **PDF 미리보기 및 인쇄**
- **실시간 검색**
- **페이지네이션**

## 🚀 배포

### 프로덕션 빌드
```bash
npm run build
```

### 환경 변수 설정
```bash
# .env 파일 생성
FLASK_SECRET=your-secret-key
JWT_SECRET=your-jwt-secret
DATABASE_URL=mysql+pymysql://user:password@localhost/hatch_db
CLIENT_ORIGIN=https://your-domain.com

# JWT 인증 설정
JWT_SECRET=change_this_long_random_string_for_production
ACCESS_TOKEN_EXPIRES_MIN=15
REFRESH_TOKEN_EXPIRES_DAYS=14
```

## 📄 표준계약서 PDF 생성 기능

### 폰트 설치
한글 PDF 생성을 위해 Noto Sans CJK 폰트를 설치하세요:
```bash
# 폰트 파일 경로: static/fonts/NotoSansCJK-Regular.ttf
# 폰트가 없는 경우 기본 Helvetica 폰트 사용
```

### 로컬 실행
```bash
# 백엔드 실행
python app.py

# 프론트엔드 실행
npm run dev
```

### 필수 환경 변수
```bash
# .env 파일에 추가
PDF_FONT_PATH=static/fonts/NotoSansCJK-Regular.ttf
```

### 전자서명 목업 사용법
1. 계약서 생성 후 `/api/contracts/{id}/sign-requests` POST 요청
2. 역할별 서명 요청 생성 (SELLER/BUYER/AGENT)
3. `/api/contracts/{id}/sign-callback` POST 요청으로 서명 완료 처리
4. 계약서 상태가 SIGNED로 변경됨

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

문제가 발생하거나 기능 요청이 있으시면 이슈를 생성해주세요.