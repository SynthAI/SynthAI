#!/usr/bin/env python3.6
#
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

"compile tests"

import unittest
import os
import sys
import shutil
from synthnetes.cli import main
from synthnetes.utils import get_directory_hash

class CompileTest(unittest.TestCase):
    def setUp(self):
        os.chdir(os.getcwd() + '/examples/kubernetes/')

    def test_compile(self):
        sys.argv = ["synthnetes", "compile"]
        main()
        compiled_dir_hash = get_directory_hash(os.getcwd() + '/compiled')
        test_compiled_dir_hash = get_directory_hash(os.getcwd() + '/../../tests/test_kubernetes_compiled')
        self.assertEqual(compiled_dir_hash, test_compiled_dir_hash)

    def tearDown(self):
        os.chdir(os.getcwd() + '/../../')
