$(document).ready(function() {
	var $addImg = $('.act-0405-add img');
	var $addBkg = $('.act-0405-add');
	//倒计时
	var timer = function(intDiff) {
			window.setInterval(function() {
				var day = 00,
					hour = 00,
					minute = 00,
					second = 00;

				//时间默认值		
				if (intDiff > 0) {
					day = Math.floor(intDiff / (60 * 60 * 24));
					hour = Math.floor(intDiff / (60 * 60)) - (day * 24);
					minute = Math.floor(intDiff / 60) - (day * 24 * 60) - (hour * 60);
					second = Math.floor(intDiff) - (day * 24 * 60 * 60) - (hour * 60 * 60) - (minute * 60);
				}
				if (day <= 9) day = '0' + day;
				if (hour <= 9) hour = '0' + hour;
				if (minute <= 9) minute = '0' + minute;
				if (second <= 9) second = '0' + second;
				$('#day_show').html(day);
				$('#hour_show').html('<s id="h"></s>' + hour);
				$('#minute_show').html('<s></s>' + minute);
				$('#second_show').html('<s></s>' + second);
				intDiff--;
			}, 1000);
		}
		//add activity
	var add = function() {
		var $addImg = $('.act-0405-add img');
		var celNum = $('input').val();
		if ($addImg.hasClass('act-0405-add-img')) {
			$addImg.removeClass('act-0405-add-img').addClass('act-0405-added-img');
			$.ajax({
				data: {
					'mobile': celNum
				},
				type: 'post',
				url: 'http://m.xiaolumeimei.com/sale/promotion/apply/3/',
				success: function(res) {
					console.log(res);
					if (res.rcode == 0) {
						if (res.next == 'download') {
							window.location.href = '../html/act-0405-2.html';
						} else if (res.next == 'mainpage') {
							window.location.href = '../html/act-0405-3.html';
						} else if (res.next == 'snsauth') {
							window.location.href = '/sale/promotion/weixin_snsauth_join/3/';
						}

					} else {
						$addImg.removeClass('act-0405-added-img').addClass('act-0405-add-img');
						$('input').val('');
						$('input')[0]['placeholder'] = '请重新输入';
					}
				}
			});
		}
	};

	var requestData = function() {
		var end_time, current_time, rest_time;
		$.ajax({
			type: 'GET',
			url: 'http://m.xiaolumeimei.com/sale/promotion/apply/3/',
			success: function(res) {
				//set rest time of activity
				end_time = (new Date(res.end_time)).getTime();
				current_time = (new Date()).getTime();
				rest_time = parseInt((end_time - current_time) / 1000);
				console.log('end_time:' + end_time);
				console.log('current_time:' + current_time);
				timer(rest_time);
				//cellNumber input
				var $cellNum = $('.act-0405-celNumber');
				if (res.mobile_required && $cellNum.hasClass('act-0405-hide')) {
					$cellNum.removeClass('act-0405-hide');
				}
				//show customer img
				if (res.img == '') {
					$('.act-0405-beInvited').addClass('act-0405-hide');
				} else {
					$('.act-0405-beInvited img')[0].src = res.img;
				}
			},
			error: function(res) {
				console.log(res);
				$('input')[0]['placeholder'] = '请重新输入';
			}
		});
	};
	requestData();
	$addImg.bind('click', add);
	$addBkg.bind('click', add);
});