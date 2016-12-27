//-------------------------------------------------------
$(document).ready(function(){

    //时间处理
    $('[unix-time-s]').each(function()
    {
        var time = parseInt($(this).attr('value'));
        var d　=　new Date(time*1000);　//事物日期
        var dat = '';
        var year= d.getFullYear();
        var mon = d.getMonth()+1;
        if (mon < 10){
            mon = '0'+mon;
        }
        var day = d.getDate();
        var h =d.getHours();
        if (h < 10){
            h = "0"+h
        }
        var min=d.getMinutes();
        if (min < 10){
            min = "0"+min
        }
        dat = year + '-' + mon + '-' + day + ' ' + h + ':' + min;
        $(this).text(dat);

    });
});