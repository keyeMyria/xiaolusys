$(".category_select").live("change",function(e){
	e.preventDefault();
	console.log('abc');
	var target = e.target;
	var sid = target.getAttribute('sid');
	var cat_id = $(target).val();
	
	var url = "/supplychain/supplier/brand/"+sid+"/";
    var callback = function (res) {
      if (res.category.toString() == cat_id) {
          $(target).after("<img src='/static/admin/img/icon-yes.gif '>");
      }
    };
	
	var csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    var data = {"csrfmiddlewaretoken":csrf_token,
    					"format":"json",
    					"category":cat_id};
    					
    var headers = {
	    'X-HTTP-Method-Override': 'PATCH'
	   };

    $.ajax({"url":url,"data":data,"success":callback,"type":"POST","headers":headers });
});

$('.btn-charge').live('click',function(e){
	e.preventDefault();
	var target = e.target;
	var sid = target.getAttribute('sid');
	
	var url = "/supplychain/supplier/brand/charge/"+sid+"/";
        var callback = function (res) {
          if (res["success"] == true) {
              $(target).attr("href",res["brand_links"]).attr("target","_blank").text('查看商品').removeClass(' btn-charge btn-primary').addClass('btn-success');
          }else{
          	$(target).removeClass().addClass("btn btn-warning").text('接管失败');
          	$(target.parentElement.parentElement).slideUp(2000);
          }
        };
	
	var csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    var data = {"csrfmiddlewaretoken":csrf_token,
    					"format":"json"};

    $.ajax({"url":url,"data":data,"success":callback,"type":"POST" });
});

$('.status_select').live("change",function(e){
	e.preventDefault();
	var target = e.target;
	var pid = target.getAttribute('pid');
	var status = target.value;
	
	var url = "/supplychain/supplier/product/"+pid+"/";
    var callback = function (res) {
      if (res["status"] != "ignored") {
      	if (res["status"]=='淘汰' || res["status"]=='忽略'){
      		$(target.parentElement.parentElement).slideUp();
      	}else{
        	$(target).after("<img src='/static/admin/img/icon-yes.gif '>");
        }
      }
    };
	
	var csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    var data = {"status": status, 
				"csrfmiddlewaretoken":csrf_token,
				"format":"json"};
    
    var headers = {
	    'X-HTTP-Method-Override': 'PATCH'
	   };

    $.ajax({"url":url,"data":data,"success":callback,"type":"POST","headers":headers });
});


$(".sale_category_select").live("change",function(e){
    e.preventDefault();

    var target = e.target;
    var spid = target.getAttribute('spid');
    var cat_id = $(target).val();

    var url = "/supplychain/supplier/product/"+ spid +"/?format=json";
    var callback = function (res) {

     if (res.sale_category.toString() == cat_id) {
          $(target).after("<img src='/static/admin/img/icon-yes.gif '>");
        }
    };
    
    var csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    var data = {"csrfmiddlewaretoken":csrf_token,
                        "format":"json",
                        "sale_category":cat_id};
	
	var headers = {
	    'X-HTTP-Method-Override': 'PATCH'
	   };
	
    $.ajax({"url":url,"data":data,"success":callback,"type":"POST", "headers":headers});
});


$(function () {
	$(".select_saletime").datepicker({
	    dateFormat: "yy-mm-dd 00:00:00"
	}).change(function (e) {
	    var pid = this.id;
	    var sale_time = this.value;
		var url = "/supplychain/supplier/product/"+pid+"/";
	        var callback = function (res) {
	        	console.log('debug sale time:',res,sale_time);
	           if (res['sale_time'] == '' || res['sale_time'] == null){
	           		alert('上架排期失败');
	           		return
	           }
	           $(e.target).after("<img src='/static/admin/img/icon-yes.gif '>");
	        };
		
		var csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
	    var data = {"sale_time": sale_time, 
					"csrfmiddlewaretoken":csrf_token,
					"format":"json"};
	    
	    var headers = {
		    'X-HTTP-Method-Override': 'PATCH'
		   };
	
	    $.ajax({"url":url,"data":data,"success":callback,"type":"POST","headers":headers });
	});
});
