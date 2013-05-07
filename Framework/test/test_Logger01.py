from Framework.Logger import Logger
from StringIO import StringIO

buf = StringIO ()
logger = Logger ("Foo", buf, standalone=True)
logger.log ("message", priority=1, format="[%(stream_name)s]")
assert (buf.getvalue () == "[Foo]message\n")
logger.log ("message", priority=1, format="[%(stream_name)s]")
assert (buf.getvalue () == "[Foo]message\n[Foo]message\n")
logger.log ("message", priority=90, format="[%(stream_name)s]")
assert (buf.getvalue () == "[Foo]message\n[Foo]message\n")
logger.detailLevel = 100
logger.log ("message", priority=90, format="[%(stream_name)s]")
assert (buf.getvalue () == "[Foo]message\n[Foo]message\n[Foo]message\n")
logger.detailFilter = [80]
logger.log ("message", priority=90, format="[%(stream_name)s]")
assert (buf.getvalue () == "[Foo]message\n[Foo]message\n[Foo]message\n")
logger.detailFilter = [90]
logger.log ("message", priority=90, format="[%(stream_name)s]")
assert (buf.getvalue () == "[Foo]message\n[Foo]message\n[Foo]message\n[Foo]message\n")

logger.error ("error")
logger.warning ("warning")
logger.debug ("debug")
logger.log ("log")

anotherLogger = Logger ("Bar", buf, parent=logger)
anotherLogger.log ("message", priority=90, format="[%(stream_name)s]")
anotherLogger.detailLevel = 200
assert (logger.detailLevel == 100)
assert (buf.getvalue () == "[Foo]message\n[Foo]message\n[Foo]message\n[Foo]message\n[Bar]message\n")
anotherLogger.log ("message", priority=190, format="[%(stream_name)s]")
assert (buf.getvalue () == "[Foo]message\n[Foo]message\n[Foo]message\n[Foo]message\n[Bar]message\n")
buf2 = StringIO ()
logger.stream = buf2
logger.log ("message", priority=90, format="[%(stream_name)s]")
assert (buf2.getvalue () == "[Foo]message\n")
logger.log ("message", priority=1, format="[%(stream_name)s]")
assert (buf2.getvalue () == "[Foo]message\n")
