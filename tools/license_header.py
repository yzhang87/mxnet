# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Add or check license header

Usuage:

- add the default license header to source files that do not contain a valid
  license:

  python license_header.py add

- check if every files has a license header

  python license_header.py check
"""

import re
import os

# the default apache license
_LICENSE = """Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License."""

# if a file contains any str in the list, then consider it has been licensed
_LICENSE_PATTERNS = ['Licensed to the Apache Software Foundation']

# the folders or files that will be ignored
_WHITE_LIST = ['R-package/',
               'cub/',
               'dlpack/',
               'dmlc-core/',
               'mshadow/',
               'nnvm',
               'ps-lite',
               'src/operator/mkl/',
               'src/operator/contrib/ctc_include/']

# language extensions and the according commment mark
_LANGS = {'.cc':'*', '.h':'*', '.cu':'*', '.cuh':'*', '.py':'#',
          '.pm':'#', '.scala':'*', '.cc':'*', '.sh':'#', '.cmake':'#'}

# Previous license header, which will be removed
_OLD_LICENSE = re.compile('.*Copyright.*by Contributors')

def _has_license(lines):
    return any([any([p in l for p in _LICENSE_PATTERNS]) for l in lines])

def _get_license(comment_mark):
    if comment_mark == '*':
        body = '/*\n'
    else:
        body = ''
    for l in _LICENSE.split('\n'):
        if comment_mark == '*':
            body += ' '
        body += comment_mark
        if len(l):
            body += ' ' + l
        body += '\n'

    if comment_mark == '*':
        body += ' */\n'
    body += '\n'
    return body

def valid_file(fname, verbose=False):
    if any([l in fname for l in _WHITE_LIST]):
        if verbose:
            print('skip ' + fname + ', it matches the white list')
        return False
    _, ext = os.path.splitext(fname)
    if ext not in _LANGS:
        if verbose:
            print('skip ' + fname + ', unknown file extension')
        return False
    return True

def process_file(fname, verbose=False):
    if not valid_file(fname, verbose):
        return
    with open(fname, 'r') as f:
        lines = f.readlines()
    if not lines:
        return
    if _has_license(lines):
        return
    _, ext = os.path.splitext(fname)
    # remove old license
    if ext == '.h' or ext == '.cc' or ext == '.cu':
        for i, l in enumerate(lines):
            if _OLD_LICENSE.match(l):
                del lines[i]
                break
    with open(fname, 'w') as f:
        # shebang line
        if lines[0].startswith('#!'):
            f.write(lines[0]+'\n')
            del lines[0]
        f.write(_get_license(_LANGS[ext]))
        for l in lines:
            f.write(l)
    print('added license header to ' + fname)

def process_folder(root):
    for root, _, files in os.walk(root):
        for f in files:
            process_file(os.path.join(root, f))

if __name__ == '__main__':
    process_folder(os.path.join(os.path.dirname(__file__), '..'))
    # process_folder('python/mxnet/rnn/')
