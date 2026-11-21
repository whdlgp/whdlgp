# 적용 방법

1. GitHub에서 `whdlgp/whdlgp` 프로필 저장소를 엽니다.
2. 이 패키지의 `README.md`, `scripts/update_projects.py`, `.github/workflows/update-projects.yml`을 같은 경로로 올립니다.
3. 저장소의 Settings → Actions → General에서 Workflow permissions가 읽기/쓰기 허용인지 확인합니다. 워크플로 파일에도 `contents: write`를 지정했습니다.
4. Actions 탭에서 `Update profile projects`를 수동 실행하면 첫 갱신을 확인할 수 있습니다. 이후 매주 월요일 UTC 03:23에 자동 갱신됩니다.

프로젝트 목록은 공개 저장소 중 fork와 archived 저장소, 설명이 없는 저장소를 제외하고 최근 업데이트 순으로 최대 8개를 가져옵니다. 특정 저장소를 고정 선정하지 않는 자동 목록입니다. 기술 스택 영역은 README에 고정되어 프로젝트 목록 위에 표시됩니다.

토큰을 별도로 만들 필요 없이 GitHub Actions가 발급하는 `GITHUB_TOKEN`을 사용합니다.
