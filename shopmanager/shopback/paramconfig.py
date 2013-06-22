#-*- coding:utf8 -*-
USER_NORMAL = "normal"     #正常
USER_INACTIVE = "inactive" #待用
USER_DELETE = "delete"     #删除
USER_FREEZE = "freeze"     #冻结
USER_SUPERVISE = "supervise" #监管

#任务状态
UNEXECUTE = 'unexecute'
EXECERROR = 'execerror'
SUCCESS = 'success'
NORMAL = 'normal'
DELETE = 'delete'
REMAIN = 'remain'  #保留
#订单类型
FENXIAO_TYPE = 'fenxiao'
TAOBAO_TYPE  = 'fixed'
DIRECT_TYPE  = 'direct'
EXCHANGE_TYPE  = 'exchange'
REISSUE_TYPE   = 'reissue'
AUTO_DELIVERY_TYPE = 'auto_delivery'
COD_TYPE        = 'cod'
GUARANTEE_TYPE  = 'guarantee_trade'
AUCTION_TYPE    = 'auction'

TAOBAO_TRADE_TYPE = (FENXIAO_TYPE,TAOBAO_TYPE,AUTO_DELIVERY_TYPE,COD_TYPE,GUARANTEE_TYPE,AUCTION_TYPE)
#商品状态
ONSALE_STATUS  = 'onsale'
INSTOCK_STATUS = 'instock'

#订单来源
TF_WAP    = 'WAP'    #手机
TF_HITAO  = 'HITAO'  #嗨淘
TF_TOP    = 'TOP'    #商城
TF_TAOBAO = 'TAOBAO' #普通淘宝
TF_JHS    = 'JHS'    #聚划算

#发货批次状态
RP_INITIAL_STATUS     = 0
RP_WAIT_ACCEPT_STATUS = 1
RP_WAIT_CHECK_STATUS  = 2
RP_ACCEPT_STATUS  = 3
RP_CANCEL_STATUS  = 4

#物流类型
EXPRESS_SHIPPING_TYPE = 'express' #快递
POST_SHIPPING_TYPE    = 'post' #平邮
EMS_SHIPPING_TYPE     = 'ems' #EMS
EXTRACT_SHIPPING_TYPE = 'extract' #无需物流

SHIPPING_TYPE_MAP = {
    "free":EXPRESS_SHIPPING_TYPE,
    "express":EXPRESS_SHIPPING_TYPE,
    "FAST":EXPRESS_SHIPPING_TYPE,
    "SELLER":EXPRESS_SHIPPING_TYPE,
    "post":POST_SHIPPING_TYPE,
    "ems":EMS_SHIPPING_TYPE,
    'EMS':EMS_SHIPPING_TYPE,
    'ORDINARY':POST_SHIPPING_TYPE,
}

SUB_TRADE_COMPANEY_CODE = u'看主订单快递'
EXTRACT_COMPANEY_CODE = u'无需物流'

REAL_ORDER_GIT_TYPE = 0 #实付
CS_PERMI_GIT_TYPE   = 1 #赠送
OVER_PAYMENT_GIT_TYPE = 2 #满就送
COMBOSE_SPLIT_GIT_TYPE = 3 #拆分
RETURN_GOODS_GIT_TYPE = 4 #退货
CHANGE_GOODS_GIT_TYPE = 5 #换货

#系统内部状态
WAIT_AUDIT_STATUS = 'WAIT_AUDIT' #等待人工审核
WAIT_PREPARE_SEND_STATUS  = 'WAIT_PREPARE_SEND' 
WAIT_CHECK_BARCODE_STATUS = 'WAIT_CHECK_BARCODE'
WAIT_SCAN_WEIGHT_STATUS   = 'WAIT_SCAN_WEIGHT'
FINISHED_STATUS = 'FINISHED'
INVALID_STATUS  = 'INVALID' 
REGULAR_REMAIN_STATUS = 'REGULAR_REMAIN'
ON_THE_FLY_STATUS = 'ON_THE_FLY' #合单
#子订单系统内部状态
IN_EFFECT = "IN_EFFECT"
#INVALID_STATUS = 'INVALID' 
#淘宝等待卖家发货对应系统内部状态
WAIT_DELIVERY_STATUS = [WAIT_AUDIT_STATUS,WAIT_PREPARE_SEND_STATUS,REGULAR_REMAIN_STATUS,ON_THE_FLY_STATUS]
#淘宝等待卖家发货对应系统内部状态
WAIT_WEIGHT_STATUS = [WAIT_AUDIT_STATUS,WAIT_PREPARE_SEND_STATUS,REGULAR_REMAIN_STATUS,
                      ON_THE_FLY_STATUS,WAIT_CHECK_BARCODE_STATUS,WAIT_SCAN_WEIGHT_STATUS]
#淘宝卖家已发货后对应系统内部状态
HAS_DELIVERY_STATUS = [WAIT_CHECK_BARCODE_STATUS,WAIT_SCAN_WEIGHT_STATUS,FINISHED_STATUS,INVALID_STATUS]

#淘宝交易状态
TRADE_NO_CREATE_PAY = 'TRADE_NO_CREATE_PAY'
WAIT_BUYER_PAY      = 'WAIT_BUYER_PAY'
WAIT_SELLER_SEND_GOODS   = 'WAIT_SELLER_SEND_GOODS'
WAIT_BUYER_CONFIRM_GOODS = 'WAIT_BUYER_CONFIRM_GOODS'
TRADE_BUYER_SIGNED = 'TRADE_BUYER_SIGNED'
TRADE_FINISHED     = 'TRADE_FINISHED'
TRADE_CLOSED       = 'TRADE_CLOSED'
TRADE_CLOSED_BY_TAOBAO   = 'TRADE_CLOSED_BY_TAOBAO'

#交易有效的订单状态
ORDER_SUCCESS_STATUS  = (WAIT_SELLER_SEND_GOODS,WAIT_BUYER_CONFIRM_GOODS,TRADE_BUYER_SIGNED,TRADE_FINISHED)
#买家付款后还没结束的订单
ORDER_UNFINISH_STATUS = (WAIT_SELLER_SEND_GOODS,WAIT_BUYER_CONFIRM_GOODS,TRADE_BUYER_SIGNED)
#卖家已发货但未结束的订单
ORDER_POST_STATUS     = (WAIT_BUYER_CONFIRM_GOODS,TRADE_BUYER_SIGNED,TRADE_FINISHED)
#交易结束的订单
ORDER_OK_STATUS       = (TRADE_FINISHED,TRADE_CLOSED)
#交易成功
ORDER_FINISH_STATUS   = TRADE_FINISHED
#交易失败
ORDER_REFUND_STATUS   = TRADE_CLOSED
#交易未付款
ORDER_UNPAY_STATUS    = WAIT_BUYER_PAY

#分销付款类型
ALIPAY_SURETY_TYPE = 'ALIPAY_SURETY'
ALIPAY_CHAIN_TYPE  = 'ALIPAY_CHAIN'
TRANSFER_TYPE      = 'TRANSFER'
PREPAY_TYPE        = 'PREPAY'
IMMEDIATELY_TYPE   = 'IMMEDIATELY'

#淘宝分销交易状态
WAIT_BUYER_CONFIRM_GOODS_ACOUNTED = "WAIT_BUYER_CONFIRM_GOODS_ACOUNTED"
WAIT_SELLER_SEND_GOODS_ACOUNTED   = "WAIT_SELLER_SEND_GOODS_ACOUNTED"
WAIT_CONFIRM = "WAIT_CONFIRM"
WAIT_CONFIRM_WAIT_SEND_GOODS = "WAIT_CONFIRM_WAIT_SEND_GOODS"
WAIT_CONFIRM_SEND_GOODS    = "WAIT_CONFIRM_SEND_GOODS"
WAIT_CONFIRM_GOODS_CONFIRM = "WAIT_CONFIRM_GOODS_CONFIRM"
CONFIRM_WAIT_SEND_GOODS    = "CONFIRM_WAIT_SEND_GOODS"
CONFIRM_SEND_GOODS   = "CONFIRM_SEND_GOODS"
TRADE_REFUNDED       = "TRADE_REFUNDED"
TRADE_REFUNDING      = "TRADE_REFUNDING"
#TRADE_NO_CREATE_PAY = 'TRADE_NO_CREATE_PAY'
#WAIT_BUYER_PAY      = 'WAIT_BUYER_PAY'
#WAIT_SELLER_SEND_GOODS = 'WAIT_SELLER_SEND_GOODS'
#WAIT_BUYER_CONFIRM_GOODS = 'WAIT_BUYER_CONFIRM_GOODS'
#TRADE_BUYER_SIGNED = 'TRADE_BUYER_SIGNED'
#TRADE_FINISHED     = 'TRADE_FINISHED'
#TRADE_CLOSED       = 'TRADE_CLOSED'


FENXIAO_TAOBAO_STATUS_MAP = {
    WAIT_BUYER_CONFIRM_GOODS_ACOUNTED:WAIT_BUYER_CONFIRM_GOODS,
    WAIT_SELLER_SEND_GOODS_ACOUNTED:WAIT_SELLER_SEND_GOODS,
    WAIT_CONFIRM:WAIT_BUYER_PAY,
    WAIT_CONFIRM_WAIT_SEND_GOODS:WAIT_SELLER_SEND_GOODS,
    WAIT_CONFIRM_SEND_GOODS:WAIT_SELLER_SEND_GOODS,
    WAIT_CONFIRM_GOODS_CONFIRM:TRADE_BUYER_SIGNED,
    CONFIRM_WAIT_SEND_GOODS:WAIT_SELLER_SEND_GOODS,
    CONFIRM_SEND_GOODS:WAIT_BUYER_CONFIRM_GOODS,
    TRADE_REFUNDED:TRADE_CLOSED,
    TRADE_REFUNDING:WAIT_SELLER_SEND_GOODS,
    TRADE_NO_CREATE_PAY:TRADE_NO_CREATE_PAY,
    WAIT_BUYER_PAY:WAIT_BUYER_PAY,
    WAIT_SELLER_SEND_GOODS:WAIT_SELLER_SEND_GOODS,
    WAIT_BUYER_CONFIRM_GOODS:WAIT_BUYER_CONFIRM_GOODS,
    TRADE_BUYER_SIGNED:TRADE_BUYER_SIGNED,
    TRADE_FINISHED:TRADE_FINISHED,
    TRADE_CLOSED:TRADE_CLOSED,
}

#淘宝退款状态
NO_REFUND = 'NO_REFUND'
REFUND_WAIT_SELLER_AGREE  = 'WAIT_SELLER_AGREE'
REFUND_WAIT_RETURN_GOODS  = 'WAIT_BUYER_RETURN_GOODS'
REFUND_CONFIRM_GOODS      = 'WAIT_SELLER_CONFIRM_GOODS'
REFUND_REFUSE_BUYER       = 'SELLER_REFUSE_BUYER'
REFUND_CLOSED   = 'CLOSED'
REFUND_SUCCESS  = 'SUCCESS'

#有效的退款状态
REFUND_APPROVAL_STATUS = [REFUND_WAIT_RETURN_GOODS,REFUND_CONFIRM_GOODS,REFUND_SUCCESS]

FRONT_NOPAID_FINAL_NOPAID = "FRONT_NOPAID_FINAL_NOPAID"
FRONT_PAID_FINAL_NOPAID   = "FRONT_PAID_FINAL_NOPAID"
FRONT_PAID_FINAL_PAID     = "FRONT_PAID_FINAL_PAID"
 
#采购付款类型
PC_COD_TYPE     = 'COD'
PC_PREPAID_TYPE = 'PP'
PC_POD_TYPE     = 'POD'
PC_OTHER_TYPE   = 'OTHER'

#采购单状态
PURCHASE_DRAFT    = 'DRAFT'
PURCHASE_APPROVAL = 'APPROVAL'
PURCHASE_RETURN   = 'RETURN'
PURCHASE_FINISH   = 'FINISH'
PURCHASE_INVALID  = 'INVALID'  
PURCHASE_CLOSE    = 'CLOSE'  #退货确认后该交易关闭
PURCHASE_REWORD   = 'REWORD' #返修
PURCHASE_REWORDOVER  = 'REWORDOVER' #返修结束


COD_NEW_CREATED = 'NEW_CREATED' #初始状态
COD_ACCEPTED_BY_COMPANY = 'ACCEPTED_BY_COMPANY' #接单成功
COD_REJECTED_BY_COMPANY = 'REJECTED_BY_COMPANY' #接单失败
COD_RECIEVE_TIMEOUT  = 'RECIEVE_TIMEOUT' #接单超时
COD_TAKEN_IN_SUCCESS = 'TAKEN_IN_SUCCESS' #揽收成功
COD_TAKEN_IN_FAILED  = 'TAKEN_IN_FAILED' #揽收失败
COD_TAKEN_TIMEOUT = 'TAKEN_TIMEOUT' #揽收超时
COD_SIGN_IN = 'SIGN_IN' #签收成功
COD_REJECTED_BY_OTHER_SIDE = 'REJECTED_BY_OTHER_SIDE' #签收失败
COD_WAITING_TO_BE_SENT = 'WAITING_TO_BE_SENT' #订单等待发送给物流公司
COD_CANCELED = 'CANCELED' #用户取消物流订单

SMS_CREATED  = 0
SMS_COMMIT   = 1
SMS_COMPLETE = 2
SMS_ERROR    = 3
SMS_CANCLE   = 4

#问题单问题编号
NEW_MEMO_CODE = 1     #新留言
NEW_REFUND_CODE = 2   #新退款
NEW_MERGE_TRADE_CODE = 3  #新合单
WAITING_REFUND_CODE = 4   #申请退款中
RULE_MATCH_CODE = 5   #有规则匹配
OUT_GOOD_CODE = 6   #订单缺货
INVALID_END_CODE = 7  #订单非正常结束
POST_MODIFY_CODE = 8 #订单发货失败
POST_SUB_TRADE_ERROR_CODE = 9 #子订单发货失败，请检查子订单是否退款,(如退款拆包并保留父订单物流单)
COMPOSE_RULE_ERROR_CODE = 10 #组合商品拆分出错 
MULTIPLE_ORDERS_CODE = 11 #买家有多单等待合并 
ADDR_CHANGE_CODE = 12 #交易物流信息
PAYMENT_RULE_ERROR_CODE = 13 #金额规则执行出错
MERGE_TRADE_ERROR_CODE = 14 #合单出错
ORDER_ADD_REMOVE_CODE  = 15 #子订单增删编号
LOGISTIC_ERROR_CODE  = 16 #系统无法选择快递或订单没有收货信息
OUTER_ID_NOT_MAP_CODE = 17 #系统该商品编码不存在，或不正常
PULL_ORDER_ERROR_CODE = 18 #手动下单失败
TRADE_BY_WLB_CODE = 19 #订单由官方合作物流宝发货
TRADE_BY_JHS_CODE = 20 #订单含聚划算入仓商品

