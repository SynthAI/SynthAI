# Copyright 2018 The Synthnetes Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"synthnetes error classes"


class SynthnetesError(Exception):
    "generic synthnetes error"
    pass


class CompileError(SynthnetesError):
    "compile error"
    pass


class InventoryError(SynthnetesError):
    "inventory error"
    pass


class SecretError(SynthnetesError):
    "secrets error"
    pass
