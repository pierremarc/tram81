#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Copyright (C) 2014  Pierre Marchand <pierremarc07@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import click
import re
from fractions import Fraction

import logging
logging.basicConfig()
log = logging.getLogger('nomi_bulk')

from nominatim import Nominatim, NominatimReverse
import pyxif



@click.group()
@click.option('--debug/--no-debug', default=False)
def main(debug):
    if debug:
        log.setLevel(logging.DEBUG)
        click.echo('Debug mode is %s' % ('on' if debug else 'off'))


def process_query(query):
    nom = Nominatim()
    result = nom.query(query)
    log.debug('{}'.format(result))
    return result[0]


@main.command('query', help="make a request on nominatim")
@click.argument('query', nargs=-1, required=True)
def query(query):
    r = process_query(query)
    click.secho(u'latitude: {}\nlongitude: {}'.format(r['lat'], r['lon']))

def NumbertoR(num):
    f = Fraction(num).limit_denominator(max_denominator=10000000)
    return (f.numerator, f.denominator)

def DDtoDMS(deg):
    d = int(deg)
    md = abs(deg - d) * 60
    m = int(md)
    sd = (md - m) * 60
    return (d, m, sd)

def latRef(latitude):
    if latitude > 0.0:
        return 'N'
    return 'S'
def lonRef(longitude):
    if longitude > 0.0:
        return 'E'
    return 'W'

def lltoEXIF(l):
    dms = DDtoDMS(l)
    res = tuple([NumbertoR(x) for x in dms])
    return res


def insert_coords(image, lat, lon):
    zeroth_dict, exif_dict, gps_dict = pyxif.load(image)
    
    zeroth_dict_new = {}
    exif_dict_new = {}

    if pyxif.ZerothIFD.Orientation in zeroth_dict:
        zeroth_dict_new[pyxif.ZerothIFD.Orientation] =  zeroth_dict[pyxif.ZerothIFD.Orientation][1]

    gps_dict_new = {
        pyxif.GPSIFD.GPSLatitude:      lltoEXIF(lat),
        pyxif.GPSIFD.GPSLatitudeRef:   latRef(lat),
        pyxif.GPSIFD.GPSLongitude:     lltoEXIF(lon),
        pyxif.GPSIFD.GPSLongitudeRef:  lonRef(lon),
    }

    exif_bytes = pyxif.dump(zeroth_dict_new, exif_dict_new, gps_dict_new)
    pyxif.insert(exif_bytes, image)

@main.command('insert', help="insert geo data in given image with query to nominatim")
@click.argument('image', nargs=1, required=True)
@click.argument('query', nargs=-1, required=True)
def insert(image, query):

    try:
        res = process_query(' '.join(query))
        lat = float(res['lat'])
        lon = float(res['lon'])
        insert_coords(image, lat, lon)
        click.secho('Successfuly inserted LatLon({}, {}) in {}'.format(lat, lon, image), fg="green")
    except Exception, ex:
        click.secho('failed: {}'.format(ex), fg="red")

re_digit = re.compile('\d')
def process_num(num):
    res = re_digit.findall(num)
    if res: 
        return unicode(res[0])
    return u''

@main.command('walk', help="walk a directory tree and try to insert geo data")
@click.argument('directory', nargs=1, required=True)
@click.argument('extra', nargs=-1)
def insert(directory, extra):

    if not extra:
        extra = []

    for root, dirs, files in os.walk(directory):
        for name in files:
            path = os.path.join(root, name)
            comps = path.split(u'/')
            num = process_num(comps[-1])
            street = comps[-2]
            query = u' '.join([num, street]) + u' ' + u' '.join(extra)
            log.debug(query.encode("utf8"))
            try:
                res = process_query(query.encode("utf8"))
            except Exception, ex:
                click.secho(u'process_query.failed: {}\n\t {}'.format(query, ex), fg="red")
                continue
            # insert_coords(path, res['lat'], res['lon'])
            try:
                insert_coords(path, float(res['lat']), float(res['lon']))
            except Exception, ex:
                click.secho(u'insert_coords.failed: {}\n\t{}'.format(path, ex), fg="red")
                continue





if __name__ == "__main__":
    main()
