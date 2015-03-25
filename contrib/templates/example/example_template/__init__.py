# Copyright (c) 2015 Rackspace Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from magnum.conductor import template_definition


class ExampleTemplate(template_definition.TemplateDefinition):
    provides = [
        {'platform': 'vm', 'os': 'example', 'coe': 'example_coe'},
    ]

    def __init__(self):
        super(ExampleTemplate, self).__init__()
        self.add_parameter('ssh_key_name',
                           baymodel_attr='keypair_id',
                           required=True)

        self.add_parameter('server_image',
                           baymodel_attr='image_id')
        self.add_parameter('master_flavor',
                           baymodel_attr='master_flavor_id')

        self.add_output('api_address', 'server_address')
        self.add_output('node_addresses', 'node_addresses')

    def template_path(self):
        return os.path.join(os.path.dirname(__file__), 'example.yaml')
