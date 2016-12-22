#! /bin/bash
searchFor="$1"
if [ -z $1 ]; then
	searchFor="."
fi

for file in naf/123[${searchFor}]*.*
do
	#echo $file
	python3 process.py $file
done

#python runtest.py123a3f1d-483c-427b-8749-db298859b836.in.naf
