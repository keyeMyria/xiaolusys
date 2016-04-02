# coding=utf-8
from flashsale.pay.models import SaleOrder, SaleTrade
from shopback.items.models import ProductSku
from flashsale.pay.models_addr import UserAddress
from shopback.trades.models import PackageOrder
from flashsale.pay.models_refund import SaleRefund


def print_out_package(buyer_id):
    # 输出一个人的所有包裹
    # 核对
    trade = SaleTrade.objects.filter(status=SaleTrade.WAIT_SELLER_SEND_GOODS, buyer_id=buyer_id)[0]
    print '================================================================='
    if trade.user_address_id:
        print str(trade.buyer_id) + ':' + str(trade.user_address_id) + ' ' + str(UserAddress.objects.get(id=trade.user_address_id))
    else:
        print str(trade.buyer_id) + ':'
    print '----------------------------------'
    res1 = {}
    for trade in SaleTrade.objects.filter(status=SaleTrade.WAIT_SELLER_SEND_GOODS, buyer_id=buyer_id):
        for order in trade.sale_orders.filter(refund_status=SaleRefund.NO_REFUND):
            if order.sku_id:
                if order.assign_status:
                #if True:
                    print str(order.id) + '|'+ str(order.sku_id) + '|' + str(order.num) + '|' + str(order.assign_status) +'|' + str(order.package_order_id)
                    res1[order.sku_id] = res1.get(order.sku_id,0) + order.num
            else:
                print order.id
    print '-              -              -'
    res2 = {}
    for p in PackageOrder.objects.filter(buyer_id=trade.buyer_id):
        print 'package_order:' + str(p.id)
        for order in SaleOrder.objects.filter(package_order_id=p.id):
            if order.assign_status:
            #if True:
                print str(order.id) + '|'+ str(order.sku_id) + '|' + str(order.num) + '|' + str(order.assign_status)
                res2[order.sku_id] = res2.get(order.sku_id,0) + order.num
            psku = ProductSku.objects.get(id=order.sku_id)
            #print 'stock: '+ str(order.sku_id)+ '| quantity ' + str(psku.quantity) +'| assign_num:' + str(psku.assign_num)
    if res1!=res2:
        print 'error'
    print res1
    print res2


def get_all_buyer():
    res = []
    for buyer_id in SaleTrade.objects.values('buyer_id').filter(status=SaleTrade.WAIT_SELLER_SEND_GOODS).distinct():
        buyer_id = buyer_id.values()[0]
        print buyer_id
        res.append(buyer_id)
    return res


def print_out_sku(sku_id):
    product_sku_res = {}
    for productSku in ProductSku.objects.filter(assign_num__gt=0):
        product_sku_res[str(productSku.id)] = productSku.assign_num
    res = {}
    for s in SaleOrder.objects.filter(sku_id=sku_id, status__in=[SaleOrder.WAIT_SELLER_SEND_GOODS],refund_status=SaleRefund.NO_REFUND):
        res[s.sku_id] = res.get(s.sku_id, 0) + s.num
    print product_sku_res
    print res
    res2 = {}
    for s in SaleOrder.objects.filter(sku_id=sku_id, assign_status=1):
        res2[s.sku_id] = res2.get(s.sku_id, 0) + s.num
    print res2
    return


if __name__ == '__main__':
    #get_all_buyer()
    #for buyer_id in get_all_buyer():
    #    print_out_package(buyer_id)
    print_out_package(4452)
    print_out_package(4452)