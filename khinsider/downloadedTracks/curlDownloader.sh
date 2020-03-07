#!/bin/bash

filename="linkData.txt"
track=1
while read -r line; do
	echo
	echo "$track : "
	curl $line
	sleep 15s
	track=$(expr $track + 1)
done < "$filename"
