def getHeader():
    header = """
    <script src="../js/jquery-1.7.1.min.js"></script>
    <script src="../js/util.js"></script>
    <form id="mturk_form" method="POST" style="display:none">
         <input id="folder" name="folder" value="">
         <input id="file_id" name="file_id" value="">
         <input id="ans" name="ans">
    </form>
    """
    return header

def getSubmission():
    sub = """
    $("#sub").click(function(){
        console.log('shot:'+shot_selection);
        /*
        ans_out = $("#shot").val();
        document.getElementById("ans").value = 'var shot_start_str="'+ans_out+'";var shot_selection_str="'+shot_selection+'"';
        document.getElementById("folder").value = get_js_name(false);
        tmp = $.post("../../save_ans.php", $("#mturk_form").serialize(), function(data) {
            window.location=window.location.href.substring(0, window.location.href.lastIndexOf("/"));
        });
        */
  });
    """
    return sub

def getImageLoader(frame_template, func_name='getImName'):
    tmp = frame_template.split('%')
    frame_prefix = tmp[0]
    frame_digit = int(tmp[1][:tmp[1].find('d')])
    frame_suffix = tmp[1][tmp[1].find('d')+1:]

    html = """
    var im_prefix = "%s";
    var im_suffix = "%s";
    var im_prefix_url = getUrlParam('pref');
    var im_suffix_url = getUrlParam('suf');
    if (im_prefix_url.length > 0){
        im_prefix = im_prefix_url;
    }
    if (im_suffix_url.length > 0){
        im_suffix = im_suffix_url;
    }
    $("#prefix").val(im_prefix)
    $("#suffix").val(im_suffix)
    
    """ % (frame_prefix, frame_suffix)
    html += """
    function getImName(i){
        var im_id = frame_offset + (i * fps);
    """
    html += 'var fn = im_prefix+printf%dd(im_id)'%frame_digit + '+im_suffix;'
    html += """
        return fn;
    }
    """
    return html

def getImageDisplay(frame_template, frame_num, frame_fps, frame_offset, js_file, var_name, func_name='getImName'):
    html = ''
    html += 'var num = ' + str(frame_num) + ';'
    html += 'var fps = ' + str(frame_fps) + ';'
    html += 'var frame_offset = ' + str(frame_offset) + ';'

    html += """
    function loadJs_cb(){
        $('#result').val(%s)
        // read from js file
        update_value(%s, shot_selection_str);
    }
    """%(var_name, var_name)

    html += 'loadJs("'+ js_file + '", loadJs_cb)'

    html += getImageLoader(frame_template, func_name)
    return html

def getHtmlCluster(frame_template, frame_num, frame_fps, frame_offset, js_file):
    var_name = 'shot_index_str' 
    html = getHeader()
    # html display
    html += """
    Shot starting IDs: <textarea id="result" cols=50 rows=10></textarea> (separated by comma)
    <br/>
    <button id="sub" style="width:400;height=200">Done</button>
    <div id="img"></div>
    """

    html += """
    <script>
    var %s = '';
    var shot_selection = [0];""" % var_name

    html += getImageDisplay(frame_template, frame_num, frame_fps, frame_offset, js_file, var_name)

    html += """
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
                if (j % numCol == 0){
                    out += '<tr>'
                }
                out += '<td>'+shot_index[i][j] + '<br/><img height=100 src="'+getImName(shot_index[i][j])+'"></td>'
                if ((j + 1) % numCol == 0){
                    out +='</tr>'
                }
            }
            if (cluster_len % numCol != 0){
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

    $("#result").change(function(){
        var tmp_index_str = $(this).val();
        var tmp_index = strToArray2(tmp_index_str);
        var tmp_start = tmp_index.map(x => x[0]);
        var shot_start = shot_index.map(x => x[0]);
        var shot_selection_str = updateArr(shot_start, shot_selection, tmp_start, '0');
        update_value(tmp_index_str, shot_selection_str);
    });
    """
    html += getSubmission()
    html += '</script>'

    return html 

def getHtmlShot(frame_template, frame_num, frame_fps, frame_offset, js_file):
    var_name = 'shot_start_str'
    html = getHeader()
    html += """
    Shot starting IDs: <textarea id="result" cols=50 rows=10></textarea> (separated by comma)
    <br/>
    Frame prefix: <textarea id="prefix" cols=50 rows=1></textarea> (e.g. refine_) <br/>
    Frame suffix: <textarea id="suffix" cols=50 rows=1></textarea> (e.g. _cluster)
    <button id="sub" style="width:400;height=200">Done</button>
    <div id="img"></div>
    """

    html += """
    <script>
    var %s = [0];
    var shot_selection = [0];"""% var_name


    html += getImageDisplay(frame_template, frame_num, frame_fps, frame_offset, js_file, var_name)

    html += """
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
                if ((j - shot_start[i]) % numCol == 0){
                    out += '<tr><td>'
                }
                out+='<img height=100 title="'+j+'" alt="'+j+'" src="'+getImName(j)+'">'
                if ((j - shot_start[i] + 1) % numCol == 0){
                    out +='</td></tr>'
                }
            }
            if ((lt - shot_start[i] + 1) % numCol != 0){
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

    function update_value(shot_start_str, shot_selection_str){
        shot_start = strToArray(shot_start_str);
        shot_selection = strToArray(shot_selection_str);
        update_display();
    }

    $("#result").change(function(){
        var shot_start_str = $(this).val();
        var shot_selection_str = updateArr(shot_start, shot_selection, strToArray(shot_start_str), '0');
        update_value(shot_start_str, shot_selection_str);
    });
    $("#prefix").change(function(){
        im_prefix = $(this).val();
        update_display();
    });
    $("#suffix").change(function(){
        im_sufix = $(this).val();
        update_display();
    });
    """
    html += getSubmission()
    html += '</script>'

    return html 

def getHtmlCharacter(video_names):
    html = getHeader()
    html += """
    Seg id 1-5: Color={blue, yellow, darkorange, magenta, cyan, yellowgreen}<br/>
    Number of Images: <textarea id="num_img" cols=10 rows=1> 5 </textarea>
    <div id="img"></div>
    """
    html += """
    <script>
    var num_img = 5;
    function update_display(){
        var seg_info = '';
        var seg_folder = '%s/';
        var seg_pref='r_'
        var video_name = '';
        var out=""
        out += "<table border=1>"
        var fn = ''
        var ind = '';
        var ind_step = 1;
        var video_id = 0;
    """
    for video_name in video_names:
        html += """
            video_name = "%s";
            seg_info = %s;
            fps = %d;
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

    html += """
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
    return html

def getVsvi(target_name, image_template, frame_ids_str, frame_size):
    vsvi = """{
      "ServerType": "imagetiles",

      "SourceFileNameTemplate": "%s",
      "SourceParamSequence": "s",
      "SourceMinS": 0,
      "SourceMaxS": 0,
      "SourceMinR": 1,
      "SourceMaxR": 1,
      "SourceMinC": 1,
      "SourceMaxC": 1,

      "MipMapFileNameTemplate": "%s",
      "MipMapParamSequence": "s",
      "SourceMinM": 0,
      "SourceMaxM": 0,
      "SourceTileSizeX": %d,
      "SourceTileSizeY": %d,
      "SourceBytesPerPixel": 3,
      "MissingImagePolicy": "nearest",
      "SourceSectionOrder": "%s",

      "TargetDataSizeX": %d,
      "TargetDataSizeY": %d,
      "TargetDataSizeZ": %d,
      "OffsetX": 0,
      "OffsetY": 0,
      "OffsetZ": 0,
      "OffsetMip": 0,
      "TargetVoxelSizeXnm": 4.000000,
      "TargetVoxelSizeYnm": 4.000000,
      "TargetVoxelSizeZnm": 4.000000,
      "TargetLayerName": "%s"
      }
    """ % (image_template, image_template, frame_size[0], frame_size[1], \
            frame_ids_str, frame_size[0], frame_size[1], frame_ids_str.count(',')+1, target_name)
    return vsvi
