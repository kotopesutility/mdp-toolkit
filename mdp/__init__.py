# Modular toolkit for Data Processing (MDP)
"""
The Modular toolkit for Data Processing (MDP) is a library of widely
used data processing algorithms that can be combined according to a
pipeline analogy to build more complex data processing software.

From the user's perspective, MDP consists of a collection of
supervised and unsupervised learning algorithms, and other data
processing units (nodes) that can be combined into data processing
sequences (flows) and more complex feed-forward network
architectures. Given a set of input data, MDP takes care of
successively training or executing all nodes in the network. This
allows the user to specify complex algorithms as a series of simpler
data processing steps in a natural way.

The base of available algorithms is steadily increasing and includes,
to name but the most common, Principal Component Analysis (PCA and
NIPALS), several Independent Component Analysis algorithms (CuBICA,
FastICA, TDSEP, JADE, and XSFA), Slow Feature Analysis, Gaussian
Classifiers, Restricted Boltzmann Machine, and Locally Linear
Embedding.

Particular care has been taken to make computations efficient in terms
of speed and memory.  To reduce memory requirements, it is possible to
perform learning using batches of data, and to define the internal
parameters of the nodes to be single precision, which makes the usage
of very large data sets possible.  Moreover, the 'parallel' subpackage
offers a parallel implementation of the basic nodes and flows.

From the developer's perspective, MDP is a framework that makes the
implementation of new supervised and unsupervised learning algorithms
easy and straightforward.  The basic class, 'Node', takes care of
tedious tasks like numerical type and dimensionality checking, leaving
the developer free to concentrate on the implementation of the
learning and execution phases. Because of the common interface, the
node then automatically integrates with the rest of the library and
can be used in a network together with other nodes. A node can have
multiple training phases and even an undetermined number of phases.
This allows the implementation of algorithms that need to collect some
statistics on the whole input before proceeding with the actual
training, and others that need to iterate over a training phase until
a convergence criterion is satisfied. The ability to train each phase
using chunks of input data is maintained if the chunks are generated
with iterators. Moreover, crash recovery is optionally available: in
case of failure, the current state of the flow is saved for later
inspection.

MDP has been written in the context of theoretical research in
neuroscience, but it has been designed to be helpful in any context
where trainable data processing algorithms are used. Its simplicity on
the user side together with the reusability of the implemented nodes
make it also a valid educational tool.

http://mdp-toolkit.sourceforge.net
"""
__docformat__ = "restructuredtext en"

class MDPException(Exception):
    """Base class for exceptions in MDP."""
    pass

class MDPWarning(UserWarning):
    """Base class for warnings in MDP."""
    pass

class MDPDeprecationWarning(DeprecationWarning, MDPWarning):
    """Warn about deprecated MDP API."""
    pass

class config(object):
    """Provide information about optional dependencies.

    This class should not be instantiated, it serves as a namespace
    for dependency information. This information is encoded as a
    series of attributes called 'has_<dependency>'.

    Dependency parameters are object which have a a boolean value
    (``True`` if the dependency is available). If False, they contain an
    error string which will be used in ``mdp.config.info()`` output. If
    ``True``, they contain information about the available version of
    the dependency. Those objects should be created by using the helper
    class methods `ExternalDepFound` and `ExternalDepFailed`.

    Dependency parameters are numbered in the order of creation,
    so the output is predictable.

    >>> config.has_python
    True
    """

    _HAS_NUMBER = 0
    class _ExternalDep(object):
        def __init__(self, name, version=None, failmsg=None):
            assert (version is not None) + (failmsg is not None) == 1

            self.version = str(version) # convert e.g. exception to str
            self.failmsg = str(failmsg) if failmsg is not None else None

            global config
            self.order = config._HAS_NUMBER
            config._HAS_NUMBER += 1
            setattr(config, 'has_' + name, self)

        def __nonzero__(self):
            return self.failmsg is None

        def __repr__(self):
            if self:
                return self.version
            else:
                return "NOT AVAILABLE: " + self.failmsg

    @classmethod
    def ExternalDepFailed(cls, name, failmsg):
        """Inform that an optional dependency was not found.

        A new `_ExternalDep` object will be created and stored
        in `config`.

        :Parameters:
          name
            identifier of the optional dependency. This should
            be a valid python identifier, because it will be
            accessible as ``mdp.config.has_<name>`` attribute.
          failmsg
            an object convertible to ``str``, which will be displayed in
            ``mdp.config.info()`` output. This will usually be either an
            exception (e.g. ``ImportError``), or a message string.
        """
        return cls._ExternalDep(name, failmsg=failmsg)

    @classmethod
    def ExternalDepFound(cls, name, version):
        """Inform that an optional dependency was found.

        A new `_ExternalDep` object will be created and stored
        in `config`.

        :Parameters:
          name
            identifier of the optional dependency. This should
            be a valid python identifier, because it will be
            accessible as ``mdp.config.has_<name>`` attribute.
          version
            an object convertible to ``str``, which will be displayed in
            ``mdp.config.info()`` output. Something like ``'0.4.3'``.
        """
        return cls._ExternalDep(name, version=version)

    @classmethod
    def info(cls):
        """Return nicely formatted info about MDP.

        >>> print mdp.config.info()                           # doctest: +SKIP
                  python: 2.6.6.final.0
                   scipy: 0.7.2
            scipy signal: 0.7.2
         parallel python: 1.6.0
                  shogun: v0.9.3_r4889_2010-05-27_20:52_
                  libsvm: NOT AVAILABLE: No module named svm
              new symeig: NOT AVAILABLE: symeig version too old
                  symeig: wrap_eigh
                  joblib: 0.4.6

        This function is used to provide the py.test report header and
        footer.
        """
        listable_features = [(f[4:].replace('_', ' '), getattr(cls, f))
                             for f in dir(cls) if f.startswith('has_')]
        maxlen = max(len(f[0]) for f in listable_features)
        listable_features = sorted(listable_features, key=lambda f: f[1].order)
        return '\n'.join('%*s: %r' % (maxlen+1, f[0], f[1])
                         for f in listable_features)

import sys, os

config.ExternalDepFound('python', '.'.join([str(x) for x in sys.version_info]))

# To force MDP to use one specific extension module
# set the environment variable MDPNUMX
# Mainly useful for testing
_USR_LABEL = os.getenv('MDPNUMX')
if _USR_LABEL and _USR_LABEL not in ('numpy', 'scipy'):
    err = """
Numerical backend '%s' not supported.
Supported backends: numpy, scipy.""" % _USR_LABEL
    raise ImportError(err)

numx_description = None
numx_exceptions = {}

if _USR_LABEL and _USR_LABEL != 'scipy':
    config.ExternalDepFailed('scipy', 'MDPNUMX set to %s' % _USR_LABEL)
else:
    try:
        import scipy as numx
        from scipy import (linalg as numx_linalg,
                           fftpack as numx_fft,
                           random as numx_rand,
                           version as numx_version)
    except ImportError, exc:
        numx_exceptions['scipy'] = exc
        config.ExternalDepFailed('scipy', exc)
    else:
        numx_description = 'scipy'
        config.ExternalDepFound('scipy', numx_version.version)

if _USR_LABEL and _USR_LABEL != 'numpy':
    config.ExternalDepFailed('numpy', 'MDPNUMX set to %s' % _USR_LABEL)
elif numx_description is None:
    try:
        import numpy as numx
        from numpy import (linalg as numx_linalg,
                           fft as numx_fft,
                           random as numx_rand,
                           version as numx_version)
        numx_description = 'numpy'
        config.ExternalDepFound('numpy', numx_version.version)
    except ImportError, exc:
        config.ExternalDepFailed('numpy', exc)
        numx_exceptions['numpy'] = exc
else:
    config.ExternalDepFailed('numpy', 'scipy is preferred')

assert config.has_scipy != config.has_numpy

if numx_description is None:
    # The test is for numx_description, not numx, because numx could
    # be imported sucessfuly, but e.g. numx_rand could later fail.
    msg = ("Could not import any of the numeric backends.\n"
           "Import errors:\n"
           + '\n'.join(label+': '+str(exc)
                       for label, exc in numx_exceptions.iteritems()))
    raise ImportError(msg)
else:
    # we have numx, we don't need the exceptions anymore
    del numx_exceptions

del _USR_LABEL

if config.has_scipy:
    try:
        import scipy.signal
    except ImportError, exc:
        config.ExternalDepFailed('scipy_signal', exc)
    else:
        config.ExternalDepFound('scipy_signal', scipy.version.version)
else:
    config.ExternalDepFailed('scipy_signal', 'scipy not available')

# import the utils module (used by other modules)
# here we set scipy_emulation if needed.
import utils

__version__ = '3.0'
__revision__ = utils.get_git_revision()
__authors__ = 'MDP Developers'
__copyright__ = '(c) 2003-2011 mdp-toolkit-devel@lists.sourceforge.net'
__license__ = 'BSD License, see COPYRIGHT'
__contact__ = 'mdp-toolkit-users@lists.sourceforge.net'

try:
    import pp
except ImportError, exc:
    config.ExternalDepFailed('parallel_python', exc)
else:
    config.ExternalDepFound('parallel_python', pp.version)

try:
    from shogun import (Kernel as sgKernel,
                        Features as sgFeatures,
                        Classifier as sgClassifier)
except ImportError, exc:
    config.ExternalDepFailed('shogun', exc)
else:
    # We need to have at least SHOGUN 0.9, as we rely on
    # SHOGUN's CClassifier::classify() method.
    # (It makes our code much nicer, by the way.)
    #
    if not hasattr(sgClassifier.Classifier, 'classify'):
        config.ExternalDepFailed('shogun', "CClassifier::classify not found")
    try:
        version = sgKernel._Kernel.Version_get_version_release()
    except AttributeError, msg:
        config.ExternalDepFailed('shogun', msg)
    else:
        if not (version.startswith('v0.9') or version.startswith('v1.')):
            config.ExternalDepFailed('We need at least SHOGUN version 0.9.')
        config.ExternalDepFound('shogun', version)

try:
    import svm as libsvm
except ImportError, exc:
    config.ExternalDepFailed('libsvm', exc)
else:
    config.ExternalDepFound('libsvm', libsvm.libsvm._name)

import inspect as _inspect

# if we have scipy, check if the version of
# scipy.linalg.eigh supports the rich interface
_args = _inspect.getargspec(numx_linalg.eigh)[0]
if len(_args) > 4:
    # if yes, just wrap it
    from utils._symeig import (wrap_eigh as symeig,
                               SymeigException)
    config.ExternalDepFound('symeig', 'scipy.linalg.eigh')
else:
    # either we have numpy, or we have an old scipy
    # we need to use our own rich wrapper
    from utils._symeig import (_symeig_fake as symeig,
                               SymeigException)
    config.ExternalDepFound('symeig', 'symeig_fake')
del _args
del _inspect

# import exceptions from nodes and flows
from signal_node import (NodeException, InconsistentDimException,
                         TrainingException,
                         TrainingFinishedException, IsNotTrainableException,
                         IsNotInvertibleException)
from linear_flows import CrashRecoveryException, FlowException, FlowExceptionCR

# import base nodes and flow classes
from signal_node import (NodeMetaclass, Node, PreserveDimNode,
                         Cumulator, VariadicCumulator)

from linear_flows import (Flow, CheckpointFlow,
                          CheckpointFunction, CheckpointSaveFunction)

# import helper functions:
from helper_funcs import pca, whitening, fastica, sfa, get_eta

# import extension mechanism
from extension import (ExtensionException, extension_method,
                       ExtensionNodeMetaclass,
                       ExtensionNode, get_extensions,
                       get_active_extensions, with_extension,
                       activate_extension, deactivate_extension,
                       activate_extensions, deactivate_extensions,
                       extension)

# import classifier node
from classifier_node import (ClassifierNode, ClassifierCumulator)

# import our modules
import nodes
import hinet
import parallel
from test import test

# clean up namespace
del signal_node
del linear_flows
del classifier_node
del os, sys

# explicitly set __all__, mainly needed for epydoc
__all__ = ['CheckpointFlow', 'CheckpointFunction', 'CheckpointSaveFunction',
           'CrashRecoveryException', 'Cumulator', 'VariadicCumulator', 'Flow',
           'FlowException',
           'FlowExceptionCR', 'IsNotInvertibleException',
           'IsNotTrainableException', 'MDPException', 'MDPWarning', 'Node',
           'NodeException', 'TrainingException', 'TrainingFinishedException',
           'ClassifierNode', 'ClassifierCumulator',
           'get_eta', 'graph', 'helper_funcs', 'hinet', 'nodes',
           'numx_description', 'pca', 'sfa', 'utils', 'whitening',
           'parallel', 'numx_version',
           'extension_method', 'ExtensionNodeMetaclass', 'ExtensionNode',
           'get_extensions', 'with_extension',
           'activate_extension', 'deactivate_extension', 'activate_extensions',
           'deactivate_extensions',
           'ClassifierNode',
           'config'
           ]

try:
    import joblib
    __all__ += ['joblib']
    config.ExternalDepFound('joblib', joblib.__version__)
except ImportError, exc:
    config.ExternalDepFailed('joblib', exc)

if config.has_joblib:
    import caching
    __all__ += ['caching']
