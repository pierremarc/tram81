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
    TILE_SERVER: JSON.parse('{{TILE_SERVER}}'),
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
            txt: {% if image.panel %} '{{ image.text|md|escapejs }}' {% else %}''{% endif %},
            pub: formatDate(parseISO8601('{{ image.pub_date|date:"c" }}')),
            panel: (('{{ image.panel }}' === 'False') ? false : true),
        },
    geometry: JSON.parse('{{ image.geom.geojson }}')
},
{% endfor %}
];

window.T81.journey = [];
{% if REQ_IMAGES %}
    {% for ri in REQ_IMAGES %}
window.T81.journey.push({{ ri.pk }});
    {% endfor %}
{% endif %}

window.T81.default_bounds = undefined;

{% endautoescape %}


