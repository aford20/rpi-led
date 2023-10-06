# Disable a job. Used for one time alarms. First arg is ID number of job
import sys

from crontab import CronTab
cron = CronTab(user='root')
import re

for job in cron.find_comment(re.compile('ID' + str(sys.argv[1]))):
    job.enable(False)
    print(job)

cron.write()