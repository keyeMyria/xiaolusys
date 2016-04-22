# coding=utf-8
from .models_freesample import ReadPacket, AwardWinner
from django.db.models import Sum, F
from flashsale.pay.models_user import BudgetLog
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


def pmt_red_to_budgetlog():
    """
    活动红包记录到钱包记录中,并且计算金额到用户的账户
    """
    # 找出没有兑换的活动红包记录
    reds = ReadPacket.objects.filter(status=ReadPacket.NOT_EXCHANGE)
    # 按计算记录的金额 按照用户和日期分组 {'created_d': datetime.date(2016, 2, 27), 'customer': u'1', 'sum_value': 5.92}
    cus_reds = reds.extra(select={'created_d': 'date(created)'}).values('created_d',
                                                                        'customer').annotate(sum_value=Sum('value'))
    for cus_red in cus_reds:
        customer_id = cus_red['customer']
        flow_amount = int(Decimal(str(cus_red['sum_value'])) * 100)  # 注意小数转换
        # 创建BudgetLog记录
        BudgetLog.objects.create(customer_id=customer_id,
                                 flow_amount=flow_amount,
                                 budget_type=BudgetLog.BUDGET_IN,
                                 budget_log_type=BudgetLog.BG_ENVELOPE,
                                 budget_date=cus_red['created_d'],
                                 referal_id=cus_red['created_d'].strftime("%Y-%m-%d"))
    # 更新到兑换状态
    reds.update(status=ReadPacket.EXCHANGE)
    return

