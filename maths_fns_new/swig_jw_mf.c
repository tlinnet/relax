/*
Copyright (C) 2003 Edward d'Auvergne

This file is part of the program relax.

relax is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

relax is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with relax; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/



/* Calculate the isotropic spectral density value for the original model-free formula with the single parameter S2.

The formula is:

	         2 /    S2 . tm    \ 
	J(w)  =  - | ------------- |
	         5 \ 1 + (w.tm)**2 /
*/
double c_calc_iso_s2_jw(double, double);

double jw;

double c_calc_iso_s2_jw(double s2_tm, double omega_tm_sqrd) {
	return  0.4 * (s2_tm / (1.0 + omega_tm_sqrd));
}

double c_calc_iso_s2f_s2s_ts_jw(double s2f, double s2s_tm, double omega_tm_sqrd, double s2s, double ts_prime, double omega_ts_prime_sqrd) {
	return 0.4 * s2f * (s2s_tm / (1.0 + omega_tm_sqrd) + (1.0 - s2s) * ts_prime / (1.0 + omega_ts_prime_sqrd));
}
