"""
Sea Cucumber is a Django email backend for Amazon Simple Email Service, 
backed by celery. The interesting bits are in backend.py and tasks.py. The
rest of the contents of this module are largely optional. 
"""
from boto import Version as BotoVersion
import re

# In the form of Major, Minor, Revision.
VERSION = (1, 5, 2)
FORCE_UNICODE = False

m = re.search(r'^\d+\.\d+', BotoVersion)
if m is not None:
    try:
        if float(m.group(0)) == 2.5:
            FORCE_UNICODE = True
    except:
        pass
