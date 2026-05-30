# Snake Game 🐍

터미널에서 즐기는 한국어 뱀 게임입니다. Python의 `curses` 라이브러리를 사용해 구현했습니다.

## 실행 방법

```bash
python snake.py
```

> Windows에서는 `windows-curses` 패키지가 필요합니다.
> ```bash
> pip install windows-curses
> ```

## 조작법

| 키 | 동작 |
|----|------|
| ↑ ↓ ← → | 이동 방향 전환 |
| R | 게임 재시작 |
| Q | 게임 종료 |

## 게임 규칙

- 음식(●)을 먹으면 1점을 얻고 뱀이 길어집니다.
- 5점마다 레벨이 오르고 속도가 빨라집니다.
- 5점마다 장애물(▪)이 추가됩니다 (최대 20개).
- 벽, 자기 몸, 장애물에 부딪히면 게임 오버.

## 점수 시스템

최고 기록은 `scores.json` 파일에 자동 저장됩니다.

## 요구 사항

- Python 3.6 이상
- `curses` (Linux/macOS 기본 내장, Windows는 `windows-curses` 설치 필요)
