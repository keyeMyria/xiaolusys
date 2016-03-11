/**
 * Created by jishu_linjie on 4/1/16.
 */

var nextReferalPage = GLConfig.agency_invitation_res;

function createInvitationListDom(obj) {
    var invitation = $("#invitation-res-template").html();
    return hereDoc(invitation).template(obj)
}

var testClickCount = 0;
$(document).ready(function () {
    getMamaInvitationRes();
    $(window).scroll(function () {
        loadData(getMamaInvitationRes);// 更具页面下拉情况来加载数据
    });
    getMamaFuturn()
    var a = window.screen.height;
    var b = window.screen.width;
    $(".invitation-bg").click(function () {
        testClickCount = testClickCount + 1;
        console.log("click time:", testClickCount);
        if (testClickCount >= 8) {
            alert(window.devicePixelRatio);
            alert(a);
            alert(b);
        }
    });

});

function getMamaFuturn() {
    var url = GLConfig.get_mama_fortune;
    $.ajax({
        "url": url,
        "type": 'get',
        "success": futurnCallBack,
        "csrfmiddlewaretoken": csrftoken
    });

    function futurnCallBack(res) {
        console.log(res.mama_fortune);
        var level = res.mama_fortune.mama_level;
        if (level == 1) {
            $(".invitation-class-gold").addClass('active');
        }
        if (level == 2) {
            $(".invitation-class-diamond").addClass('active');
        }
        if (level == 3) {
            $(".invitation-class-crown").addClass('active');
        }
        if (level == 4) {
            $(".invitation-class-gold-crown").addClass('active');
        }
    }
}

function getMamaInvitationRes() {
    var url = nextReferalPage;
    if (url == null) {
        //drawToast('~');
        return
    }
    var body = $(".invited-friends-list");

    if (body.hasClass('loading')) {// 如果没有返回则　return
        return
    }

    body.addClass('loading');
    $.ajax({
        "url": url,
        "type": 'get',
        "success": callback,
        "csrfmiddlewaretoken": csrftoken
    });
    function callback(res) {
        console.log('res:', res);
        body.removeClass('loading');
        nextReferalPage = res.next;
        var num1 = parseInt(res.count / 100);
        var num2 = parseInt(res.count / 10) % 10;
        var num3 = res.count % 10;
        $("#invitation-num-1").html(num1);//百位数
        $("#invitation-num-2").html(num2);//十位数
        $("#invitation-num-3").html(num3);//个位数
        $.each(res.results, function (i, invitation) {
            if (invitation.referal_to_mama_img == '') {
                invitation.referal_to_mama_img = 'http://7xogkj.com2.z0.glb.qiniucdn.com/1181123466.jpg'
            }
            var head = createInvitationListDom(invitation);
            $('.invited-friends-list').append(head);
        });

    }
}

function loadData(func) {//动态加载数据
    var totalheight = parseFloat($(window).height()) + parseFloat($(window).scrollTop()); //浏览器的高度加上滚动条的高度
    var scroll_height = $(document).height() - totalheight;
    if ($(document).height() - 600 <= totalheight && scroll_height < 600) //当文档的高度小于或者等于总的高度的时候，开始动态加载数据
    {
        func();
    }
}
