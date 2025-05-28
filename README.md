# 실행방법

1. venv\Scripts\activate (가상환경 활성화)
2. python scripts/run_real_server.py (실제 데이터 대상으로 테스트용 서버 실행)
3. python scripts/run_dummy_server.py (더미 데이터 생성 후 테스트용 서버 실행)
4. uvicorn app.main:app --reload (서버 실행)
5. python scripts/selective_reset.py (DB 초기화)
6. 점수 계산 대시보드: http://127.0.0.1:8000/admin/dashboard
7. python scripts/download_images.py

<br> 

<details>
<summary>처음 클론했을 때 아래 실행</summary>

> - python -m venv venv (venv 폴더 생성)
> - venv\Scripts\activate (가상환경 활성화)
> - pip install -r requirements.txt (의존성 설치)
> - pip install xmltodict
> - pip install pillow
> - 처음 클론했다면 .env 파일을 만들어야 함 (.env 파일에 open api에서 발급받은 키를 넣어야 함.)
> - ASSEMBLY_API_KEY=your_api_key_here
</details>

<details>
<summary>사전 준비</summary>

> - powershell 말고 cmd에서 해야 함.
> - 컴퓨터에 git과 python이 깔려 있어야 됨
> - 처음 클론했다면 .env 파일을 만들어야 함.

</details>

<details>
<summary>uvicorn app.main:app --reload 도 서버 실행인데 왜 안 써요?</summary>

> - 데이터가 없으면 오류나서 서버 실행 안 됨. 다 구현 안 돼서 지금 안 됨.

</details>

<details>
<summary>이미지 최적화 방법</summary>

> - 이미지 최적화 스크립트 실행 방법:
> - `python scripts/optimize_images.py app/static/images/legislators app/static/images/optimized 800 85`
> - 위 명령은 의원 이미지를 최대 너비 800px, 품질 85%로 최적화하여 optimized 폴더에 저장합니다.
> - 최적화된 이미지를 기존 이미지로 교체: `xcopy /y app/static/images/optimized/* app/static/images/legislators/`
> - 이미지 최적화는 배포 전에 한 번만 실행하면 됩니다.
> - 웹사이트에는 자동으로 이미지 캐싱 및 지연 로딩 기능이 적용되어 있습니다.

</details>