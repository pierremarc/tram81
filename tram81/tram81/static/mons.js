
 function styleFunction(feature, resolution) {
    var s = new ol.style.Style({
        stroke: new ol.style.Stroke({
          color: 'yellow',
          width: 1
        }),
        fill: new ol.style.Fill({
          color: 'rgba(255, 255, 0, 0.5)'
        })
    });
    return [];
};


function reverseRotate(r){
    if(0 === r || 360 === r){ return 0; }
    return 360 - r;
};    

function prepareMap(){

    var tileSource = new ol.source.XYZ(window.T81.config.TILE_SERVER);
    // var tileSource = new ol.source.OSM();
    var tileLayer = new ol.layer.Tile({source: tileSource});

    var view = new ol.View({zoom: 8 });

    window.T81.dataSource = new ol.source.GeoJSON({
        projection: view.getProjection(),
        object:{
            'type': 'FeatureCollection',
            'crs': {'type': 'EPSG', 'properties': {'code': 4326}},
            'features': window.T81.data
        }
    });

    // view.setCenter(ol.extent.getCenter(window.T81.dataSource.getExtent()));

    var dataLayer = new ol.layer.Vector({
        source: window.T81.dataSource,
        style: styleFunction
    });

    window.T81.map = new ol.Map({
        target: 'map',
        layers: [
          tileLayer,
          dataLayer
        ],
        view: view,
        loadTilesWhileAnimating: true,
      });
    var feature = _.last(window.T81.dataSource.getFeatures());

    view.fitExtent(feature.getGeometry().getExtent(), window.T81.map.getSize());
};

function setupInteraction(){
    var select = new ol.interaction.Select({
        style:[],
    });
    var features = select.getFeatures();
    features.on('add', function(event){
        pushState(event.element);
    });

    window.T81.map.addInteraction(select);
};


function showFeature(feature){
    var map = window.T81.map;
    var props = feature.getProperties();
    var rot = props.rotation * Math.PI / 180;
    var extent = feature.getGeometry().getExtent();
    var center = ol.extent.getCenter(extent);
    var duration = 600 * 2;
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


function pushState(feature){
    var props = feature.getProperties();
    var geom = feature.getGeometry();

    if(window.history && window.history.pushState)
    {
        window.history.pushState(
            props.pk,
            props.img_url,
            props.pk
        );
    }

    showFeature(feature);
};

function popState(evt){
    var state = evt.state;
    if(state){
        var feature = window.T81.dataSource.getFeatureById(state);
        if(feature){
            showFeature(feature);
        }
    }
    else{
        window.T81.map.getView().fitExtent(
            _.last(window.T81.dataSource.getFeatures()), window.T81.map.getSize());
    }
};



$(document).ready(function(){

    $('#info_box').hide();
    $('#page').hide();
    prepareMap();
    setupInteraction();

    if(window.history && window.history.pushState)
    {
        window.onpopstate = popState;
    }

});
