#
# Copyright (C) 2025 Salvo Giangreco
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# [
# shellcheck disable=SC1007,SC2164
# https://android.googlesource.com/platform/build/+/refs/tags/android-15.0.0_r1/envsetup.sh#18
_GET_SRC_DIR()
{
    local TOPFILE="unica/configs/version.sh"
    if [ -n "$SRC_DIR" ] && [ -f "$SRC_DIR/$TOPFILE" ]; then
        # The following circumlocution ensures we remove symlinks from SRC_DIR.
        (cd "$SRC_DIR"; PWD= /bin/pwd)
    else
        if [ -f "$TOPFILE" ]; then
            # The following circumlocution (repeated below as well) ensures
            # that we record the true directory name and not one that is
            # faked up with symlink names.
            PWD= /bin/pwd
        else
            local HERE="$PWD"
            local T=
            while [ \( ! \( -f "$TOPFILE" \) \) ] && [ \( "$PWD" != "/" \) ]; do
                \cd ..
                T="$(PWD= /bin/pwd -P)"
            done
            \cd "$HERE"
            if [ -f "$T/$TOPFILE" ]; then
                echo "$T"
            fi
        fi
    fi
}

_PRINT_USAGE()
{
    echo "Usage: source buildenv.sh [--debug] [--model] <target>" >&2
    echo "Example: source buildenv.sh --model M346B m34x" >&2
    echo "Options:" >&2
    echo "    --debug  Make a debug build" >&2
    echo "    --model  Use a different model" >&2
    echo "Available devices:" >&2
    printf '%s\n' "${TARGETS[@]}" >&2
}

# https://android.googlesource.com/platform/build/+/refs/tags/android-15.0.0_r1/envsetup.sh#806
croot()
{
    if [ -d "$SRC_DIR" ]; then
        if [ "$1" ]; then
            cd "$SRC_DIR/$1"
        else
            cd "$SRC_DIR"
        fi
    else
        echo "Couldn't locate the top of the tree. Try setting SRC_DIR."
        return 1
    fi
}

run_cmd()
{
    local CMD="$1"

    if [ -x "$SRC_DIR/scripts/$CMD.sh" ]; then
        shift
        mkdir -p "$(dirname "$WORK_DIR")"
        (set -o pipefail; "$SRC_DIR/scripts/$CMD.sh" "$@" |& tee \
            >(sed -r -e "s/\x1B\[([0-9]{1,3}(;[0-9]{1,2};?)?)?[mGK]//g" -e "/#/d" > "$(dirname "$WORK_DIR")/$CMD-$(date +%Y%m%d_%H%M%S).log"))
        return $?
    else
        local CMDS=()
        while IFS= read -r f; do
            CMDS+=("$f")
        done < <(find "$SRC_DIR/scripts" -maxdepth 1 ! -type d -printf '%f\n' | sort | sed "s/.sh//")

        if [ "$CMD" ]; then
            if [[ "$CMD" == "--help" ]] || [[ "$CMD" == "-h" ]]; then
                echo "Available cmds:" >&2
                for c in "${CMDS[@]}"; do
                    echo -e '\n\033[1;37m'"$c:"'\033[0m'
                    "$SRC_DIR/scripts/$c.sh" --help
                done
                return 0
            else
                echo -e '\033[0;31m'"\"$CMD\" is not a valid cmd."'\033[0m' >&2
            fi
        fi

        echo "Available cmds:" >&2
        printf '%s\n' "${CMDS[@]}" >&2
        return 1
    fi
}

alias unica=run_cmd
# ]

SRC_DIR="$(_GET_SRC_DIR)"
if [ ! "$SRC_DIR" ]; then
    echo "Couldn't locate the top of the tree. Always source buildenv.sh from the root of the tree." >&2
    return 1
fi

unset MODEL
unset -f _GET_SRC_DIR

export DEBUG=false
export TARGET_MODEL=""
export SRC_DIR
export OUT_DIR="$SRC_DIR/out"
export TMP_DIR="$OUT_DIR/tmp"
export ODIN_DIR="$OUT_DIR/odin"
export FW_DIR="$OUT_DIR/fw"
export TOOLS_DIR="$OUT_DIR/tools"
export PATH="$TOOLS_DIR/bin:$PATH"

[ -f "$OUT_DIR/config.sh" ] && rm -f "$OUT_DIR/config.sh"

TARGETS=()
while IFS= read -r t; do
    TARGETS+=("$t")
done < <(find "$SRC_DIR/target" -mindepth 1 -maxdepth 1 -type d -printf "%f\n" | sort)

while [[ "$1" == "-"* ]]; do
    case "$1" in
        --debug)
            export DEBUG=true
            shift
            ;;
        --model)
            shift
            if [ -z "$1" ]; then
                echo "Missing argument for --model" >&2
                _PRINT_USAGE
                return 1
            fi
            export TARGET_MODEL="$1"
            shift
            ;;
        --help|-h)
            _PRINT_USAGE
            return 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            _PRINT_USAGE
            return 1
            ;;
    esac
done

if [ "$#" -ne 1 ]; then
    echo "No target specified. Please choose from the available devices below:"

    select SELECTED_TARGET in "${TARGETS[@]}"; do
        if [ -n "$SELECTED_TARGET" ]; then
            break
        else
            echo "Invalid selection. Please try again."
        fi
    done
else
    SELECTED_TARGET="$1"
fi

if [ ! -d "$SRC_DIR/target/$SELECTED_TARGET" ]; then
    echo "\"$SELECTED_TARGET\" is not a valid device." >&2
    _PRINT_USAGE
    return 1
fi

if [ -n "$TARGET_MODEL" ]; then
    if ! grep -q "$TARGET_MODEL" "$SRC_DIR/target/$SELECTED_TARGET/config.sh"; then
        echo "\"$TARGET_MODEL\" is not a valid model." >&2
        _PRINT_USAGE
        return 1
    fi
fi

unset -f _PRINT_USAGE

export APKTOOL_DIR="$OUT_DIR/target/$SELECTED_TARGET/apktool"
export WORK_DIR="$OUT_DIR/target/$SELECTED_TARGET/work_dir"

mkdir -p "$OUT_DIR/target/$SELECTED_TARGET"
# shellcheck disable=SC2046
[ -f "$OUT_DIR/config.sh" ] && unset $(sed "/Automatically/d" "$OUT_DIR/config.sh" | cut -d "=" -f 1)
"$SRC_DIR/scripts/internal/gen_config_file.sh" "$SELECTED_TARGET" || return 1
set -o allexport; source "$OUT_DIR/config.sh"; set +o allexport

if [ -n "$TARGET_MODEL" ]; then
    if ! grep -q "TARGET_MODEL" "$SRC_DIR/target/$TARGET_CODENAME/config.sh"; then
        echo "- TARGET_MODEL variable does not exist in \"$TARGET_CODENAME\" target. Ignoring --model."
        unset TARGET_MODEL
    fi
fi

if [ -n "$TARGET_MODEL" ]; then
    if ! grep -q "\"\\\$TARGET_MODEL\" = \"$TARGET_MODEL\" \| \"\\\$TARGET_MODEL\" == \"$TARGET_MODEL\" \| \"\\\$TARGET_MODEL\" -eq \"$TARGET_MODEL\"" "$SRC_DIR/target/$TARGET_CODENAME/config.sh"; then
        echo "- \"$TARGET_MODEL\" not found in $TARGET_CODENAME config.sh."
        return 1
    fi
fi

unset TARGETS SELECTED_TARGET

if [ -n "$TARGET_ASSERT_MODEL" ] && ! grep -q "TARGET_ASSERT_MODEL" "$SRC_DIR/target/$TARGET_CODENAME/config.sh"; then
    unset TARGET_ASSERT_MODEL
fi

echo "=============================="
sed "/Automatically/d" "$OUT_DIR/config.sh"
echo "=============================="

return 0
