{% load md %}
{% autoescape off %}
function formatDate(d){
    function pad(n){return n<10 ? '0'+n : n};
    return d.getUTCFullYear()+'-'
        + pad(d.getUTCMonth()+1)+'-'
        + pad(d.getUTCDate());
};

window.T81 = {};
window.T81.config = {
    TILE_SERVER: '{{TILE_SERVER}}',
};
window.T81.data = [
{% for image in images %}
{
    pk: {{ image.pk }},
    url: '{% url 'index' pk=image.pk %}',
    img_url: '{{ image.image.url }}',
    img_thumnail_url: '{{ image.img_thumbnail }}',
    geo: JSON.parse('{{ image.geom.geojson }}'),
    txt: '{{ image.text|md|escapejs }}',
    pub: formatDate(new Date('{{ image.pub_date|date:"c" }}')),
},
{% endfor %}
];

var default_bounds = undefined;

{% if REQ_IMAGES %}
(function(){
    var rims = [];
    {% for rim in REQ_IMAGES %}
    rims.push(  new L.geoJson(JSON.parse('{{ rim.geom.geojson }}')) );
    {% endfor %}
    default_bounds = rims[0].getBounds();
    _.each(rims,function(r){
        default_bounds.extend(r.getBounds());
    });
})();

{% endif %}

{% endautoescape %}


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
    
//     L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
//     attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
// }).addTo(map);
//     
    function px(i){
        return i + 'px';
    };
    
    function mapElement(layer, append){
        var bounds = layer.getBounds();
        var $el = layer.$data_content;
        $el.detach();
        var NW = map.latLngToContainerPoint(bounds.getNorthWest());
        var SE = map.latLngToContainerPoint(bounds.getSouthEast());
        
        var bb = new L.Bounds(NW, SE);
        $el.css({
            position:'absolute',
            top:px(bb.min.y),
            left:px(bb.min.x),
            width:px(bb.getSize().x),
            height:px(bb.getSize().y),
        });
        $map.append($el);
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
                $.post('{% url 'comment_new' %}', {txt:txt, thread:thread}, function(response){
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
//         console.log(data.geo);
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
            {% if HAS_COMMENTS %}
            var $info = $('#info_box');
            var ui = {
                img_box: $('<div />').addClass('img_box'),
                txt_box: $('<div />').addClass('txt_box'),
            };
            var txt = {
                close: $('<close>fermer</close>').addClass('close_box'),
                time: $('<div />').addClass('time_box'),
                txt: $('<div />').addClass('txt'),
//                 link: $('<div />').addClass('link_box'),
             
            };
            
            var comment = resetComments(this.data.pub, $('<div />').addClass('cinner'));
            var img = $('<img />').addClass('img')
            img.attr('src', this.data.img_thumnail_url);
            var link = $('<a />').attr('href', this.data.img_url).attr('target','_blank');
            link.append(img);
            
            txt.time.html('<a href="/'+this.data.pub+'">'+this.data.pub+'</a>');
            txt.txt.html(this.data.txt);
            txt.close.on('click',function(){hidePanel();});
            
            ui.img_box.append(link);
            
            
            $info.empty();
            $info.append(txt.time);
            $info.append(ui.img_box);
            if(this.data.txt 
                && this.data.txt.length > 12)
            {
                $info.append(txt.txt);
            }
            $info.append(ui.txt_box);
            $info.append(txt.close);
            /*
            _.each(ui, function($el){
                $info.append($el);
            });
            _.each(txt, function($el){
                $info.append($el);
            });*/
            ui.txt_box.append(comment);
            
            
            showPanel();
            
            {% else %}
            
            map.fitBounds(this.getBounds());
            if(window.history && window.history.pushState)
            {
                hasHistory = true;
                var bnds = this.getBounds();
                var bounds = {
                    sw:[bnds.getSouth(), bnds.getWest()],
                    ne:[bnds.getNorth(), bnds.getEast()],
                }
//                 console.log('pushState', this.data.pk, bounds);
                window.history.pushState(
                    bounds,
                    this.data.img_url,
                    this.data.pk
                );
            }
            
            {% endif %}
        });
    };
    _.each(window.T81.data, prepareLayers);
    var las_image = global_images[global_images.length -1].getBounds();
    var init_bounds = default_bounds || las_image;
    map.whenReady(function(){
            window.setTimeout(function(){
                map.fitBounds(init_bounds);
            }, 1000);
    });
    map.setView([50.854075572144815, 4.38629150390625], 13);
    
    if(window.history && window.history.pushState)
    {
        window.onpopstate = function(evt){
            var state = evt.state;
            if(state && state.sw && state.ne){
                var bounds = L.latLngBounds(state.sw, state.ne);
                map.fitBounds(bounds);
            }
            else if(hasHistory){
                map.fitBounds(init_bounds);
            }
        };
    }

    {% if user %}
    var user = '{{ user.username }}';
    {% endif %}

});
