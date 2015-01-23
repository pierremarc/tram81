
'use strict';
 
(function(undefined){

if (typeof String.prototype.startsWith != 'function') {
  String.prototype.startsWith = function (str){
    return this.slice(0, str.length) == str;
  };
}

var T81 = window.T81;

var baseStyle = new ol.style.Style({
    stroke: new ol.style.Stroke({
      color: 'yellow',
      width: 1
    }),
    fill: new ol.style.Fill({
      color: 'rgba(255, 255, 0, 0.5)'
    })
});

function styleFunction(feature, resolution) {
    return [baseStyle];
};


function reverseRotate(r){
    if(0 === r || 360 === r){ return 0; }
    return 360 - r;
};    

function prepareMap(){

    var tileSource = new ol.source.XYZ(T81.config.TILE_SERVER);
    // var tileSource = new ol.source.OSM();
    var tileLayer = new ol.layer.Tile({source: tileSource});

    var view = new ol.View({zoom: 8 });

    T81.dataSource = new ol.source.GeoJSON({
        projection: view.getProjection(),
        object:{
            'type': 'FeatureCollection',
            'crs': {'type': 'EPSG', 'properties': {'code': 4326}},
            'features': T81.data
        }
    });

    // view.setCenter(ol.extent.getCenter(T81.dataSource.getExtent()));

    var dataLayer = new ol.layer.Vector({
        source: T81.dataSource,
        style: styleFunction,
        // opacity: 0,
    });

    T81.map = new ol.Map({
        target: 'map',
        layers: [
          tileLayer,
          dataLayer
        ],
        view: view,
        loadTilesWhileAnimating: true,
      });

    var feature = _.last(T81.dataSource.getFeatures());
    view.fitExtent(feature.getGeometry().getExtent(), T81.map.getSize());
};

function preparePane(){
    T81.$panel = $('#info_box');
    hidePane();
};

function setupInteraction(){
    var select = new ol.interaction.Select({
        style: [baseStyle],
    });
    var features = select.getFeatures();
    features.on('add', function(event){
            pushState(event.element);
    });

    T81.map.addInteraction(select);
};


function showFeature(feature){
    hidePane();
    var map = T81.map;
    var props = feature.getProperties();
    var rot = props.rotation * Math.PI / 180;
    var extent = feature.getGeometry().getExtent();
    var center = ol.extent.getCenter(extent);
    // var distance = (new ol.geom.LineString([center, map.getView().getCenter()])).getLength(); 
    var duration = 1200;
    console.log(duration);
    var rotate = ol.animation.rotate({
        duration: duration,
        rotation: map.getView().getRotation(),
        anchor: map.getView().getCenter()
    });
    var pan = ol.animation.pan({
        duration: duration,
        source: map.getView().getCenter()
    });
    var zoom = ol.animation.zoom({
        duration: duration,
        resolution: map.getView().getResolution()
    });

    map.beforeRender(zoom, pan, rotate);
    map.getView().rotate(rot, center);
    map.getView().fitExtent(extent, map.getSize());
};

function showPane(props){
    var $close = T81.$panel.find('#panel_close');
    $close.detach();
    T81.$panel.empty();

    var $content = $('<div />')
        .addClass('pane-content')
        .html(props.txt);
    
    T81.$panel.append($content);
    T81.$panel.append($close);

    $('body').append(T81.$panel);
    $close.one('click', hidePane);
};


function hidePane(){
    T81.$panel.detach();
};


function pushState(feature){
    var props = feature.getProperties();
    var geom = feature.getGeometry();

    if(window.history && window.history.pushState)
    {
        window.history.pushState(
            props.pk,
            props.img_url,
            props.url
        );
    }

    showFeature(feature);
    if(props.panel){
        showPane(props);
    }

};

function popState(evt){
    var state = evt.state;
    if(state){
        var feature = T81.dataSource.getFeatureById(''+state);
        if(feature){
            var props = feature.getProperties();
            if(props.panel){
                showPane(props);
            }
            else{
                showFeature(feature);
            }
        }
    }
    else{
        var feature = _.last(T81.dataSource.getFeatures());
        showFeature(feature);
    }
};


function journey(idList){
    var id = idList.shift();
    if(id){
        var feature = T81.dataSource.getFeatureById(id);
        if(feature){
            pushState(feature);
        }
        window.setTimeout(_.partial(journey, idList), 5000);
    }
};


$(document).ready(function(){

    prepareMap();
    preparePane();
    setupInteraction();

    if(window.history 
        && window.history.pushState)
    {
        window.onpopstate = popState;
        if(T81.journey){
            journey(_.clone(T81.journey));
        }
    }

});

})();
