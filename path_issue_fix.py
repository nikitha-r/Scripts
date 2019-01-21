path = os.path.abspath(os.path.join(os.path.dirname('__file__'), '..'))
export PYTHONPATH=$PYTHONPATH:/Users/nr012/Downloads/super1

import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname('__file__'), '..'))
sys.path.insert(0, path)
