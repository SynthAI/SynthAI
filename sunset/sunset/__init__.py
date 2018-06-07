# Copyright 2017 The Sunset Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or  implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================

"""This python module contains Neural Network Modules for TensorFlow.

Each module is a Python object which conceptually "owns" any
variables required in that part of the Neural Network. The `__call__` function
on the object is used to connect that Module into the Graph, and this may be
called repeatedly with sharing automatically taking place.

Everything public should be imported by this top level `__init__.py` so that the
library can be used as follows:

```
import sunset as snt

linear = snt.Linear(...)
```
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys

from sunset.python import custom_getters
from sunset.python.modules import experimental
from sunset.python.modules import nets
from sunset.python.modules.attention import AttentiveRead
from sunset.python.modules.base import AbstractModule
from sunset.python.modules.base import Module
from sunset.python.modules.base import Transposable
from sunset.python.modules.base_errors import DifferentGraphError
from sunset.python.modules.base_errors import Error
from sunset.python.modules.base_errors import IncompatibleShapeError
from sunset.python.modules.base_errors import ModuleInfoError
from sunset.python.modules.base_errors import NotConnectedError
from sunset.python.modules.base_errors import NotInitializedError
from sunset.python.modules.base_errors import NotSupportedError
from sunset.python.modules.base_errors import ParentNotBuiltError
from sunset.python.modules.base_errors import UnderspecifiedError
from sunset.python.modules.base_info import SUNSET_COLLECTION_NAME
from sunset.python.modules.basic import AddBias
from sunset.python.modules.basic import BatchApply
from sunset.python.modules.basic import BatchFlatten
from sunset.python.modules.basic import BatchReshape
from sunset.python.modules.basic import FlattenTrailingDimensions
from sunset.python.modules.basic import Linear
from sunset.python.modules.basic import merge_leading_dims
from sunset.python.modules.basic import MergeDims
from sunset.python.modules.basic import SelectInput
from sunset.python.modules.basic import SliceByDim
from sunset.python.modules.basic import split_leading_dim
from sunset.python.modules.basic import TileByDim
from sunset.python.modules.basic import TrainableVariable
from sunset.python.modules.basic_rnn import DeepRNN
from sunset.python.modules.basic_rnn import ModelRNN
from sunset.python.modules.basic_rnn import VanillaRNN
from sunset.python.modules.batch_norm import BatchNorm
from sunset.python.modules.batch_norm_v2 import BatchNormV2
from sunset.python.modules.clip_gradient import clip_gradient
from sunset.python.modules.conv import CausalConv1D
from sunset.python.modules.conv import Conv1D
from sunset.python.modules.conv import Conv1DTranspose
from sunset.python.modules.conv import Conv2D
from sunset.python.modules.conv import Conv2DTranspose
from sunset.python.modules.conv import Conv3D
from sunset.python.modules.conv import Conv3DTranspose
from sunset.python.modules.conv import DepthwiseConv2D
from sunset.python.modules.conv import InPlaneConv2D
from sunset.python.modules.conv import SAME
from sunset.python.modules.conv import SeparableConv1D
from sunset.python.modules.conv import SeparableConv2D
from sunset.python.modules.conv import VALID
from sunset.python.modules.embed import Embed
from sunset.python.modules.gated_rnn import BatchNormLSTM
from sunset.python.modules.gated_rnn import Conv1DLSTM
from sunset.python.modules.gated_rnn import Conv2DLSTM
from sunset.python.modules.gated_rnn import GRU
from sunset.python.modules.gated_rnn import highway_core_with_recurrent_dropout
from sunset.python.modules.gated_rnn import HighwayCore
from sunset.python.modules.gated_rnn import LSTM
from sunset.python.modules.gated_rnn import lstm_with_recurrent_dropout
from sunset.python.modules.gated_rnn import lstm_with_zoneout
from sunset.python.modules.gated_rnn import LSTMState
from sunset.python.modules.layer_norm import LayerNorm
from sunset.python.modules.pondering_rnn import ACTCore
from sunset.python.modules.residual import Residual
from sunset.python.modules.residual import ResidualCore
from sunset.python.modules.residual import SkipConnectionCore
from sunset.python.modules.rnn_core import RNNCore
from sunset.python.modules.rnn_core import trainable_initial_state
from sunset.python.modules.rnn_core import TrainableInitialState
from sunset.python.modules.scale_gradient import scale_gradient
from sunset.python.modules.sequential import Sequential
from sunset.python.modules.spatial_transformer import AffineGridWarper
from sunset.python.modules.spatial_transformer import AffineWarpConstraints
from sunset.python.modules.spatial_transformer import GridWarper
from sunset.python.modules.util import check_initializers
from sunset.python.modules.util import check_partitioners
from sunset.python.modules.util import check_regularizers
from sunset.python.modules.util import custom_getter_router
from sunset.python.modules.util import format_variable_map
from sunset.python.modules.util import format_variables
from sunset.python.modules.util import get_normalized_variable_map
from sunset.python.modules.util import get_saver
from sunset.python.modules.util import get_variables_in_module
from sunset.python.modules.util import get_variables_in_scope
from sunset.python.modules.util import has_variable_scope
from sunset.python.modules.util import log_variables
from sunset.python.modules.util import reuse_variables
from sunset.python.modules.util import summarize_variables
from sunset.python.modules.util import variable_map_items
from sunset.python.ops import nest
from sunset.python.ops.initializers import restore_initializer

__version__ = '1.21'

