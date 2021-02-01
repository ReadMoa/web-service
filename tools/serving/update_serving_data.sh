#!/bin/bash
#
# Should execute under the root directory (web-service)
# $ ./tools/serving/update_serving_data.sh test

echo "----------------------------------------------"
echo "START updating serving storage"
echo "----------------------------------------------"

START=$(date +%s)

# Take the first argument as 'mode'
mode=$1
# Run the command.
PYTHONPATH=./ python3 tools/serving/update_serving_data.py --mode=$mode 

END=$(date +%s)
DIFF=$(echo "$END - $START" | bc)

echo "----------------------------------------------"
echo "COMPLETED updating serving storage (time passed: $DIFF seconds)"
echo "----------------------------------------------"