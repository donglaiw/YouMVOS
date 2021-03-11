html_seg = """
<script src="../../js/jquery-1.7.1.min.js"></script>
<script src="../../js/util.js"></script>
Shot starting IDs: <textarea id="shot" cols=50 rows=10></textarea> (separated by comma)
<br/>
fps: <textarea id="fps" cols=2 rows=1></textarea> (e.g. 25) <br/>
Mask prefix: <textarea id="prefix" cols=50 rows=1></textarea> (e.g. refine_) <br/>
Keyframe suffix: <textarea id="suffix" cols=50 rows=1></textarea> (e.g. _cluster)
<br/>
<button id="sub" style="width:400;height=200">Done</button>

<div id="img"></div>

<form id="mturk_form" method="POST" style="display:none">
     <input id="folder" name="folder" value="">
     <input id="file_id" name="file_id" value="">
     <input id="ans" name="ans">
</form>
<script>
var shot_index = [0];
var shot_selection = [0];
var frame_folder = "%s";
var seg_folder = "%s";
var video_name = "%s";
var overlay_id = [%s];
var num_frames = %d;
var seg_prefix = "%s";
var seg_suffix = "%s";
var fps = %d;

// get prefix from url
var seg_prefix_url = getUrlParam('pref');
if (seg_prefix_url.length > 0){
    seg_prefix = seg_prefix_url;
}
var seg_suffix_url = getUrlParam('suf');
if (seg_suffix_url.length > 0){
    seg_suffix = seg_suffix_url;
}
var fps_url = getUrlParam('fps');
if (fps_url.length > 0){
    fps = fps_url;
}

$("#prefix").val(seg_prefix)
$("#suffix").val(seg_suffix)
$("#fps").val(fps)

var genre_name = "./";
var bad_seg = [];
var bad_shot = [];
var video_url = video_name;
if (video_name.includes('/')){
    genre_name = video_name.substr(0, video_name.lastIndexOf('/'));
    video_url = video_name.substr(video_name.lastIndexOf('/') + 1);
}

var shot_index_str="";


// init
function loadJs_cb(){
    if(shot_index_str==""){
        $('#shot').val(shot_start_str)
        update_value(shot_start_str, shot_selection_str);
    }else{
        $('#shot').val(shot_index_str)
        update_value(shot_index_str, shot_selection_str);
    }
}
loadJs(seg_suffix, loadJs_cb)

// shot index: 0 - K
// original index: shot*fps +1
function getIndex(i, scale){
    return 1 + (i * scale);
}
function getMaskName(i, scale){
    var fn = seg_folder + video_name + "/" + seg_prefix + printf5d(getIndex(i, scale)) + '.png';
    return fn;
}

function getImName(i, scale){
    var fn = frame_folder + video_name + "/image_" + printf5d(getIndex(i, scale)) + '.png';
    return fn;
}

function update_display(){
    var num_frames_dsp = Math.ceil(num_frames / fps)
    var out=""
    // do shot display
    if(shot_index_str==""){
        out += "<table border=1>"
        out += '<thead style="display:block;">'
        out += "<tr><td>shot ID</td><td>frame ID</td><td>images</td></tr>"
        out += "</thead>"
        out += '<tbody style="display:block;height:1300px;overflow-y:auto">'
        var lt = 1;
        for(i = 0;i < shot_index.length; i ++){
            if(i == shot_index.length - 1){
                lt = num_frames_dsp - 1;
            }else{
                lt = shot_index[i+1] - 1
            }
            out+='<tr><td id="t'+(i)+'" class="shot_sel" style="background-color:'+color_name_shot[shot_selection[i]]+';">'+(i)+"</td><td>"+shot_index[i]+"-"+(lt)+"</td><td>"
            out+='<table>'
            for(j = shot_index[i]; j < lt + 1; j ++){
                if ((j - shot_index[i]) %% numCol == 0){
                    out += '<tr>'
                }
                out+='<td class="mask" style="padding:6px;background-color:white" id="i'+j+'">'
                if(overlay_id.includes(getIndex(j, fps))){
                //if(true){
                    //out += '<img height=100 src="'+ loadImage(getMaskName(j, fps), getImName(j, fps))+'">' 
                    out += '<img height=100 src="'+getMaskName(j, fps)+'">'
                }else{
                    out += '<img height=100 src="'+getImName(j, fps)+'">'
                }
                out += '</td>'
                if ((j - shot_index[i] + 1) %% numCol == 0){
                    out +='</tr>'
                }
            }
            if ((lt - shot_index[i] + 1) %% numCol != 0){
                out += '</td></tr>'
            }
            out += '</table>'
            out += "</td></tr>"
        }
        out += "</tbody>"
        out += "</table>"
    }else{
        out += "<table border=1>"
        out += '<thead style="display:block;">'
        out += "<tr><td>shot ID</td><td>frame ID</td><td>images</td></tr>"
        out += "</thead>"
        out += '<tbody style="display:block;height:1300px;overflow-y:auto">'
        var lt = 1;
        for(i = 0;i < shot_index.length; i ++){
            out+='<tr><td id="t'+(i)+'" class="shot_sel" style="background-color:'+color_name_shot[shot_selection[i]]+';">cluster '+(i)+"</td><td>"+shot_index[i][0]+'-'+shot_index[i][shot_index[i].length-1]+"</td><td>"
            out+='<table>'
            var cluster_len = shot_index[i].length;
            for(var j = 0; j < cluster_len; j ++){
                if (j %% numCol == 0){
                    out += '<tr>'
                }
                out += '<td>'+shot_index[i][j] + '<br/>'
                if(overlay_id.includes(getIndex(shot_index[i][j], fps))){
                //if(true){
                    //out += '<img height=100 src="'+ loadImage(getMaskName(shot_index[i][j], fps), getImName(shot_index[i][j], fps))+'">' 
                    out += '<img height=100 src="'+getMaskName(shot_index[i][j], fps)+'">'
                }else{
                    out += '<img height=100 src="'+getImName(shot_index[i][j], fps)+'">'
                }
                out += '</td>'

                if ((j + 1) %% numCol == 0){
                    out +='</tr>'
                }
            }
            if (cluster_len %% numCol != 0){
                out += '</td></tr>'
            }
            out += '</table>'
            out += "</td></tr>"
        }
        out += "</tbody>"
        out += "<table>"
    }
    $("#img").html(out)

    $(".shot_sel").click(function() {
        var color_id = getNextColorId($(this)[0].style.backgroundColor, color_name_shot);
        $(this)[0].style.backgroundColor = color_name_shot[color_id];
        var row_id = parseInt($(this)[0].id.substr(1))
        shot_selection[row_id] = color_id;
    });
       
    $(".mask").click(function() {
        var color = getNextColor($(this)[0].style.backgroundColor, color_name_seg);
        var seg_id = parseInt($(this)[0].id.substr(1))
        
        if (bad_seg.includes(seg_id)){
            bad_seg = bad_seg.filter(function(value, index, arr){ return value != seg_id;});
        }
        if (bad_shot.includes(seg_id)){
            bad_shot = bad_shot.filter(function(value, index, arr){ return value != seg_id;});
        }
        if(color=="red"){
           bad_seg.push(seg_id) 
        }else if(color=="green"){
           bad_shot.push(seg_id) 
        }
        $(this)[0].style.backgroundColor = color;
    });
}

function update_value(index_str, selection_str){
    if(shot_index_str == ""){
        // do shot
        shot_index = strToArray(index_str);
    }else{
        shot_index = strToArray2(index_str);
    }
    shot_selection = strToArray(selection_str);
    update_display();
}

$("#shot").change(function(){
    var index_str = $(this).val();
    var selection_str = updateArr(shot_index, shot_selection, strToArray(shot_index_str), '0');
    update_value(index_str, selection_str);
});

$("#prefix").change(function(){
    seg_prefix = $(this).val();
    update_display();
});

$("#fps").change(function(){
    fps = $(this).val();
    update_display();
});


$("#suffix").change(function(){
    seg_suffix = $(this).val();
    shot_index_str="";
    shot_start_str="";
    loadJs(seg_suffix, loadJs_cb)
});
$("#sub").click(function(){
    ans_out = $("#shot").val();
    console.log('bad-ids');
    console.log(bad_seg + ';' + bad_shot);
  });
</script>
"""
