import math

"""
Original code in JavaScript was found on this website: http://neogeo.lv/ekartes/koord2/, and
translated to Python by Aleksandrs Korņijenko

Copyright 1997-1998 by Charles L. Taylor
"""

SM_A = 6378137.0
SM_B = 6356752.314140
SM_ECC_SQUARED = 6.69437999013e-03
UTM_SCALE_FACTOR = 0.9996
CENTRAL_MERIDIAN = math.radians(24.0)

def ark_length_of_meridian(phi):
    n = (SM_A - SM_B) / (SM_A + SM_B)

    alpha = ((SM_A + SM_B) / 2.0) * (1.0 + (math.pow (n, 2.0) / 4.0) + (math.pow (n, 4.0) / 64.0))
    beta = (-3.0 * n / 2.0) + (9.0 * math.pow (n, 3.0) / 16.0) + (-3.0 * math.pow (n, 5.0) / 32.0)
    gamma = (15.0 * math.pow (n, 2.0) / 16.0) + (-15.0 * math.pow (n, 4.0) / 32.0)
    delta = (-35.0 * math.pow (n, 3.0) / 48.0) + (105.0 * math.pow (n, 5.0) / 256.0)
    epsilon = (315.0 * math.pow (n, 4.0) / 512.0)

    result = alpha \
        * (phi + (beta * math.sin (2.0 * phi)) \
        + (gamma * math.sin (4.0 * phi)) \
        + (delta * math.sin (6.0 * phi)) \
        + (epsilon * math.sin (8.0 * phi)))
    
    return result

def footpoint_latitude(y):
    n = (SM_A - SM_B) / (SM_A + SM_B)

    alpha_ = ((SM_A + SM_B) / 2.0) * (1 + (math.pow(n, 2.0) / 4) + (math.pow(n, 4.0) / 64))
    y_ = y / alpha_
    beta_ = (3.0 * n / 2.0) + (-27.0 * math.pow(n, 3.0) / 32.0) + (269.0 * math.pow(n, 5.0) / 512.0)
    gamma_ = (21.0 * math.pow(n, 2.0) / 16.0) + (-55.0 * math.pow(n, 4.0) / 32.0)
    delta_ = (151.0 * math.pow(n, 3.0) / 96.0) + (-417.0 * math.pow(n, 5.0) / 128.0)
    epsilon_ = (1097.0 * math.pow (n, 4.0) / 512.0)

    result = y_ + (beta_ * math.sin (2.0 * y_)) \
        + (gamma_ * math.sin (4.0 * y_)) \
        + (delta_ * math.sin (6.0 * y_)) \
        + (epsilon_ * math.sin (8.0 * y_))
    
    return result

def from_lat_long_to_lks92(latitude: float, longtitude: float) -> tuple:
    """
    Converts latitude and longtitude in decimal degrees to LKS-92 easting and northing.
    #### Arguments
    - latitude (float), lattitude in degrees
    - longtitude (float), longtitude in degrees
    
    #### Returns
    tuple -> (<easting: float>, <northing: float>)
    """

    latitude = math.radians(latitude)
    longtitude = math.radians(longtitude)

    ep2 = (SM_A**2 - SM_B**2) / SM_B**2
    nu2 = ep2 * math.pow(math.cos(latitude), 2.0)
    N = math.pow(SM_A, 2.0) / (SM_B * math.sqrt(1 + nu2))

    t = math.tan(latitude)
    t2 = t * t

    l = longtitude - CENTRAL_MERIDIAN

    l3coef = 1.0 - t2 + nu2
    l4coef = 5.0 - t2 + 9 * nu2 + 4.0 * (nu2 * nu2)
    l5coef = 5.0 - 18.0 * t2 + (t2 * t2) + 14.0 * nu2 - 58.0 * t2 * nu2
    l6coef = 61.0 - 58.0 * t2 + (t2 * t2) + 270.0 * nu2 - 330.0 * t2 * nu2
    l7coef = 61.0 - 479.0 * t2 + 179.0 * (t2 * t2) - (t2 * t2 * t2)
    l8coef = 1385.0 - 3111.0 * t2 + 543.0 * (t2 * t2) - (t2 * t2 * t2)

    easting = N * math.cos (latitude) * l \
        + (N / 6.0 * math.pow (math.cos(latitude), 3.0) * l3coef * math.pow(l, 3.0)) \
        + (N / 120.0 * math.pow (math.cos(latitude), 5.0) * l5coef * math.pow(l, 5.0)) \
        + (N / 5040.0 * math.pow (math.cos(latitude), 7.0) * l7coef * math.pow(l, 7.0))
    
    northing = ark_length_of_meridian(latitude) \
        + (t / 2.0 * N * math.pow (math.cos(latitude), 2.0) * math.pow(l, 2.0)) \
        + (t / 24.0 * N * math.pow (math.cos(latitude), 4.0) * l4coef * math.pow(l, 4.0)) \
        + (t / 720.0 * N * math.pow (math.cos(latitude), 6.0) * l6coef * math.pow(l, 6.0)) \
        + (t / 40320.0 * N * math.pow (math.cos(latitude), 8.0) * l8coef * math.pow(l, 8.0))

    easting = easting * UTM_SCALE_FACTOR + 500000.0
    northing = northing * UTM_SCALE_FACTOR - 6000000.0

    if northing < 0:
        northing += 10000000.0
    
    return easting, northing

def from_lks92_to_lat_long(easting: float, northing: float) -> tuple:
    """
    Converts LKS-92 easting and northing to latitude and longtitude in decimal degrees.   
    #### Arguments
    - easting (float), lattitude
    - northing (float), longtitude

    #### Returns
    tuple -> (<latitude: float>, <longtitude: float>)
    """

    easting -= 500000.0
    northing -= -6000000.0
    easting /= UTM_SCALE_FACTOR
    northing /= UTM_SCALE_FACTOR

    phif = footpoint_latitude(northing)
    ep2 = (math.pow (SM_A, 2.0) - math.pow (SM_B, 2.0)) / math.pow (SM_B, 2.0)
    cf = math.cos(phif)
    nuf2 = ep2 * math.pow(cf, 2.0)
    Nf = math.pow(SM_A, 2.0) / (SM_B * math.sqrt(1 + nuf2))
    Nfpow = Nf

    tf = math.tan(phif)
    tf2 = tf * tf
    tf4 = tf2 * tf2

    x1frac = 1.0 / (Nfpow * cf)
    Nfpow *= Nf
    x2frac = tf / (2.0 * Nfpow)
    Nfpow *= Nf
    x3frac = 1.0 / (6.0 * Nfpow * cf)
    Nfpow *= Nf
    x4frac = tf / (24.0 * Nfpow)
    Nfpow *= Nf
    x5frac = 1.0 / (120.0 * Nfpow * cf)
    Nfpow *= Nf
    x6frac = tf / (720.0 * Nfpow)
    Nfpow *= Nf
    x7frac = 1.0 / (5040.0 * Nfpow * cf)
    Nfpow *= Nf
    x8frac = tf / (40320.0 * Nfpow)

    x2poly = -1.0 - nuf2
    x3poly = -1.0 - 2 * tf2 - nuf2
    x4poly = 5.0 + 3.0 * tf2 + 6.0 * nuf2 - 6.0 * tf2 * nuf2 - 3.0 * (nuf2 *nuf2) - 9.0 * tf2 * (nuf2 * nuf2)
    x5poly = 5.0 + 28.0 * tf2 + 24.0 * tf4 + 6.0 * nuf2 + 8.0 * tf2 * nuf2
    x6poly = -61.0 - 90.0 * tf2 - 45.0 * tf4 - 107.0 * nuf2 + 162.0 * tf2 * nuf2
    x7poly = -61.0 - 662.0 * tf2 - 1320.0 * tf4 - 720.0 * (tf4 * tf2)
    x8poly = 1385.0 + 3633.0 * tf2 + 4095.0 * tf4 + 1575 * (tf4 * tf2)

    latitude = phif + x2frac * x2poly * (easting * easting) \
        + x4frac * x4poly * math.pow (easting, 4.0) \
        + x6frac * x6poly * math.pow (easting, 6.0) \
        + x8frac * x8poly * math.pow (easting, 8.0)
    
    longtitude = CENTRAL_MERIDIAN + x1frac * easting  \
        + x3frac * x3poly * math.pow (easting, 3.0) \
        + x5frac * x5poly * math.pow (easting, 5.0) \
        + x7frac * x7poly * math.pow (easting, 7.0)
    
    return math.degrees(latitude), math.degrees(longtitude)

if __name__ == "__main__":
    test_coords = (506392.45774739253, 311411.55646529514)
    print("Test coordinates: latitude - {}, longtitude - {}".format(*test_coords))
    after_conversions = from_lks92_to_lat_long(*test_coords)
    print("After conversion: latitude - {}, longtitude - {}".format(*after_conversions))