html_seg = """
<script src="../../js/jquery-1.7.1.min.js"></script>
<script src="../../js/util.js"></script>
Shot starting IDs: <textarea id="shot" cols=50 rows=10></textarea> (separated by comma)
<br/>
Mask prefix: <textarea id="prefix" cols=50 rows=1></textarea> (e.g. refine_)
<br/>
<button id="sub" style="width:400;height=200">Done</button>

<div id="img"></div>

<form id="mturk_form" method="POST" style="display:none">
     <input id="folder" name="folder" value="">
     <input id="file_id" name="file_id" value="">
     <input id="ans" name="ans">
</form>
<script>
var shot_start = [0];
var shot_selection = [0];
var frame_folder = "%s";
var mask_folder = "%s";
var mask_prefix = "%s";

var pid=parseInt();
// get prefix from url
var mask_prefix_url = getUrlParam('pref');
if (mask_prefix_url.length > 0){
    mask_prefix = mask_prefix_url;
}

$("#prefix").val(mask_prefix)
var video_name = "%s";
var overlay_id = [%s];
var genre_name = "./";
var bad_seg = [];
var video_url = video_name;
if (video_name.includes('/')){
    genre_name = video_name.substr(0, video_name.lastIndexOf('/'));
    video_url = video_name.substr(video_name.lastIndexOf('/') + 1);
}
var num = %d;
var fps = %d;

// init
function loadJs_cb(){
    $('#shot').val(shot_start_str)
    update_value(shot_start_str, shot_selection_str);
}
loadJs('_shot', loadJs_cb)

// shot index: 0 - K
// original index: shot*fps +1
function getIndex(i){
    return 1 + (i * fps);
}
function getMaskName(i){
    var fn = mask_folder + video_name + "/" + mask_prefix + printf5d(getIndex(i)) + '.png';
    return fn;
}

function getImName(i){
    var fn = frame_folder + video_name + "/image_" + printf5d(getIndex(i)) + '.png';
    return fn;
}

function update_display(){
    var out=""
    out += "<table border=1>"
    out += '<thead style="display:block;">'
    out += "<tr><td>shot ID</td><td>frame ID</td><td>images</td></tr>"
    out += "</thead>"
    out += '<tbody style="display:block;height:1300px;overflow-y:auto">'
    var lt = 1;
    for(i = 0;i < shot_start.length; i ++){
        if(i == shot_start.length - 1){
            lt = num - 1;
        }else{
            lt = shot_start[i+1] - 1
        }
        out+='<tr><td id="t'+(i)+'" class="shot_sel" style="background-color:'+color_name_shot[shot_selection[i]]+';">'+(i)+"</td><td>"+shot_start[i]+"-"+(lt)+"</td><td>"
        out+='<table>'
        for(j = shot_start[i]; j < lt + 1; j ++){
            if ((j - shot_start[i]) %% numCol == 0){
                out += '<tr>'
            }
            out+='<td class="mask" style="padding:6px;background-color:white" id="i'+j+'">'
            if(overlay_id.includes(getIndex(j))){
                out += '<img height=100 src="'+getMaskName(j)+'">' 
            }else{
                out += '<img height=100 src="'+getImName(j)+'">'
            }
            out += '</td>'
            if ((j - shot_start[i] + 1) %% numCol == 0){
                out +='</tr>'
            }
        }
        if ((lt - shot_start[i] + 1) %% numCol != 0){
            out += '</td></tr>'
        }
        out += '</table>'
        out += "</td></tr>"
    }
    out += "</tbody>"
    out += "<table>"
    $("#img").html(out)

    $(".shot_sel").click(function() {
        var color_id = getNextColorId($(this)[0].style.backgroundColor, color_name_shot);
        $(this)[0].style.backgroundColor = color_name_shot[color_id];
        var row_id = parseInt($(this)[0].id.substr(1))
        shot_selection[row_id] = color_id;
    });
       
    $(".mask").click(function() {
        var color = getNextColor($(this)[0].style.backgroundColor, color_name_seg);
        var mask_id = parseInt($(this)[0].id.substr(1))
        if(color=="red" && !bad_seg.includes(mask_id)){
           bad_seg.push(mask_id) 
        }else{
           bad_seg = bad_seg.filter(function(value, index, arr){ return value != mask_id;});
        }
        $(this)[0].style.backgroundColor = color;
    });
}

function update_value(shot_start_str, shot_selection_str){
    shot_start = strToArray(shot_start_str);
    shot_selection = strToArray(shot_selection_str);
    update_display();
}

$("#shot").change(function(){
    var shot_start_str = $(this).val();
    var shot_selection_str = updateArr(shot_start, shot_selection, strToArray(shot_start_str), '0');
    update_value(shot_start_str, shot_selection_str);
});

$("#prefix").change(function(){
    mask_prefix = $(this).val();
    update_display();
});

$("#sub").click(function(){
    ans_out = $("#shot").val();
    console.log('shot:'+shot_selection);
    console.log('bad-seg:'+bad_seg);
  });
</script>
"""
