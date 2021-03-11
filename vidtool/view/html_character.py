html_character_header = """
<script src="../../js/jquery-1.7.1.min.js"></script>
<script src="../../js/util.js"></script>

Number of Images: <textarea id="num_img" cols=10 rows=1> 5 </textarea>
<div id="img"></div>

<script>
var num_img = 5;

function update_display(){
    var seg_info = '';
    var seg_folder = '%s/';
    var video_name = '';
    var out=""
    out += "<table border=1>"
    var fn = ''
    var ind = '';
    var ind_step = 1;
    var video_id = 0;
    var seg_pref='stm_'
"""

html_character_body = """
    video_name = "%s";
    seg_info = %s;
    fps = %d;
    seg_pref = "/%s";
    out += "<tr><td>"+video_id+'. '+video_name+"</td><td colspan=" + num_img + ">images</td></tr>"
    for(var i = 0;i < seg_info.length; i ++){
        if( seg_info[i].length-1 < num_img){
            ind = seg_info[i].splice(1);
        }else{
            ind_step = (seg_info[i].length-1-1) / (num_img - 1);
            ind = Array(num_img);
            for(var j = 0; j < num_img; j++){
                ind[j] = seg_info[i][1+parseInt(ind_step *j)]
            }
        }
        out += '<tr><td>'+seg_info[i][0]+'</td>'
        for(var j = 0; j < ind.length; j ++){
            fn = seg_folder + video_name + seg_pref + printf5d(1 + (ind[j] * fps)) + '.png';
            out += '<td><img height=100 src="'+fn+'">' 
            out += '</td>'
        }
        out += '</tr>'
    }
    video_id += 1;

"""

html_character_footer = """
    out += "</table>"
    $("#img").html(out)
}

$("#num_img").change(function(){
    num_img = $(this).val();
    update_display();
});

update_display();
</script>
"""
