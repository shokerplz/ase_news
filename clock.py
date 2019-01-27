from apscheduler.schedulers.blocking import BlockingScheduler
import logging
import os
import subprocess
import psutil
import signal
log = logging.getLogger('apscheduler.executors.default')
tg_bot = subprocess.Popen("python tg_bot_stat.py", shell=True, preexec_fn=os.setsid)
sched = BlockingScheduler()
def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()
@sched.scheduled_job('interval', hours=6)
def timed_job():
    global tg_bot
    kill(tg_bot.pid)
    tg_bot = subprocess.Popen("python tg_bot_stat.py", shell=True, preexec_fn=os.setsid)
    print('#RESTART#')
sched.start()