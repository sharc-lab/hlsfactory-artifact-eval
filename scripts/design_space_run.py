import shutil
from pathlib import Path

from hlsfactory.datasets_builtin import (
    dataset_chstone_builder,
    dataset_machsuite_builder,
    dataset_polybench_builder,
)
from hlsfactory.flow_vitis import (
    VitisHLSImplFlow,
    VitisHLSImplReportFlow,
    VitisHLSSynthFlow,
)
from hlsfactory.framework import (
    DesignDatasetCollection,
    count_total_designs_in_dataset_collection,
)
from hlsfactory.opt_dsl_frontend import OptDSLFrontend
from utils.utils import get_env_vars

DIR_DATASETS = get_env_vars(["DIR_DATASETS"])["DIR_DATASETS"]
assert isinstance(DIR_DATASETS, Path)

WORK_DIR = DIR_DATASETS / "hlsfactory_workdir_design_space_sampled"

if WORK_DIR.exists():
    shutil.rmtree(WORK_DIR)
WORK_DIR.mkdir()

N_JOBS = get_env_vars(["N_JOBS"])["N_JOBS"]
assert isinstance(N_JOBS, int)
CPU_AFFINITY = list(range(N_JOBS))


dataset_polybench_xilinx = dataset_polybench_builder("polybench_xilinx", WORK_DIR)
dataset_machsuite_xilinx = dataset_machsuite_builder("machsuite_xilinx", WORK_DIR)
dataset_chstone_xilinx = dataset_chstone_builder("chstone_xilinx", WORK_DIR)

datasets: DesignDatasetCollection = {
    "polybench_xilinx": dataset_polybench_xilinx,
    "machsuite_xilinx": dataset_machsuite_xilinx,
    "chstone_xilinx": dataset_chstone_xilinx,
}

total_count = count_total_designs_in_dataset_collection(datasets)


N_RANDOM_SAMPLES = 12
RAMDOM_SAMPLE_SEED = 64
opt_dsl_frontend = OptDSLFrontend(
    WORK_DIR,
    random_sample=True,
    random_sample_num=N_RANDOM_SAMPLES,
    random_sample_seed=RAMDOM_SAMPLE_SEED,
    log_execution_time=True,
)
datasets_post_frontend = (
    opt_dsl_frontend.execute_multiple_design_datasets_fine_grained_parallel(
        datasets,
        True,
        lambda x: f"{x}__post_frontend",
        n_jobs=N_JOBS,
        cpu_affinity=CPU_AFFINITY,
    )
)

total_count_post_frontend = count_total_designs_in_dataset_collection(
    datasets_post_frontend
)

print(f"Total Designs: {total_count}")
print(f"Total Designs post-frontend: {total_count_post_frontend}")

TIMEOUT_HLS_SYNTH = 60.0 * 8  # 8 minutes
TIMEOUT_HLS_IMPL = 60.0 * 30  # 30 minutes

total_time_estimation = (
    total_count_post_frontend * (TIMEOUT_HLS_SYNTH + TIMEOUT_HLS_IMPL) / N_JOBS
)

print(
    f"Estimated worst-case build time:\n{total_time_estimation} seconds\n{total_time_estimation / 60} minutes\n{total_time_estimation / 3600} hours"
)

VIVADO_PATH = get_env_vars(["VIVADO_PATH__2023_1"])["VIVADO_PATH__2023_1"]
assert isinstance(VIVADO_PATH, Path)
VITIS_HLS_PATH = get_env_vars(["VITIS_HLS_PATH__2023_1"])["VITIS_HLS_PATH__2023_1"]
assert isinstance(VITIS_HLS_PATH, Path)

VIVADO_BIN = VIVADO_PATH / "bin" / "vivado"
VITIS_HLS_BIN = VITIS_HLS_PATH / "bin" / "vitis_hls"


toolflow_vitis_hls_synth = VitisHLSSynthFlow(
    vitis_hls_bin=str(VITIS_HLS_BIN),
    env_var_xilinx_hls=str(VITIS_HLS_PATH),
    env_var_xilinx_vivado=str(VIVADO_PATH),
)
datasets_post_hls_synth = (
    toolflow_vitis_hls_synth.execute_multiple_design_datasets_fine_grained_parallel(
        datasets_post_frontend,
        False,
        n_jobs=N_JOBS,
        cpu_affinity=CPU_AFFINITY,
        timeout=TIMEOUT_HLS_SYNTH,
    )
)

toolflow_vitis_hls_implementation = VitisHLSImplFlow(
    vitis_hls_bin=str(VITIS_HLS_BIN),
    env_var_xilinx_hls=str(VITIS_HLS_PATH),
    env_var_xilinx_vivado=str(VIVADO_PATH),
)
datasets_post_hls_implementation = toolflow_vitis_hls_implementation.execute_multiple_design_datasets_fine_grained_parallel(
    datasets_post_hls_synth,
    False,
    n_jobs=N_JOBS,
    cpu_affinity=CPU_AFFINITY,
    timeout=TIMEOUT_HLS_IMPL,
)

toolflow_vitis_hls_impl_report = VitisHLSImplReportFlow(
    vitis_hls_bin=str(VITIS_HLS_BIN),
    vivado_bin=str(VIVADO_BIN),
    env_var_xilinx_hls=str(VITIS_HLS_PATH),
    env_var_xilinx_vivado=str(VIVADO_PATH),
)
toolflow_vitis_hls_impl_report.execute_multiple_design_datasets_fine_grained_parallel(
    datasets_post_hls_implementation,
    False,
    n_jobs=N_JOBS,
    cpu_affinity=CPU_AFFINITY,
)
