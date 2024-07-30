from pathlib import Path

from dotenv import dotenv_values

TOOL_PATH_VARS = [
    "VIVADO_PATH__2021_1",
    "VIVADO_PATH__2023_1",
    "VITIS_HLS_PATH__2023_1",
    "VITIS_HLS_PATH__2021_1",
    "IPP_BIN_PATH",
    "QUARTUS_SH_BIN_PATH",
]
ANALYSIS_PATH_VARS = ["DIR_DATASETS", "DIR_FIGURES", "DIR_RESULTS"]

PATH_VARS = TOOL_PATH_VARS + ANALYSIS_PATH_VARS

INT_VARS = ["N_JOBS"]

ALL_VARS = PATH_VARS + INT_VARS


def get_env_vars(
    vars: list[str], env_path: Path | str | None = None
) -> dict[str, int | Path]:
    vars_loaded: dict[str, int | Path] = {}

    if env_path is not None:
        env_data = dotenv_values(env_path)
    else:
        env_data = dotenv_values()

    for var_name in vars:
        if var_name not in env_data:
            raise ValueError(f"Environment variable {var_name} not found in .env file")
        var_data = env_data[var_name]
        var_data_raw = var_data
        if var_data is None:
            raise ValueError(f"Environment variable {var_name} is not set")
        if var_data.strip() == "":
            raise ValueError(f"Environment variable {var_name} is empty")
        var_data = var_data.strip()

        if var_name in INT_VARS:
            try:
                var_data_int = int(var_data)
            except ValueError:
                raise ValueError(
                    f"Can not parse {var_name}={var_data_raw} as integer. "
                    "Please update this variable with a valid integer."
                )

            vars_loaded[var_name] = var_data_int
        if var_name in PATH_VARS:
            if "<some_path>" in var_data:
                raise ValueError(
                    f"Placeholder string `<some_path>` is still being used in {var_name}={var_data_raw}. "
                    "Please update this variable with a valid path."
                )
            try:
                vars_data_path = Path(var_data)
            except ValueError:
                raise ValueError(
                    f"Can not parse {var_name}={var_data_raw} as valid path. "
                    "Please update this variable with a valid path."
                )

            if var_name in TOOL_PATH_VARS and not vars_data_path.exists():
                raise ValueError(
                    f"Tool path {vars_data_path}={var_data_raw} does not exist. "
                    "Please update this variable with a valid path."
                )
            try:
                vars_data_path = vars_data_path.resolve()
            except FileNotFoundError:
                raise FileNotFoundError(
                    f"Could not resolve path {vars_data_path}={var_data_raw}. "
                    "Please update this variable with a valid path."
                )
            vars_loaded[var_name] = vars_data_path

    return vars_loaded


def get_all_env_vars(env_path: Path | str | None = None) -> dict[str, int | Path]:
    return get_env_vars(ALL_VARS, env_path)
