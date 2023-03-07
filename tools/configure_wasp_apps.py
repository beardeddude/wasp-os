"""Configure the wasp distribution based on the provided wasp.toml config

    This script generates the following files and directories
        wasp/apps/user/
        wasp/boards/manifest_user_apps.py
        wasp/appregistry.py
"""

import tomli
import os
import sys


with open(sys.argv[1:][0], 'rb') as config_file:
  config = tomli.load(config_file)

  # Copy selected apps to the wasp app user directory
  for app in config.get('app'):
      os.system('cp ' + app.get('file') + ' wasp/apps/user/' + app.get('file').split('/')[-1])

  # Copy selected watch faces to the wasp app user directory
  for app in config.get('watchface'):
      os.system('cp ' + app.get('file') + ' wasp/apps/user/' + app.get('file').split('/')[-1])

  # Create the user app manifest containing all user apps and watch faces
  with open('wasp/boards/manifest_user_apps.py', 'w') as manifest_file:
      manifest_file.write('# This file is auto generated from the wasp.toml. Manual changes will be overwritten. \n\n')
      manifest_file.write('manifest = (\n')
      for app in config.get('app'):
          manifest_file.write('    \'' + 'apps/user/' + app.get('file').split('/')[-1] + '\',\n')
      for watchface in config.get('watchface'):
          manifest_file.write('    \'' + 'apps/user/' + watchface.get('file').split('/')[-1] + '\',\n')
      manifest_file.write(')')

  # Create a registry for the os to use to populate its lists
  with open('wasp/appregistry.py', 'w') as reg_file:

    # Software to display in the software app
    reg_file.write('# This file is auto generated from the wasp.toml. Manual changes will be overwritten. \n\n')
    reg_file.write('software_list = (\n')
    for app in config.get('app'):
        if not app.get('quick_ring'):
            app_module_name = 'apps.user.' + app.get('file').split('/')[-1].split('.')[0]
            app_display_name = app.get('class')[:-3]
            reg_file.write('    (\'' + app_module_name + '\', \'' + app_display_name + '\'),\n')
    reg_file.write(')\n\n')

    # Software to display in the faces app
    reg_file.write('faces_list = (\n')
    for face in config.get('watchface'):
        watchface_module = 'apps.user.' + face.get('file').split('/')[-1].split('.')[0]
        watchface_class = face.get('class')[:-3]
        reg_file.write('    (\'' + watchface_module + '\',\'' + watchface_class + '\'),\n')
    reg_file.write(')\n\n')


    # Software to be loaded at startup (default watch face, quick ring apps, any apps marked auto_load in the config)
    reg_file.write('autoload_list = (\n')

    # Fist app to autoload should be the default watch face
    default_watchface = None
    for watchface in config.get('watchface'):
        if watchface.get('default'):
            default_watchface = watchface
        elif not default_watchface:
            default_watchface = watchface
    watchface_path = 'apps.user.' + default_watchface.get('file').split('/')[-1].split('.')[0] + '.' + default_watchface.get('class')
    reg_file.write('    (\'' + watchface_path + '\', True, False, True),\n')

    # The next apps should be the quick ring and any auto_load apps (in order specified in the config)
    for app in config.get('app'):
        if (app.get('quick_ring') or app.get('auto_load')):
            app_path = 'apps.user.' + app.get('file').split('/')[-1].split('.')[0] + '.' + app.get('class')
            app_quick_ring = str(not (app.get('quick_ring') is None))
            app_no_except = str(not (app.get('no_except') is None))
            reg_file.write('    (\'' + app_path + '\', ' + app_quick_ring + ', False, ' + app_no_except + '),\n')
    reg_file.write(')\n\n')

