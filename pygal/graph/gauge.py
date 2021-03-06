# -*- coding: utf-8 -*-
# This file is part of pygal
#
# A python svg graph plotting library
# Copyright © 2012 Kozea
#
# This library is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pygal. If not, see <http://www.gnu.org/licenses/>.
"""
Gauge chart

"""

from __future__ import division
from pygal.util import decorate, compute_scale
from pygal.view import PolarView
from pygal.graph.graph import Graph
from math import pi


class Gauge(Graph):
    """Gauge graph"""

    def _set_view(self):
        self.view = PolarView(
            self.width - self.margin.x,
            self.height - self.margin.y,
            self._box)

    def arc_pos(self, value):
        aperture = pi / 3
        if value > self._max:
            return (3 * pi - aperture / 2) / 2
        if value < self._min:
            return (3 * pi + aperture / 2) / 2
        start = 3 * pi / 2 + aperture / 2
        return start + (2 * pi - aperture) * (
            value - self.min_) / (self.max_ - self.min_)

    def needle(self, serie_node, serie,):
        thickness = .05
        for i, value in enumerate(serie.values):
            if value is None:
                continue
            theta = self.arc_pos(value)
            fmt = lambda x: '%f %f' % x
            value = self._format(serie.values[i])
            metadata = serie.metadata.get(i)
            gauges = decorate(
                self.svg,
                self.svg.node(serie_node['plot'], class_="dots"),
                metadata)

            self.svg.node(
                gauges, 'polygon', points=' '.join([
                    fmt(self.view((0, 0))),
                    fmt(self.view((.75, theta + thickness))),
                    fmt(self.view((.8, theta))),
                    fmt(self.view((.75, theta - thickness)))]),
                class_='line reactive tooltip-trigger')

            x, y = self.view((.75, theta))
            self._tooltip_data(gauges, value, x, y)
            self._static_value(serie_node, value, x, y)

    def _x_axis(self, draw_axes=True):
        if not self._x_labels:
            return

        axis = self.svg.node(self.nodes['plot'], class_="axis x gauge")

        for i, (label, pos) in enumerate(self._x_labels):
            guides = self.svg.node(axis, class_='guides')
            theta = self.arc_pos(pos)
            self.svg.line(
                guides, [self.view((.95, theta)), self.view((1, theta))],
                close=True,
                class_='line')

            self.svg.line(
                guides, [self.view((0, theta)), self.view((.95, theta))],
                close=True,
                class_='guide line %s' % (
                    'major' if i in (0, len(self._x_labels) - 1)
                    else ''))

            x, y = self.view((.9, theta))
            self.svg.node(guides, 'text',
                          x=x,
                          y=y
                      ).text = label

    def _y_axis(self, draw_axes=True):
        axis = self.svg.node(self.nodes['plot'], class_="axis y gauge")
        x, y = self.view((0, 0))
        self.svg.node(axis, 'circle', cx=x, cy=y, r=4)

    def _compute(self):
        self._box.xmin = -1
        self._box.ymin = -1

        self.min_ = self._min
        self.max_ = self._max
        if self.max_ - self.min_ == 0:
            self.min_ -= 1
            self.max_ += 1

        x_pos = compute_scale(
            self.min_, self.max_, self.logarithmic, self.order_min
        )
        self._x_labels = zip(map(self._format, x_pos), x_pos)

    def _plot(self):
        for index, serie in enumerate(self.series):
            self.needle(
                self._serie(index), serie)
