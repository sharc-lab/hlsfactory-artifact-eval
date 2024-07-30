import shutil
from pathlib import Path

from hlsfactory.datasets_builtin import (
    dataset_machsuite_builder,
    dataset_polybench_builder,
)
from hlsfactory.flow_intel import IntelHLSSynthFlow, IntelQuartusImplFlow
from hlsfactory.opt_dsl_frontend_intel import OptDSLFrontendIntel
from utils.utils import get_env_vars

DIR_DATASETS = get_env_vars(["DIR_DATASETS"])["DIR_DATASETS"]
assert isinstance(DIR_DATASETS, Path)

WORK_DIR = DIR_DATASETS / "hlsfactory_intel_data"

if WORK_DIR.exists():
    shutil.rmtree(WORK_DIR)
WORK_DIR.mkdir()

N_JOBS = get_env_vars(["N_JOBS"])["N_JOBS"]
assert isinstance(N_JOBS, int)
CPU_AFFINITY = list(range(N_JOBS))


dataset_polybench_intel = dataset_polybench_builder("polybench_xilinx", WORK_DIR)
dataset_machsuite_intel = dataset_machsuite_builder("machsuite_xilinx", WORK_DIR)

datasets = {
    "polybench_intel": dataset_polybench_intel,
    "machsuite_intel": dataset_machsuite_intel,
}

opt_dsl_frontend_intel = OptDSLFrontendIntel(
    WORK_DIR, random_sample=True, random_sample_num=1
)

designs_after_frontend = {
    dataset_name: opt_dsl_frontend_intel.execute_multiple_designs(
        dataset.designs, n_jobs=N_JOBS
    )
    for dataset_name, dataset in datasets.items()
}

IPP_BIN = get_env_vars(["IPP_BIN_PATH"])["IPP_BIN_PATH"]
assert isinstance(IPP_BIN, Path)
QUARTUS_BIN = get_env_vars(["QUARTUS_SH_BIN_PATH"])["QUARTUS_SH_BIN_PATH"]
assert isinstance(QUARTUS_BIN, Path)


toolflow_intel_hls_synth = IntelHLSSynthFlow(ipp_bin=str(IPP_BIN.resolve()))
toolflow_intel_impl_synth = IntelQuartusImplFlow(quartus_bin=str(QUARTUS_BIN.resolve()))

for dataset_name, design_list in designs_after_frontend.items():
    toolflow_intel_hls_synth.execute_multiple_designs(design_list)


for dataset_name, design_list in designs_after_frontend.items():
    toolflow_intel_impl_synth.execute_multiple_designs(
        design_list, n_jobs=N_JOBS, cpu_affinity=CPU_AFFINITY
    )
