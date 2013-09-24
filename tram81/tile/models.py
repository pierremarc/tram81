from django.conf import settings
import  json

class BaseCache(object):
    """
    
    """
    def PUT(self, key, bounds, data):
        raise NotImplementedError()
    
    def HAS(self, key):
        raise NotImplementedError()
    
    def GET(self, key):
        raise NotImplementedError()
    
    def DELETE(self, bounds):
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
    
    def DELETE(self, bounds):
        
        def intersects(A, B):
            return A['minx'] <= B['maxx'] and B['minx'] <= A['maxx'] and A['miny'] <= B['maxy'] and B['miny'] <= A['maxy']
        
        for keys in self.bucket.stream_keys():
            for key in keys:
                bnd = self.index.get(key).data
                print '============================='
                print '%s %s'%(bounds,bnd)
                if bnd and intersects(bounds, bnd):
                    print 'About to remove tile %s'%(key,)
                    self.bucket.delete(key)
                    self.index.delete(key)
        
        print 'END DELETE: %s'%(bounds)
        return
        
        print 'START DELETE: %s'%(bounds)
        mr = self.riak.RiakMapReduce(self.client)
        mr.add_bucket(self.bucket.name)
        mr.map("""function(v, keyData, arg){
                var data = JSON.parse(v.values[0].data);
                
                function intersects(A, B){
                    return ( A.minx <= B.maxx 
                                && B.minx <= A.maxx
                                && A.maxy <= B.miny 
                                && B.maxy <= A.miny );
                };
        
               /* if(data 
                    && arg 
                    && intersects(data, arg)){
                    return [v.key];
                } */
                return [[intersects(data, arg), v.key]];
            }""", {'arg':bounds})
        mr.reduce("""function(v){ return v; }""")
        
        #result = mr.run()
        #if result:
            #for key in result:
                #print 'About to remove tile %s'%(key,)
                #self.bucket.delete(key)
        for vals in mr.stream():
            print vals
            if vals[1]:
                for val in vals[1]:
                    if val[0]:
                        print 'Keep %s'%(val[1],)
                    else:
                        print 'About to remove tile %s'%(val[1],)
                        self.bucket.delete(key)
        
        print 'END DELETE: %s'%(bounds)
        
        