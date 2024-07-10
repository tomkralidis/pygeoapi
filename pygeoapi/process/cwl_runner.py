# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#
# Copyright (c) 2024 Tom Kralidis
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import logging
from typing import Any

from cwl_utils.parser import load_document_by_string
from cwltool.factory import Factory

from pygeoapi.process.base import BaseProcessor


LOGGER = logging.getLogger(__name__)

#: Process metadata and description
PROCESS_METADATA = {
    'version': '0.1.0',
    'id': 'cwl-runner',
    'title': {
        'en': 'CWL Runner',
    },
    'description': {
        'en': 'CWL runner'
    },
    'jobControlOptions': ['sync-execute', 'async-execute'],
    'keywords': ['cwl-runner'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://www.commonwl.org',
        'hreflang': 'en-US'
    }],
    'inputs': {
    },
    'outputs': {
    }
}


class CwlRunnerProcessor(BaseProcessor):
    """CWL runner Processor example"""

    def __init__(self, processor_def):
        """
        Initialize object

        :param processor_def: provider definition

        :returns: pygeoapi.process.cwl_runner.CwlRunnerProcessor
        """

        super().__init__(processor_def, PROCESS_METADATA)
        self.cwl = processor_def.get('cwl')
        self.supports_outputs = True
        self.mutable = True

    def execute(self, data, outputs=None):
        mimetype = 'application/json'

        LOGGER.debug(f'Data {data}')
        LOGGER.debug(f'Loading CWL file {self.cwl}')

        cwl_factory = Factory()

        workflow = cwl_factory.make(self.cwl)

        result = workflow(**data)

        produced_outputs = {}
        if not bool(outputs) or 'echo' in outputs:
            produced_outputs = {
                'id': 'cwl-runner-output',
                'value': result
            }

        return mimetype, produced_outputs

    def create(self, data: Any):

        cwl = load_document_by_string(data, 'pygeoapi-cwl-runner-process')

        process_id = cwl.id.split('#')[-1]

        # FIXME: do not hard code basedir
        # filename = f'/{api.manager.output_dir}/{process_id}'
        filename = f'/tmp/{process_id}'
        with open(filename, 'wb') as fh:
            fh.write(data)

        return process_id

    def __repr__(self):
        return f'<CwlRunnerProcessor> {self.name}'
