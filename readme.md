# Table Of Contents

# INTRO

## POINT 적립 서비스

- 사용자에게 제공되는 적립금과 적립금 이력 관리 모델

## Technical Point

1. Optimistic Locking 기반의 동시성 제어
   - 적립금 내역을 기록 시, Optimistic Locking을 이용한 동시성 제어 처리
     - Django ORM을 이용해 Optimistic Locking 구현
     - Optimistic Locking 의 재시도를 backoff로 구현하여 트랜잭션 실패에 대한 재시도 구현
2. Caching
   - 초당 RPS 처리 성능을 향상시키기 위한 Redis 기반의 캐싱 처리
     - Django Cache를 이용한 Redis 처리
3. Batch
   - apscheduler를 django에 통합 시키고 일별 적립금 리포트 저장
4. Locust를 이용한 성능 테스트

## Etc
- src-layout 구조의 Django Project
- pytest-django를 이용한 test suite 구현
- "APIVIEW + LimitOffsetPagination"을 이용한 Pagination 구현


---

# 1. Enviornment

- Language
    - Python 3.11.5
- DataBase
    - MySQL 8.0
- FrameWork
    - Django==5.2.2
    - djangorestframework==3.16.0

# 2. Command

> 프로젝트 명령어

- makefile을 통해서 프로젝트 실행에 필요한 명령어셋을 관리

## 2.1 Execution

> 프로젝트 실행 방법

- Makefile을 통해서 프로젝트를 실행하는 방법

  ```shell
  $ make run.db
  $ make run.local
  ```

# 3. Data Model

Project에 사용된 데이터 모델과 관계

## 3.1 Entity

### 3.1.1 Points

> 사용자의 포인트 적립 또는 차감 이력을 나타내는 엔티티  
> 각각의 적립금 트랜잭션을 나타냄

- DDL
  ```sql
  CREATE TABLE `points` (
    `created_at` datetime(6) NOT NULL,
    `updated_at` datetime(6) NOT NULL,
    `id` bigint NOT NULL AUTO_INCREMENT,
    `user_id` bigint unsigned NOT NULL,
    `amount` bigint unsigned NOT NULL,
    `type` varchar(50) COLLATE utf8mb3_unicode_ci NOT NULL,
    `description` varchar(255) COLLATE utf8mb3_unicode_ci NOT NULL,
    `balance_snapshot` bigint unsigned NOT NULL,
    `version` bigint unsigned NOT NULL,
    `point_balance_id` bigint NOT NULL,
    PRIMARY KEY (`id`),
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci
  ```

### 3.1.2 Point Balance

> 사용자의 포인트 발급 이력을 나타내는 엔티티

- DDL
  ```sql
  CREATE TABLE `point_balances` (
    `created_at` datetime(6) NOT NULL,
    `updated_at` datetime(6) NOT NULL,
    `id` bigint NOT NULL AUTO_INCREMENT,
    `user_id` bigint unsigned NOT NULL,
    `balance` decimal(19,10) NOT NULL,
    `version` bigint unsigned NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `user_id` (`user_id`),  
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci
  ```

### 3.1.3 Dailay Point Reports

> 일별 포인트 적립금 트랜잭션을 나타내는 엔티티

- DDL
  ```sql 
  CREATE TABLE `daily_point_reports` (
    `id` bigint NOT NULL AUTO_INCREMENT,
    `created_at` datetime(6) NOT NULL,
    `updated_at` datetime(6) NOT NULL,
    `user_id` bigint NOT NULL,
    `report_date` date NOT NULL,
    `earn_amount` bigint NOT NULL,
    `use_amount` bigint NOT NULL,
    `cancel_amount` bigint NOT NULL,
    `net_amount` bigint NOT NULL,
    PRIMARY KEY (`id`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci 
  ```

## 3.2 Relation

### 3.2.1 Point & Point Balance

```mermaid
graph LR
    PointBalance["PointBalance"] -->|has| Point["Point"]
```

- Point Balance 와 Point 는 1:N 관계




