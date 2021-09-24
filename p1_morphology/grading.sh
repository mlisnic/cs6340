echo '####################'
echo '#  Grading Script  #'
echo '####################'
echo

scoring=false
python3 morphology.py sampleDict.txt sampleRules.txt sampleTest.txt > yourTrace.txt

if $scoring; then
    missing=$( comm -13 <(sed '/^$/d' yourTrace.txt | sort ) \
                        <(sed '/^$/d' sampleTrace.txt | sort ) | wc -l )
    extra=$( comm -23 <(sed '/^$/d' yourTrace.txt | sort ) \
                      <(sed '/^$/d' sampleTrace.txt | sort ) | wc -l )
    t1=$( sed '/^$/d' sampleTrace.txt | wc -l )
    t2=$( sed '/^$/d' yourTrace.txt | wc -l )
    pre=$(( 100-100*extra/t2 ))
    rec=$(( 100-100*missing/t1 ))
    f1=$(( 2*pre*rec/(pre+rec) ))
    echo "Missing Derivations:" $missing
    echo "Extra Derivations:" $extra
    if [[ $missing -eq "0" && $extra -eq "0" ]]; then
        echo "Correct!"
    fi
    # echo "Final Score: $f1/100"
else
    ds=$( diff yourTrace.txt sampleTrace.txt )
    if [ -z "$ds" ]; then
        echo "Correct!"
    else
        echo "There are some errors!"
        diff yourTrace.txt sampleTrace.txt
    fi
fi
