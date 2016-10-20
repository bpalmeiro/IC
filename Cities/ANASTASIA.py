"""
ANASTASIA
GML October 2016

What ANASTASIA does:
1) Reads a hdf5 file containing the PMT's CWF and the SiPMs' RWF in ADC counts.
2) Creates a single "big" PMT summing up PMTs' waveforms.
3) Applies zero-suppression to both the big PMT and the individual SiPMs.
3) Expresses the waveforms in pes.
4) Writes a new file with the ZS waveforms as tables.
"""

from __future__ import print_function

import sys
from time import time

import numpy as np
import tables as tb

from system_of_units import *
from LogConfig import logger
from Configure import configure, define_event_loop
from Nh5 import SENSOR_WF
from FEParam import NOISE_ADC

import sensorFunctions as snf
import wfmFunctions as wfm
import tblFunctions as tbl

from RandomSampling import NoiseSampler as SiPMsNoiseSampler
#------

'''

ANASTASIA
ChangeLog:

14.10 First version.
18.10 Big PMT implemented and ZS methods implemented.

'''


def scale_to_pes(sens_wf, sensdf):
    '''
        Transform the ene_pes field to pes for each sensor.
    '''
    return { key : wfm.wf2df(df.time_mus, -df.ene_pes / sensdf['adc_to_pes'][key]) for key, df in sens_wf.iteritems() }

def ANASTASIA(argv):
    '''
        ANASTASIA driver
    '''
    DEBUG_LEVEL, INFO, CYTHON, CFP = configure(argv[0],argv[1:])

    if INFO:
        print(__doc__)

    PATH_IN   = CFP['PATH_IN']
    FILE_IN   = CFP['FILE_IN']
    PATH_DB   = CFP['PATH_DB']
    FIRST_EVT = CFP['FIRST_EVT']
    LAST_EVT  = CFP['LAST_EVT']
    RUN_ALL   = CFP['RUN_ALL']
    CLIB      = CFP['CLIB']
    CLEVEL    = CFP['CLEVEL']
    NEVENTS   = LAST_EVT - FIRST_EVT

    PMT_ZS_METHOD  = CFP['PMT_ZS_METHOD']
    SIPM_ZS_METHOD = CFP['SIPM_ZS_METHOD']
    PMT_NOISE_CUT  = CFP['PMT_NOISE_CUT']
    SIPM_NOISE_CUT = CFP['SIPM_NOISE_CUT']

    logger.info('Debug level = {}'.format(DEBUG_LEVEL))
    logger.info("input file = {}/{}".format(PATH_IN,FILE_IN))
    logger.info("path to database = {}".format(PATH_DB))
    logger.info("first event = {}; last event = {} nof events requested = {} ".format(FIRST_EVT,LAST_EVT,NEVENTS))
    logger.info("Compression library = {} Compression level = {} ".format(CLIB,CLEVEL))
    logger.info("ZS method PMTS  = {}. Cut value = {}".format(PMT_ZS_METHOD,PMT_NOISE_CUT))
    logger.info("ZS method SIPMS = {}. Cut value = {}".format(SIPM_ZS_METHOD,SIPM_NOISE_CUT))

    # open the input file
    with tb.open_file("{}/{}".format(PATH_IN,FILE_IN), "r+") as h5in:
        # access the PMT raw data in file

        pmtblr   = h5in.root.RD.pmtblr
        pmtcwf   = h5in.root.RD.pmtcwf
        sipmrwf  = h5in.root.RD.sipmrwf
        mcdata   = h5in.root.MC.MCTracks
        geodata  = h5in.root.Detector.DetectorGeometry
        pmtdata  = h5in.root.Sensors.DataPMT
        sipmdata = h5in.root.Sensors.DataSiPM
        pmtdf    = snf.read_data_sensors(pmtdata)
        sipmdf   = snf.read_data_sensors(sipmdata)

        NEVT, NPMT , PMTWL  = pmtcwf.shape
        NEVT, NSIPM, SIPMWL = sipmrwf.shape

        logger.info("#PMTs = {}; #SiPMs = {}; #events in DST = {}".format(NPMT,NSIPM,NEVT))
        logger.info("PMT WFL = {}; SiPM WFL = {}".format(PMTWL,SIPMWL))

        pmt_adc_consts = 1.0/np.array([19.200523269821286,18.337220349094959,18.277890643055709,20.094008664586799,19.623449041069801,18.267600383584281,19.062919010617382, 17.392029016798073, 18.334949819343084,18.462968438179974,18.634919155741205,18.112776381185306]).reshape(NPMT,1)
        pmt_ave_consts = 1.0/np.mean([19.200523269821286,18.337220349094959,18.277890643055709,20.094008664586799,19.623449041069801,18.267600383584281,19.062919010617382, 17.392029016798073, 18.334949819343084,18.462968438179974,18.634919155741205,18.112776381185306])

        # Create instance of the noise sampler and compute noise thresholds
        sipms_noise_sampler_    = SiPMsNoiseSampler(PATH_DB+"/NoiseSiPM_NEW.dat",sipmdf,SIPMWL)
        pmts_noise_threshold_   = PMT_NOISE_CUT * NOISE_ADC * pmt_ave_consts * NPMT**0.5 if PMT_ZS_METHOD == 'RMS_CUT' else 1.01 * PMT_NOISE_CUT * NPMT * pmt_ave_consts
        sipms_noise_thresholds_ = sipms_noise_sampler_.ComputeThresholds(SIPM_NOISE_CUT,sipmdf = sipmdf) if SIPM_ZS_METHOD == 'FRACTION' else np.ones(NSIPM) * SIPM_NOISE_CUT

        if not '/ZS' in h5in:
            rgroup = h5in.create_group(h5in.root, "ZS")
        if '/ZS/PMT' in h5in:
            h5in.remove_node("/ZS","PMT")
        if '/ZS/PMTBLR' in h5in:
            h5in.remove_node("/ZS","PMTBLR")
        if '/ZS/SiPM' in h5in:
            h5in.remove_node("/ZS","SiPM")

        pmt_zs_  = h5in.create_earray(h5in.root.ZS, "PMT",
                                      atom=tb.Int16Atom(),     #not Float32! bad for compression
                                      shape=(0, 1, PMTWL),
                                      expectedrows=NEVT)

        pmt_zs_blr_  = h5in.create_earray(h5in.root.ZS, "PMTBLR",
                                          atom=tb.Int16Atom(),     #not Float32! bad for compression
                                          shape=(0, 1, PMTWL),
                                          expectedrows=NEVT)

        sipm_zs_  = h5in.create_earray(h5in.root.ZS, "SiPM",
                                       atom=tb.Int16Atom(),     #not Float32! bad for compression
                                       shape=(0, NSIPM, SIPMWL),
                                       expectedrows=NEVT)

        first_evt, last_evt = define_event_loop(FIRST_EVT,LAST_EVT,NEVENTS,NEVT,RUN_ALL)

        t0 = time()
        for i in range(first_evt,last_evt):
            logger.info("-->event number ={}".format(i))

            # Integrate PMT plane in pes (not in time!)
            pmtcwf_int_pes = (pmtcwf[i] * pmt_adc_consts).sum(axis=0)
            pmtblr_int_pes = ((2500-pmtblr[i]) * pmt_adc_consts).sum(axis=0)

            # suppress_wf puts zeros where the wf is below the threshold
            wfm.suppress_wf(pmtcwf_int_pes,pmts_noise_threshold_)
            wfm.suppress_wf(pmtblr_int_pes,pmts_noise_threshold_)

            pmt_zs_.append( pmtcwf_int_pes.reshape(1,1,PMTWL) )
            pmt_zs_blr_.append( pmtblr_int_pes.reshape(1,1,PMTWL) )

            SiPMdata = wfm.to_pes( wfm.noise_suppression( sipmrwf[i], sipms_noise_thresholds_ ), sipmdf )
            sipm_zs_.append( SiPMdata.reshape(1,NSIPM,SIPMWL) )
        t1 = time()

        print("ANASTASIA has run over {} events in {} seconds".format(i, t1-t0))
    print("Leaving ANASTASIA. Safe travels!")

if __name__ == '__main__':
    #import cProfile

    #cProfile.run('ANASTASIA(sys.argv)', sort='time')
    ANASTASIA(sys.argv)
