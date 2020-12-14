import sys
sys.path.append('path-to-site-packages-for-current-working-environment')
from fbprophet import Prophet
import logging
logger = logging.getLogger('fbprophet')
logger.setLevel(logging.DEBUG)

m = Prophet()
print(m.stan_backend)