all: clean refresh out

clean:
	rm -rf ./*.dmp ./*.out ./*.tmp

refresh:
	./mercury6_4mult_passstarsfeelplum_instantremove_closeenc_nogasdisk

out:
	rm -rf  ./*.aei
	./element6

compile:
	gfortran -O3 -funroll-all-loops -ffixed-line-length-0 mercury6_4mult_passstarsfeelplum_instantremove_closeenc_nogasdisk.for -o mercury6_4mult_passstarsfeelplum_instantremove_closeenc_nogasdisk
	gfortran -O3 -funroll-all-loops -ffixed-line-length-0 element6.for -o element6

jacobi:
	python ./find_jacobi.py -i config_toymodel.py 