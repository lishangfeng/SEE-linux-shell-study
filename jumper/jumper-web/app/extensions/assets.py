# -*- coding: utf-8 -*-

from flask_assets import Bundle, Environment


js_head = Bundle(
    'vendor/modernizr/modernizr.js',
    filters='jsmin',
    output='gen/head.js'
)

js_all = Bundle(
    'vendor/jquery/dist/jquery.min.js',
    'vendor/fastclick/lib/fastclick.js',
    'vendor/foundation/js/foundation.min.js',
    'js/*.js',
    filters='jsmin',
    output='gen/packed.js'
)

css_all = Bundle(
    'vendor/foundation/css/foundation.min.css',
    'css/*.css',
    filters='cssmin',
    output='gen/packed.css'
)

extension = Environment()
extension.register('js_head', js_head)
extension.register('js_all', js_all)
extension.register('css_all', css_all)
