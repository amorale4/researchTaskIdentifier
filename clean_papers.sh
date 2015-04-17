#!/bin/bash
#path to data/executables
executable="project/parscit/bin/citeExtract.pl"
DataPath="data"
#output directories
CleanPath="cleanXMLdataV2/"
if [ ! -d "$CleanPath" ]; then
	mkdir $CleanPath
	for i in $(ls $DataPath | grep "\.txt"); do
		echo  item: $i
		#first need to clean the review data
		output="${i%.*}"	
		outputClean="${output//,}.out"
		#if [ -f $CleanPath/"${outputClean}" ];
		#then
	 	#		echo "File $CleanPath/$outputClean exists."
		#else
		#	echo "File $CleanPath/$outputClean does not exist."
		./$executable -m extract_all $DataPath/"${i}" $CleanPath/"${outputClean}"
		#fi
	done
fi

