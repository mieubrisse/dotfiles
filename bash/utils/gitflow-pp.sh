#!/bin/bash

# ====================================================================================================================
#
# Gitflow++ - A saner wrapper around Gitflow that:
# 
#  - ensures local master & develop branches are up-to-date with remote before releasing
#  - auto-creates an empty commit after '_gitflow release start X.Y.Z' and tags it with X.Y.Z-rc
#  - auto-creates the X.Y.(Z+1)-dev tag after `_gitflow release finish X.Y.Z`
#  - allows you to undo the last '_gitflow release finish' with '_gitflow release unfinish'
#  - provides '_gitflow push' for pushing tags and master/develop branch to remote (in that order, for Jenkins)
# 
# Installation:
#  1. Install the Gitflow tooling: https://github.com/nvie/gitflow/wiki/Installation
#  2. Clone this repo somewhere on your machine
#  3. In your .bashrc, add `alias gfl="bash /path/to/this/gitflow-pp.sh"`
# 
# To run through a normal release flow inside a repo:
# 
#  1. Run `gfl release start` (a version will be suggested if you have an X.Y.Z-dev tag on your develop branch)
#  2. Make any necessary changes on your release branch (e.g. updating your CHANGELOG.md)
#  3. Run `gfl release finish` (a version will be suggested if you're on the release branch)
#  4. Verify that all merges happened as expected and your `git log --graph` looks sane
#  5. Run `gfl push` to push all branches and tags up to the remote
#
# ====================================================================================================================

# Helper function for printing errors to STDOUT
function _print_error() {
    local msg="${1}"
    echo "${msg}" >&2
}

# Helper function to bump the patch version of dot-delimited version input by one
# $1 - Version to bump
# STDOUT - Input with least-significant version bumped (e.g. 1.2 => 1.3, 1.4.0 => 1.4.1)
function _bump_version() {
    IFS='.' read -ra version_fragments <<< "${1}"
    version_fragments_last_idx="$((${#version_fragments[@]} - 1))"
    version_fragments[${version_fragments_last_idx}]=$((version_fragments[version_fragments_last_idx] + 1))
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
        _print_error "Could not retrieve Gitflow param '${config_param}'... is Gitflow initialized?"
    fi
    return ${retcode}
}

# Helper method to ensure that the develop and master branches are up-to-date with their remotes, and
#  returns a nonzero exit code if the fetch failed or if this is not the case
function _ensure_branch_sync() {
    local develop_branch="$(_get_gitflow_param "branch.develop")" || return 1
    local master_branch="$(_get_gitflow_param "branch.master")" || return 1

    echo "Checking that '${master_branch}' and '${develop_branch}' are in sync with remotes..."

    local project_root_dirpath="$(git rev-parse --show-toplevel)"
    local sync_timestamp_filepath="${project_root_dirpath}/.git/gitflow-sync"
    
    # Don't check if branches are in sync if we've just done it recently
    local do_sync="true"
    if [ -f "${sync_timestamp_filepath}" ]; then
        local last_synced_timestamp="$(cat "${sync_timestamp_filepath}")"
        local now="$(date +%s)"
        if [ $(( now - last_synced_timestamp )) -lt 180 ]; then
            echo "'git fetch' was done recently; skipping"
            do_sync="false"
        fi
    fi

    if [ "${do_sync}" = "true" ]; then
        if ! git fetch; then
            _print_error "`git fetch` failed"
            return 1
        fi

        date +%s > "${sync_timestamp_filepath}"
    fi

    # Check the remote branches are in sync
    local develop_branch_diff=""
    local master_branch_diff=""
    if ! develop_branch_diff="$(git log "${develop_branch}..origin/${develop_branch}" --oneline)"; then
        _print_error "Error occurred when checking differences between ${develop_branch} and origin/${develop_branch}"
        return 2
    fi
    [ -z "${develop_branch_diff}" ] || return 3
    if ! master_branch_diff="$(git log "${master_branch}..origin/${master_branch}" --oneline)"; then
        _print_error "Error occurred when checking differences between ${master_branch} and origin/${master_branch}"
        return 4
    fi
    [ -z "${master_branch_diff}" ] || return 5

    echo "Verified '${master_branch}' and '${develop_branch}' are in sync with remotes!"
}

# Helper method for handling all `gitflow release start` subcommands
# $@ - All the arguments to Gitflow
function _gitflow_release_start() {
    if ! _ensure_branch_sync; then
        _print_error "Cannot start a release; branches are out of sync with remote!"
        return 1
    fi

    local develop_branch="$(_get_gitflow_param "branch.develop")" || return 1
    local version_tag="$(_get_gitflow_param "prefix.versiontag")" || return 1

    # If the user doesn't specify a version, do some niceties to try and autodetect it or let them specify
    local suggested_release_version=""
    local actual_version=""
    if [ ${#} -eq 2 ]; then
        newest_develop_tag="$(git describe --tags --match='*-dev' --abbrev=0 "${develop_branch}")"
        if ! [ -z "${newest_develop_tag}" ]; then
            minus_version_tag="${newest_develop_tag##${version_tag}}"
            suggested_release_version="${minus_version_tag%%-dev}"
            if [ -z "${suggested_release_version}" ]; then
                echo "Couldn't autodetect version from ${develop_branch}; version will need to be entered manually"
            fi
        else
            echo "Couldn't find X.Y.Z-dev tag on ${develop_branch}"
        fi

        if ! [ -z "${suggested_release_version}" ]; then
            read -p "What version should we release with? (${suggested_release_version}): " actual_version
            if [ -z "${actual_version}" ]; then
                actual_version="${suggested_release_version}"
            fi
        else
            while [ -z "${actual_version}" ]; do
                read -p "What version should we release with?: " actual_version
                if [ -z "${actual_version}" ]; then
                    echo "Release version cannot be empty"
                fi
            done
        fi

        command+=" ${actual_version}"
    else 
        actual_version="${!#}"
    fi
    git-flow release start "${actual_version}" && 
        git commit --allow-empty -m "Starting release/${actual_version}" && 
        git tag "${actual_version}-rc"
}

# Helper function for handling all `gitflow release finish` subcommands
# $@ - All arguments the user passed to the Gitflow command
function _gitflow_release_finish() {
    if ! _ensure_branch_sync; then
        _print_error "Cannot finish release; branches are out of sync with remote!"
        return 1
    fi

    local develop_branch="$(_get_gitflow_param "branch.develop")" || return 1
    local master_branch="$(_get_gitflow_param "branch.master")" || return 1
    local release_prefix="$(_get_gitflow_param "prefix.release")" || return 1

    # If we're on a release/ branch, try to autodetect the version to finish
    local suggested_release_version=""
    local actual_version=""
    if [ -z "${3}" ]; then
        local current_branch="$(git rev-parse --abbrev-ref HEAD)"
        if [[ "${current_branch}" == ${release_prefix}* ]]; then
            suggested_release_version="${current_branch##${release_prefix}}"
            if [ -z "${suggested_release_version}" ]; then
                echo "Couldn't autodetect version from current branch; version will need to be entered manually"
            fi
        else
            echo "Current branch is not a release branch; version will need to be entered manually"
        fi

        if ! [ -z "${suggested_release_version}" ]; then
            read -p "What version should we release with? (${suggested_release_version}): " actual_version
            if [ -z "${actual_version}" ]; then
                actual_version="${suggested_release_version}"
            fi
        else
            while [ -z "${actual_version}" ]; do
                read -p "What version should we release with?: " actual_version
                if [ -z "${actual_version}" ]; then
                    echo "Release version cannot be empty"
                fi
            done
        fi
    else
        actual_version="${3}"
    fi

    GIT_MERGE_AUTOEDIT=no git-flow release finish -m "${actual_version}" "${actual_version}" || { _print_error "git-flow release failed" && return 2; }
    git checkout "${develop_branch}" || { _print_error "Couldn't check out develop branch" && return 3; }
    local bumped_version="$( _bump_version "${actual_version}" )"
    if [ -z "${bumped_version}" ]; then
        _print_error "Couldn't increment the maintenance version of semver '${actual_version}'"
        return 4
    fi
    git tag "${bumped_version}-dev"
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
        _print_error "No version to unrelease"
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
