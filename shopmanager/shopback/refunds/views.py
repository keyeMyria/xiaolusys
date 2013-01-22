import json
from django.http import HttpResponse
from django.conf import settings
from auth import staff_requried
from auth.utils import parse_datetime,parse_date,format_time,map_int2str
from shopback.refunds.tasks import updateAllUserRefundOrderTask

__author__ = 'meixqhi'


@staff_requried(login_url=settings.LOGIN_URL)
def update_interval_refunds(request,dt_f,dt_t):

    dt_f = parse_date(dt_f)
    dt_t = parse_date(dt_t)

    logistics_task = updateAllUserRefundOrderTask.delay(update_from=dt_f,update_to=dt_t)

    ret_params = {'task_id':logistics_task.task_id}

    return HttpResponse(json.dumps(ret_params),mimetype='application/json')