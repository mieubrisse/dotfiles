#!/bin/bash

# ====================================================================================================================
#
# Gitflow++ - A saner wrapper around Gitflow that:
#  - auto-creates an empty commit after '_gitflow release start X.Y.Z' and tags it with X.Y.Z-rc
#  - auto-creates the X.Y.(Z+1)-dev tag after `_gitflow release finish X.Y.Z`
#  - allows you to undo the last '_gitflow release finish' with '_gitflow release unfinish'
#  - provides '_gitflow push' for pushing tags and master/develop branch to remote (in that order, for Jenkins)
#
# ====================================================================================================================


# Helper function to bump the patch version of dot-delimited version input by one
# $1 - Version to bump
# STDOUT - Input with least-significant version bumped (e.g. 1.2 => 1.3, 1.4.0 => 1.4.1)
function _bump_version() {
    IFS='.' read -ra version_fragments <<< "${1}"
    version_fragments[-1]=$((version_fragments[-1] + 1))
    local return_str="$(printf ".%s" "${version_fragments[@]}")"
    echo "${return_str:1}"
}

# Helper function to get a Gitflow param
# $1 - Partially-qualified param name, e.g. 'branch.master' or 'prefix.release'
# STDOUT - Config parameter
# RETURN - Return code of 'git config' command to retrieve the parameter
function _get_gitflow_param() {
    config_param="gitflow.${1}"
    git config --get "${config_param}"
    retcode=${?}
    if [ ${retcode} -ne 0 ]; then
        echo "Error: Could not retrieve Gitflow param '${config_param}'... is Gitflow initialized?" >&2
    fi
    return ${retcode}
}

# Helper method to ensure that the develop and master branches are up-to-date with their remotes, and
#  returns a nonzero exit code if the fetch failed or if this is not the case
function _ensure_branch_sync() {
    echo "Checking that master & develop are in sync with remotes..."

    local develop_branch="$(_get_gitflow_param "branch.develop")" || return 1
    local master_branch="$(_get_gitflow_param "branch.master")" || return 1

    local project_root_dirpath="$(git rev-parse --show-toplevel)"
    local sync_timestamp_filepath="${project_root_dirpath}/.git/gitflow-sync"
    
    # Don't check if branches are in sync if we've just done it recently
    if [ -f "${sync_timestamp_filepath}" ]; then
        local last_synced_timestamp="$(cat "${sync_timestamp_filepath}")"
        local now="$(date +%s)"
        if [ $(( now - last_synced_timestamp )) -lt 180 ]; then
            echo "Sync was done recently; skipping"
            return 0
        fi
    fi

    if ! git fetch; then
        echo "Error: `git fetch` failed" >&2
        return 1
    fi
    date +%s > "${sync_timestamp_filepath}"

    # Check against the remotes
    [ -z "$(git log "${develop_branch}..origin/${develop_branch}" --oneline)" ] || return 2
    [ -z "$(git log "${master_branch}..origin/${master_branch}" --oneline)" ] || return 3
}

# Helper method for handling all `gitflow release start` subcommands
# $@ - All the arguments to Gitflow
function _gitflow_release_start() {
    if ! _ensure_branch_sync; then
        echo "Error: master and/or develop branch are out of sync with their remotes" >&2
        return 1
    fi

    local develop_branch="$(_get_gitflow_param "branch.develop")" || return 1
    local version_tag="$(_get_gitflow_param "prefix.versiontag")" || return 1

    # Try and autodetect the version if a user doesn't specify one
    local version=""
    if [ ${#} -eq 2 ]; then
        newest_develop_tag="$(git describe --tags --match='*-dev' --abbrev=0 "${develop_branch}")"
        minus_version_tag="${newest_develop_tag##${version_tag}}"
        version="${minus_version_tag%%-dev}"
        if [ -z "${version}" ]; then
            echo "Error: Couldn't autodetect version from latest develop branch; specify a version instead" >&2
            return 1
        fi
        read -p "What version should we release with? (${version}): " corrected_version 
        version="${corrected_version:-${version}}"
        command+=" ${version}"
    else 
        version="${!#}"
    fi
    git-flow release start "${version}" && 
        git commit --allow-empty -m "Starting release/${version}" && 
        git tag "${version}-rc"
}

# Helper function for handling all `gitflow release finish` subcommands
# $@ - All arguments the user passed to the Gitflow command
function _gitflow_release_finish() {
    if ! _ensure_branch_sync; then
        echo "Error: master and/or develop branch are out of sync with their remotes" >&2
        return 1
    fi

    local develop_branch="$(_get_gitflow_param "branch.develop")" || return 1
    local master_branch="$(_get_gitflow_param "branch.master")" || return 1
    local release_prefix="$(_get_gitflow_param "prefix.release")" || return 1

    # If we're on a release/ branch, autodetect the version to finish
    local version=""
    if [ -z "${3}" ]; then
        local current_branch="$(git rev-parse --abbrev-ref HEAD)"
        if [[ "${current_branch}" == ${release_prefix}* ]]; then
            version="${current_branch##${release_prefix}}"
            echo "No version provided; using version detected from release branch: ${version}"
        else
            echo "Error: Couldn't autodetect version from current branch; specify a version instead" >&2
            return 1
        fi
    else
        version="${3}"
    fi

    git-flow release finish -m "${version}" "${version}" &&
        git checkout "${develop_branch}" &&
        git tag "$( _bump_version "${version}" )-dev"
}

# Helper function for handling the `gitflow release push` subcommand
function _gitflow_push() {
    local develop_branch="$(_get_gitflow_param "branch.develop")" || return 1
    local master_branch="$(_get_gitflow_param "branch.master")" || return 1

    # Always do tags first, so Jenkins behaves properly!
    git push --tags
    
    echo "Pushing ${master_branch}..."
    git checkout "${master_branch}" &&
        git push origin "${master_branch}" &&
        git checkout "${develop_branch}" &&
        git push origin "${develop_branch}"
}

# Helper function to undo the effects of 'git flow release finish <version>', which are a pain to do
#  by hand
# RETURN - 0 if successful, >0 otherwise
function _gitflow_release_unfinish() {
    local develop_branch="$(_get_gitflow_param "branch.develop")" || return 1
    local master_branch="$(_get_gitflow_param "branch.master")" || return 1
    local release_prefix="$(_get_gitflow_param "prefix.release")" || return 1
    local version_tag="$(_get_gitflow_param "prefix.versiontag")" || return 1

    newest_master_tag="$(git describe --tags --abbrev=0 "${master_branch}")"
    if [ -z "${newest_master_tag}" ]; then
        echo "Error: No version to unrelease" >&2
        return 3
    fi

    release_branch_tip="$(git merge-base "${develop_branch}" "${master_branch}")"
    if [ -z "${release_branch_tip}" ]; then
        echo "Error: Could not find common ancestor of ${develop_branch} and ${master_branch}"
        return 4
    fi

    # If the user isn't using X.X.X-dev tags, we don't want to accidentally delete an old tag
    newest_develop_tag="$(git describe --tags --match='*-dev' --abbrev=0 "${develop_branch}")"
    if [ -z "${newest_develop_tag}" ] || [ "${newest_develop_tag%%-dev}" == "${newest_master_tag}" ]; then
        delete_develop_tag=false
    else
        delete_develop_tag=true
    fi

    newest_release_branch_name="${release_prefix}${newest_master_tag}"

    echo "To undo 'git flow release finish ${newest_master_tag##${version_tag}}' we'll:"
    echo ""
    echo " - Undo merge: ${newest_release_branch_name} => ${develop_branch}"
    echo " - Undo merge: ${newest_release_branch_name} => ${master_branch}"
    echo " - Delete tag: ${newest_master_tag} on ${master_branch}"
    if ${delete_develop_tag}; then
        echo " - Delete tag: ${newest_develop_tag} on ${develop_branch}"
    fi
    echo " - Recreate branch: ${newest_release_branch_name}"
    echo ""
    echo "We will NOT change anything on the remote!"
    echo ""
    read -p "Is this okay? ENTER for YES, Ctrl-C for NO"

    git checkout "${develop_branch}"
    git reset --hard HEAD^
    git checkout "${master_branch}"
    git reset --hard HEAD^
    git tag -d "${newest_master_tag}"
    if ${delete_develop_tag}; then
        git tag -d "${newest_develop_tag}"
    fi
    git branch "${newest_release_branch_name}" "${release_branch_tip}"
    git checkout "${newest_release_branch_name}"
}

# Main function
function _gitflow() {
    # Make sure we're initialized... maybe a bad idea?
    # TODO Only initialize if we're not initialized already, and print errors if there are any
    git-flow init -d || return 1

    # If we're starting a release, make sure to push an empty commit and add the vX.X.X-rc tag
    if [ "${1}" == "release" ] && [ "${2}" == "start" ]; then
        _gitflow_release_start "${@}"
    # If we're finishing a release, make sure to tag the develop branch with vX.X.X-dev
    elif [ "${1}" == "release" ] && [ "${2}" == "finish" ]; then
        _gitflow_release_finish "${@}"
    # Give the option to undo a release (before push, at least)
    elif [ "${1}" == "release" ] && [ "${2}" == "unfinish" ]; then
        _gitflow_release_unfinish
    # Make pushing easier and more standardized
    elif [ "${1}" == "push" ]; then
        _gitflow_push "${@}"
    else
        git-flow "${@}"
    fi
}

_gitflow "${@}"
