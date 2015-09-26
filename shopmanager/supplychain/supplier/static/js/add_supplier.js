jQuery(document).ready(function () {
    $('.submit_button').click(function () {
        var supplier_name = $('.supplier_name').val().trim();
        var supplier_code = $('.supplier_code').val().trim();
        var main_page = $('.main_page').val().trim();
        var category = $('#category').val().trim();
        var platform = $('#platform').val().trim();
        var progress = $('#progress').val().trim();
        var contact_name = $('#contact_name').val().trim();
        var mobile = $('#mobile').val().trim();
        var contact_address = $('#contact_address').val().trim();
        var note = $('#note').val().trim();

        if (supplier_name == '') {
            showtip("Tips", "供应商没有填写", "warning");
            return false;
        }
        if (contact_name == '') {
            showtip("Tips", "联系人没有填写", "warning");
            return false;
        }
        if (mobile == '') {
            showtip("Tips", "手机没有填写", "warning");
            return false;
        }
        if (contact_address == '') {
            showtip("Tips", "地址没有填写", "warning");
            return false;
        }
        $.ajax({
            type: 'post',
            url: "/supplychain/supplier/addsupplier/",
            data: {
                supplier_name: supplier_name,
                supplier_code: supplier_code,
                main_page: main_page,
                category: category,
                platform: platform,
                progress: progress,
                contact_name: contact_name,
                mobile: mobile,
                contact_address: contact_address,
                note: note
            },
            dataType: 'json',
            success: function (data) {
                swal({
                        title: "Tips",
                        text: "成功(^_^)",
                        type: "success",
                        showCancelButton: false,
                        confirmButtonText: "确定"
                    }, function () {
                        window.location = "/admin/supplier/salesupplier/?id=" + data.supplier_id;
                    });
            },
            error: function (data) {
                if (data.status == 403) {
                    swal({
                        title: "Tips",
                        text: "请先登录一下(^_^)",
                        type: "warning",
                        showCancelButton: false,
                        confirmButtonText: "确定"
                    }, function () {
                        window.location = "/admin";
                    });
                } else {
                    swal("Tips", "有错误，请联系技术人员(^_^)", "warning");
                }
            }
        });
    });
    $('.check_button').click(function () {
        var supplier_name = $('.supplier_name').val().trim();
        if (supplier_name == '') {
            showtip("Tips", "供应商没有填写", "warning");
            return false;
        }
        $.ajax({
            type: 'post',
            url: "/supplychain/supplier/checksupplier/",
            data: {"supplier_name": supplier_name},
            dataType: 'json',
            success: function (data) {
                var tb = $(".result-table")
                $(".result-table tr").remove();
                if (data.result == "0") {
                    tb.append("<tr><td>可以创建</td></tr>");
                }
                if (data.result == "10") {
                    $.each(data.supplier, function (index, dd) {
                        tb.append("<tr><td>" + dd + "</td></tr>");
                    });
                }
                if (data.result == "more") {
                    tb.append("<tr><td>超过10个包含关键字的供应商</td></tr>");
                }
            },
            error: function (data) {
                if (data.status == 403) {
                    swal({
                        title: "Tips",
                        text: "请先登录一下(^_^)",
                        type: "warning",
                        showCancelButton: false,
                        confirmButtonText: "确定"
                    }, function () {
                        window.location = "/admin";
                    });
                } else {
                    swal("Tips", "有错误，请联系技术人员(^_^)", "warning");
                }
            }
        });
    })
});

function showtip(title, text, type) {
    swal(title, text, type);
}