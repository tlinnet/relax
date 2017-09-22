#!/usr/bin/python
###############################################################################
#                                                                             #
# Copyright (C) 2011 Corrado Chisari                                          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU Lesser General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU Lesser General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the GNU Lesser General Public License    #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

from numpy import bitwise_xor
from extern.sobol.sobol_lib import i4_bit_hi1, i4_bit_lo0, i4_sobol, i4_uniform, prime_ge
import datetime
def sobol_test01 ( ):
#*****************************************************************************80
#
## SOBOL_TEST01 tests BITXOR.
#
#	Licensing:
#
#		This code is distributed under the GNU LGPL license.
#
#  	Modified:
#
#    		22 February 2011
#
#	Author:
#
#		Original MATLAB version by John Burkardt.
#		PYTHON version by Corrado Chisari
#
	print('\nSOBOL_TEST01') 
	print('  BITXOR is a MATLAB intrinsic function which returns') 
	print('  the bitwise exclusive OR of two integers.') 
	print('\n     I     J     BITXOR(I,J)\n') 

	seed = 123456789

	for test in range(0, 10):

		[ i, seed ] = i4_uniform ( 0, 100, seed )
		[ j, seed ] = i4_uniform ( 0, 100, seed )
		k = bitwise_xor ( i, j )

		print('  %6d  %6d  %6d'%( i, j, k ))

	return


def sobol_test02 ( ):
#*****************************************************************************80
#
## SOBOL_TEST02 tests I4_BIT_HI1.
#
#	Licensing:
#
#		This code is distributed under the GNU LGPL license.
#
#  	Modified:
#
#    		22 February 2011
#
#	Author:
#
#		Original MATLAB version by John Burkardt.
#		PYTHON version by Corrado Chisari
#
	print('\nSOBOL_TEST02') 
	print('  I4_BIT_HI1 returns the location of the high 1 bit.') 
	print('\n     I     I4_BIT_HI1(I)\n')

	seed = 123456789

	for test in range( 0, 10):

		[ i, seed ] = i4_uniform ( 0, 100, seed )

		j = i4_bit_hi1 ( i )

		print('%6d %6d'%( i, j ))
	return
	

def sobol_test03 ( ):
#*****************************************************************************80
#
## SOBOL_TEST03 tests I4_BIT_LO0.
#
#	Licensing:
#
#		This code is distributed under the GNU LGPL license.
#
#  	Modified:
#
#    		22 February 2011
#
#	Author:
#
#		Original MATLAB version by John Burkardt.
#		PYTHON version by Corrado Chisari
#
	print('\nSOBOL_TEST03')
	print('  I4_BIT_LO0 returns the location of the low 0 bit.')
	print('\n     I     I4_BIT_LO0(I)')

	seed = 123456789

	for test in range(0, 10):

		[ i, seed ] = i4_uniform ( 0, 100, seed )

		j = i4_bit_lo0 ( i )

		print('%6d %6d'%( i, j ))
	return


def sobol_test04 ( ):

#*****************************************************************************80
#
## SOBOL_TEST04 tests I4_SOBOL.
#
#	Licensing:
#
#		This code is distributed under the GNU LGPL license.
#
#  	Modified:
#
#    		22 February 2011
#
#	Author:
#
#		Original MATLAB version by John Burkardt.
#		PYTHON version by Corrado Chisari
#
	print('\nSOBOL_TEST04')
	print('  I4_SOBOL returns the next element')
	print('  of a Sobol sequence.')
	print('\n  In this test, we call I4_SOBOL repeatedly.\n')

	dim_max = 4

	for dim_num in range( 2, dim_max+1):

		seed = 0
		qs = prime_ge ( dim_num )

		print('\n  Using dimension DIM_NUM =   %d'%dim_num)
		print('\n  Seed  Seed   I4_SOBOL')
		print('  In    Out\n')
		for i in range( 0, 111):
			[ r, seed_out ] = i4_sobol ( dim_num, seed )
			if ( i <= 11 or 95 <= i ):
				out='%6d %6d  '%(seed, seed_out )
				for j in range (0, dim_num):
					out+='%10f  '%r[j]
				print(out)
			elif ( i == 12 ):
				print('......................')
			seed = seed_out
	return



def sobol_test05 ( ):
#*****************************************************************************80
#
## SOBOL_TEST05 tests I4_SOBOL.
#
#  	Licensing:
#
#    		This code is distributed under the GNU LGPL license.
#
#  	Modified:
#
#    		22 February 2011
#
#	Author:
#
#		Original MATLAB version by John Burkardt.
#		PYTHON version by Corrado Chisari
#
  print('')
  print('SOBOL_TEST05')
  print('  I4_SOBOL computes the next element of a Sobol sequence.')
  print('')
  print('  In this test, we demonstrate how the SEED can be')
  print('  manipulated to skip ahead in the sequence, or')
  print('  to come back to any part of the sequence.')
  print('')

  dim_num = 3

  print('')
  print('  Using dimension DIM_NUM =   %d\n'%dim_num) 

  seed = 0

  print('')
  print('  Seed  Seed   I4_SOBOL')
  print('  In    Out')
  print('')

  for i in range( 0, 10+1):
    [ r, seed_out ] = i4_sobol ( dim_num, seed )
    out= '%6d %6d  '%( seed, seed_out )
    for j in range( 1, dim_num+1):
      out+= '%10f  '% r[j-1] 
    print(out)
    seed = seed_out

  print('')
  print('  Jump ahead by increasing SEED:')
  print('')

  seed = 100

  print('')
  print('  Seed  Seed   I4_SOBOL')
  print('  In    Out')
  print('')

  for i in range( 1, 6):
    [ r, seed_out ] = i4_sobol ( dim_num, seed )
    out='%6d %6d  '%( seed, seed_out)
    for j in range( 1, dim_num+1):
      out+= '%10f  '% r[j-1] 
    print(out)
    seed = seed_out
  print('')
  print('  Jump back by decreasing SEED:')
  print('')

  seed = 3

  print('')
  print('  Seed  Seed   I4_SOBOL')
  print('  In    Out')
  print('')

  for i in range( 0, 11):
    [ r, seed_out ] = i4_sobol ( dim_num, seed )
    out='%6d %6d  '%( seed, seed_out)
    for j in range( 1, dim_num+1):
      out+= '%10f  '% r[j-1] 
    print(out)
    seed = seed_out

  print('')
  print('  Jump back by decreasing SEED:')
  print('')

  seed = 98

  print('')
  print('  Seed  Seed   I4_SOBOL')
  print('  In    Out')
  print('')

  for i in range( 1, 6):
    [ r, seed_out ] = i4_sobol ( dim_num, seed )
    out= '%6d %6d  '%( seed, seed_out )
    for j in range( 1, dim_num+1):
      out+= '%10f  '%r[j-1] 
    print(out)
    seed = seed_out

  return




##############MAIN#############
def main(argv=None):
	d=datetime.datetime.today()
	print(d.strftime("%d-%b-%Y %H:%M:%S"))
	print('\nSOBOL_TEST')
	print('  Test the MATLAB SOBOL routines.')

	sobol_test01()
	sobol_test02()
	sobol_test03()
	sobol_test04()
	sobol_test05()
	
	print('SOBOL_TEST')
	print('  Normal end of execution.')

	d=datetime.datetime.today()
	print(d.strftime("%d-%b-%Y %H:%M:%S"))

if __name__ == "__main__":
	main()
