#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


from bincrafters import build_template_default
import platform


def add_build_requires(builds):
    return map(add_required_installers, builds)

def add_required_installers(build):
    installers = ['ninja_installer/1.8.2@bincrafters/stable']
    build.build_requires.update({"*" : installers})
    return build

if __name__ == "__main__":

    builder = build_template_default.get_builder()

    builder.items = add_build_requires(builder.items)

    filtered_builds = []
    for settings, options, env_vars, build_requires, reference in builder.items:
        modified_options = options.copy()
        if platform.system() == 'Linux':
            modified_options['sdl2:esd'] = 'False'
            modified_options['sdl2:wayland'] = 'True'
            modified_options['sdl2:x11'] = 'True'
        filtered_builds.append([settings, modified_options, env_vars, build_requires])
    builder.builds = filtered_builds
    builder.run()
