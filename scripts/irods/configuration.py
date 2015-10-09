from __future__ import print_function
import contextlib
import inspect
import json
import logging
import os
import sys

from . import six
from . import pypyodbc

from . import database_connect
from .exceptions import IrodsError, IrodsWarning
from . import lib
from . import json_validation

class IrodsConfig(object):
    def __init__(self,
                 top_level_directory=None,
                 config_directory=None,
                 injected_environment={},
                 insert_behavior=True):

        self._top_level_directory = top_level_directory
        self._config_directory = config_directory
        self._injected_environment = lib.callback_on_change_dict(self.clear_cache, injected_environment)
        self._insert_behavior = insert_behavior
        self.clear_cache()

    @property
    def version_tuple(self):
        if os.path.exists(self.version_path):
            return tuple(map(int, self.version['irods_version'].split('.')))

        legacy_version_file_path = os.path.join(self.top_level_directory, 'VERSION')
        if os.path.exists(legacy_version_file_path):
            with open(legacy_version_file_path) as f:
                for line in f:
                    key, _, value = line.strip().partition('=')
                    if key == 'IRODSVERSION':
                        return tuple(map(int, value.split('.')))

        raise IrodsError('Unable to determine iRODS version')

    @property
    def top_level_directory(self):
        return self._top_level_directory if self._top_level_directory else get_default_top_level_directory()

    @top_level_directory.setter
    def top_level_directory(self, value):
        self.clear_cache()
        self._top_level_directory = value

    @property
    def config_directory(self):
        if self._config_directory:
            return self._config_directory
        elif self.binary_installation:
            return os.path.join(
                lib.get_root_directory(),
                'etc',
                'irods')
        else:
            return os.path.join(
                self._irods_directory,
                'server',
                'config')

    @config_directory.setter
    def config_directory(self, value):
        self.clear_cache()
        self._config_directory = value

    @property
    def binary_installation(self):
        if self._binary_installation is None:
            self._binary_installation = os.path.exists(
                    os.path.join(
                        self.top_level_directory,
                        'packaging',
                        'binary_installation.flag'))
        return self._binary_installation

    @property
    def core_re_directory(self):
        if self.binary_installation:
            return self.config_directory
        else:
            return os.path.join(self.config_directory, 'reConfigs')

    @property
    def scripts_directory(self):
        return os.path.join(self.top_level_directory, 'scripts')

    @property
    def irods_directory(self):
        return os.path.join(
            self.top_level_directory,
            'iRODS')

    @property
    def server_config_path(self):
        return os.path.join(
            self.config_directory,
            'server_config.json')

    @property
    def server_config(self):
        if self._server_config is None:
            self._server_config = load_json_config(self.server_config_path)
        return self._server_config

    @property
    def database_config_path(self):
        return os.path.join(
            self.config_directory,
            'database_config.json')

    @property
    def database_config(self):
        if self._database_config is None:
            self._database_config = load_json_config(self.database_config_path)
            if not 'db_odbc_driver' in self._database_config.keys():
                l = logging.getLogger(__name__)
                odbc_ini_path = database_connect.get_odbc_ini_path()
                l.debug('No driver found in the database config, attempting to retrieve the one in the odbc ini file at "%s"...', odbc_ini_path)
                if os.path.exists(odbc_ini_path):
                    with open(odbc_ini_path) as f:
                        odbc_ini_contents = database_connect.load_odbc_ini(f)
                else:
                    l.debug('No odbc.ini file present')
                    odbc_ini_contents = {}
                if self._database_config['catalog_database_type'] in odbc_ini_contents.keys() and 'Driver' in odbc_ini_contents[self._database_config['catalog_database_type']].keys():
                    self._database_config['db_odbc_driver'] = odbc_ini_contents[self._database_config['catalog_database_type']]['Driver']
                    l.debug('Adding driver "%s" to database_config', self._database_config['db_odbc_driver'])
                    self.commit(self._database_config, self.database_config_path, clear_cache=False)
                else:
                    l.debug('Unable to retrieve "Driver" field from odbc ini file')

        return self._database_config

    @property
    def version_path(self):
        return os.path.join(
            self.top_level_directory,
            'VERSION.json')

    @property
    def version(self):
        if self._version is None:
            self._version = load_json_config(self.version_path)
        return self._version

    @property
    def hosts_config_path(self):
        return os.path.join(
            self.config_directory,
            'hosts_config.json')

    @property
    def hosts_config(self):
        if self._hosts_config is None:
            self._hosts_config = load_json_config(self.hosts_config_path)
        return self._hosts_config

    @property
    def host_access_control_config_path(self):
        return os.path.join(
            self.config_directory,
            'host_access_control_config.json')

    @property
    def host_access_control_config(self):
        if self._host_access_control_config is None:
            self._host_access_control_config = load_json_config(self.host_access_control_config_path)
        return self._host_access_control_config

    @property
    def client_environment_path(self):
        if 'IRODS_ENVIRONMENT_FILE' in self.execution_environment:
            return self.execution_environment['IRODS_ENVIRONMENT_FILE']
        else:
            return get_default_client_environment_path()

    @property
    def client_environment(self):
        if self._client_environment is None:
            self._client_environment = load_json_config(self.client_environment_path)
        return self._client_environment

    @property
    def server_environment(self):
        return self.server_config.get('environment_variables', {})

    @property
    def execution_environment(self):
        if self._execution_environment is None:
            if self.insert_behavior:
                self._execution_environment = dict(self.server_environment)
                self._execution_environment.update(os.environ)
                self._execution_environment['irodsConfigDir'] = self.config_directory
                self._execution_environment['PWD'] = self.server_bin_directory
                self._execution_environment.update(self.injected_environment)
            else:
                self._execution_environment = dict(self.injected_environment)
        return self._execution_environment

    @property
    def insert_behavior(self):
        return self._insert_behavior

    @insert_behavior.setter
    def insert_behavior(self, value):
        self._insert_behavior = value
        self.clear_cache()

    @property
    def injected_environment(self):
        return self._injected_environment

    @injected_environment.setter
    def injected_environment(self, value):
        self._injected_environment = lib.callback_on_change_dict(self.clear_cache, value if value is not None else {})
        self.clear_cache()

    @property
    def log_directory(self):
        return os.path.join(
            self.top_level_directory,
            'log')

    @property
    def control_log_path(self):
        return os.path.join(
            self.log_directory,
            'control_log.txt')

    @property
    def test_log_path(self):
        return os.path.join(
            self.log_directory,
            'test_log.txt')

    @property
    def icommands_test_directory(self):
        return os.path.join(
            self.irods_directory,
            'clients',
            'icommands',
            'test')

    @property
    def server_test_directory(self):
        return os.path.join(
            self.irods_directory,
            'server',
            'test',
            'bin')

    @property
    def server_log_directory(self):
        return os.path.join(
            self.irods_directory,
            'server',
            'log')

    @property
    def server_log_path(self):
        return sorted([os.path.join(self.server_log_directory, name)
                for name in os.listdir(self.server_log_directory)
                if name.startswith('rodsLog')],
            key=lambda path: os.path.getctime(path))[-1]

    @property
    def re_log_path(self):
        return sorted([os.path.join(self.server_log_directory, name)
                for name in os.listdir(self.server_log_directory)
                if name.startswith('reLog')],
            key=lambda path: os.path.getctime(path))[-1]

    @property
    def server_bin_directory(self):
        return os.path.join(
            self.irods_directory,
            'server',
            'bin')

    @property
    def server_executable(self):
        return os.path.join(
            self.server_bin_directory,
            'irodsServer')

    @property
    def rule_engine_executable(self):
        return os.path.join(
            self.server_bin_directory,
            'irodsReServer')

    @property
    def xmsg_server_executable(self):
        return os.path.join(
            self.server_bin_directory,
            'irodsXmsgServer')

    @property
    def agent_executable(self):
        return os.path.join(
            self.server_bin_directory,
            'irodsAgent')

    @property
    def schema_uri_prefix(self):
        if self._schema_uri_prefix is None:
            l = logging.getLogger(__name__)
            l.debug('Attempting to construct schema URI...')
            try:
                key = 'schema_validation_base_uri'
                base_uri = self.server_config[key]
            except KeyError:
                base_uri = None
                raise IrodsWarning(
                        '%s did not contain \'%s\'' %
                        (self.server_config_path, key))

            try:
                key = 'configuration_schema_version'
                uri_version = self.version[key]
            except KeyError:
                uri_version = None
                raise IrodsWarning(
                        '%s did not contain \'%s\'' %
                        (self.version_path, key))

            self._schema_uri_prefix = '/'.join([
                    base_uri,
                    'v%s' % (uri_version)])
            l.debug('Successfully constructed schema URI.')
        return self._schema_uri_prefix

    @property
    def database_schema_update_directory(self):
        if self.binary_installation:
            return os.path.join(
                    self.top_level_directory,
                    'packaging',
                    'schema_updates')
        else:
            return os.path.join(
                    self.top_level_directory,
                    'plugins',
                    'database',
                    'packaging',
                    'schema_updates')

    def get_database_connection(self):
        return database_connect.get_connection(self.database_config)

    def get_next_schema_update_path(self, cursor=None):
        database_schema_version = self.get_schema_version_in_database(cursor)
        if database_schema_version is not None:
            return os.path.join(
                    self.database_schema_update_directory,
                    '%d.%s.sql' % (
                        database_schema_version + 1,
                        self.database_config['catalog_database_type']))

    def get_schema_version_in_database(self, cursor=None):
        if not os.path.exists(self.database_config_path):
            return None

        if cursor is None:
            with contextlib.closing(database_connect.get_connection(self.database_config)) as connection:
                with contextlib.closing(connection.cursor()) as cursor:
                    return self.get_schema_version_in_database(cursor)
        else:
            l = logging.getLogger(__name__)
            query = "select option_value from R_GRID_CONFIGURATION where namespace='database' and option_name='schema_version';"
            try :
                l.debug('Executing query: %s' % (query))
                rows = cursor.execute(query).fetchall()
            except pypyodbc.Error:
                six.reraise(IrodsError,
                        IrodsError('pypyodbc encountered an error executing '
                            'the query:\n\t%s' % (query)),
                        sys.exc_info()[2])
            if len(rows) == 0:
                raise IrodsError('No schema version present, unable to upgrade. '
                        'If this is an upgrade from a pre-4.0 installation, '
                        'a manual upgrade is required.')
            if len(rows) > 1:
                raise IrodsError('Expected one row when querying '
                    'for database schema version, received %d rows' % (len(rows)))

            try:
                schema_version = int(rows[0][0])
            except ValueError:
                raise RuntimeError(
                    'Failed to convert [%s] to an int for database schema version' % (rows[0][0]))
            l.debug('Schema_version in database: %s' % (schema_version))

            return schema_version

    def validate_configuration(self):
        l = logging.getLogger(__name__)

        configuration_schema_mapping = {
                'server_config': {
                    'dict': self.server_config,
                    'path': self.server_config_path},
                'VERSION': {
                    'dict': self.version,
                    'path': self.version_path},
                'hosts_config': {
                    'dict': self.hosts_config,
                    'path': self.hosts_config_path},
                'host_access_control_config': {
                    'dict': self.host_access_control_config,
                    'path': self.host_access_control_config_path},
                'irods_environment': {
                    'dict': self.client_environment,
                    'path': self.client_environment_path}}

        if os.path.exists(self.database_config_path):
            configuration_schema_mapping['database_config'] = {
                    'dict': self.database_config,
                    'path': self.database_config_path}
        else:
            l.debug('The database config file, \'%s\', does not exist.', self.database_config_path)

        skipped = []

        for schema_uri_suffix, config_file in configuration_schema_mapping.items():
            try:
                schema_uri = '%s/%s.json' % (
                        self.schema_uri_prefix,
                        schema_uri_suffix)
            except IrodsError as e:
                l.debug('Failed to construct schema URI')
                six.reraise(IrodsWarning, IrodsWarning('%s\n%s' % (
                        'Preflight Check problem:',
                        lib.indent('JSON Configuration Validation failed.'))),
                    sys.exc_info()[2])

            l.debug('Attempting to validate against %s against %s', config_file['path'], schema_uri)
            try:
                json_validation.validate_dict(
                        config_file['dict'],
                        schema_uri,
                        name=config_file['path'])
            except IrodsWarning as e:
                l.warning(e)
                l.warning('Warning encountered in json_validation for %s, skipping validation...',
                        config_file['path'])
                l.debug('Exception:', exc_info=True)
                skipped.append(config_file['path'])
        if skipped:
            raise IrodsWarning('%s\n%s' % (
                'Skipped validation for the following files:',
                lib.indent(*skipped)))

    def commit(self, config_dict, path, clear_cache=True):
        l = logging.getLogger(__name__)
        l.info('Updating %s...', path)
        with open(path, mode='w') as f:
            json.dump(config_dict, f, indent=4, sort_keys=True)
        if clear_cache:
            self.clear_cache()

    def clear_cache(self):
        self._database_config = None
        self._server_config = None
        self._version = None
        self._hosts_config = None
        self._host_access_control_config = None
        self._client_environment = None
        self._binary_installation = None
        self._schema_uri_prefix = None
        self._execution_environment = None

def load_json_config(path):
    l = logging.getLogger(__name__)
    if os.path.exists(path):
        l.debug('Loading %s into dictionary', path)
        try :
            return lib.open_and_load_json(path)
        except ValueError as e:
            six.reraise(IrodsError,
                    IrodsError('%s\n%s' % (
                        'JSON load failed for [%s]:' % (path),
                        lib.indent('Invalid JSON.',
                            '%s: %s' % (e.__class__.__name__, e)))),
                    sys.exc_info()[2])
    else:
        raise IrodsError(
            'File %s does not exist.' % (path))

def get_default_client_environment_path():
    return os.path.join(
        lib.get_home_directory(),
        '.irods',
        'irods_environment.json')

def get_default_top_level_directory():
    scripts_directory = os.path.dirname(os.path.dirname(os.path.abspath(
        inspect.stack()[0][1])))
    return os.path.dirname(
            scripts_directory)