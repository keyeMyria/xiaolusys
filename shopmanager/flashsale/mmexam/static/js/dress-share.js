
function listenWeixinShareEvent(configParams) {
    var imgUrl      = configParams.share_img;
    var lineLink    = configParams.share_link;
    var descContent = configParams.share_desc;
    var shareTitle  = configParams.share_title;
    var user_openid = configParams.openid;
    var signkey     = configParams.wx_singkey;
    var callbackUrl = configParams.callback_url;
    wx.config({
        debug: false,
        // 开启调试模式,调用的所有api的返回值会在客户端alert出来，若要查看传入的参数，可以在pc端打开，参数信息会通过log打出，仅在pc端时才会打印。
        appId: signkey.app_id,
        // 必填，公众号的唯一标识
        timestamp: signkey.timestamp,
        // 必填，生成签名的时间戳
        nonceStr: signkey.noncestr,
        // 必填，生成签名的随机串
        signature: signkey.signature,
        // 必填，签名，见附录1
        jsApiList: ["onMenuShareTimeline", "onMenuShareAppMessage", "onMenuShareQQ", "onMenuShareWeibo"] // 必填，需要使用的JS接口列表，所有JS接口列表见附录2
    });
    function shareCallback(share_type){
        $.post(callbackUrl, {
            share_type: share_type,
        }, function(res) {
            console.log('share resp:',res);
            if (res.is_sendenvelop == true){
                alert(res.info);
            }
        },'json');
    }
    wx.ready(function() {
        wx.onMenuShareAppMessage({
            title: shareTitle,
            // 分享标题
            desc: descContent,
            // 分享描述
            link: lineLink,
            // 分享链接
            imgUrl: imgUrl,
            // 分享图标
            type: 'link',
            // 分享类型,music、video或link，不填默认为link
            dataUrl: '',
            // 如果type是music或video，则要提供数据链接，默认为空
            success: function() {
                shareCallback('wxapp');
            },
            cancel: function() {
                console.log("取消分享");
            }
        });
        wx.onMenuShareTimeline({
            title: shareTitle,
            // 分享标题
            link: lineLink,
            // 分享链接
            imgUrl: imgUrl,
            // 分享图标
            type: 'link',
            success: function() {
                shareCallback('pyq');
            },
            cancel: function() {
                console.log("取消分享");
            },
            fail: function() {
                console.log("分享失败")
            }
        });
        wx.onMenuShareQQ({
            title: shareTitle,
            // 分享标题
            desc: descContent,
            // 分享描述
            link: lineLink,
            // 分享链接
            imgUrl: imgUrl,
            // 分享图标
            type: 'link',
            success: function() {
                shareCallback('qq');
            },
            cancel: function() {
                console.log("取消分享");
            },
            fail: function() {
                console.log("分享失败")
            }
        });
        wx.onMenuShareWeibo({
            title: shareTitle,
            // 分享标题
            desc: descContent,
            // 分享描述
            link: lineLink,
            // 分享链接
            imgUrl: imgUrl,
            // 分享图标
            type: 'link',
            success: function() {
                shareCallback('txwb');
            },
            cancel: function() {
                // 用户取消分享后执行的回调函数
            }
        });
    });
}