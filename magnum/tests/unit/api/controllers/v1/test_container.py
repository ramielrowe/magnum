# Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from magnum import objects
from magnum.tests.unit.db import base as db_base
from magnum.tests.unit.db import utils

import mock
from mock import patch
from webtest.app import AppError


class TestContainerController(db_base.DbTestCase):
    @patch('magnum.objects.bay.Bay.get_by_uuid')
    @patch('magnum.conductor.api.API.container_create')
    @patch('magnum.conductor.api.API.container_delete')
    def test_create_container_with_command(self,
                                           mock_container_delete,
                                           mock_container_create,
                                           mock_get_by_uuid):
        mock_container_create.side_effect = lambda x, y, z: z
        # Create a container with a command
        params = ('{"name": "My Docker", "image_id": "ubuntu",'
                  '"command": "env",'
                  '"bay_uuid": "fff114da-3bfa-4a0f-a123-c0dffad9718e"}')
        self.fake_bay = utils.get_test_bay()
        value = self.fake_bay['uuid']
        mock_get_by_uuid.return_value = self.fake_bay
        bay = objects.Bay.get_by_uuid(self.context, value)
        self.assertEqual(value, bay['uuid'])
        response = self.app.post('/v1/containers',
                                 params=params,
                                 content_type='application/json')
        self.assertEqual(response.status_int, 201)
        # get all containers
        response = self.app.get('/v1/containers')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(1, len(response.json))
        c = response.json['containers'][0]
        self.assertIsNotNone(c.get('uuid'))
        self.assertEqual('My Docker', c.get('name'))
        self.assertEqual('env', c.get('command'))
        # Delete the container we created
        response = self.app.delete('/v1/containers/%s' % c.get('uuid'))
        self.assertEqual(response.status_int, 204)

        response = self.app.get('/v1/containers')
        self.assertEqual(response.status_int, 200)
        c = response.json['containers']
        self.assertEqual(0, len(c))
        self.assertTrue(mock_container_create.called)

    @patch('magnum.objects.bay.Bay.get_by_uuid')
    @patch('magnum.conductor.api.API.container_create')
    @patch('magnum.conductor.api.API.container_delete')
    def test_create_container_with_bay_uuid(self,
                                           mock_container_delete,
                                           mock_container_create,
                                           mock_get_by_uuid):
        mock_container_create.side_effect = lambda x, y, z: z
        # Create a container with a command
        params = ('{"name": "My Docker", "image_id": "ubuntu",'
                  '"command": "env",'
                  '"bay_uuid": "fff114da-3bfa-4a0f-a123-c0dffad9718e"}')
        self.fake_bay = utils.get_test_bay()
        value = self.fake_bay['uuid']
        mock_get_by_uuid.return_value = self.fake_bay
        bay = objects.Bay.get_by_uuid(self.context, value)
        self.assertEqual(value, bay['uuid'])
        response = self.app.post('/v1/containers',
                                 params=params,
                                 content_type='application/json')
        self.assertEqual(response.status_int, 201)
        # get all containers
        response = self.app.get('/v1/containers')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(1, len(response.json))
        c = response.json['containers'][0]
        self.assertIsNotNone(c.get('uuid'))
        self.assertEqual('My Docker', c.get('name'))
        self.assertEqual('env', c.get('command'))
        # Delete the container we created
        response = self.app.delete('/v1/containers/%s' % c.get('uuid'))
        self.assertEqual(response.status_int, 204)

        response = self.app.get('/v1/containers')
        self.assertEqual(response.status_int, 200)
        c = response.json['containers']
        self.assertEqual(0, len(c))
        self.assertTrue(mock_container_create.called)

    @patch('magnum.conductor.api.API.container_create')
    def test_create_container_without_name(self, mock_container_create):
        # No name param
        params = ('{"image_id": "ubuntu", "command": "env",'
                  '"bay_uuid": "fff114da-3bfa-4a0f-a123-c0dffad9718e"}')
        self.assertRaises(AppError, self.app.post, '/v1/containers',
                          params=params, content_type='application/json')
        self.assertTrue(mock_container_create.not_called)

    @patch('magnum.conductor.api.API.container_create')
    def test_create_container_invalid_long_name(self, mock_container_create,):
        # Long name
        params = ('{"name": "' + 'i' * 256 + '", "image_id": "ubuntu",'
                  '"command": "env",'
                  '"bay_uuid": "fff114da-3bfa-4a0f-a123-c0dffad9718e"}')
        self.assertRaises(AppError, self.app.post, '/v1/containers',
                          params=params, content_type='application/json')
        self.assertTrue(mock_container_create.not_called)


class ExistingContainerTestCase(db_base.DbTestCase):
    def setUp(self):
        super(ExistingContainerTestCase, self).setUp()
        self.bay_get_by_uuid_patch = patch('magnum.objects.Bay.get_by_uuid')
        self.mock_bay_get_by_uuid = self.bay_get_by_uuid_patch.start()
        self.addCleanup(self.bay_get_by_uuid_patch.stop)

        def fake_get_by_uuid(context, uuid):
            return objects.Bay(self.context, **utils.get_test_bay(uuid=uuid))

        self.mock_bay_get_by_uuid.side_effect = fake_get_by_uuid

    @patch('magnum.conductor.api.API.container_create')
    def test_create_container(self, mock_container_create,):
        mock_container_create.side_effect = lambda x, y, z: z

        params = ('{"name": "My Docker", "image_id": "ubuntu",'
                  '"command": "env",'
                  '"bay_uuid": "fff114da-3bfa-4a0f-a123-c0dffad9718e"}')
        response = self.app.post('/v1/containers',
                                 params=params,
                                 content_type='application/json')

        self.assertEqual(response.status_int, 201)
        self.assertTrue(mock_container_create.called)

    @patch('magnum.objects.Container.list')
    def test_get_all_containers(self, mock_container_list):
        test_container = utils.get_test_container()
        containers = [objects.Container(self.context, **test_container)]
        mock_container_list.return_value = containers

        response = self.app.get('/v1/containers')

        mock_container_list.assert_called_once_with(mock.ANY,
                                                    1000, None, sort_dir='asc',
                                                    sort_key='id')
        self.assertEqual(response.status_int, 200)
        actual_containers = response.json['containers']
        self.assertEqual(len(actual_containers), 1)
        self.assertEqual(actual_containers[0].get('uuid'),
                         test_container['uuid'])

    @patch('magnum.objects.Container.get_by_uuid')
    def test_get_one_by_uuid(self, mock_container_get_by_uuid):
        test_container = utils.get_test_container()
        test_container_obj = objects.Container(self.context, **test_container)
        mock_container_get_by_uuid.return_value = test_container_obj

        response = self.app.get('/v1/containers/%s' % test_container['uuid'])

        mock_container_get_by_uuid.assert_called_once_with(mock.ANY,
                                                       test_container['uuid'])
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.json['uuid'],
                         test_container['uuid'])

    @patch('magnum.objects.Container.get_by_name')
    def test_get_one_by_name(self, mock_container_get_by_name):
        test_container = utils.get_test_container()
        test_container_obj = objects.Container(self.context, **test_container)
        mock_container_get_by_name.return_value = test_container_obj

        response = self.app.get('/v1/containers/%s' % test_container['name'])

        mock_container_get_by_name.assert_called_once_with(mock.ANY,
                                                       test_container['name'])
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.json['uuid'],
                         test_container['uuid'])

    @patch('magnum.objects.Container.get_by_uuid')
    def test_patch_by_uuid(self, mock_container_get_by_uuid):
        test_container = utils.get_test_container()
        test_container_obj = objects.Container(self.context, **test_container)
        mock_container_get_by_uuid.return_value = test_container_obj

        with patch.object(test_container_obj, 'save') as mock_save:
            params = [{'path': '/name',
                       'value': 'new_name',
                       'op': 'replace'}]
            container_uuid = test_container.get('uuid')
            response = self.app.patch_json(
                                '/v1/containers/%s' % container_uuid,
                                params=params)

            mock_save.assert_called_once_with()
            self.assertEqual(response.status_int, 200)
            self.assertEqual(test_container_obj.name, 'new_name')

    @patch('magnum.objects.Container.get_by_name')
    def test_patch_by_name(self, mock_container_get_by_name):
        test_container = utils.get_test_container()
        test_container_obj = objects.Container(self.context, **test_container)
        mock_container_get_by_name.return_value = test_container_obj

        with patch.object(test_container_obj, 'save') as mock_save:
            params = [{'path': '/name',
                       'value': 'new_name',
                       'op': 'replace'}]
            container_name = test_container.get('name')
            response = self.app.patch_json(
                                    '/v1/containers/%s' % container_name,
                                    params=params)

            mock_save.assert_called_once_with()
            self.assertEqual(response.status_int, 200)
            self.assertEqual(test_container_obj.name, 'new_name')

    def _action_test(self, container, action, ident_field):
        test_container_obj = objects.Container(self.context, **container)
        ident = container.get(ident_field)
        get_by_ident_loc = 'magnum.objects.Container.get_by_%s' % ident_field
        with patch(get_by_ident_loc) as mock_get_by_indent:
            mock_get_by_indent.return_value = test_container_obj
            response = self.app.put('/v1/containers/%s/%s' % (ident,
                                                              action))
            self.assertEqual(response.status_int, 200)

            # Only PUT should work, others like GET should fail
            self.assertRaises(AppError, self.app.get,
                              ('/v1/containers/%s/%s' %
                               (ident, action)))

    @patch('magnum.conductor.api.API.container_start')
    def test_start_by_uuid(self, mock_container_start):
        test_container = utils.get_test_container()
        self._action_test(test_container, 'start', 'uuid')
        mock_container_start.assert_called_once_with(
                                            test_container.get('uuid'))

    @patch('magnum.conductor.api.API.container_start')
    def test_start_by_name(self, mock_container_start):
        test_container = utils.get_test_container()
        self._action_test(test_container, 'start', 'name')
        mock_container_start.assert_called_once_with(
                                            test_container.get('uuid'))

    @patch('magnum.conductor.api.API.container_stop')
    def test_stop_by_uuid(self, mock_container_stop):
        test_container = utils.get_test_container()
        self._action_test(test_container, 'stop', 'uuid')
        mock_container_stop.assert_called_once_with(
                                            test_container.get('uuid'))

    @patch('magnum.conductor.api.API.container_stop')
    def test_stop_by_name(self, mock_container_stop):
        test_container = utils.get_test_container()
        self._action_test(test_container, 'stop', 'name')
        mock_container_stop.assert_called_once_with(
                                            test_container.get('uuid'))

    @patch('magnum.conductor.api.API.container_pause')
    def test_pause_by_uuid(self, mock_container_pause):
        test_container = utils.get_test_container()
        self._action_test(test_container, 'pause', 'uuid')
        mock_container_pause.assert_called_once_with(
                                            test_container.get('uuid'))

    @patch('magnum.conductor.api.API.container_pause')
    def test_pause_by_name(self, mock_container_pause):
        test_container = utils.get_test_container()
        self._action_test(test_container, 'pause', 'name')
        mock_container_pause.assert_called_once_with(
                                            test_container.get('uuid'))

    @patch('magnum.conductor.api.API.container_unpause')
    def test_unpause_by_uuid(self, mock_container_unpause):
        test_container = utils.get_test_container()
        self._action_test(test_container, 'unpause', 'uuid')
        mock_container_unpause.assert_called_once_with(
                                                test_container.get('uuid'))

    @patch('magnum.conductor.api.API.container_unpause')
    def test_unpause_by_name(self, mock_container_unpause):
        test_container = utils.get_test_container()
        self._action_test(test_container, 'unpause', 'name')
        mock_container_unpause.assert_called_once_with(
                                                test_container.get('uuid'))

    @patch('magnum.conductor.api.API.container_reboot')
    def test_reboot_by_uuid(self, mock_container_reboot):
        test_container = utils.get_test_container()
        self._action_test(test_container, 'reboot', 'uuid')
        mock_container_reboot.assert_called_once_with(
                                                test_container.get('uuid'))

    @patch('magnum.conductor.api.API.container_reboot')
    def test_reboot_by_name(self, mock_container_reboot):
        test_container = utils.get_test_container()
        self._action_test(test_container, 'reboot', 'name')
        mock_container_reboot.assert_called_once_with(
                                                test_container.get('uuid'))

    @patch('magnum.conductor.api.API.container_logs')
    @patch('magnum.objects.Container.get_by_uuid')
    def test_get_logs_by_uuid(self, mock_get_by_uuid, mock_container_logs):
        test_container = utils.get_test_container()
        test_container_obj = objects.Container(self.context, **test_container)
        mock_get_by_uuid.return_value = test_container_obj

        container_uuid = test_container.get('uuid')
        response = self.app.get('/v1/containers/%s/logs' % container_uuid)

        self.assertEqual(response.status_int, 200)
        mock_container_logs.assert_called_once_with(container_uuid)

    @patch('magnum.conductor.api.API.container_logs')
    @patch('magnum.objects.Container.get_by_name')
    def test_get_logs_by_name(self, mock_get_by_name, mock_container_logs):
        test_container = utils.get_test_container()
        test_container_obj = objects.Container(self.context, **test_container)
        mock_get_by_name.return_value = test_container_obj

        container_name = test_container.get('name')
        container_uuid = test_container.get('uuid')
        response = self.app.get('/v1/containers/%s/logs' % container_name)

        self.assertEqual(response.status_int, 200)
        mock_container_logs.assert_called_once_with(container_uuid)

    @patch('magnum.conductor.api.API.container_logs')
    @patch('magnum.objects.Container.get_by_uuid')
    def test_get_logs_put_fails(self, mock_get_by_uuid, mock_container_logs):
        test_container = utils.get_test_container()
        test_container_obj = objects.Container(self.context, **test_container)
        mock_get_by_uuid.return_value = test_container_obj

        container_uuid = test_container.get('uuid')
        self.assertRaises(AppError, self.app.put,
                          '/v1/containers/%s/logs' % container_uuid)
        self.assertFalse(mock_container_logs.called)

    @patch('magnum.conductor.api.API.container_execute')
    @patch('magnum.objects.Container.get_by_uuid')
    def test_execute_command_by_uuid(self, mock_get_by_uuid,
                                     mock_container_execute):
        test_container = utils.get_test_container()
        test_container_obj = objects.Container(self.context, **test_container)
        mock_get_by_uuid.return_value = test_container_obj

        container_uuid = test_container.get('uuid')
        url = '/v1/containers/%s/%s' % (container_uuid, 'execute')
        cmd = {'command': 'ls'}
        response = self.app.put(url, cmd)
        self.assertEqual(response.status_int, 200)
        mock_container_execute.assert_called_one_with(container_uuid, cmd)

    @patch('magnum.conductor.api.API.container_execute')
    @patch('magnum.objects.Container.get_by_name')
    def test_execute_command_by_name(self, mock_get_by_name,
                                     mock_container_execute):
        test_container = utils.get_test_container()
        test_container_obj = objects.Container(self.context, **test_container)
        mock_get_by_name.return_value = test_container_obj

        container_name = test_container.get('name')
        container_uuid = test_container.get('uuid')
        url = '/v1/containers/%s/%s' % (container_name, 'execute')
        cmd = {'command': 'ls'}
        response = self.app.put(url, cmd)
        self.assertEqual(response.status_int, 200)
        mock_container_execute.assert_called_one_with(container_uuid, cmd)

    @patch('magnum.conductor.api.API.container_delete')
    @patch('magnum.objects.Container.get_by_uuid')
    def test_delete_container_by_uuid(self, mock_get_by_uuid,
                                      mock_container_delete):
        test_container = utils.get_test_container()
        test_container_obj = objects.Container(self.context, **test_container)
        mock_get_by_uuid.return_value = test_container_obj

        with patch.object(test_container_obj, 'destroy') as mock_destroy:
            container_uuid = test_container.get('uuid')
            response = self.app.delete('/v1/containers/%s' % container_uuid)

            self.assertEqual(response.status_int, 204)
            mock_container_delete.assert_called_once_with(container_uuid)
            mock_destroy.assert_called_once_with()

    @patch('magnum.conductor.api.API.container_delete')
    @patch('magnum.objects.Container.get_by_name')
    def test_delete_container_by_name(self, mock_get_by_name,
                                      mock_container_delete):
        test_container = utils.get_test_container()
        test_container_obj = objects.Container(self.context, **test_container)
        mock_get_by_name.return_value = test_container_obj

        with patch.object(test_container_obj, 'destroy') as mock_destroy:
            container_name = test_container.get('name')
            container_uuid = test_container.get('uuid')
            response = self.app.delete('/v1/containers/%s' % container_name)

            self.assertEqual(response.status_int, 204)
            mock_container_delete.assert_called_once_with(container_uuid)
            mock_destroy.assert_called_once_with()
