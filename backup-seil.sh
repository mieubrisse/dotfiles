
echo "THIS IS NOT FINISHED YET" >&2
exit 99

if [ "${#}" -ne 2 ]; then
    echo -e "Usage:\t${0} <Seil app script> <output file>" >&2
    exit 1
fi

seil_script_filepath="${1}"
output_filepath="${2}"

"${seil_script_dirpath}" export > "${output_filepath}"
