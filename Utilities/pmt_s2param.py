"""
pmt_s2param.py
author: jrenner

Defines the PMT S2 parameterization functions as:

N(x) = sum(c_n*x^n) for n = 0 to n = 9

where x is the distance of the PMT from some central point of
light emission.

Because the response is characterized over several time bins, we
have several values for M and the coefficients.

bin0:  0.000574750745019*x^0 + 1.10551593622e-06*x^1 - 9.235238402e-08*x^2   + 3.46259217873e-09*x^3 - 7.33713600058e-11*x^4 + 9.19898878737e-13*x^5 - 6.98227428799e-15*x^6 + 3.1406356128e-17*x^7  - 7.67645875755e-20*x^8 + 7.81040203096e-23*x^9
bin1:  0.000576954290746*x^0 + 8.78011324737e-07*x^1 - 8.22143465033e-08*x^2 + 3.18869631098e-09*x^3 - 6.85073893144e-11*x^4 + 8.63609118076e-13*x^5 - 6.57006249998e-15*x^6 + 2.95827405899e-17*x^7 - 7.23392664106e-20*x^8 + 7.35945039447e-23*x^9
bin2:  0.000578108308502*x^0 + 8.16118351894e-07*x^1 - 8.30107505956e-08*x^2 + 3.35258465302e-09*x^3 - 7.38824219574e-11*x^4 + 9.47609532406e-13*x^5 - 7.29824173982e-15*x^6 + 3.31661244129e-17*x^7 - 8.17118999116e-20*x^8 + 8.37157182849e-23*x^9
bin3:  0.000495309397899*x^0 - 8.74900211294e-07*x^1 + 5.79412323677e-08*x^2 - 2.089855146e-09*x^3   + 4.19338939231e-11*x^4 - 5.10932057104e-13*x^5 + 3.84259233625e-15*x^6 - 1.74610409097e-17*x^7 + 4.40483644801e-20*x^8 - 4.76012133086e-23*x^9
bin4:  0.00049155157453*x^0  - 3.75866255465e-07*x^1 + 3.24714942369e-08*x^2 - 1.40460432424e-09*x^3 + 3.08930234049e-11*x^4 - 3.98172411026e-13*x^5 + 3.10395528288e-15*x^6 - 1.44517108666e-17*x^7 + 3.71145639744e-20*x^8 - 4.07128459092e-23*x^9
bin5:  0.000492422910691*x^0 - 5.79651875185e-07*x^1 + 4.50930127733e-08*x^2 - 1.77213874314e-09*x^3 + 3.68741257838e-11*x^4 - 4.56774272891e-13*x^5 + 3.45728394596e-15*x^6 - 1.57337973971e-17*x^7 + 3.96798186426e-20*x^8 - 4.28836540614e-23*x^9
bin6:  0.000489879221214*x^0 + 3.14888194402e-08*x^1 + 2.281955989e-09*x^2   - 3.42247992559e-10*x^3 + 1.02160948405e-11*x^4 - 1.58788715645e-13*x^5 + 1.41282327182e-15*x^6 - 7.29359049174e-18*x^7 + 2.04259688965e-20*x^8 - 2.4227556935e-23*x^9
bin7:  0.000492121183465*x^0 - 3.90498366526e-07*x^1 + 2.88057266601e-08*x^2 - 1.14426814935e-09*x^3 + 2.37568978414e-11*x^4 - 2.95497255381e-13*x^5 + 2.25724892981e-15*x^6 - 1.04235486152e-17*x^7 + 2.68259104525e-20*x^8 - 2.97837892742e-23*x^9
bin8:  0.000489848667428*x^0 - 3.88892291584e-08*x^1 + 1.10660377769e-08*x^2 - 7.59463455552e-10*x^3 + 1.99087018557e-11*x^4 - 2.84045584982e-13*x^5 + 2.36346532875e-15*x^6 - 1.15178586493e-17*x^7 + 3.06140878368e-20*x^8 - 3.45355997085e-23*x^9
bin9:  0.000493143292534*x^0 - 5.6374631665e-07*x^1  + 4.22958897313e-08*x^2 - 1.69171135989e-09*x^3 + 3.59225827322e-11*x^4 - 4.52157197502e-13*x^5 + 3.45743092631e-15*x^6 - 1.58151550099e-17*x^7 + 3.99336276825e-20*x^8 - 4.3094742905e-23*x^9
bin10: 0.0004923417941*x^0   - 4.11234294378e-07*x^1 + 2.93754637435e-08*x^2 - 1.15454784504e-09*x^3 + 2.39470430743e-11*x^4 - 2.98805051852e-13*x^5 + 2.29375955357e-15*x^6 - 1.06465342982e-17*x^7 + 2.75197280692e-20*x^8 - 3.06453165348e-23*x^9
bin11: 0.000489274455129*x^0 + 5.60837649759e-08*x^1 + 3.14640500149e-09*x^2 - 4.40454932281e-10*x^3 + 1.30286063911e-11*x^4 - 1.98484935388e-13*x^5 + 1.7291504843e-15*x^6  - 8.7476460792e-18*x^7  + 2.40339375305e-20*x^8 - 2.79778399428e-23*x^9

"""
import numpy as np

# Number of time bins
n_tbins = 12 

# Coefficients from S2 parameterization
c0 = [0.000574750745019,   0.000576954290746,  0.000578108308502,  0.000495309397899,  0.00049155157453,   0.000492422910691,  0.000489879221214,  0.000492121183465,  0.000489848667428,  0.000493143292534,  0.0004923417941,    0.000489274455129]
c1 = [1.10551593622e-06,   8.78011324737e-07,  8.16118351894e-07, -8.74900211294e-07, -3.75866255465e-07, -5.79651875185e-07,  3.14888194402e-08, -3.90498366526e-07, -3.88892291584e-08, -5.6374631665e-07,  -4.11234294378e-07,  5.60837649759e-08]
c2 = [-9.235238402e-08,   -8.22143465033e-08, -8.30107505956e-08,  5.79412323677e-08,  3.24714942369e-08,  4.50930127733e-08,  2.281955989e-09,    2.88057266601e-08,  1.10660377769e-08,  4.22958897313e-08,  2.93754637435e-08,  3.14640500149e-09]
c3 = [3.46259217873e-09,   3.18869631098e-09,  3.35258465302e-09, -2.089855146e-09,   -1.40460432424e-09, -1.77213874314e-09, -3.42247992559e-10, -1.14426814935e-09, -7.59463455552e-10, -1.69171135989e-09, -1.15454784504e-09, -4.40454932281e-10]
c4 = [-7.33713600058e-11, -6.85073893144e-11, -7.38824219574e-11,  4.19338939231e-11,  3.08930234049e-11,  3.68741257838e-11,  1.02160948405e-11,  2.37568978414e-11,  1.99087018557e-11,  3.59225827322e-11,  2.39470430743e-11,  1.30286063911e-11]
c5 = [9.19898878737e-13,   8.63609118076e-13,  9.47609532406e-13, -5.10932057104e-13, -3.98172411026e-13, -4.56774272891e-13, -1.58788715645e-13, -2.95497255381e-13, -2.84045584982e-13, -4.52157197502e-13, -2.98805051852e-13, -1.98484935388e-13]
c6 = [-6.98227428799e-15, -6.57006249998e-15, -7.29824173982e-15,  3.84259233625e-15,  3.10395528288e-15,  3.45728394596e-15,  1.41282327182e-15,  2.25724892981e-15,  2.36346532875e-15,  3.45743092631e-15,  2.29375955357e-15,  1.7291504843e-15]
c7 = [3.1406356128e-17,    2.95827405899e-17,  3.31661244129e-17, -1.74610409097e-17, -1.44517108666e-17, -1.57337973971e-17, -7.29359049174e-18, -1.04235486152e-17, -1.15178586493e-17, -1.58151550099e-17, -1.06465342982e-17, -8.7476460792e-18]
c8 = [-7.67645875755e-20, -7.23392664106e-20, -8.17118999116e-20,  4.40483644801e-20,  3.71145639744e-20,  3.96798186426e-20,  2.04259688965e-20,  2.68259104525e-20,  3.06140878368e-20,  3.99336276825e-20,  2.75197280692e-20,  2.40339375305e-20]
c9 = [7.81040203096e-23,   7.35945039447e-23,  8.37157182849e-23, -4.76012133086e-23, -4.07128459092e-23, -4.28836540614e-23, -2.4227556935e-23,  -2.97837892742e-23, -3.45355997085e-23, -4.3094742905e-23,  -3.06453165348e-23, -2.79778399428e-23]

# Maximum radial extent of parameterization
rmax = 210.

# Return the SiPM response for the specified time bin and radial distance.
def pmt_s2par(tbin,r):

    # Ensure the time bin value is valid.
    if(tbin < 0 or tbin >= n_tbins):
        print "Invalid time bin in sipm_param: returning 0.0 ..."
        return 0.0

    # Calculate the response based on the parametrization.
    vpar = (c0[tbin] + c1[tbin]*r + c2[tbin]*r**2 + c3[tbin]*r**3 + 
    c4[tbin]*r**4 + c5[tbin]*r**5 + c6[tbin]*r**6 + c7[tbin]*r**7 + 
    c8[tbin]*r**8 + c9[tbin]*r**9)

    # Zero the response for radii too large.
    if(hasattr(vpar, "__len__")):
        ret = np.zeros(len(vpar)); iret = 0
        for rv,pv in zip(r,vpar):
            if(rv < rmax):
                ret[iret] = pv
            iret += 1
        return ret
    else:
        if(r < rmax):
            return vpar
        return 0.0
        
        
