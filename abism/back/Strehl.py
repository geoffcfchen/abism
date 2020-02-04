"""
    Strehl meter
    TODO prettify, the function division is nto judicious:
        Error goes along with mesure (always)
"""
import numpy as np

from abism.back import ImageFunction as IF
from abism.back import StrehlImage as SI
from abism.back.image_info import ImageInfo, get_array_stat

from abism.util import log, get_root, get_state, set_aa, get_aa, \
    EA, EPhot, ESky


######################################################################
#######################  ONE  ########################################
######################################################################


def strehl_one(rectangle):
    """ Note : this should just be a caller
        this is the first written, strehlMeter for pick one,
        I putted more for ellipse and binary
    """
    # pylint: disable = too-many-locals

    # Find center && fwhm
    # TODO bad pixels
    # IF.FindBadPixel(get_state().image.im0,(rx1,rx2,ry1,ry2))
    rectangle = IF.Order4(rectangle, grid=get_state().image.im0)
    star_center = IF.FindMaxWithBin(get_state().image.im0, rectangle)
    tmp = IF.LocalMax(get_state().image.im0, center=star_center, size=3)
    star_max, star_center = tmp[2], (tmp[0], tmp[1])
    IF.FWHM(get_state().image.im0, star_center)

    # Delegate fit && Save
    o_psf = SI.PsfFit(
        get_state().image.im0, rectangle,
        center=star_center, my_max=star_max)
    psf_fit = o_psf.do_fit().get_result()
    get_state().d_fit_param.update(psf_fit[0])
    get_state().d_fit_error.update(psf_fit[1])

    # Save what it take
    center = psf_fit[0]['center_x'], psf_fit[0]['center_y']
    # pylint: disable = unsubscriptable-object
    dcenter = psf_fit[1]['center_x'], psf_fit[1]['center_y']
    set_aa(EA.CENTER, center, error=dcenter)

    # Intensity
    intensity = psf_fit[0]['intensity']
    if get_state().e_phot_type and get_state().s_fit_type != "None":
        dI = get_state().d_fit_error["intensity"]
    else:
        x0, y0 = int(get_state().d_fit_param["center_x"]), int(get_state().d_fit_param["center_y"])
        mean = np.mean(get_state().image.im0[x0-1:x0+2, y0-1:y0+2])
        dI = (get_state().d_fit_param["intensity"] - mean)
        dI /= 2
    set_aa(EA.INTENSITY, intensity, error=dI)


    # Get Background && Save
    background, rms = get_background(get_state().image.im0, r=rectangle)
    set_aa(EA.BACKGROUND, background, error=rms)

    # Get photometry && Save
    # TODO better error from SI
    a_phot, a_fwhm_x, a_fwhm_y = IF.FwhmFromFit(psf_fit[0], psf_fit[1])
    photometry, err_photometry, _, number_count = \
        get_photometry(get_state().image.im0, background, rms, rectangle=rectangle, a_phot=a_phot)
    set_aa(EA.PHOTOMETRY, photometry, error=err_photometry)

    # Get Signal on noise && Save
    signal_on_noise = photometry / background / np.sqrt(number_count)
    dsignal_on_noise = np.sqrt(err_photometry**2 + rms**2) / np.sqrt(number_count)
    set_aa(EA.SN, signal_on_noise, error=dsignal_on_noise)

    # Save FWHM
    a_fwhm = craft_fwhm(a_fwhm_x, a_fwhm_y)
    set_aa(EA.FWHM_ABE, a_fwhm)

    # Math
    save_strehl_ratio()


######################################################################
#######################  TWO  ########################################
######################################################################


def craft_fwhm(a_fwhm_x, a_fwhm_y):
    # (Long, Short axe, Excentricity)
    # TODO error propagation, get cool for fwhm
    fwhm_a = max(a_fwhm_x.value, a_fwhm_y.value)
    fwhm_b = min(a_fwhm_x.value, a_fwhm_y.value)
    fwhm_e = np.sqrt(fwhm_a**2 - fwhm_b**2) / fwhm_a
    return get_state().craft_answer(EA.FWHM_ABE, (fwhm_a, fwhm_b, fwhm_e))


def BinaryStrehl(star1, star2):
    binary_psf = SI.BinaryPsf(get_state().image.im0, star1, star2)
    psf_fit = binary_psf.do_fit().get_result()
    get_state().d_fit_param = psf_fit[0]
    get_state().d_fit_error = psf_fit[1]
    append_binary_info()


def TightBinaryStrehl(star1, star2):
    tight_psf = SI.TightBinaryPsf(get_state().image.im0, star1, star2)
    psf_fit = tight_psf.do_fit().get_result()
    get_state().d_fit_param = psf_fit[0]
    get_state().d_fit_error = psf_fit[1]
    append_binary_info()


def append_binary_info():
    """Read
    Write: Separatation"""
    # pylint: disable = too-many-locals
    # Fit type
    fit_dic, err_dic = get_state().d_fit_param, get_state().d_fit_error
    log(9, 'Binary dic (Removes me)', fit_dic, err_dic)

    # Uglily set fit type here
    set_aa(EA.BINARY, get_state().s_fit_type)

    # Some lookup due to move
    x0, x1, y0, y1 = fit_dic["x0"], fit_dic["x1"], fit_dic["y0"], fit_dic["y1"]
    dx0, dx1 = err_dic["x0"], err_dic["x1"]
    dy0, dy1 = err_dic["y0"], err_dic["y1"]

    # Save center
    set_aa(EA.STAR1, (y0, x0), error=(err_dic['y0'], err_dic['x0']))
    set_aa(EA.STAR2, (y1, x1), error=(err_dic['y1'], err_dic['x1']))

    # Get separation
    separation_dic = get_separation(point=((x0, x1), (y0, y1)), error=((dx0, dx1), (dy0, dy1)))
    separation = separation_dic["dist"]
    sep_err = separation_dic["dist_err"]
    xy_angle = separation_dic["xy_angle"]
    set_aa(EA.ORIENTATION, xy_angle)
    set_aa(EA.SEPARATION, separation, error=sep_err)

    # Get Background
    if get_state().e_sky_type in (ESky.MANUAL, ESky.NONE):
        rms = 0.0
    else:
        rms = err_dic['background']
    set_aa(EA.BACKGROUND, fit_dic['background'], error=rms)

    # Get parameter for each star individualy
    def copy_dic(fit_dic, err_dic, s_num):
        """Copy dic replaceing some `0` and `1`"""
        fit_res = fit_dic.copy()
        err_res = err_dic.copy()
        for res, dic in zip((fit_res, err_res), (fit_dic, err_dic)):
            for key in dic.keys():
                log(9, s_num, key)
                if s_num in key:
                    res[key.replace(s_num, "")] = dic[key]
            try:
                res["exponent"] = dic["b" + s_num]
            except:
                pass
        return fit_res, err_res
    fit_copy1, err_copy1 = copy_dic(fit_dic, err_dic, "0")
    fit_copy2, err_copy2 = copy_dic(fit_dic, err_dic, "1")
    log(9, 'Binary Fit copies:',  fit_copy1)
    log(9, 'Binary Fit copies:',  err_copy1)
    log(9, 'Binary Fit copies:',  fit_copy2)
    log(9, 'Binary Fit copies:',  err_copy2)

    a_phot1, a_fwhm_x1, a_fwhm_y1 = IF.FwhmFromFit(fit_copy1, err_copy1)
    a_phot2, a_fwhm_x2, a_fwhm_y2 = IF.FwhmFromFit(fit_copy2, err_copy2)

    # Save photometry
    set_aa(EA.PHOTOMETRY1, a_phot1.value, error=a_phot1.error.value)
    set_aa(EA.PHOTOMETRY2, a_phot2.value, error=a_phot2.error.value)
    set_aa(EA.FLUX_RATIO, a_phot1 / a_phot2)

    # Save fwhm

    # Calculate Strehl
    bessel_integer = get_bessel_integer()
    a_Ith1, a_Ith2 = a_phot1 / bessel_integer, a_phot2 / bessel_integer
    a_intensity1 = set_aa(
        EA.INTENSITY1, fit_dic["intensity0"], error=err_dic["intensity0"])
    a_intensity2 = set_aa(
        EA.INTENSITY2, fit_dic["intensity1"], error=err_dic["intensity1"])
    a_strehl1 = a_intensity1 / a_Ith1
    a_strehl2 = a_intensity2 / a_Ith2
    set_aa(EA.STREHL1, 100 * a_strehl1, unit=' %')
    set_aa(EA.STREHL2, 100 * a_strehl2, unit=' %')


def get_separation(point=((0, 0), (0, 0)), error=((0, 0), (0, 0))):
    """point1i  (and 2) : list of 2 float = (x,y)= row, column
    err_point1 = 2 float = x,y )
    read north position in W
    """
    point1, point2 = point[0], point[1]
    err_point1, err_point2 = error[0], error[1]
    x0, x1, y0, y1 = point1[0], point1[1], point2[0], point2[1]
    dx0, dx1, dy0, dy1 = err_point1[0], err_point1[1], err_point2[0], err_point2[1]

    # Get separation distance <- Pythagora
    dist = np.sqrt((y1-y0)**2 + (x1-x0)**2)

    # Get error
    dist_err = np.sqrt(dx0**2 + dx1**2)
    dx0 = np.sqrt(err_point1[0]**2 + err_point1[1]**2)
    dx1 = np.sqrt(err_point2[0]**2 + err_point2[1]**2)

    # Get angle
    angle = np.array([(y1-y0),   (x1-x0)])
    angle /= np.sqrt((y0-y1)**2 + (x0-x1)**2)

    res = {"xy_angle": angle,
           "dist": dist, "dist_err": dist_err,
           }
    return res


######################################################################
#######################  Ellipse  ####################################
######################################################################


def EllipseEventStrehl(ellipse):
    """Main ellipse worker,
    Param: ellipse artist with ru, rv, position
    """
    if get_state().e_phot_type == EPhot.FIT:
        log(0, "Warning: Ellipse Mesurement ignoring fit photometric type")

    # Background
    back_stat = SI.EllipseEventBack(ellipse)
    background = back_stat.mean
    get_state().add_answer(EA.BACKGROUND, background)

    # Photometry
    photometry, _, _ = SI.EllipseEventPhot(ellipse, background)
    get_state().add_answer(EA.PHOTOMETRY, photometry)

    # Get maximum (side effect)
    SI.EllipseEventMax(ellipse)

    # Math
    save_strehl_ratio()


######################################################################
#######################  Helpers  ####################################
######################################################################


def get_photometry(grid, background, rms, rectangle=None, a_phot=None):
    """Make photometry of region
    In: center, r99
        Only one reading variable photometric type
        background
        a_phot, fit photometry
    Returns: photometry, total, number_count
             1. total phtotometric adu (backgound subtracted)
             Other. to estimate error
    Note Background must be called before
    TODO answer coherent (in / out) so I get rms
    """
    # pylint: disable = too-many-locals
    phot = err_phot = total = number_count = 0
    e_phot_type = get_state().e_phot_type

    r99x, r99y = get_state().d_fit_param['r99x'], get_state().d_fit_param['r99y']
    r99u, r99v = get_state().d_fit_param['r99u'], get_state().d_fit_param['r99v']
    theta = get_state().d_fit_param.get('theta', 0)

    x0, y0 = get_state().d_fit_param['center_x'], get_state().d_fit_param['center_y']
    ax1, ax2 = int(x0-r99x), int(x0+r99x)
    ay1, ay2 = int(y0-r99y), int(y0+r99y)

    # Fit
    if e_phot_type == EPhot.FIT:
        log(3, "Photometry <- fit")
        phot = a_phot.value
        err_phot = a_phot.error.value
        number_count = r99u * r99y

    # Rectangle apperture
    elif e_phot_type == EPhot.RECTANGLE:
        log(3, 'Photometry <- encircled energy (i.e. rectangle)')
        total = np.sum(grid[ax1:ax2, ay1:ay2])
        number_count = 4 * r99x * r99y
        phot = total - number_count * background

    # Elliptical apperture
    elif e_phot_type == EPhot.ELLIPTICAL:
        log(3, 'Photometry <- elliptical aperture')
        ellipse_dic = {"center_x": x0, "center_y": y0,
                       "ru": r99u, "rv": r99v, "theta": theta}
        bol = IF.EllipticalAperture(grid, dic=ellipse_dic)["bol"]
        image_elliptic = grid[bol]

        stat = get_array_stat(image_elliptic)
        number_count = stat.number_count
        total = stat.sum
        phot = total  - number_count * background

    # Manual
    elif e_phot_type == EPhot.MANUAL:
        log(3, "Photometry <- manual")
        stat = get_state().image.RectanglePhot(rectangle)
        total = stat.sum
        number_count = stat.number_count
        phot = total - number_count * background

    else:
        log(0, "Error: Photometry do not know tipe:", e_phot_type)

    if err_phot == 0:
        err_phot = 2 * rms * np.sqrt(number_count)

    return phot, err_phot, total, number_count


def get_background(grid, r=None):
    """Read from fit param, fit err
    TODO check r
    """
    # pylint: disable = too-many-locals


    # Log
    background_type = get_state().e_sky_type

    # Background and rms
    background = rms = 0

    # 8 rects
    if background_type == ESky.RECT8:
        log(2, 'Getting Background in 8 rects')
        xtmp, ytmp = get_state().d_fit_param['center_x'], get_state().d_fit_param['center_y']
        r99x, r99y = get_state().d_fit_param["r99x"], get_state().d_fit_param["r99y"]
        restmp = IF.EightRectangleNoise(
            grid, (xtmp-r99x, xtmp+r99x, ytmp-r99y, ytmp+r99y))
        background, rms = restmp["background"], restmp['rms']
        log(3, "ImageFunction.py : Background, I am in 8 rects ")

    # Manual
    elif background_type == ESky.MANUAL:
        log(2, 'Getting Background manual')
        background = get_state().i_background
        rms = get_state().image.stat.rms

    # Fit
    elif background_type == ESky.FIT:
        log(2, 'Getting Background from fit')
        # Check if no fit which is incoherent
        # TODO not working well yet (Currently refactoring globals)
        if get_state().s_fit_type == "None":
            log(0, "\n\n Warning, cannot estimate background with fit if fit type = None, "
                "return to Annnulus background")
            param = param.copy()
            param.update({"noise": "elliptical_annulus"})
            get_state().e_sky_type = ESky.ANNULUS
            return Background(get_state().image.im0)
        try:
            background = get_state().d_fit_param['background']
            rms = get_state().d_fit_error['background']
        except:
            log(-1, 'Error: background not in fit parameters')
            rms = background = float('nan')
        background = get_state().d_fit_param["background"]

    # None
    elif background_type == ESky.NONE:
        log(2, 'Getting Background from None <- 0')
        background = rms = 0

    # Elliptical annulus
    elif background_type == ESky.ANNULUS:
        log(2, 'Getting Background from elliptical annulus')
        # TODO hardcode as in AnswerReturn
        ell_inner_ratio, ell_outer_ratio = 1.3, 1.6
        rui, rvi = 1.3 * get_state().d_fit_param["r99u"], 1.3 * get_state().d_fit_param["r99v"]
        ruo, rvo = 1.6 * get_state().d_fit_param["r99u"], 1.6 * get_state().d_fit_param["r99v"]

        # Cut
        myrad = max(ruo, rvo) + 2  # In case
        ax1 = int(get_state().d_fit_param["center_x"] - myrad)
        ax2 = int(get_state().d_fit_param["center_x"] + myrad)
        ay1 = int(get_state().d_fit_param["center_y"] - myrad)
        ay2 = int(get_state().d_fit_param["center_y"] + myrad)
        ax1, ax2, ay1, ay2 = IF.Order4((ax1, ax2, ay1, ay2), grid=grid)
        image_cut = get_state().image.im0[ax1: ax2, ay1: ay2]

        bol_i = IF.EllipticalAperture(
            image_cut, dic={"center_x": myrad, "center_y": myrad, "ru": rui,
                            "rv": rvi, "theta": get_state().d_fit_param["theta"]})["bol"]

        bol_o = IF.EllipticalAperture(
            image_cut, dic={"center_x": myrad, "center_y": myrad, "ru": ruo,
                            "rv": rvo, "theta": get_state().d_fit_param["theta"]})["bol"]

        bol_a = bol_o ^ bol_i

        iminfo_cut = ImageInfo(image_cut[bol_a])
        tmp = iminfo_cut.sky()
        rms = tmp["rms"]
        background = tmp["mean"]

    else:
        log(-1, 'Error: I dont know sky mesure type', get_state.e_sky_type)
        rms = background = float('nan')

    log(3, 'Background returned:', background, rms)
    return background, rms


def save_strehl_ratio():
    """Save Strehl ratio (and friends) to global answers
    Reads: phot, back, intensity, header
    Writes:strehl ratio, equivalent sr, intensity theory, bessel integer (for curious)
    """
    # Read from global
    bessel_integer = get_bessel_integer()
    a_sky = get_aa(EA.BACKGROUND)
    a_photometry = get_aa(EA.PHOTOMETRY)
    a_intensity = get_aa(EA.INTENSITY)
    wavelength = get_root().header.wavelength
    log(5, 'Calculating Strehl with', "\n"
        'sky =', a_sky, "\n"
        'intensity =', a_intensity, "\n"
        'photometry =', a_photometry, "\n"
        'bessel_integer =', bessel_integer, "\n"
        'wavelength =', wavelength, "\n")

    # Get theoretical intensity && Save
    a_Ith = a_photometry / bessel_integer
    set_aa(EA.INTENSITY_THEORY, a_Ith.value, error=a_Ith.error)

    # Save strehl (finally)
    a_strehl = a_intensity / a_Ith
    set_aa(EA.STREHL, 100 * a_strehl, unit=' %')

    # Save equivalent Strehl ratio
    strehl_eq = get_equivalent_strehl_ratio(a_strehl.value, wavelength)
    err_strehl = a_strehl.error.value * strehl_eq / a_strehl.value
    set_aa(EA.STREHL_EQ, 100 * strehl_eq, error=100 * err_strehl, unit=' %')

    # Saven for error just after
    set_aa(EA.INTENSITY_THEORY, a_Ith)
    set_aa(EA.BESSEL_INTEGER, bessel_integer)


def get_bessel_integer():
    """Read wavelenght, pixel_scale, diameter, obstruction"""
    bessel_integer = get_root().header.wavelength * \
        10**(-6.) / np.pi / (get_root().header.pixel_scale/206265) / get_root().header.diameter
    bessel_integer = bessel_integer**2 * 4 * \
        np.pi / (1-(get_root().header.obstruction/100)**2)
    return bessel_integer


def get_equivalent_strehl_ratio(strehl, wavelength):
    """Get equivalent Strehl ration at 2.17"""
    if strehl < 0:
        factor = 0
    else:
        factor = wavelength / 2 / np.pi * np.sqrt(-np.log(strehl))

    factor = - (factor * 2 * np.pi / 2.17)**2

    return np.exp(factor)
