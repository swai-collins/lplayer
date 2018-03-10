#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# listboxrowwithdata.py
#
# This file is part of yoaup (YouTube Audio Player)
#
# Copyright (C) 2017
# Lorenzo Carbonell Cerezo <lorenzo.carbonell.cerezo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import gi
try:
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gdk', '3.0')
    gi.require_version('Gio', '2.0')
    gi.require_version('GLib', '2.0')
    gi.require_version('GObject', '2.0')
    gi.require_version('GdkPixbuf', '2.0')
    gi.require_version('Notify', '0.7')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import GdkPixbuf
import time
from .utils import get_pixbuf_from_base64string
from . import comun

PLAY = GdkPixbuf.Pixbuf.new_from_file_at_size(comun.PLAY_ICON, 32, 32)
INFO = GdkPixbuf.Pixbuf.new_from_file_at_size(comun.INFO_ICON, 16, 16)
PAUSE = GdkPixbuf.Pixbuf.new_from_file_at_size(comun.PAUSE_ICON, 32, 32)
DOWNLOAD = GdkPixbuf.Pixbuf.new_from_file_at_size(comun.DOWNLOAD_ICON, 32, 32)
DOWNLOAD_ANIM = GdkPixbuf.PixbufAnimation.new_from_file(comun.DOWNLOAD_ANIM)
LDOWNLOAD = GdkPixbuf.Pixbuf.new_from_file_at_size(comun.DOWNLOAD_ICON, 16, 16)
LDELETE = GdkPixbuf.Pixbuf.new_from_file_at_size(comun.DELETE_ICON, 16, 16)
LWAIT = GdkPixbuf.Pixbuf.new_from_file_at_size(comun.WAIT_ICON, 16, 16)
LISTENED = GdkPixbuf.Pixbuf.new_from_file_at_size(
    comun.LISTENED_ICON, 16, 16)
NOLISTENED = GdkPixbuf.Pixbuf.new_from_file_at_size(
    comun.NOLISTENED_ICON, 16, 16)


class ListBoxRowWithData(Gtk.ListBoxRow):
    __gsignals__ = {
        'button_info_clicked': (GObject.SIGNAL_RUN_FIRST,
                                GObject.TYPE_NONE, ()),
        'button_listened_clicked': (GObject.SIGNAL_RUN_FIRST,
                                    GObject.TYPE_NONE, ()),
        'position-changed': (GObject.SIGNAL_RUN_FIRST,
                                    GObject.TYPE_NONE, (int,)),
    }

    def __init__(self, audio, index):
        super(Gtk.ListBoxRow, self).__init__()
        self.set_name('listboxrowwithdata')
        grid = Gtk.Grid()
        self.add(grid)

        self.image = Gtk.Image()
        self.image.set_margin_top(5)
        self.image.set_margin_bottom(5)
        self.image.set_margin_left(5)
        self.image.set_margin_right(5)
        grid.attach(self.image, 0, 0, 4, 4)

        self.label1 = Gtk.Label()
        self.label1.set_name('label')
        self.label1.set_margin_top(5)
        self.label1.set_alignment(0, 0.5)
        grid.attach(self.label1, 4, 0, 1, 1)

        self.label2 = Gtk.Label()
        self.label2.set_name('label')
        self.label2.set_valign(Gtk.Align.FILL)
        self.label2.set_line_wrap(True)
        self.label2.set_alignment(0, 0.5)
        grid.attach(self.label2, 4, 1, 1, 1)

        self.label3 = Gtk.Label()
        self.label3.set_name('label')
        self.label3.set_alignment(0, 0.5)
        grid.attach(self.label3, 4, 2, 1, 1)

        self.label4 = Gtk.Label()
        self.label4.set_name('label')
        self.label4.set_alignment(0, 0.5)
        self.label4.set_margin_right(5)
        self.label4.set_halign(Gtk.Align.END)
        grid.attach(self.label4, 5, 2, 1, 1)

        self.button_listened = Gtk.Button()
        self.button_listened.set_name('button')
        self.button_listened.connect('clicked',
                                     self.on_button_clicked,
                                     'listened')

        self.listened = Gtk.Image()
        self.listened.set_from_pixbuf(NOLISTENED)
        self.listened.set_margin_left(5)
        self.button_listened.add(self.listened)
        grid.attach(self.button_listened, 6, 0, 1, 1)

        self.button_info = Gtk.Button()
        self.button_info.set_name('button')
        self.button_info.connect('clicked',
                                 self.on_button_clicked,
                                 'info')
        info = Gtk.Image()
        info.set_from_pixbuf(INFO)
        info.set_margin_left(5)
        self.button_info.add(info)
        grid.attach(self.button_info, 6, 2, 1, 1)

        self.progressbar = Gtk.Scale()
        self.progressbar.set_margin_bottom(5)
        self.progressbar.set_valign(Gtk.Align.CENTER)
        self.progressbar.set_hexpand(True)
        self.progressbar.set_margin_right(5)
        self.progressbar.set_name('progressbar')
        self.progressbar.set_adjustment(
            Gtk.Adjustment(0, 0, 100, 1, 1, 5))
        self.progressbar.connect('value-changed', self.on_position_changed)
        self.progressbar.set_sensitive(False)
        grid.attach(self.progressbar, 4, 3, 2, 1)

        self.index = index
        self.active = False
        self.set_audio(audio)

        self.override_background_color(Gtk.StateFlags.SELECTED,
                                       Gdk.RGBA(0.72941, 0.85490, 0.79608))
        self.override_background_color(Gtk.StateFlags.FOCUSED,
                                       Gdk.RGBA(0.72941, 0.85490, 0.79608))
        self.override_background_color(Gtk.StateFlags.ACTIVE,
                                       Gdk.RGBA(1, 0, 0, 0.2))
        self.override_background_color(Gtk.StateFlags.NORMAL,
                                       Gdk.RGBA(1, 1, 1, 1))

    def on_position_changed(self, widget):
        print(widget, self.progressbar.get_value())
        self.emit('position-changed', self.progressbar.get_value())

    def on_clicked(self, widget, event):
        print(widget, event)

    def on_button_clicked(self, widget, button_name):
        if button_name == 'info':
            self.emit('button_info_clicked')
        elif button_name == 'listened':
            self.emit('button_listened_clicked')

    def emit(self, *args):
        GLib.idle_add(GObject.GObject.emit, self, *args)

    def set_active(self, active):
        self.active = active
        if(active):
            self.override_background_color(Gtk.StateFlags.NORMAL,
                                           Gdk.RGBA(1, 0, 0, 0.2))
            self.progressbar.set_sensitive(True)
        else:
            self.override_background_color(Gtk.StateFlags.NORMAL,
                                           Gdk.RGBA(1, 1, 1, 1))
            self.progressbar.set_sensitive(False)

    def get_active(self):
        return self.active

    def __eq__(self, other):
        if other is not None and type(other) == ListBoxRowWithData:
            return self.audio['hash'] == other.audio['hash']
        return False

    def set_duration(self, duration):
        self.label4.set_text(time.strftime('%H:%M:%S', time.gmtime(duration)))

    def get_duration(self):
        return self.audio['length']

    def get_position(self):
        return self.audio['position']

    def set_listened(self, listened):
        self.audio['listened'] = listened
        if listened is True:
            self.listened.set_from_pixbuf(LISTENED)
        else:
            self.listened.set_from_pixbuf(NOLISTENED)

    def set_position(self, position):
        self.progressbar.handler_block_by_func(self.on_position_changed)

        self.audio['position'] = position
        self.label3.set_text(time.strftime('%H:%M:%S', time.gmtime(
            self.audio['length'] * position)))
        # self.progressbar.set_fraction(position)
        self.progressbar.set_value(int(position * 100))
        self.progressbar.handler_unblock_by_func(self.on_position_changed)

    def set_audio(self, audio):
        self.audio = audio
        pixbuf = get_pixbuf_from_base64string(
            audio['thumbnail_base64']).scale_simple(
            64, 64, GdkPixbuf.InterpType.BILINEAR)
        self.image.set_from_pixbuf(pixbuf)
        if len(audio['artist']) > 35:
            artist = audio['artist'][:32] + '...'
        else:
            artist = audio['artist']
        self.label1.set_markup(
            '<big><b>{0}</b></big>'.format(artist))
        if len(audio['title']) > 35:
            title = audio['title'][:32] + '...'
        else:
            title = audio['title']
        self.label2.set_text(title)
        if audio['listened'] is True:
            self.listened.set_from_pixbuf(LISTENED)
        else:
            self.listened.set_from_pixbuf(NOLISTENED)
        self.set_duration(audio['length'])
        self.set_position(audio['position'])
