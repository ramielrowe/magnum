#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Starter script for magnum-template-manage."""

from oslo_config import cfg
import prettytable

from magnum.conductor import template_definition
from magnum.openstack.common import log as logging

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


def is_enabled(name):
    return name in CONF.bay.enabled_definitions


def shift_lines_right(lines, num_spaces):
    return [' ' * num_spaces + row for row in lines]


def details(definition):
    columns = ['Platform', 'OS', 'CoE']
    table = prettytable.PrettyTable(columns)
    for column in columns:
        table.align[column] = 'l'

    for bay_type in definition.provides:
        table.add_row([bay_type['platform'],
                       bay_type['os'],
                       bay_type['coe']])

    table_lines = table.get_string(border=False).split('\n')
    return shift_lines_right(table_lines, 4)


def to_string(name, definition):
    lines = ['  %s: %s' % (name, definition.template_path())]
    if CONF.command.details:
        lines.extend(details(definition))
    return lines


def list_templates():
    enabled_lines = []
    disabled_lines = []
    templates = dict()

    for entry_point, cls in template_definition.load_entry_points():
        templates[entry_point.name] = cls()

    for name, definition in templates.iteritems():
        lines = to_string(name, definition)
        if is_enabled(name):
            enabled_lines.extend(lines)
        else:
            disabled_lines.extend(lines)

    if not CONF.command.disabled:
        print('Enabled Templates')
        print('\n'.join(enabled_lines))

    if not CONF.command.enabled:
        print('Disabled Templates')
        print('\n'.join(disabled_lines))


def add_command_parsers(subparsers):
    parser = subparsers.add_parser('list-templates')
    parser.set_defaults(func=list_templates)
    parser.add_argument('-d', '--details', action='store_true')
    parser.add_argument('--enabled', action='store_true')
    parser.add_argument('--disabled', action='store_true')


def main():
    command_opt = cfg.SubCommandOpt('command',
                                    title='Command',
                                    help='Available commands',
                                    handler=add_command_parsers)
    CONF.register_cli_opt(command_opt)

    CONF(project='magnum')
    CONF.command.func()
