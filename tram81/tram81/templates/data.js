{% load md %}
{% autoescape off %}
function formatDate(d){
    function pad(n){return n<10 ? '0'+n : n};
    return d.getUTCFullYear()+'-'
        + pad(d.getUTCMonth()+1)+'-'
        + pad(d.getUTCDate());
};

/**
 * from http://stackoverflow.com/questions/2182246/javascript-dates-in-ie-nan-firefox-chrome-ok/2182529#2182529
 * Parses string formatted as YYYY-MM-DD to a Date object.
 * If the supplied string does not match the format, an 
 * invalid Date (value NaN) is returned.
 * @param {string} dateStringInRange format YYYY-MM-DD, with year in
 * range of 0000-9999, inclusive.
 * @return {Date} Date object representing the string.
 */

function parseISO8601(dateStringInRange) {
    var isoExp = /^\s*(\d{4})-(\d\d)-(\d\d)\s*$/,
    date = new Date(NaN), month,
    parts = isoExp.exec(dateStringInRange);
    
    if(parts) {
        month = +parts[2];
        date.setFullYear(parts[1], month - 1, parts[3]);
        if(month != date.getMonth() + 1) {
            date.setTime(NaN);
        }
    }
    return date;
}

window.T81 = {};
window.T81.config = {
    TILE_SERVER: '{{TILE_SERVER}}',
};
window.T81.data = [
{% for image in images %}
{
    type: "Feature",
    id: {{ image.pk }},
    properties : {
            pk: {{ image.pk }},
            url: '{% url 'index' pk=image.pk %}',
            img_url: '{{ image.image.url }}',
            img_large_url: '{{ image.img_large }}',
            img_thumnail_url: '{{ image.img_thumbnail }}',
            rotation: {{ image.rotation }},
            txt: '{{ image.text|md|escapejs }}',
            pub: formatDate(parseISO8601('{{ image.pub_date|date:"c" }}')),
        },
    geometry: JSON.parse('{{ image.geom.geojson }}')
},
{% endfor %}
];

window.T81.default_bounds = undefined;

{% if REQ_IMAGES %}
(function(){
    // var rims = [];
    // {% for rim in REQ_IMAGES %}
    // var source = new ol.source.GeoJSON({
    //     object: JSON.parse('{{ rim.geom.geojson }}')
    // });
    // //rims.push(  new L.geoJson(JSON.parse('{{ rim.geom.geojson }}')) );
    // rims.push(source);
    // {% endfor %}
    // window.T81.default_bounds = rims[0].getBounds();
    // _.each(rims,function(r){
    //     window.T81.default_bounds.extend(r.getBounds());
    // });
})();

{% endif %}

{% endautoescape %}


{% if HAS_COMMENTS %}
window.T81.config.HAS_COMMENTS = true;
window.T81.config.NEW_COMMENT_URL = '{% url 'comment_new' %}';
{% endif %}

{% if user %}
window.T81.config.USERNAME = '{{ user.username }}';
{% endif %}
