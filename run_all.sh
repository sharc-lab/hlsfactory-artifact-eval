#!/usr/bin/env sh

echo "Obtaining pregenerated datasets..."
python scripts/obtain_pregenerated_datasets.py

echo "Running all case study scripts..."

echo "- Running design_space_vis_2d.py"
python scripts/design_space_vis_2d.py > /dev/null
echo "- Running design_space_vis_stacked.py"
python scripts/design_space_vis_stacked.py > /dev/null
echo "- Running regression_testing_vis.py"
python scripts/regression_testing_vis.py > /dev/null
echo "- Running parallel_test_vis.py"
python scripts/parallel_test_vis.py > /dev/null
echo "- Running hlsyn_vis.py"
python scripts/hlsyn_vis.py > /dev/null
echo "- Running intel_vis.py"
python scripts/intel_vis.py > /dev/null