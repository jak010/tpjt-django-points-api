# Dev Note

## 25.06.07

### makefile 로 django project 실행 오류

- src 구조 중심으로 manage.py 를 실행시키려면 모듈 참조 에러가 남, 다음과 같이 해겷
    ```text
    import os
    import sys
    ...
    sys.path.append(os.path.join(os.path.dirname(__file__), '..')) 
    ...
    ```
