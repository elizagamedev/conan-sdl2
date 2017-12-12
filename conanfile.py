#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class SDL2Conan(ConanFile):
    name = "sdl2"
    version = "2.0.7"
    url = "https://github.com/bincrafters/conan-libname"
    description = "Simple DirectMedia Layer is a cross-platform development library designed to provide low level " \
                  "access to audio, keyboard, mouse, joystick, and graphics hardware via OpenGL and Direct3D"
    license = "hhttps://hg.libsdl.org/SDL/file/5c8fc26757d7/COPYING.txt"
    exports_sources = ["CMakeLists.txt", "LICENSE"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "directx": [True, False],
               "alsa": [True, False],
               "jack": [True, False],
               "pulse": [True, False],
               "nas": [True, False],
               "esd": [True, False]}
    default_options = ("shared=False",
                       "directx=True",
                       "alsa=True",
                       "jack=True",
                       "pulse=True",
                       "nas=True",
                       "esd=True")
    generators = ['cmake']

    def build_requirements(self):
        self.build_requires("ninja_installer/[>=1.8.2]@bincrafters/stable")

    def requirements(self):
        self.requires.add("libiconv/[>=1.15]@bincrafters/stable")

    def system_requirements(self):
        if self.settings.os == "Linux" and tools.os_info.is_linux:
            if tools.os_info.with_apt:
                installer = tools.SystemPackageTool()
                arch_suffix = ''
                if self.settings.arch == "x86" and tools.detected_architecture() == "x86_64":
                    arch_suffix = ':i386'
                packages = ['pkg-config']
                if self.options.alsa:
                    packages.append('libasound2-dev%s' % arch_suffix)
                if self.options.jack:
                    packages.append('libjack-dev%s' % arch_suffix)
                if self.options.pulse:
                    packages.append('libpulse-dev%s' % arch_suffix)
                if self.options.nas:
                    packages.append('libaudio-dev%s' % arch_suffix)
                if self.options.esd:
                    packages.append('libesd0-dev%s' % arch_suffix)
                for package in packages:
                    installer.install(package)

    def config_options(self):
        if self.settings.os != "Linux":
            self.options.remove("alsa")
            self.options.remove("jack")
            self.options.remove("pulse")
            self.options.remove("nas")
            self.options.remove("esd")
        if self.settings.os != "Windows":
            self.options.remove("directx")

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        source_url = "https://www.libsdl.org/release/SDL2-%s.tar.gz" % self.version
        tools.get(source_url)
        extracted_dir = "SDL2-" + self.version
        os.rename(extracted_dir, "sources")

    def build(self):
        cmake = CMake(self, generator='Ninja')
        cmake.definitions['HAVE_LIBC'] = True
        cmake.definitions['SDL_SHARED'] = self.options.shared
        cmake.definitions['SDL_STATIC'] = not self.options.shared
        if self.settings.os == "Linux":
            cmake.definitions['ALSA'] = self.options.alsa
            cmake.definitions['JACK'] = self.options.jack
            cmake.definitions['PULSEAUDIO'] = self.options.pulse
            cmake.definitions['NAS'] = self.options.nas
        elif self.settings.os == "Windows":
            cmake.definitions["DIRECTX"] = self.options.directx
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        self.copy(pattern="COPYING.txt", src="sources")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join('include', 'SDL2'))
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(['dl', 'rt', 'pthread'])
            if self.options.alsa:
                self.cpp_info.libs.append('asound')
            if self.options.jack:
                self.cpp_info.libs.append('jack')
            if self.options.pulse:
                self.cpp_info.libs.append('pulse')
            if self.options.nas:
                self.cpp_info.libs.append('audio')
            if self.options.esd:
                self.cpp_info.libs.append('esd')
        elif self.settings.os == "Macos":
            frameworks = ['Cocoa', 'Carbon', 'IOKit', 'CoreVideo', 'CoreAudio', 'AudioToolbox', 'ForceFeedback']
            for framework in frameworks:
                self.cpp_info.exelinkflags.append("-framework %s" % framework)
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
        elif self.settings.os == "Windows":
            self.cpp_info.libs.extend(['imm32', 'winmm', 'version'])
