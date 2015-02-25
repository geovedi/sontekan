#!/bin/bash

args=`getopt hl:j:f: $*`

set -- $args

# You cannot use the set command with a backquoted getopt directly,
# since the exit code from getopt would be shadowed by those of set,
# which is zero by definition.
for i
do
    case "$i"
    in
        -h)
            echo "Usage: psort -l [LINE] -j [NUM_JOBS] -f [FILE]";
            shift;;
        -l)
            line="$2"; shift;
            shift;;
        -j)
            jobs="$2"; shift;
            shift;;
        -f)
            file="$2"; shift;
            shift;;
        --)
            shift; break;;
    esac
done

if [[ ${file} && ${jobs} && ${line} ]]
then
    split -a 3 -l ${line} ${file} ${file}.part.

    suffix=sorttemp_$(date +%F)
    nthreads=${jobs}

    i=0
    for fname in `ls ${file}.part*`
    do
            let i++
            sort $fname > $fname.$suffix &
            mres=$(($i % $nthreads))
            test "$mres" -eq 0 && wait
    done
    wait
    sort -m ${file}.part*.$suffix > ${file}.sorted
    rm ${file}.part*
fi
