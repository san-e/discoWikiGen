#!/usr/bin/env bash
# Written in [Amber](https://amber-lang.com/)
# version: 0.6.0-alpha
if [ -n "$ZSH_VERSION" ]; then
    EXEC_SHELL="zsh"
    IFS='.' read -A EXEC_SHELL_VERSION <<< "$ZSH_VERSION"
elif [ -n "$KSH_VERSION" ]; then
    EXEC_SHELL="ksh"
    __exec_shell_version="${.sh.version##*/}"
    IFS='.' read -a EXEC_SHELL_VERSION <<< "${__exec_shell_version%% *}"
else
    EXEC_SHELL="bash"
    EXEC_SHELL_VERSION=("${BASH_VERSINFO[0]}" "${BASH_VERSINFO[1]}" "${BASH_VERSINFO[2]}")
fi
# dir_exists(path: Text)
dir_exists__38_v0() {
    local path_4="${1}"
    [ -d "${path_4}" ]
    __status=$?
    ret_dir_exists38_v0="$(( __status == 0 ))"
    return 0
}

command -v uv>/dev/null 2>&1
__status=$?
if [ "${__status}" != 0 ]; then
    echo "This project requires the uv package manager. Find installation instructions here: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi
__pwd_0="$PWD"
dir_exists__38_v0 "${__pwd_0}/.venv"
ret_dir_exists38_v0__8_5="${ret_dir_exists38_v0}"
if [ "${ret_dir_exists38_v0__8_5}" != 0 ]; then
    source .venv/bin/activate
    __status=$?
    exec $SHELL
    __status=$?
fi
uv init>/dev/null 2>&1
__status=$?
uv venv
__status=$?
if [ "${__status}" != 0 ]; then
    echo "Failed to initialize virtual environment."
    exit 1
fi
uv pip install -r requirements.txt
__status=$?
if [ "${__status}" != 0 ]; then
    echo "Failed to install dependencies."
    exit 1
fi
