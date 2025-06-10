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

### src layout 에서의 pytest-django 설정

- src 구조 중심으로 pytest-django 를 실행시키려면 모듈 참조 에러가 남, 다음과 같이 해겷
    ```text
    # apps.py
      class AppsConfig(AppConfig):
        default_auto_field = 'django.db.models.BigAutoField'
        name = 'src.apps' # 수정
  
    # settings
    INSTALLED_APPS = [
        'src.apps', # 수정
    ] 
    ...    

## 25.06.09

## APIView에 Pagination 적용하기

- 이 프로젝트를 진행하면서 APIView를 사용하는 경우, Pagination을 구현한 방법은 다음과 같다.
    - Examples
        ```text
        class PointHistoryView(APIView, LimitOffsetPagination):                  
            ...
            def get(self, request, *args, **kwargs):
               ...
       
                paginate_queryset = self.paginate_queryset(
                    self.point_service.search_points(user_id=user_id),
                    request,
                    view=self
                )
        
                paginate = point_search_schema.PointHistoryPaginateResponse(
                    {
                        "count": self.count,
                        "next": self.get_next_link(),
                        "previous": self.get_previous_link(),
                        "data": paginate_queryset
                    }
                )
        
                return Response(
                    content_type="application/json",
                    status=200,
                    data=paginate.data
                ) 
        ```

## 25.06.10

### Django ORM으로 Optimistic Lock 구현하기

- src/apps/service/v1/point_service.py#L26 번 로직 참고