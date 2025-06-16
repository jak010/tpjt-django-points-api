from apscheduler.schedulers.background import BackgroundScheduler

from src.apps.batch.point_balance_sync_job_config import PointBalanceSyncJobConfig

sched = BackgroundScheduler()


@sched.scheduled_job('cron', hour=1, minute=0)  # 매일 새벽 1시에 수행
def point_balance_reader():
    PointBalanceSyncJobConfig.point_balance_sync_job()


def on_start():
    sched.start()
