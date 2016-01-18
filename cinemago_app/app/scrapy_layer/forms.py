from schematics.models import Model
from schematics.types import StringType


class JobForm(Model):
    project = StringType(required=True)
    spider = StringType(required=True)
    setting = StringType()
    jobid = StringType()

    class Options:
        serialize_when_none = False
