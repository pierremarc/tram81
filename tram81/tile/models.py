from django.conf import settings



class BaseCache(object):
    """
    
    """
    def PUT(self, key, bounds, data):
        raise NotImplementedError()
    
    def HAS(self, key):
        raise NotImplementedError()
    
    def GET(self, key):
        raise NotImplementedError()
    
    def REMOVE(self, bounds):
        raise NotImplementedError()
    
    
class RiakCache(BaseCache):
    
    def __init__(self, *args, **kwargs):
        import riak
        self.riak = riak
        RC = settings.RIAK_TILE_CONNECTION
        self.client = riak.RiakClient(**RC)
        self.bucket = self.client.bucket(settings.RIAK_TILE_BUCKET)
        self.index = self.client.bucket(settings.RIAK_TILE_BUCKET + '_index')
        
        
    def PUT(self, key, bounds, data):
        D = self.bucket.new(key, 
                                   encoded_data=data, 
                                   content_type='application/octet-stream')
        I = self.index.new(key, bounds)
        D.store()
        I.store()
        
    def HAS(self, key):
        D  = self.bucket.get(key)
        return D.exists
    
    def GET(self, key):
        return self.bucket.get(key).encoded_data
    
    def REMOVE(self, bounds):
        mr = self.riak.RiakMapReduce(self.client)
        mr.add_bucket(self.index)
        mr.map("""function(v, keyData, arg){
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
            };""")
        mr.reduce("""function(v){ return v; };""")
        
        for key in mr.run():
            print 'About to remove tile %s'%(key,)
            self.bucket.delete(key)
        
        
        