###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################


from Numeric import Float64, zeros



############################
# Spectral density values. #
############################


# Original {tm} and {tm, S2}.
#############################

def calc_tm_jw_comps(data):
    """Spectral density component function.

    Calculate the components of the isotropic spectral density value for the original model-free
    formula with the parameter tm.

    The model-free formula is:

                 2 /      tm      \ 
        J(w)  =  - | ------------ |
                 5 \ 1 + (w.tm)^2 /


    Calculations which are replicated in the gradient equations are:

        w_tm_sqrd = (w.tm)^2
        two_fifths_tm = 2/5 * tm
        two_fifths_tm_sqrd = 2/5 * tm^2
        fact_tm = 1 / (1 + (w.tm)^2)
    """

    data.w_tm_sqrd = data.frq_sqrd_list[data.i] * data.params[data.tm_index[data.i]] ** 2
    data.two_fifths_tm = 0.4 * data.params[data.tm_index[data.i]]
    data.two_fifths_tm_sqrd = 0.4 * data.params[data.tm_index[data.i]] ** 2
    data.fact_tm = 1.0 / (1.0 + data.w_tm_sqrd)



# Original {S2, te}.
####################

def calc_S2_te_jw_comps(data):
    """Spectral density component function.

    Calculate the components of the isotropic spectral density value for the original model-free
    formula with the parameters S2 and te.

    The model-free formula is:

                 2 /   S2 . tm        (1 - S2) . te' \ 
        J(w)  =  - | ------------  +  -------------- |
                 5 \ 1 + (w.tm)^2     1 + (w.te')^2  /


    Simplified:

                 2    /      S2             (1 - S2)(te + tm)te    \ 
        J(w)  =  - tm | ------------  +  ------------------------- |
                 5    \ 1 + (w.tm)^2     (te + tm)^2 + (w.te.tm)^2 /


    Replicated calculations are:

        w_tm_sqrd = (w.tm)^2        (pre-calculated during initialisation)

        te_tm = te + tm
        te_tm_te = (te + tm).te


    Calculations which are replicated in the gradient equations are:

        two_fifths_tm = 2/5 * tm        (pre-calculated during initialisation)
        fact_tm = 1 / (1 + (w.tm)^2)    (pre-calculated during initialisation)

        one_s2 = 1 - S2

        te_tm_sqrd = (te + tm)^2
        w_te_tm_sqrd = (w.te.tm)^2
        inv_te_denom = 1 / ((te + tm)^2 + (w.te.tm)^2)
        te_num = (te + tm)te
    """

    data.one_s2 = 1.0 - data.params[data.s2_index[data.i]]

    data.te_tm = data.params[data.te_index[data.i]] + data.diff_params[0]
    data.te_tm_te = data.te_tm * data.params[data.te_index[data.i]]
    data.te_tm_sqrd = data.te_tm ** 2
    data.w_te_tm_sqrd = data.w_tm_sqrd[data.i] * data.params[data.te_index[data.i]] ** 2
    if data.te_tm == 0.0:
        data.inv_te_denom = 0.0 * data.w_te_tm_sqrd
    else:
        data.inv_te_denom = 1.0 / (data.te_tm_sqrd + data.w_te_tm_sqrd)
    data.te_num = data.te_tm * data.params[data.te_index[data.i]]



# Original {tm, S2, te}.
########################

def calc_tm_S2_te_jw_comps(data):
    """Spectral density component function.

    Calculate the components of the isotropic spectral density value for the original model-free
    formula with the parameters S2 and te.

    The model-free formula is:

                 2 /   S2 . tm        (1 - S2) . te' \ 
        J(w)  =  - | ------------  +  -------------- |
                 5 \ 1 + (w.tm)^2     1 + (w.te')^2  /


    Simplified:

                 2    /      S2             (1 - S2)(te + tm)te    \ 
        J(w)  =  - tm | ------------  +  ------------------------- |
                 5    \ 1 + (w.tm)^2     (te + tm)^2 + (w.te.tm)^2 /


    Replicated calculations are:

        w_tm_sqrd = (w.tm)^2

        te_tm = te + tm
        te_tm_te = (te + tm).te


    Calculations which are replicated in the gradient equations are:

        two_fifths_tm = 2/5 * tm        (pre-calculated during initialisation)
        fact_tm = 1 / (1 + (w.tm)^2)    (pre-calculated during initialisation)

        one_s2 = 1 - S2

        te_tm_sqrd = (te + tm)^2
        w_te_tm_sqrd = (w.te.tm)^2
        inv_te_denom = 1 / ((te + tm)^2 + (w.te.tm)^2)
        te_num = (te + tm)te
    """

    data.w_tm_sqrd = data.frq_sqrd_list * data.params[data.tm_index[data.i]] ** 2
    data.two_fifths_tm = 0.4 * data.params[data.tm_index[data.i]]
    data.two_fifths_tm_sqrd = 0.4 * data.params[data.tm_index[data.i]] ** 2
    data.fact_tm = 1.0 / (1.0 + data.w_tm_sqrd)

    data.one_s2 = 1.0 - data.params[data.s2_index[data.i]]

    data.te_tm = data.params[data.te_index[data.i]] + data.params[data.tm_index[data.i]]
    data.te_tm_te = data.te_tm * data.params[data.te_index[data.i]]
    data.te_tm_sqrd = data.te_tm ** 2
    data.w_te_tm_sqrd = data.w_tm_sqrd * data.params[data.te_index[data.i]] ** 2
    if data.te_tm == 0.0:
        data.inv_te_denom = 0.0 * data.w_te_tm_sqrd
    else:
        data.inv_te_denom = 1.0 / (data.te_tm_sqrd + data.w_te_tm_sqrd)
    data.te_num = data.te_tm * data.params[data.te_index[data.i]]



# Extended {S2f, S2, ts}.
#########################

def calc_S2f_S2_ts_jw_comps(data):
    """Spectral density component function.

    Calculate the components of the isotropic spectral density value for the extended model-free
    formula with the parameters S2f, S2, and ts.

    The formula is:

                 2 /    S2 . tm        (S2f - S2) . ts' \ 
        J(w)  =  - | -------------  +  ---------------- |
                 5 \ 1 + (w.tm)**2      1 + (w.ts')**2  /


    Simplified:

                 2    /      S2            (S2f - S2)(ts + tm)ts   \ 
        J(w)  =  - tm | ------------  +  ------------------------- |
                 5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /


    Replicated calculations are:

        w_tm_sqrd = (w.tm)^2        (pre-calculated during initialisation)

        ts_tm = ts + tm
        ts_tm_ts = (ts + tm).ts


    Calculations which are replicated in the gradient equations are:

        two_fifths_tm = 2/5 * tm        (pre-calculated during initialisation)
        fact_tm = 1 / (1 + (w.tm)^2)    (pre-calculated during initialisation)

        s2f_s2 = S2f - S2

        ts_tm_sqrd = (ts + tm)^2
        w_ts_tm_sqrd = (w.ts.tm)^2
        inv_ts_denom = 1 / ((ts + tm)^2 + (w.ts.tm)^2)
        ts_num = (ts + tm)ts
    """

    data.s2f_s2 = data.params[data.s2f_index[data.i]] - data.params[data.s2_index[data.i]]

    data.ts_tm = data.params[data.ts_index[data.i]] + data.diff_params[0]
    data.ts_tm_ts = data.ts_tm * data.params[data.ts_index[data.i]]
    data.ts_tm_sqrd = data.ts_tm ** 2
    data.w_ts_tm_sqrd = data.w_tm_sqrd[data.i] * data.params[data.ts_index[data.i]] ** 2
    if data.ts_tm == 0.0:
        data.inv_ts_denom = 0.0 * data.w_ts_tm_sqrd
    else:
        data.inv_ts_denom = 1.0 / (data.ts_tm_sqrd + data.w_ts_tm_sqrd)
    data.ts_num = data.ts_tm * data.params[data.ts_index[data.i]]



# Extended {tm, S2f, S2, ts}.
#############################

def calc_tm_S2f_S2_ts_jw_comps(data):
    """Spectral density component function.

    Calculate the components of the isotropic spectral density value for the extended model-free
    formula with the parameters S2f, S2, and ts.

    The formula is:

                 2 /    S2 . tm        (S2f - S2) . ts' \ 
        J(w)  =  - | -------------  +  ---------------- |
                 5 \ 1 + (w.tm)**2      1 + (w.ts')**2  /


    Simplified:

                 2    /      S2            (S2f - S2)(ts + tm)ts   \ 
        J(w)  =  - tm | ------------  +  ------------------------- |
                 5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /


    Replicated calculations are:

        w_tm_sqrd = (w.tm)^2

        ts_tm = ts + tm
        ts_tm_ts = (ts + tm).ts


    Calculations which are replicated in the gradient equations are:

        two_fifths_tm = 2/5 * tm
        fact_tm = 1 / (1 + (w.tm)^2)

        s2f_s2 = S2f - S2

        ts_tm_sqrd = (ts + tm)^2
        w_ts_tm_sqrd = (w.ts.tm)^2
        inv_ts_denom = 1 / ((ts + tm)^2 + (w.ts.tm)^2)
        ts_num = (ts + tm)ts
    """

    data.w_tm_sqrd = data.frq_sqrd_list * data.params[data.tm_index[data.i]] ** 2
    data.two_fifths_tm = 0.4 * data.params[data.tm_index[data.i]]
    data.two_fifths_tm_sqrd = 0.4 * data.params[data.tm_index[data.i]] ** 2
    data.fact_tm = 1.0 / (1.0 + data.w_tm_sqrd)

    data.s2f_s2 = data.params[data.s2f_index[data.i]] - data.params[data.s2_index[data.i]]

    data.ts_tm = data.params[data.ts_index[data.i]] + data.params[data.tm_index[data.i]]
    data.ts_tm_ts = data.ts_tm * data.params[data.ts_index[data.i]]
    data.ts_tm_sqrd = data.ts_tm ** 2
    data.w_ts_tm_sqrd = data.w_tm_sqrd * data.params[data.ts_index[data.i]] ** 2
    if data.ts_tm == 0.0:
        data.inv_ts_denom = 0.0 * data.w_ts_tm_sqrd
    else:
        data.inv_ts_denom = 1.0 / (data.ts_tm_sqrd + data.w_ts_tm_sqrd)
    data.ts_num = data.ts_tm * data.params[data.ts_index[data.i]]



# Extended 2 {S2f, S2s, ts}.
############################

def calc_S2f_S2s_ts_jw_comps(data):
    """Spectral density component function.

    Calculate the components of the isotropic spectral density value for the extended model-free
    formula with the parameters S2f, S2s, and ts.

    The formula is:

                 2 /    S2 . tm        (S2f - S2) . ts' \ 
        J(w)  =  - | -------------  +  ---------------- |
                 5 \ 1 + (w.tm)**2      1 + (w.ts')**2  /


    Simplified:

                 2    /   S2f . S2s       S2f(1 - S2s)(ts + tm)ts  \ 
        J(w)  =  - tm | ------------  +  ------------------------- |
                 5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /


    Replicated calculations are:

        w_tm_sqrd = (w.tm)^2        (pre-calculated during initialisation)

        ts_tm = ts + tm
        ts_tm_ts = (ts + tm).ts


    Calculations which are replicated in the gradient equations are:

        two_fifths_tm = 2/5 * tm        (pre-calculated during initialisation)
        fact_tm = 1 / (1 + (w.tm)^2)    (pre-calculated during initialisation)

        one_s2s = 1 - S2s
        s2f_s2 = S2f(1 - S2s) = S2f - S2

        ts_tm_sqrd = (ts + tm)^2
        w_ts_tm_sqrd = (w.ts.tm)^2
        inv_ts_denom = 1 / ((ts + tm)^2 + (w.ts.tm)^2)
        ts_num = (ts + tm)ts
    """

    data.one_s2s = 1.0 - data.params[data.s2s_index[data.i]]
    data.s2f_s2 = data.params[data.s2f_index[data.i]] * data.one_s2s

    data.ts_tm = data.params[data.ts_index[data.i]] + data.diff_params[0]
    data.ts_tm_ts = data.ts_tm * data.params[data.ts_index[data.i]]
    data.ts_tm_sqrd = data.ts_tm ** 2
    data.w_ts_tm_sqrd = data.w_tm_sqrd * data.params[data.ts_index[data.i]] ** 2
    if data.ts_tm == 0.0:
        data.inv_ts_denom = 0.0 * data.w_ts_tm_sqrd
    else:
        data.inv_ts_denom = 1.0 / (data.ts_tm_sqrd + data.w_ts_tm_sqrd)
    data.ts_num = data.ts_tm * data.params[data.ts_index[data.i]]



# Extended {S2f, tf, S2, ts}.
#############################

def calc_S2f_tf_S2_ts_jw_comps(data):
    """Spectral density component function.

    Calculate the components of the isotropic spectral density value for the extended model-free
    formula with the parameters S2f, tf, S2, and ts.

    The formula is:

                 2 /    S2 . tm        (1 - S2f) . tf'     (S2f - S2) . ts' \ 
        J(w)  =  - | -------------  +  ---------------  +  ---------------- |
                 5 \ 1 + (w.tm)**2     1 + (w.tf')**2       1 + (w.ts')**2  /


    Simplified:

                 2    /      S2            (1 - S2f)(tf + tm)tf          (S2f - S2)(ts + tm)ts   \ 
        J(w)  =  - tm | ------------  +  -------------------------  +  ------------------------- |
                 5    \ 1 + (w.tm)^2     (tf + tm)^2 + (w.tf.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /


    Replicated calculations are:

        w_tm_sqrd = (w.tm)^2        (pre-calculated during initialisation)

        tf_tm = tf + tm
        ts_tm = ts + tm
        tf_tm_tf = (tf + tm).tf
        ts_tm_ts = (ts + tm).ts


    Calculations which are replicated in the gradient equations are:

        two_fifths_tm = 2/5 * tm        (pre-calculated during initialisation)
        fact_tm = 1 / (1 + (w.tm)^2)    (pre-calculated during initialisation)

        one_s2f = 1 - S2f
        s2f_s2 = S2f - S2

        tf_tm_sqrd = (tf + tm)^2
        ts_tm_sqrd = (ts + tm)^2
        w_tf_tm_sqrd = (w.tf.tm)^2
        w_ts_tm_sqrd = (w.ts.tm)^2
        inv_tf_denom = 1 / ((tf + tm)^2 + (w.tf.tm)^2)
        inv_ts_denom = 1 / ((ts + tm)^2 + (w.ts.tm)^2)
        tf_num = (tf + tm)tf
        ts_num = (ts + tm)ts
    """

    data.one_s2f = 1.0 - data.params[data.s2f_index[data.i]]
    data.s2f_s2 = data.params[data.s2f_index[data.i]] - data.params[data.s2_index[data.i]]

    data.tf_tm = data.params[data.tf_index[data.i]] + data.diff_params[0]
    data.ts_tm = data.params[data.ts_index[data.i]] + data.diff_params[0]
    data.tf_tm_tf = data.tf_tm * data.params[data.tf_index[data.i]]
    data.ts_tm_ts = data.ts_tm * data.params[data.ts_index[data.i]]
    data.tf_tm_sqrd = data.tf_tm ** 2
    data.ts_tm_sqrd = data.ts_tm ** 2
    data.w_tf_tm_sqrd = data.w_tm_sqrd[data.i] * data.params[data.tf_index[data.i]] ** 2
    data.w_ts_tm_sqrd = data.w_tm_sqrd[data.i] * data.params[data.ts_index[data.i]] ** 2
    if data.tf_tm == 0.0:
        data.inv_tf_denom = 0.0 * data.w_tf_tm_sqrd
    else:
        data.inv_tf_denom = 1.0 / (data.tf_tm_sqrd + data.w_tf_tm_sqrd)
    if data.ts_tm == 0.0:
        data.inv_ts_denom = 0.0 * data.w_ts_tm_sqrd
    else:
        data.inv_ts_denom = 1.0 / (data.ts_tm_sqrd + data.w_ts_tm_sqrd)
    data.tf_num = data.tf_tm * data.params[data.tf_index[data.i]]
    data.ts_num = data.ts_tm * data.params[data.ts_index[data.i]]



# Extended {tm, S2f, tf, S2, ts}.
#################################

def calc_tm_S2f_tf_S2_ts_jw_comps(data):
    """Spectral density component function.

    Calculate the components of the isotropic spectral density value for the extended model-free
    formula with the parameters S2f, tf, S2, and ts.

    The formula is:

                 2 /    S2 . tm        (1 - S2f) . tf'     (S2f - S2) . ts' \ 
        J(w)  =  - | -------------  +  ---------------  +  ---------------- |
                 5 \ 1 + (w.tm)**2     1 + (w.tf')**2       1 + (w.ts')**2  /


    Simplified:

                 2    /      S2            (1 - S2f)(tf + tm)tf          (S2f - S2)(ts + tm)ts   \ 
        J(w)  =  - tm | ------------  +  -------------------------  +  ------------------------- |
                 5    \ 1 + (w.tm)^2     (tf + tm)^2 + (w.tf.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /


    Replicated calculations are:

        w_tm_sqrd = (w.tm)^2

        tf_tm = tf + tm
        ts_tm = ts + tm
        tf_tm_tf = (tf + tm).tf
        ts_tm_ts = (ts + tm).ts


    Calculations which are replicated in the gradient equations are:

        two_fifths_tm = 2/5 * tm
        fact_tm = 1 / (1 + (w.tm)^2)

        one_s2f = 1 - S2f
        s2f_s2 = S2f - S2

        tf_tm_sqrd = (tf + tm)^2
        ts_tm_sqrd = (ts + tm)^2
        w_tf_tm_sqrd = (w.tf.tm)^2
        w_ts_tm_sqrd = (w.ts.tm)^2
        inv_tf_denom = 1 / ((tf + tm)^2 + (w.tf.tm)^2)
        inv_ts_denom = 1 / ((ts + tm)^2 + (w.ts.tm)^2)
        tf_num = (tf + tm)tf
        ts_num = (ts + tm)ts
    """

    data.w_tm_sqrd = data.frq_sqrd_list * data.params[data.tm_index[data.i]] ** 2
    data.two_fifths_tm = 0.4 * data.params[data.tm_index[data.i]]
    data.two_fifths_tm_sqrd = 0.4 * data.params[data.tm_index[data.i]] ** 2
    data.fact_tm = 1.0 / (1.0 + data.w_tm_sqrd)

    data.one_s2f = 1.0 - data.params[data.s2f_index[data.i]]
    data.s2f_s2 = data.params[data.s2f_index[data.i]] - data.params[data.s2_index[data.i]]

    data.tf_tm = data.params[data.tf_index[data.i]] + data.params[data.tm_index[data.i]]
    data.ts_tm = data.params[data.ts_index[data.i]] + data.params[data.tm_index[data.i]]
    data.tf_tm_tf = data.tf_tm * data.params[data.tf_index[data.i]]
    data.ts_tm_ts = data.ts_tm * data.params[data.ts_index[data.i]]
    data.tf_tm_sqrd = data.tf_tm ** 2
    data.ts_tm_sqrd = data.ts_tm ** 2
    data.w_tf_tm_sqrd = data.w_tm_sqrd * data.params[data.tf_index[data.i]] ** 2
    data.w_ts_tm_sqrd = data.w_tm_sqrd * data.params[data.ts_index[data.i]] ** 2
    if data.tf_tm == 0.0:
        data.inv_tf_denom = 0.0 * data.w_tf_tm_sqrd
    else:
        data.inv_tf_denom = 1.0 / (data.tf_tm_sqrd + data.w_tf_tm_sqrd)
    if data.ts_tm == 0.0:
        data.inv_ts_denom = 0.0 * data.w_ts_tm_sqrd
    else:
        data.inv_ts_denom = 1.0 / (data.ts_tm_sqrd + data.w_ts_tm_sqrd)
    data.tf_num = data.tf_tm * data.params[data.tf_index[data.i]]
    data.ts_num = data.ts_tm * data.params[data.ts_index[data.i]]



# Extended 2 {S2f, tf, S2s, ts}.
################################

def calc_S2f_tf_S2s_ts_jw_comps(data):
    """Spectral density component function.

    Calculate the components of the isotropic spectral density value for the extended model-free
    formula with the parameters S2f, tf, S2s, and ts.

    The formula is:

                 2 /    S2 . tm        (1 - S2f) . tf'     (S2f - S2) . ts' \ 
        J(w)  =  - | -------------  +  ---------------  +  ---------------- |
                 5 \ 1 + (w.tm)**2     1 + (w.tf')**2       1 + (w.ts')**2  /


    Simplified:

                 2    /   S2f . S2s        (1 - S2f)(tf + tm)tf         S2f(1 - S2s)(ts + tm)ts  \ 
        J(w)  =  - tm | ------------  +  -------------------------  +  ------------------------- |
                 5    \ 1 + (w.tm)^2     (tf + tm)^2 + (w.tf.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /


    Replicated calculations are:

        w_tm_sqrd = (w.tm)^2        (pre-calculated during initialisation)

        tf_tm = tf + tm
        ts_tm = ts + tm
        tf_tm_tf = (tf + tm).tf
        ts_tm_ts = (ts + tm).ts


    Calculations which are replicated in the gradient equations are:

        two_fifths_tm = 2/5 * tm        (pre-calculated during initialisation)
        fact_tm = 1 / (1 + (w.tm)^2)    (pre-calculated during initialisation)

        one_s2s = 1 - S2s
        one_s2f = 1 - S2f
        s2f_s2 = S2f(1 - S2s) = S2f - S2

        tf_tm_sqrd = (tf + tm)^2
        ts_tm_sqrd = (ts + tm)^2
        w_tf_tm_sqrd = (w.tf.tm)^2
        w_ts_tm_sqrd = (w.ts.tm)^2
        inv_tf_denom = 1 / ((tf + tm)^2 + (w.tf.tm)^2)
        inv_ts_denom = 1 / ((ts + tm)^2 + (w.ts.tm)^2)
        tf_num = (tf + tm)tf
        ts_num = (ts + tm)ts
    """

    data.one_s2s = 1.0 - data.params[data.s2s_index[data.i]]
    data.one_s2f = 1.0 - data.params[data.s2f_index[data.i]]
    data.s2f_s2 = data.params[data.s2f_index[data.i]] * data.one_s2s

    data.tf_tm = data.params[data.tf_index[data.i]] + data.diff_params[0]
    data.ts_tm = data.params[data.ts_index[data.i]] + data.diff_params[0]
    data.tf_tm_tf = data.tf_tm * data.params[data.tf_index[data.i]]
    data.ts_tm_ts = data.ts_tm * data.params[data.ts_index[data.i]]
    data.tf_tm_sqrd = data.tf_tm ** 2
    data.ts_tm_sqrd = data.ts_tm ** 2
    data.w_tf_tm_sqrd = data.w_tm_sqrd * data.params[data.tf_index[data.i]] ** 2
    data.w_ts_tm_sqrd = data.w_tm_sqrd * data.params[data.ts_index[data.i]] ** 2
    if data.tf_tm == 0.0:
        data.inv_tf_denom = 0.0 * data.w_tf_tm_sqrd
    else:
        data.inv_tf_denom = 1.0 / (data.tf_tm_sqrd + data.w_tf_tm_sqrd)
    if data.ts_tm == 0.0:
        data.inv_ts_denom = 0.0 * data.w_ts_tm_sqrd
    else:
        data.inv_ts_denom = 1.0 / (data.ts_tm_sqrd + data.w_ts_tm_sqrd)
    data.tf_num = data.tf_tm * data.params[data.tf_index[data.i]]
    data.ts_num = data.ts_tm * data.params[data.ts_index[data.i]]




###############################
# Spectral density gradients. #
###############################


# Original {tm} and {tm, S2}.
#############################

def calc_tm_djw_comps(data):
    """Spectral density gradient component function.

    Calculate the components of the isotropic spectral density gradient for the original model-free
    formula with the parameters tm and S2.

    Replicated calculations are:

                           1 - (w.tm)^2
        fact_djw_dtm  =  ----------------
                         (1 + (w.tm)^2)^2
    """

    data.fact_djw_dtm = (1.0 - data.w_tm_sqrd) * data.fact_tm**2



# Original {S2, te}.
####################

def calc_S2_te_djw_comps(data):
    """Spectral density gradient component function.

    Calculate the components of the isotropic spectral density gradient for the original model-free
    formula with the parameters S2 and te.

    Replicated calculations are:

        two_fifths_tm_sqrd = 2/5 * tm^2        (pre-calculated during initialisation)

                         2        (te + tm)^2 - (w.te.tm)^2
        fact_djw_dte  =  - tm^2 -----------------------------
                         5      ((te + tm)^2 + (w.te.tm)^2)^2
    """

    data.fact_djw_dte = data.two_fifths_tm_sqrd * (data.te_tm_sqrd - data.w_te_tm_sqrd) * data.inv_te_denom ** 2



# Original {tm, S2, te}.
########################

def calc_tm_S2_te_djw_comps(data):
    """Spectral density gradient component function.

    Calculate the components of the isotropic spectral density gradient for the original model-free
    formula with the parameters tm, S2, and te.

    Replicated calculations are:

                       (te + tm)^2 - (w.te.tm)^2
        fact_djw  =  -----------------------------
                     ((te + tm)^2 + (w.te.tm)^2)^2

                            1 - (w.tm)^2
        fact1_djw_dtm  =  ----------------
                          (1 + (w.tm)^2)^2

                                 (te + tm)^2 - (w.te.tm)^2
        fact2_djw_dtm  =  te^2 -----------------------------
                               ((te + tm)^2 + (w.te.tm)^2)^2

                         2        (te + tm)^2 - (w.te.tm)^2
        fact_djw_dte  =  - tm^2 -----------------------------
                         5      ((te + tm)^2 + (w.te.tm)^2)^2
    """

    # tm.
    data.fact1_djw_dtm = (1.0 - data.w_tm_sqrd) * data.fact_tm**2

    # te.
    data.fact_djw = (data.te_tm_sqrd - data.w_te_tm_sqrd) * data.inv_te_denom ** 2
    data.fact2_djw_dtm = data.params[data.te_index[data.i]]**2 * data.fact_djw
    data.fact_djw_dte = data.two_fifths_tm_sqrd * data.fact_djw



# Extended {S2f, S2, ts}.
#########################

def calc_S2f_S2_ts_djw_comps(data):
    """Spectral density gradient component function.

    Calculate the components of the isotropic spectral density gradient for the extended model-free
    formula with the parameters S2f, S2, and ts.

    Replicated calculations are:

        two_fifths_tm_sqrd = 2/5 * tm^2        (pre-calculated during initialisation)


                         2        (ts + tm)^2 - (w.ts.tm)^2
        fact_djw_dts  =  - tm^2 -----------------------------
                         5      ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    data.fact_djw_dts = data.two_fifths_tm_sqrd * (data.ts_tm_sqrd - data.w_ts_tm_sqrd) * data.inv_ts_denom ** 2



# Extended {tm, S2f, S2, ts}.
#############################

def calc_tm_S2f_S2_ts_djw_comps(data):
    """Spectral density gradient component function.

    Calculate the components of the isotropic spectral density gradient for the extended model-free
    formula with the parameters S2f, S2, and ts.

    Replicated calculations are:

                       (ts + tm)^2 - (w.ts.tm)^2
        fact_djw  =  -----------------------------
                     ((ts + tm)^2 + (w.ts.tm)^2)^2


                            1 - (w.tm)^2
        fact1_djw_dtm  =  ----------------
                          (1 + (w.tm)^2)^2


                                 (ts + tm)^2 - (w.ts.tm)^2
        fact2_djw_dtm  =  ts^2 -----------------------------
                               ((ts + tm)^2 + (w.ts.tm)^2)^2


                         2        (ts + tm)^2 - (w.ts.tm)^2
        fact_djw_dts  =  - tm^2 -----------------------------
                         5      ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    # tm.
    data.fact1_djw_dtm = (1.0 - data.w_tm_sqrd) * data.fact_tm**2

    # ts.
    data.fact_djw = (data.ts_tm_sqrd - data.w_ts_tm_sqrd) * data.inv_ts_denom ** 2
    data.fact2_djw_dtm = data.params[data.ts_index[data.i]]**2 * data.fact_djw
    data.fact_djw_dts = data.two_fifths_tm_sqrd * data.fact_djw



# Extended {S2f, tf, S2, ts}.
#############################

def calc_S2f_tf_S2_ts_djw_comps(data):
    """Spectral density gradient component function.

    Calculate the components of the isotropic spectral density gradient for the extended model-free
    formula with the parameters S2f, tf, S2, and ts.

    Replicated calculations are:

        two_fifths_tm_sqrd = 2/5 * tm^2        (pre-calculated during initialisation)


                         2        (tf + tm)^2 - (w.tf.tm)^2
        fact_djw_dtf  =  - tm^2 -----------------------------
                         5      ((tf + tm)^2 + (w.tf.tm)^2)^2


                         2        (ts + tm)^2 - (w.ts.tm)^2
        fact_djw_dts  =  - tm^2 -----------------------------
                         5      ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    data.fact_djw_dtf = data.two_fifths_tm_sqrd * (data.tf_tm_sqrd - data.w_tf_tm_sqrd) * data.inv_tf_denom ** 2
    data.fact_djw_dts = data.two_fifths_tm_sqrd * (data.ts_tm_sqrd - data.w_ts_tm_sqrd) * data.inv_ts_denom ** 2



# Extended {tm, S2f, tf, S2, ts}.
#################################

def calc_tm_S2f_tf_S2_ts_djw_comps(data):
    """Spectral density gradient component function.

    Calculate the components of the isotropic spectral density gradient for the extended model-free
    formula with the parameters tm, S2f, tf, S2, and ts.

    Replicated calculations are:

                        (tf + tm)^2 - (w.tf.tm)^2
        fact2_djw  =  -----------------------------
                      ((tf + tm)^2 + (w.tf.tm)^2)^2


                        (ts + tm)^2 - (w.ts.tm)^2
        fact3_djw  =  -----------------------------
                      ((ts + tm)^2 + (w.ts.tm)^2)^2


                            1 - (w.tm)^2
        fact1_djw_dtm  =  ----------------
                          (1 + (w.tm)^2)^2


                                 (tf + tm)^2 - (w.tf.tm)^2
        fact2_djw_dtm  =  tf^2 -----------------------------
                               ((tf + tm)^2 + (w.tf.tm)^2)^2


                                 (ts + tm)^2 - (w.ts.tm)^2
        fact3_djw_dtm  =  ts^2 -----------------------------
                               ((ts + tm)^2 + (w.ts.tm)^2)^2


                         2        (tf + tm)^2 - (w.tf.tm)^2
        fact_djw_dtf  =  - tm^2 -----------------------------
                         5      ((tf + tm)^2 + (w.tf.tm)^2)^2


                         2        (ts + tm)^2 - (w.ts.tm)^2
        fact_djw_dts  =  - tm^2 -----------------------------
                         5      ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    # tm.
    data.fact1_djw_dtm = (1.0 - data.w_tm_sqrd) * data.fact_tm**2

    # tf.
    data.fact2_djw = (data.tf_tm_sqrd - data.w_tf_tm_sqrd) * data.inv_tf_denom ** 2
    data.fact2_djw_dtm = data.params[data.tf_index[data.i]]**2 * data.fact2_djw
    data.fact_djw_dtf = data.two_fifths_tm_sqrd * data.fact2_djw

    # ts.
    data.fact3_djw = (data.ts_tm_sqrd - data.w_ts_tm_sqrd) * data.inv_ts_denom ** 2
    data.fact3_djw_dtm = data.params[data.ts_index[data.i]]**2 * data.fact3_djw
    data.fact_djw_dts = data.two_fifths_tm_sqrd * data.fact3_djw



# Extended 2 {S2f, S2s, ts}.
############################

def calc_S2f_S2s_ts_djw_comps(data):
    """Spectral density gradient component function.

    Calculate the components of the isotropic spectral density gradient for the extended model-free
    formula with the parameters S2f, S2s, and ts.

    Replicated calculations are:

        two_fifths_tm_sqrd = 2/5 * tm^2        (pre-calculated during initialisation)


                         2        (ts + tm)^2 - (w.ts.tm)^2
        fact_djw_dts  =  - tm^2 -----------------------------
                         5      ((ts + tm)^2 + (w.ts.tm)^2)^2


                          2    /      1                 (ts + tm).ts        \ 
        fact_djw_ds2s  =  - tm | ------------  -  ------------------------- |
                          5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    data.fact_djw_dts = data.two_fifths_tm_sqrd * (data.ts_tm_sqrd - data.w_ts_tm_sqrd) * data.inv_ts_denom ** 2
    data.fact_djw_ds2s = data.two_fifths_tm * (data.fact_tm - data.ts_tm_ts * data.inv_ts_denom)



# Extended 2 {S2f, tf, S2s, ts}.
################################

def calc_S2f_tf_S2s_ts_djw_comps(data):
    """Spectral density gradient component function.

    Calculate the components of the isotropic spectral density gradient for the extended model-free
    formula with the parameters S2f, tf, S2s, and ts.

    Replicated calculations are:

        two_fifths_tm_sqrd = 2/5 * tm^2        (pre-calculated during initialisation)


                         2        (tf + tm)^2 - (w.tf.tm)^2
        fact_djw_dtf  =  - tm^2 -----------------------------
                         5      ((tf + tm)^2 + (w.tf.tm)^2)^2


                         2        (ts + tm)^2 - (w.ts.tm)^2
        fact_djw_dts  =  - tm^2 -----------------------------
                         5      ((ts + tm)^2 + (w.ts.tm)^2)^2


                          2    /      1                 (ts + tm).ts        \ 
        fact_djw_ds2s  =  - tm | ------------  -  ------------------------- |
                          5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    data.fact_djw_dtf = data.two_fifths_tm_sqrd * (data.tf_tm_sqrd - data.w_tf_tm_sqrd) * data.inv_tf_denom ** 2
    data.fact_djw_dts = data.two_fifths_tm_sqrd * (data.ts_tm_sqrd - data.w_ts_tm_sqrd) * data.inv_ts_denom ** 2
    data.fact_djw_ds2s = data.two_fifths_tm * (data.fact_tm - data.ts_tm_ts * data.inv_ts_denom)
