template_proofread_shot = """
<script src="../../jquery-1.7.1.min.js"></script>
Shot starting IDs: <textarea id="shot" cols=50 rows=10></textarea> (separated by comma)
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
var genre_name = "%s";
var video_name = "%s";
var num = %d;
var fps = %d;
var numCol = 6;
var color_name=["green","red","white"];

load_js()

function getImName(i){
    var im_id = 1 + (i * fps)
    var fn = "../../download/" + genre_name + "/" + video_name + "/image_";
    if(im_id<10){
        fn += '0000'+im_id;
    }else if(im_id<100){
        fn += '000'+im_id;
    }else if(im_id<1000){
        fn += '00'+im_id;
    }else if(im_id<10000){
        fn += '0'+im_id;
    }else{
        fn += im_id;
    }
    return fn + '.png'
}

function update(){
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
        out+='<tr><td id="t'+(i)+'" class="shot_sel" style="background-color:'+color_name[shot_selection[i]]+';">'+(i)+"</td><td>"+shot_start[i]+"-"+(lt)+"</td><td>"
        out+='<table>'
        for(j = shot_start[i]; j < lt + 1; j ++){
            if ((j - shot_start[i]) %% numCol == 0){
                out += '<tr><td>'
            }
            out+='<img height=100 src="'+getImName(j)+'">'
            if ((j - shot_start[i] + 1) %% numCol == 0){
                out +='</td></tr>'
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
         var bg_color = $(this)[0].style.backgroundColor;
        var color_id = color_name.indexOf(bg_color);
        color_id = (color_id + 1) %% (color_name.length);
        $(this)[0].style.backgroundColor = color_name[color_id];
        var row_id = parseInt($(this)[0].id.substr(1))
        shot_selection[row_id] = color_id;
    });
}

function strToArray(input_str){
    output_array = input_str.split(",");
    for (a in output_array){
        output_array[a] = parseInt(output_array[a]);
    }
    return output_array;
}

function update_shot_start(shot_start_str, shot_selection_str){
    shot_start = strToArray(shot_start_str);
    shot_selection = strToArray(shot_selection_str);
    update();
}

$("#shot").change(function(){
    var shot_start_str = $(this).val();
    var tmp_start = strToArray(shot_start_str);
    var tmp_id = -1;
    var shot_selection_str = "";

    for(a in tmp_start){
        tmp_id = shot_start.indexOf(tmp_start[a])
        if (tmp_id==-1){
            shot_selection_str += '0,'
        }else{
            shot_selection_str += (shot_selection[tmp_id] + ',');
         }
    }
    shot_selection_str = shot_selection_str.substr(0, shot_selection_str.length-1);
    update_shot_start(shot_start_str, shot_selection_str);
});

// init
function get_js_name(same_folder){
    var out = video_name + '_shot.js';
    if (! same_folder){
        out = genre_name + '/saved/' + out
    } else {
        out = '../saved/' + out
    }
    return out;
}
function load_js(){
    var filename = get_js_name(true); 
    $.get(filename).done(function(){
        $.getScript(filename, function(){
            $('#shot').val(shot_start_str)
            update_shot_start(shot_start_str, shot_selection_str);
        });
     }).fail(function(){
        alert("can't find file: " + filename)
     })
}
 function get_selection() {
    for (var i = 0; i < shot_selection.length; ++ i) {      
        var bg_color = $("#t"+i)[0].style.backgroundColor
        shot_selection[i] = color_name.indexOf(bg_color);
    }
  }
$("#sub").click(function(){
    //
    ans_out = $("#shot").val();
    get_selection();
    document.getElementById("ans").value = 'var shot_start_str="'+ans_out+'";var shot_selection_str="'+shot_selection+'"';
    document.getElementById("folder").value = get_js_name(false);
    tmp = $.post("../../save_ans.php", $("#mturk_form").serialize(), function(data) {
        window.location='http://140.247.107.50/donglai/movie/';
        });
  });
</script>
"""
