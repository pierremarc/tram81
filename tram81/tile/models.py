
import os
import json

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
    
    def DELETE(self, bounds):
        raise NotImplementedError()
    
    def intersects(A, B):
        return (    A['minx'] <= B['maxx']
                and B['minx'] <= A['maxx']
                and A['miny'] <= B['maxy']
                and B['miny'] <= A['maxy'])
    
    
    
class MongoCache(BaseCache):
    """
    
    """
    
    def __init__(self, *args, **kwargs):
        import pymongo
        self.mongo = pymongo
        ms = settings.MONGO_TILE_SETTINGS
        self.client = self.mongo.MongoClient(ms['host'], ms['port'])
        self.database = self.client[ms['database']]
        self.index = self.database.tile_index
        self.index.ensure_index([('bounds', self.mongo.GEOSPHERE),])
        self.root_dir = os.path.abspath(ms['root_dir'])
        
    def make_mongo_key(self, key, sep='_'):
        return sep.join(key.split('.'))
    
    def make_path_from_key(self, key):
        path = os.path.join(self.root_dir,
                            os.path.sep.join(key.split('.')))
        pdir = os.path.dirname(path)
        if not os.path.exists(pdir):
            try:
                os.makedirs(pdir)
            except Exception:
                pass # likely it has been made in another thread
            
        return path
        
    def get_center(self, bounds):
        coords = [ 
            bounds['minx'] + ((bounds['maxx'] - bounds['minx']) / 2.0),
            bounds['miny'] + ((bounds['maxy'] - bounds['miny']) / 2.0),
            ]
        return dict(type="Point", coordinates=coords)
    
    def get_polygon(self, bounds):
        coords = [[
            [bounds['minx'],bounds['miny']],
            [bounds['minx'],bounds['maxy']],
            [bounds['maxx'],bounds['maxy']],
            [bounds['maxx'],bounds['miny']],
            [bounds['minx'],bounds['miny']],
            ]]
        return dict(type="Polygon", coordinates=coords)
    
    def PUT(self, key, bounds, data):
        fn = self.make_path_from_key(key)
        with open(fn, 'wb') as sink:
            try:
                sink.write(data)
                idx_entry = dict(_id=self.make_mongo_key(key), 
                                 bounds=self.get_polygon(bounds), 
                                 path=fn)
                self.index.insert(idx_entry)
            except Exception, e:
                print '[MongoCache.PUT] Failed to store %s'%key
                print str(e)
                
            
    
    def HAS(self, key):
        if self.index.find_one(dict(_id=self.make_mongo_key(key))) is not None:
            return True
        return False
    
    def GET(self, key):
        print 'MongoCache.GET %s'%key
        entry = self.index.find_one(dict(_id=self.make_mongo_key(key)))
        f = open(entry['path'], 'r')
        data = f.read()
        f.close()
        return data
    
    def DELETE(self, bounds):
        
        polygon = self.get_polygon(bounds)
        request = { 'bounds' : { '$geoIntersects' : { '$geometry' : polygon } } }
        
        print 'MongoCache.DELETE: %s'%request
        
        try:
            for item in self.index.find(request):
                path = item['path']
                id = item['_id']
                print 'MongoCache.DELETE: item %s %s'%(id, path)
                if id is not None:
                    try:
                        self.index.remove(id)
                        os.unlink(path)
                    except Exception, e:
                        print '[MongoCache.DELETE] Failed to delete %s, %s'%(id, path)
                        print str(e)
        except Exception, e:
            print 'MongoCache.DELETE: %s'%(e,)
                
            
        return
    
    
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
        
        for keys in self.bucket.stream_keys():
            for key in keys:
                bnd = self.index.get(key).data
                #print '============================='
                #print '%s %s'%(bounds,bnd)
                if bnd and self.intersects(bounds, bnd):
                    #print 'About to remove tile %s'%(key,)
                    self.bucket.delete(key)
                    self.index.delete(key)
        
        #print 'END DELETE: %s'%(bounds)
        return
        
        #print 'START DELETE: %s'%(bounds)
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
            #print vals
            if vals[1]:
                for val in vals[1]:
                    if val[0]:
                        #print 'Keep %s'%(val[1],)
                        pass
                    else:
                        #print 'About to remove tile %s'%(val[1],)
                        self.bucket.delete(key)
        
        #print 'END DELETE: %s'%(bounds)
        
        