import shutil
from pathlib import Path

from hlsfactory.datasets_builtin import (
    dataset_chstone_builder,
    dataset_machsuite_builder,
    dataset_polybench_builder,
)
from hlsfactory.flow_vitis import VitisHLSSynthFlow
from hlsfactory.opt_dsl_frontend import OptDSLFrontend
from utils.utils import get_env_vars

DIR_DATASETS = get_env_vars(["DIR_DATASETS"])["DIR_DATASETS"]
assert isinstance(DIR_DATASETS, Path)

WORK_DIR = DIR_DATASETS / "hlsfactory_workdir_regression_testing"

if WORK_DIR.exists():
    shutil.rmtree(WORK_DIR)
WORK_DIR.mkdir()

N_JOBS = get_env_vars(["N_JOBS"])["N_JOBS"]
assert isinstance(N_JOBS, int)
CPU_AFFINITY = list(range(N_JOBS))


dataset_polybench_xilinx = dataset_polybench_builder("polybench_xilinx", WORK_DIR)
dataset_machsuite_xilinx = dataset_machsuite_builder("machsuite_xilinx", WORK_DIR)
dataset_chstone_xilinx = dataset_chstone_builder("chstone_xilinx", WORK_DIR)


datasets = {
    "polybench_xilinx": dataset_polybench_xilinx,
    "machsuite_xilinx": dataset_machsuite_xilinx,
    "chstone_xilinx": dataset_chstone_xilinx,
}


N_RANDOM_SAMPLES = 16
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
        lambda x: f"{x}_post_frontend",
        n_jobs=N_JOBS,
        cpu_affinity=CPU_AFFINITY,
    )
)


TIMEOUT_HLS_SYNTH = 60.0 * 5  # 5 minutes


VIVADO_PATH__2021_1 = get_env_vars(["VIVADO_PATH__2021_1"])["VIVADO_PATH__2021_1"]
assert isinstance(VIVADO_PATH__2021_1, Path)
VIVADO_PATH__2023_1 = get_env_vars(["VIVADO_PATH__2023_1"])["VIVADO_PATH__2023_1"]
assert isinstance(VIVADO_PATH__2023_1, Path)

VITIS_HLS_PATH__2021_1 = get_env_vars(["VITIS_HLS_PATH__2021_1"])[
    "VITIS_HLS_PATH__2021_1"
]
assert isinstance(VITIS_HLS_PATH__2021_1, Path)
VITIS_HLS_PATH__2023_1 = get_env_vars(["VITIS_HLS_PATH__2023_1"])[
    "VITIS_HLS_PATH__2023_1"
]
assert isinstance(VITIS_HLS_PATH__2023_1, Path)

VIVADO_PATHS = {
    "2021_1": VIVADO_PATH__2021_1,
    "2023_1": VIVADO_PATH__2023_1,
}

VITIS_HLS_PATHS = {
    "2021_1": VITIS_HLS_PATH__2021_1,
    "2023_1": VITIS_HLS_PATH__2023_1,
}

VITIS_HLS_BINS = {
    version: path / "bin" / "vitis_hls" for version, path in VITIS_HLS_PATHS.items()
}

DATASET_VERSIONS = {
    year: {
        dataset_name: dataset.copy_and_rename(
            f"{dataset_name}_post_hls_synth__{year}", WORK_DIR
        )
        for dataset_name, dataset in datasets_post_frontend.items()
    }
    for year, _ in VITIS_HLS_BINS.items()
}

for vitis_hls_version, datasets in DATASET_VERSIONS.items():
    vitis_hls_bin = VITIS_HLS_BINS[vitis_hls_version]
    vitis_hls_path = VITIS_HLS_PATHS[vitis_hls_version]
    vivado_path = VIVADO_PATHS[vitis_hls_version]
    toolflow_vitis_hls_synth = VitisHLSSynthFlow(
        vitis_hls_bin=str(vitis_hls_bin),
        env_var_xilinx_hls=str(vitis_hls_path),
        env_var_xilinx_vivado=str(vivado_path),
    )
    datasets_post_hls_synth = (
        toolflow_vitis_hls_synth.execute_multiple_design_datasets_fine_grained_parallel(
            datasets,
            False,
            lambda x: f"{x}_post_hls_synth__{vitis_hls_version}",
            n_jobs=N_JOBS,
            cpu_affinity=CPU_AFFINITY,
            timeout=TIMEOUT_HLS_SYNTH,
        )
    )
