/**
 * Created by jishu_linjie on 9/7/15.
 */
/**
 *@author: imeron
 *@date: 2015-07-22
 */
var timestamp = Date.parse(new Date());
var wait = 60;
function time(btn) {
    if (wait == 0) {
        btn.click(get_code);
        btn.text("获取验证码");
        wait = 60;
    } else {
        btn.unbind("click")
        btn.text(wait + "秒后重新获取");
        wait--;
        setTimeout(function () {
                time(btn);
            },
            1000)
    }
}

var today = new Date();
function today_timer() {
    /*
     * 首页(今日)倒计时
     * auther:yann
     * date:2015/6/8
     */
    var ts = (new Date(today.getFullYear(), today.getMonth(), today.getDate() + 1, 14, 0, 0)) - (new Date());//计算剩余的毫秒数
    var dd = parseInt(ts / 1000 / 60 / 60 / 24, 10);//计算剩余的天数
    var hh = parseInt(ts / 1000 / 60 / 60 % 24, 10);//计算剩余的小时数
    var mm = parseInt(ts / 1000 / 60 % 60, 10);//计算剩余的分钟数
    var ss = parseInt(ts / 1000 % 60, 10);//计算剩余的秒数
    dd = checkTime(dd);
    hh = checkTime(hh);
    mm = checkTime(mm);
    ss = checkTime(ss);

    if (ts > 100800000 && ts < 136800000) {
        $(".poster_timer.tm2").text("敬请期待");
    } else if (ts < 100800000 && ts >= 86400000) {
        $(".poster_timer.tm2").text("剩余" + dd + "天" + hh + "时" + mm + "分" + ss + "秒");
        setTimeout(function () {
                today_timer();
            },
            1000);
    } else if (ts < 86400000) {
        $(".poster_timer.tm2").text("剩余" + hh + "时" + mm + "分" + ss + "秒");
        setTimeout(function () {
                today_timer();
            },
            1000);
    }

}

function yesterday_timer() {
    /*
     * 昨日特卖倒计时
     * auther:yann
     * date:2015/6/8
     */
    var ts = (new Date(today.getFullYear(), today.getMonth(), today.getDate(), 14, 0, 0)) - (new Date());//计算剩余的毫秒数
    var dd = parseInt(ts / 1000 / 60 / 60 / 24, 10);//计算剩余的天数
    var hh = parseInt(ts / 1000 / 60 / 60 % 24, 10);//计算剩余的小时数
    var mm = parseInt(ts / 1000 / 60 % 60, 10);//计算剩余的分钟数
    var ss = parseInt(ts / 1000 % 60, 10);//计算剩余的秒数
    dd = checkTime(dd);
    hh = checkTime(hh);
    mm = checkTime(mm);
    ss = checkTime(ss);
    console.log(dd, hh, mm, ss);
    if (ts > 0) {
        $(".poster_timer.tm2").text(hh + "时" + mm + "分" + ss + "秒");
        setTimeout(function () {
                yesterday_timer();
            },
            1000);
    } else {
        $(".poster_timer.tm2").text("敬请期待明日上新");
    }
}
function tm_timer_today() {
    /*
     * 今天海报特卖倒计时
     * auther:yann
     * date:2015/20/8
     */
    var ts = (new Date(today.getFullYear(), today.getMonth(), today.getDate() + 1, 14, 0, 0)) - (new Date());//计算剩余的毫秒数
    var dd = parseInt(ts / 1000 / 60 / 60 / 24, 10);//计算剩余的天数
    var hh = parseInt(ts / 1000 / 60 / 60 % 24, 10);//计算剩余的小时数
    var mm = parseInt(ts / 1000 / 60 % 60, 10);//计算剩余的分钟数
    var ss = parseInt(ts / 1000 % 60, 10);//计算剩余的秒数
    dd = checkTime(dd);
    hh = checkTime(hh);
    mm = checkTime(mm);
    ss = checkTime(ss);
    if (ts > 100800000 && ts < 136800000) {
        $(".poster_timer.tm1").text("敬请期待");
    } else if (ts < 100800000 && ts >= 86400000) {
        $(".poster_timer.tm1").text("剩余" + dd + "天" + hh + "时" + mm + "分" + ss + "秒");
        setTimeout(function () {
                tm_timer_today();
            },
            1000);
    } else if (ts < 86400000) {
        $(".poster_timer.tm1").text("剩余" + hh + "时" + mm + "分" + ss + "秒");
        setTimeout(function () {
                tm_timer_today();
            },
            1000);
    }
}
function tm_timer() {
    /*
     * 昨日海报特卖倒计时
     * auther:yann
     * date:2015/20/8
     */
    var ts = (new Date(today.getFullYear(), today.getMonth(), today.getDate(), 14, 0, 0)) - (new Date());//计算剩余的毫秒数
    var dd = parseInt(ts / 1000 / 60 / 60 / 24, 10);//计算剩余的天数
    var hh = parseInt(ts / 1000 / 60 / 60 % 24, 10);//计算剩余的小时数
    var mm = parseInt(ts / 1000 / 60 % 60, 10);//计算剩余的分钟数
    var ss = parseInt(ts / 1000 % 60, 10);//计算剩余的秒数
    dd = checkTime(dd);
    hh = checkTime(hh);
    mm = checkTime(mm);
    ss = checkTime(ss);
    console.log(dd, hh, mm, ss);
    if (ts >= 86400000) {
        $(".poster_timer.tm1").text("剩余" + dd + "天" + hh + "时" + mm + "分" + ss + "秒");
        setTimeout(function () {
                tm_timer();
            },
            1000);
    } else if (ts < 86400000 && ts > 0) {
        $(".poster_timer.tm1").text("剩余" + hh + "时" + mm + "分" + ss + "秒");
        setTimeout(function () {
                tm_timer();
            },
            1000);
    } else {
        $(".poster_timer.tm1").text("敬请期待");
    }
}
function checkTime(i) {
    if (i < 10) {
        i = "0" + i;
    }
    return i;
}

function Set_posters(suffix) {
    //获取海报
    var posterUrl = GLConfig.baseApiUrl + suffix;

    var posterCallBack = function (data) {
        if (!isNone(data.wem_posters)) {
            //设置女装海报链接及图片
            $.each(data.wem_posters,
                function (index, poster) {
                    $('.poster .nvzhuang').attr('href', poster.item_link);
                    $('.poster .nvzhuang img').attr('src', poster.pic_link + "?imageMogr2/format/jpg/quality/100");
                    if (poster.subject === 'undifine' || poster.subject === null) {
                        return
                    }
                    //$('.poster .nvzhuang .subject').html('<span class="tips">'+poster.subject[0]+'</span>'+poster.subject[1]);
                }
            );
        }

        if (!isNone(data.chd_posters)) {
            //设置童装海报链接及图片
            $.each(data.chd_posters,
                function (index, poster) {
                    $('.poster .chaotong').attr('href', poster.item_link);
                    $('.poster .chaotong img').attr('src', poster.pic_link + "?imageMogr2/format/jpg/quality/100");
                    if (poster.subject === 'undifine' || poster.subject === null) {
                        return
                    }
                    //$('.poster .chaotong .subject').html('<span class="tips">'+poster.subject[0]+'</span>'+poster.subject[1]);
                }
            );
        }
    };
    // 请求海报数据
    $.ajax({
        type: 'get',
        url: posterUrl,
        data: {},
        dataType: 'json',
        success: posterCallBack
    });
}
function preview_verify(verify, id, dom, model_id) {
    console.log("预览审核产品id:", id);
    console.log("预览审核产品款式:", model_id);
    if (verify == false)//如果审核状态不是true,即没有审核，或者被修改状态
    {
        var redom = $(dom).append('<img id="previev_vierify_'+id+'" src="images/tuihuo-jujue.png" width="32px" onclick="verify_categray(' + id + ',' + model_id +')"/>');
    }
    else {
        redom = $(dom).append('<img id="previev_vierify_'+id+'" src="images/icon-ok.png" width="32px" onclick="verify_categray(' + id + ',' + model_id +')"/>');
    }
    return redom
}

function verify_categray(id, model_id) {
    console.log("product id:", id, "model_id",model_id);
    //判断是否存在多款，model_id
    // 如果在同款页面则不去判断是否跳转
    var current_url = window.location.href.split('?')[0].split("/");
    if (current_url[current_url.length - 1] == "tongkuan-preview.html") {
        verify_action(id); //直接审核
    }
    else if (model_id != null) {//如果不是单款
        //跳转到同款页面
        window.location = "/static/wap/tongkuan-preview.html?id=" + model_id;
    }
    else {//是单款情况下则在当前页面去修改is_verify状态
        //调用接口
        verify_action(id);
    }
}
function verify_action(id) {
    console.log("action id: ",id);
    var data = {'csrfmiddlewaretoken': getCSRF()};
    console.log(id);
    var verifyurl = GLConfig.baseApiUrl + GLConfig.verify_product.template({"id": id});
    console.log("verifyurl:", verifyurl);
    $.ajax({
        "url": verifyurl,
        "data": data,
        "type": "post",
        dataType: 'json',
        success: requetCall,
        error: function (resp) {
            if (resp.status == 403) {
                // 跳转到登陆
                var redirectUrl = window.location.href;
                window.location = GLConfig.login_url + '?next=' + encodeURIComponent(redirectUrl);
            }
        }
    });
    function requetCall(res) {
        console.log("debug preview :", res);
        var png = $("#previev_vierify_"+id).attr("src").split("/")[1];
        if(png=="icon-ok.png"){//切换图标
            $("#previev_vierify_"+id).attr("src","images/tuihuo-jujue.png");
        }
        else if(png=="tuihuo-jujue.png"){
            $("#previev_vierify_"+id).attr("src","images/icon-ok.png");
        }

    }
}

function Create_item_dom(p_obj, close_model) {

    //创建商品DOM
    function Item_dom() {
        /*
         <li>
         <a href="pages/shangpinxq.html?id={{ id }}">
         <img src="{{ head_img }}?imageMogr2/thumbnail/289x289/format/jpg/quality/85">
         <p class="gname">{{ name }}</p>
         <p class="gprice">
         <span class="nprice"><em>¥</em> {{ agent_price }} </span>
         <s class="oprice"><em>¥</em> {{ std_sale_price }}</s>
         </p>{{ saleout_dom }}
         </a>
         </li>
         */
    };

    //创建商品款式DOM
    function Model_dom() {
        /*
         <li>
         <a href="tongkuan.html?id={{ product_model.id }}">
         <img src="{{ product_model.head_img }}?imageMogr2/thumbnail/289x289/format/jpg/quality/85">
         <p class="gname">{{ product_model.name }}</p>
         <p class="gprice">
         <span class="nprice"><em>¥</em> {{ agent_price }} </span>
         <s class="oprice"><em>¥</em> {{ std_sale_price }}</s>
         </p>{{ saleout_dom }}
         </a>
         </li>
         */
    };

    p_obj.saleout_dom = '';
    var today = new Date().Format("yyyy-MM-dd");

    //如果没有close model,并且model_product存在
    if (!close_model && !isNone(p_obj.product_model)) {
        if (!p_obj.is_saleopen) {
            if (p_obj.sale_time >= today) {
                p_obj.saleout_dom = '<div class="mask"></div><div class="text">即将开售</div>';
            } else {
                p_obj.saleout_dom = '<div class="mask"></div><div class="text">已抢光</div>';
            }
        }
        p_obj.product_model.head_img = p_obj.product_model.head_imgs[0]
        return hereDoc(Model_dom).template(p_obj);
    }

    //上架判断
    if (!p_obj.is_saleopen) {
        if (p_obj.sale_time >= today) {
            p_obj.saleout_dom = '<div class="mask"></div><div class="text">即将开售</div>';
        } else {
            p_obj.saleout_dom = '<div class="mask"></div><div class="text">已抢光</div>';
        }
    } else if (p_obj.is_saleout) {
        p_obj.saleout_dom = '<div class="mask"></div><div class="text">已抢光</div>';
    }
    if (close_model && true) {
        p_obj.head_img = p_obj.pic_path;
    }
    return hereDoc(Item_dom).template(p_obj);
}

function Set_promotes_product(suffix) {
    //获取今日推荐商品
    var promoteUrl = GLConfig.baseApiUrl + suffix;

    var promoteCallBack = function (data) {
        console.log("debug data :", data);
        $("#loading").hide();
        if (!isNone(data.female_list)) {

            $('.glist .nvzhuang').empty();
            //设置女装推荐链接及图片
            $.each(data.female_list,
                function (index, p_obj) {
                    var item_dom = Create_item_dom(p_obj);
                    item_dom = preview_verify(p_obj.is_verify, p_obj.id, item_dom, p_obj.model_id);
                    $('.glist .nvzhuang').append(item_dom);
                }
            );
        }

        if (!isNone(data.child_list)) {
            $('.glist .chaotong').empty();
            //设置童装推荐链接及图片
            $.each(data.child_list,
                function (index, p_obj) {
                    var item_dom = Create_item_dom(p_obj);
                    item_dom = preview_verify(p_obj.is_verify, p_obj.id, item_dom, p_obj.model_id);
                    $('.glist .chaotong').append(item_dom);
                }
            );
        }
    };
    // 请求推荐数据
    $.ajax({
        type: 'get',
        url: promoteUrl,
        data: {},
        dataType: 'json',
        beforeSend: function () {
            $("#loading").show();
        },
        success: promoteCallBack
    });

}

function Set_category_product(suffix) {
    //获取潮流童装商品
    var promoteUrl = GLConfig.baseApiUrl + suffix;

    var promoteCallBack = function (data) {
        if (!isNone(data.results)) {
            $("#loading").hide();
            //设置女装推荐链接及图片
            $.each(data.results,
                function (index, p_obj) {
                    var item_dom = Create_item_dom(p_obj, false);
                    $('.glist').append(item_dom);
                }
            );
        }
    };
    // 请求推荐数据
    $.ajax({
        type: 'get',
        url: promoteUrl,
        data: {},
        dataType: 'json',
        beforeSend: function () {
            $("#loading").show();
        },
        success: promoteCallBack
    });

}

function Set_model_product(suffix) {
    //获取同款式商品列表
    console.log("同款商品");
    var promoteUrl = GLConfig.baseApiUrl + suffix;

    var promoteCallBack = function (data) {
        $("#loading").hide();
        //设置女装推荐链接及图片

        $.each(data,
            function (index, p_obj) {
                var item_dom = Create_item_dom(p_obj, true);
                item_dom = preview_verify(p_obj.is_verify, p_obj.id, item_dom, p_obj.model_id);
                $('.glist').append(item_dom);
            }
        );
        if (data && data.length > 0 && data[0].sale_time) {
            var shelf_time = new Date(data[0].sale_time);
            product_timer(shelf_time);
        }
    };
    // 请求推荐数据
    $.ajax({
        type: 'get',
        url: promoteUrl,
        data: {},
        dataType: 'json',
        beforeSend: function () {
            $("#loading").show();
        },
        success: promoteCallBack
    });

}

function product_timer(shelf_time) {
    /*
     * 商品倒计时
     * auther:yann
     * date:2015/15/8
     */
    var ts = (new Date(shelf_time.getFullYear(), shelf_time.getMonth(), shelf_time.getDate() + 1, 14, 0, 0)) - (new Date());//计算剩余的毫秒数

    var dd = parseInt(ts / 1000 / 60 / 60 / 24, 10);//计算剩余的天数
    var hh = parseInt(ts / 1000 / 60 / 60 % 24, 10);//计算剩余的小时数
    var mm = parseInt(ts / 1000 / 60 % 60, 10);//计算剩余的分钟数
    var ss = parseInt(ts / 1000 % 60, 10);//计算剩余的秒数
    dd = checkTime(dd);
    hh = checkTime(hh);
    mm = checkTime(mm);
    ss = checkTime(ss);

    if (ts > 100800000 && ts < 136800000) {
        $(".top p").text("敬请期待");
    } else if (ts < 100800000 && ts >= 86400000) {
        $(".top p").text("剩余" + dd + "天" + hh + "时" + mm + "分");
        setTimeout(function () {
                product_timer(shelf_time);
            },
            2000);
    } else if (ts < 86400000 && ts > 0) {
        $(".top p").text("剩余" + hh + "时" + mm + "分");
        setTimeout(function () {
                product_timer(shelf_time);
            },
            2000);
    } else if (ts < 0) {
        $(".top p").text("已下架");
    }

}

/*
 * 时间格式化
 * auther:yann
 * date:2015/22/8
 */
Date.prototype.Format = function (fmt) {
    var o = {
        "M+": this.getMonth() + 1, //月份
        "d+": this.getDate(), //日
        "h+": this.getHours(), //小时
        "m+": this.getMinutes(), //分
        "s+": this.getSeconds(), //秒
        "q+": Math.floor((this.getMonth() + 3) / 3), //季度
        "S": this.getMilliseconds() //毫秒
    };
    if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    for (var k in o)
        if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
    return fmt;
}


function need_set_info() {
    //获取设置帐号的信息
    var requestUrl = GLConfig.baseApiUrl + "/users/need_set_info";

    var requestCallBack = function (res) {
        var result = res.result;
        if (result == "yes") {
            $(".p-center").append('<span class="center-red-dot"></span>');
        }
    };
    // 请求推荐数据
    $.ajax({
        type: 'get',
        url: requestUrl,
        data: {},
        dataType: 'json',
        success: requestCallBack
    });
}