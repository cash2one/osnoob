
//-------------------------------------------------------
$(document).ready(function(){
    var email = getCookie("visitor_email");
    var name = getCookie("visitor_name");
    $("#username").val(name);
    $("#email").val(email);

});

  // add tag
function add_tag(){
    $("#flash-c").empty();
    $("#flash-a").empty();
    $("#flash-s").empty();
    var tags = $('#tag').val();
    $.post("/api/post/add-tag",{tag:tags},function(data,status){
        if (data){
            $.each(data.tags,function(n,value){
                var lab = '<label 　id="'+value+'" style="color:#1AB667" class="btn btn-sm" >'
                           +'  <input id="boolean_l" name="boolean_l" type="checkbox" value="'
                           +value
                           +'"><i style="color:#1AB667" class="fa fa-check text-active"></i>'
                            +value
                          +'</label>';
                $("#tags").append(lab);
            });
            $('#tag').val('');
        }
        if(data.flash){
            $("#flash-a").text(data.flash.msg);

        }
    });
}

// del tag
function del_tag(){
    $("#flash-c").empty();
    $("#flash-a").empty();
    $("#flash-s").empty();
    var tags = '';
    $('.active input').each(function(index, element) {
		tags += $(this).val()+",";
		$("#"+$(this).val()).remove();
    });
    $.post("/api/post/del-tag",{tag:tags},function(data,status){
        if(data.flash){
            $("#flash-c").text(data.flash.msg);
        }else{
            $("#flash-s").text('删除成功!');
        }
    });
}

//show
function topay() {
    var sta = $('#pay').attr("style");
    if( sta == 'display="display";' || !sta){
        display="block";
        document.getElementsByClassName('pay')[0].style.display="block";
    }else{
        $('#pay').attr("style", 'display="display";');
    }
}

 function close_pay() {
    $('#pay').attr("style", 'display="display";');

}

function show_alipay() {

    $('#ali-img').show();
    $('#wechat-img').hide();
    $('#ali-i').attr("class", "fa fa-check-square-o");
    $('#wechat-i').attr("class", "fa fa-square-o");
}
function show_wechatpay() {

    $('#ali-img').hide();
    $('#wechat-img').show();
    $('#ali-i').attr("class", "fa fa-square-o");
    $('#wechat-i').attr("class", "fa fa-check-square-o");

}

