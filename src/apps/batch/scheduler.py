from apscheduler.schedulers.background import BackgroundScheduler

from src.apps.batch.point_balance_sync_job_config import PointBalanceSyncJobConfig

sched = BackgroundScheduler()


@sched.scheduled_job('interval', seconds=5)
def point_balance_reader():
    PointBalanceSyncJobConfig.sync_point_balance_step()


def on_start():
    sched.start()
