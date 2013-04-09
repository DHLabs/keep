# -*-Python-*-
###############################################################################
#
# File:         map2d.py
# RCS:          $Header: $
# Description:  Transform 2d map coordinates providing Differential Privacy
# Author:       Staal Vinterbo
# Created:      Wed Mar 27 17:07:29 2013
# Modified:     Thu Mar 28 13:25:58 2013 (Staal Vinterbo) staal@mats
# Language:     Python
# Package:      N/A
# Status:       Experimental
#
# (c) Copyright 2013, Staal Vinterbo, all rights reserved.
#
###############################################################################

from random import random
from math import log
import numpy as np


def intervalq(point, bounds):
    '''find which interval a point lies in given interval bounds

      input: point - number to identify bucket for
             bounds -  list of increasing bucket bounds including ends

      output: index such that bounds[index - 1] <= point < bounds[index]
    '''

    right = len(bounds) - 1
    left = 0

    assert(right > 0)  # check that bounds contains at least two elements

    # deal with points outside bounds range
    if point >= bounds[right]:
        return right
    if point <= bounds[left]:
        return 1

    # binary search for interval
    while left < right - 1:
        assert(bounds[left] < bounds[right])  # check that bounds are sorted
        mid = (left + right)/2
        if point >= bounds[mid]:
            left = mid
        else:
            right = mid

    return right


def rlaplace(scale, location=0):
    '''genrate a random deviate from Laplace(location, scale)'''
    assert(scale > 0)
    r = random()
    signr = 1 if r >= 0.5 else -1
    rr = r if r < 0.5 else 1 - r
    return location - signr * scale * log(2 * rr)


def noisyh(h, epsilon=1.0, tau=0.5):
    '''make a histogram ina numpy array differentially private.

       Expected maximal noise added is O(lon(n)/epsilon) where
       n are the number of times noise is added, i.e., size of
       histogram. Using this, we set entries that are smaller than
       tau * log(n)/epsilon 0.'''
    hp = map(lambda x: rlaplace(scale=2/epsilon, location=x), h.flatten())
    threshold = tau * log(len(hp))/epsilon
    hpt = map(lambda y: 0 if y < threshold else y, hp)
    return np.reshape(hpt, h.shape)


def p2m(points, xbounds, ybounds):
    '''convert a list of points to histogram.

       xbounds and ybounds contain grid axis points
       into which points are discretized.'''
    xb = sorted(xbounds)  # make sure boundaries are sorted
    yb = sorted(ybounds)  # make sure boundaries are sorted

    nxb = len(xb) - 1  # number of x intervals
    nyb = len(yb) - 1  # number of y intervals

    h = np.zeros((nxb, nyb))

    for x, y in points:
        i = intervalq(x, xb) - 1
        j = intervalq(y, yb) - 1
        h[i, j] += 1

    return h


def m2p(h, xbounds, ybounds):
    '''transform histogram into points

       xbounds and ybounds give grid axis points,
       meaning that h[i,j] is translated into a
       point (x,y) such that x is uniformly distributed
       in [xbounds[i], xbounds[i + 1]), and similarly for y.'''
    xb = sorted(xbounds)  # make sure boundaries are sorted
    yb = sorted(ybounds)  # make sure boundaries are sorted

    nxb = len(xb) - 1  # number of x intervals
    nyb = len(yb) - 1  # number of y intervals

    assert(h.shape == (nxb, nyb))

    points = []

    for i in range(nxb):
        ax = xb[i]
        bx = xb[i + 1]
        xwidth = bx - ax
        for j in range(nyb):
            ay = yb[j]
            by = yb[j + 1]
            ywidth = by - ay

            pnts = map(lambda _:  (ax + random() * xwidth,
                                   ay + random() * ywidth),
                       range(int(h[i, j])))
            points = pnts + points

    return points


def privatize(points, xbounds, ybounds, epsilon=1.0, tau=1.0):
    '''create differentially private version of list of points using a grid

       the grid is defined by axis points in xbounds and ybounds.
       epsilon is the differential privacy level.
       tau is a filtering parameter, see noisyh().
    '''
    dph = np.array( noisyh( p2m(points, xbounds, ybounds), epsilon, tau).round(), int)
    return m2p(dph, xbounds, ybounds)
