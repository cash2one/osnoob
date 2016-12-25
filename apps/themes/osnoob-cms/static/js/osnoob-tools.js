
function getUrlParam(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)"); //构造一个含有目标参数的正则表达式对象
    var r = window.location.search.substr(1).match(reg);  //匹配目标参数
    if (r != null) return unescape(r[2]); return null; //返回参数值
}

function get_vercode(){
    $.get("/api/get-vercode",function(data,status){
       var url = '/static/'+data.url;
        $("#code-img").attr("src", url);
        $("#code-url").attr("value", data.url);
    });
}