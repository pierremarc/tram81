/*
 * remove map function
 * 
 */


function(v, keyData, arg){
    var data = JSON.parse(v.values[0].data);
    
    function intersects(A, B){
        return(
            A.minx <= B.maxx
            && B.minx <= A.maxx
            && A.maxy <= B.miny
            && B.maxy <= A.miny
        );
    };
    if(intersects(data, arg)){
        return [v.key];
    }
    return [];
};