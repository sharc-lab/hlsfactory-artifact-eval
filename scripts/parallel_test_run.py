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

WORK_DIR = DIR_DATASETS / "hlsfactory_workdir_parallel_test_run"

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

datasets_expanded = {
    **{
        f"{name}__naive": dataset.copy_and_rename(f"{name}__naive", WORK_DIR)
        for name, dataset in datasets.items()
    },
    **{
        f"{name}__fine_grained": dataset.copy_and_rename(
            f"{name}__fine_grained", WORK_DIR
        )
        for name, dataset in datasets.items()
    },
}

datasets_naive = {
    name: dataset for name, dataset in datasets_expanded.items() if "__naive" in name
}

datasets_fine = {
    name: dataset for name, dataset in datasets_expanded.items() if "__fine" in name
}


N_RANDOM_SAMPLES = 8
RAMDOM_SAMPLE_SEED = 64
opt_dsl_frontend = OptDSLFrontend(
    WORK_DIR,
    random_sample=True,
    random_sample_num=N_RANDOM_SAMPLES,
    random_sample_seed=RAMDOM_SAMPLE_SEED,
    log_execution_time=True,
)

datasets_naive_post_frontend = (
    opt_dsl_frontend.execute_multiple_design_datasets_naive_parallel(
        datasets_naive,
        True,
        lambda x: f"{x}__post_frontend",
        n_jobs=N_JOBS,
        cpu_affinity=CPU_AFFINITY,
    )
)

datasets_fine_post_frontend = (
    opt_dsl_frontend.execute_multiple_design_datasets_fine_grained_parallel(
        datasets_fine,
        True,
        lambda x: f"{x}__post_frontend",
        n_jobs=N_JOBS,
        cpu_affinity=CPU_AFFINITY,
    )
)


TIMEOUT_HLS_SYNTH = 60.0 * 5  # 5 minutes


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

datasets_naive_post_hls_synth = (
    toolflow_vitis_hls_synth.execute_multiple_design_datasets_naive_parallel(
        datasets_naive_post_frontend,
        False,
        n_jobs=N_JOBS,
        cpu_affinity=CPU_AFFINITY,
        timeout=TIMEOUT_HLS_SYNTH,
    )
)

datasets_fine_post_hls_synth = (
    toolflow_vitis_hls_synth.execute_multiple_design_datasets_fine_grained_parallel(
        datasets_fine_post_frontend,
        False,
        n_jobs=N_JOBS,
        cpu_affinity=CPU_AFFINITY,
        timeout=TIMEOUT_HLS_SYNTH,
    )
)
