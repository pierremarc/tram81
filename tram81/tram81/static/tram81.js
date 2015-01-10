
$(document).ready(function(){
    function csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
//     _.extend($.ajaxSettings, {
//         crossDomain: false,
//     });
    
    $(document).on('ajaxBeforeSend', function(e, xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", '{{ csrf }}' );
            }
        });
    
    
    var hasHistory = false;
    
    $('#info_box').hide();
    $('#page').hide();
    
    (function prepapePages(undefined){
        var $pages = $('.page');
        $pages.each(function(idx, el){
            var $el = $(el);
            var content = $el.find('div.content');
            content.detach();
            
            $el.on('click', function(evt){
                if(content.hasClass('is_visible')){
                    content.removeClass('is_visible');
                    content.detach();
                }
                else{
                    content.addClass('is_visible');
                    content.appendTo('body');
                }
            });
            
            content.on('click', function(evt){
                content.removeClass('is_visible');
                content.detach();
            });
        });
    })();
    
    var panelIsVisible = false;
    var $map = $('#map');
    var map = L.map('map');
    L.tileLayer(window.T81.config.TILE_SERVER, {
        attribution: 'Me',
        maxZoom: 28
    }).addTo(map);

    var currentImage;

    var $mapPane = $('.leaflet-map-pane');
    map.on('moveend', function(){
        var transformString = $mapPane.css('transform');
        var matrix = function(a,b,c,d,e,f){
            var m = new Geom.Matrix;
            m.m[1][1] = a; m.m[1][2] = b;
            m.m[2][1] = c; m.m[2][2] = d;
            m.m[3][1] = e; m.m[3][2] = f;
            var t = new Geom.Transform;
            t.m = m;
            return t;
        }

        var transform = eval(transformString);
        if(currentImage){
            var imageCenter = map.latLngToContainerPoint(currentImage.getBounds().getCenter());
            var rot = reverseRotate(currentImage.data.rotation);
            // var bounds = map.getPixelBounds();
            // var mapSize = bounds.getSize();
            // // var rect = new Geom.Rect(rectOrigin.x, rectOrigin.y, mapSize.x, mapSize.y);
            // var rectOrigin = transform.getTranslate();
            // var deltaX = rectOrigin.x + (mapSize.x/2.0);
            // var deltaY = rectOrigin.y + (mapSize.y/2.0);
            // console.log('deltas', deltaX, deltaY);
            transform.resetTranslate(-imageCenter.x, -imageCenter.y);
            transform.rotate(rot);//, new Geom.Point(imageCenter.x, imageCenter.y));
            transform.translate(imageCenter.x, imageCenter.y);
            // transform.resetTranslate(deltaX, deltaY);
            console.log('moveend', transformString, transform.toString());
            // L.marker(map.layerPointToLatLng([deltaX,deltaY])).addTo(map);
        }

        window.setTimeout(function(){
            $mapPane.css('transform', 'matrix'+transform.toString());
        }, 300);
            
    });

    function reverseRotate(r){
        if(0 === r || 360 === r){ return 0; }
        return 360 - r;
    };

    
    function rotate(rot){
       
        $wrapper.css({
            'transform': 'rotate3d(0,0,1,'+rot+'deg)',
            // 'transform-origin':'0% 100%',
        });
    };

    
    
    function showPanel(){
        $('#pages').hide();
        var $info = $('#info_box');
        if(!panelIsVisible)
        {
            $info.css({opacity:'0'});
            $info.show();
            $info.animate({opacity:'1'},400);
        }
        panelIsVisible = true;
        return $info;
    };
    function hidePanel(){
        $('#pages').show();
        var $info = $('#info_box');
        if(panelIsVisible)
        {
            $info.animate({opacity:'0'},400, function(){
                $info.hide();
            });
        }
        panelIsVisible = false;
        return $info;
    };
    
    function px(i){
        return i + 'px';
    };
    
    var standard_style = {
                    fill:true,
                    fillOpacity:0.0,
                    stroke:false,
                    clickable:true,
                    };
    var highlight_style = {
                    fill:true,
                    fillOpacity:0.0,
                    stroke:true,
                    clickable:true,
                    weight:2,
                    color:'#FFF400',
                    };
                    
                    
    var commentHandled = {};
    function resetComments(pk, $comment){
        $comment.empty();
        document.title = document.title.split(' #').pop()  + ' #'+pk;
        $comment.load("/comments/"+pk);
        if(!commentHandled[pk])
        {
            $comment.on('click', '#nc', function sendComment(){
            var txt = $('#new_comment').val();
                var thread = pk;
                $.post(window.T81.config.NEW_COMMENT_URL, {txt:txt, thread:thread}, function(response){
                    resetComments(pk, $comment);
                });
            });
            commentHandled[pk] = true;
        }
        
        return $comment;
    };
    
    var global_images = [];
    function prepareLayers(data, idx){
        if(!data || !data.geo) return;
        var l = new L.geoJson(data.geo,{
            style: function (feature) {
                return standard_style;
            },
        });
        global_images.push(l);
        l.data = data;
        l.addTo(map);
        l.on('mouseover', function(evt){
            _.each(global_images, function(layer){
                layer.setStyle(standard_style);
            });
            l.setStyle(highlight_style);
        });
        l.on('click', function(evt){
            currentImage = this;
            if(window.T81.config.HAS_COMMENTS){
                var $info = $('#info_box');
                var ui = {
                    img_box: $('<div />').addClass('img_box'),
                    txt_box: $('<div />').addClass('txt_box'),
                };
                var txt = {
                    close: $('<div>×</div>').addClass('close_box'),
                    time: $('<div />').addClass('time_box'),
                    txt: $('<div />').addClass('txt'),
    //                 link: $('<div />').addClass('link_box'),
                 
                };
                
                var comment = resetComments(this.data.pub, $('<div />').addClass('cinner'));
                var img = $('<img />').addClass('img')
                img.attr('src', this.data.img_large_url);
                var link = $('<a />').attr('href', this.data.img_url).attr('target','_blank');
                link.append(img);
                
                txt.time.html('<a href="/'+this.data.pk+'">'+this.data.pub+'</a>');
                txt.txt.html(this.data.txt);
                txt.close.on('click',function(){
                    if(window.history && window.history.back) {
                        window.history.back();
                    }
                    else{
                        hidePanel();
                    }
                    
                });
                
                ui.img_box.append(link);
                $info.empty();
                $info.append(txt.time);
                $info.append(ui.img_box);
                $info.append(txt.close);
                if(window.history && window.history.pushState)
                {
                    hasHistory = true;
                    window.history.pushState( {}, '', 'i/' + this.data.pk);
                }
                showPanel();
            }
            else{ // no comments
            
                map.fitBounds(this.getBounds());
                if(window.history && window.history.pushState)
                {
                    hasHistory = true;
                    var bnds = this.getBounds();
                    var bounds = {
                        sw:[bnds.getSouth(), bnds.getWest()],
                        ne:[bnds.getNorth(), bnds.getEast()],
                    }
                    
                    window.history.pushState(
                        bounds,
                        this.data.img_url,
                        this.data.pk
                    );
                }
            }
        });
    };
    _.each(window.T81.data, prepareLayers);
    if(global_images.length > 0){
        var las_image = global_images[global_images.length -1].getBounds();
        var init_bounds = window.T81.default_bounds || las_image;
        map.whenReady(function(){
                window.setTimeout(function(){
                    map.fitBounds(init_bounds);
                }, 1000);
        });
    }
    map.setView([50.854075572144815, 4.38629150390625], 15);
    
    if(window.history && window.history.pushState)
    {
        
        window.onpopstate = function(evt){
            var state = evt.state;
            if(window.T81.config.HAS_COMMENTS){
                hidePanel();
            }
            else{
                if(state && state.sw && state.ne){
                    var bounds = L.latLngBounds(state.sw, state.ne);
                    map.fitBounds(bounds);
                }
                else if(hasHistory){
                    map.fitBounds(init_bounds);
                }
            }
        };
    }

});
