#!/bin/sh

for collection in 'ace2004' 'aidatesta' 'aidatestb' 'msnbc' 'wes2015'
do
	for system in 'our' #'spotlight'
	do
		python3 test.py $collection $system
	done
done
