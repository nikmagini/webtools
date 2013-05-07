from Tools.YUICache import YUICache
import os
from pprint import pprint

try:
    os.environ["YUI_ROOT"]
except:
    assert (False)
cache = YUICache (os.environ["YUI_ROOT"])
assert (cache.size ())
assert (cache.getContentByLabel ("datatable.js"))
assert (cache.getContentByLabel ("datatable.js"))
assert (cache.getContentByLabel ("datatable.css"))
assert (cache.getContentByLabel ("/container/assets/container.css"))
assert (cache.getContentByLabel ("/menu/assets/menu.css"))
assert (cache.getContentByLabel ("/grids/grids-min.css"))
assert (cache.getContentByLabel ("menu.css"))
assert (cache.getContentByLabel ("menu.css").lenght != 0)
assert (cache.getContentByLabel ("/datatable/datatable.js"))
assert (cache.getContentByLabel ("menu.css").data != cache.getContentByLabel ("/menu/assets/menu.css").data)
assert (cache.getContentByLabel ("menu.css").data == cache.getContentByLabel ("/menu/assets/skins/sam/menu.css").data)
assert (cache.getContentByLabel ("datatable").data != cache.getContentByLabel ("datatable.css").data)
assert (cache.getContentByLabel ("datatable").data == cache.getContentByLabel ("datatable.js").data)
assert (cache.getContentByLabel ("datatable").data == cache.getContentByLabel ("/datatable/datatable.js").data)
assert (cache.getContentByLabel ("datatable").data == cache.getContentByLabel ("datatable.js").data)

#for (key, content) in cache.iteritems ():
#    pprint (key)