#!/bin/bash

# need to run this command:
# xattr -d com.apple.quarantine batch_score_calc.sh
# if following error occurs:
# -bash: ./demo.sh: /bin/bash: bad interpreter: Operation not permitted

echo "server is set up"


for value in {0..457}
do
    python score_calculator.py $value
done
python adaptive_hist_eq.py
