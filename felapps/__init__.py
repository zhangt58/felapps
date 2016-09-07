from .utils import felutils
from .utils import funutils
from .utils import resutils
from .utils import scanutils
from .utils import datautils
from .utils import matchutils
from .utils import imageutils
from .utils import uiutils
from .utils import myui
from .utils import analysisframe
from .physics import felcalc
from .physics import felbase
from .facilities import dcls
from .apps.imageviewer  import imageviewer
from .apps.cornalyzer   import cornalyzer
from .apps.felformula   import felformula
from .apps.dataworkshop import dataworkshop
from .apps.matchwizard  import matchwizard
from .apps.appdrawer    import appdrawer
from .apps.wxmpv        import wxmpv

__version__ = appdrawer.__version__
__author__ = "Tong Zhang"

__doc__ = """Python package created for the commissioning of free-electron 
laser facilities, providing general-purpose graphical user interface 
applications to fulfill various tasks, such as image DAQ, 
data post-processing, data correlation analysis and FEL physics 
calculations, etc. Friendly user interative approaches are subtly 
designed, as well as the straight-forward distribution manner. 

``felapps`` is the beginning phase to the world of python-powered software
ecosystem that could be served as the infrastructure for the future 
versatile large-scale scientific facilities.

.. warning:: Before installing ``felapps``, another python package 
    ``beamline`` is required, so install that package first, 
    see `the documentation <https://archman.github.io/beamline>`_.

Brief guide to the users:

1. type ``runfelapps`` or ``appdrawer`` in the terminal to open the main 
   app portal of ``felapps``;
2. in [i]python terminal, first ``import felapps``, then call 
   ``felapps.imageviewer.run()`` to open ``imageviewer`` app, the same rule
   applies to other apps:
    * ``dataworkshop``
    * ``cornalyzer``
    * ``felformula``
    * ``wxmpv``

:Version: %s
:Author: Tong Zhang (zhangtong@sinap.ac.cn)
""" % (__version__)


#__all__ = [imageviewer]
