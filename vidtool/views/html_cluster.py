html_cluster = """
<script src="../../js/jquery-1.7.1.min.js"></script>
<script src="../../js/util.js"></script>
Shot starting IDs: <textarea id="shot" cols=120 rows=10></textarea> (separated by comma)
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
var video_name = "%s";
var genre_name = "./";
var video_url = video_name;
if (video_name.includes('/')){
    genre_name = video_name.substr(0, video_name.lastIndexOf('/'));
    video_url = video_name.substr(video_name.lastIndexOf('/') + 1);
}
var num = %d;

function loadJs_cb(){
    $('#shot').val(shot_index_str)
    update_value(shot_index_str, shot_selection_str);
}
loadJs('_cluster', loadJs_cb)


function getImName(i){
    var im_id = 1 + i;
    var fn = frame_folder + video_name + "/image_" + printf5d(im_id) + '.png';
    return fn
}

function update_display(){
    var out=""
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
                out += '<tr><td>'
            }
            out+='<img height=100 src="'+getImName(shot_index[i][j])+'">'
            if ((j + 1) %% numCol == 0){
                out +='</td></tr>'
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
    $("#img").html(out)

    $(".shot_sel").click(function() {
        var color_id = getNextColorId($(this)[0].style.backgroundColor, color_name_shot);
        $(this)[0].style.backgroundColor = color_name_shot[color_id];
        var row_id = parseInt($(this)[0].id.substr(1))
        shot_selection[row_id] = color_id;
    });
}

function update_value(shot_index_str, shot_selection_str){
    shot_index = strToArray2(shot_index_str);
    shot_selection = strToArray(shot_selection_str);
    update_display();
}

$("#shot").change(function(){
    var tmp_index_str = $(this).val();
    var tmp_index = strToArray2(tmp_index_str);
    var tmp_start = tmp_index.map(x => x[0]);
    var shot_start = shot_index.map(x => x[0]);
    var shot_selection_str = updateArr(shot_start, shot_selection, tmp_start, '0');

    update_value(tmp_index_str, shot_selection_str);

});


$("#sub").click(function(){
    //
    console.log(''+shot_selection)
    /*
    ans_out = $("#shot").val();
    document.getElementById("ans").value = 'var shot_index_str="'+ans_out+'";var shot_selection_str="'+shot_selection+'"';
    document.getElementById("folder").value = get_js_name(false);
    tmp = $.post("../../save_ans.php", $("#mturk_form").serialize(), function(data) {
        window.location=window.location.href.substring(0, window.location.href.lastIndexOf("/"));
    });
    */
  });
</script>
"""
