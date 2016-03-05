#!/bin/bash
# -*- coding: utf-8 -*-
#
# Produces Git information to add to our prompt
#
# This file's contents shamelessly cannibalized from here:
# https://github.com/magicmonty/bash-git-prompt/blob/master/gitstatus.sh
#

# Prompt colors
RESET_COLOR='\[\e[0m\]'
RED='\[\e[0;31m\]'
GREEN='\[\e[0;32m\]'
BRIGHT_YELLOW='\[\e[1;33m\]'
BRIGHT_RED='\[\e[1;31m\]'

git_status="$( LC_ALL=C git status --porcelain --branch 2>/dev/null )"
retcode="${?}"
# If we couldn't get Git status, exit now
[[ ${retcode} -ne 0 ]] && exit 0

# Split the branch line of the status into "local branch" and "remote"
raw_branch_line="$(echo "${git_status}" | head -n 1)"
branch_line="${raw_branch_line/\.\.\./^}"
IFS="^" read -ra branch_fields <<< "${branch_line/\#\# }"
branch="${branch_fields[0]}"

# "remote" here means how many commits ahead/behind the branch is in relation to a remote repo
remote=""

# # TODO I'm not actually interested in tracking this right now, but maybe one day...
# # "upstream" here means the name of the branch on the remote tracking our branch
# upstream=""

# We haven't added any remotes yet
if [[ "$branch" == *"Initial commit on"* ]]; then
    IFS=" " read -ra fields <<< "$branch"
    branch="${fields[3]}"
    remote="_NO_REMOTE_TRACKING_"
# Case of a tag or a commit hash checked out
elif [[ "$branch" == *"no branch"* ]]; then
    tag=$( git describe --tags --exact-match 2>/dev/null )
    if [[ -n "$tag" ]]; then
        branch="$tag"
    else
        branch="$( git rev-parse --short HEAD )"
    fi
# All other cases (i.e. we can diff against a remote to find ahead/behind)
else
    # We have a remote, but haven't pushed the branch we're on (no upstream)
    if [[ "${#branch_fields[@]}" -eq 1 ]]; then
        remote="_NO_REMOTE_TRACKING_"
    # We're on a normal branch that can be compared against the remote tracking branch
    else
        IFS="[,]" read -ra remote_fields <<< "${branch_fields[1]}"
        # upstream="${remote_fields[0]}"

        # Calculate ahead/behind-ness
        for remote_field in "${remote_fields[@]}"; do
            if [[ "$remote_field" == *ahead* ]]; then
                num_ahead=${remote_field:6}
                ahead="_AHEAD_${num_ahead}"
            fi
            if [[ "$remote_field" == *behind* ]]; then
                num_behind=${remote_field:7}
                behind="_BEHIND_${num_behind# }"
            fi
        done
        remote="${behind}${ahead}"
    fi
fi

returnstr="${RESET_COLOR}${BRIGHT_YELLOW}(${branch}${RESET_COLOR}"
if [ "${remote}" == "_NO_REMOTE_TRACKING_" ]; then
    returnstr+=" ${BRIGHT_RED}local${RESET_COLOR}"
else
    if [ -n "${num_ahead}" ]; then
        returnstr+="${GREEN}+${num_ahead}${RESET_COLOR}"
    fi
    if [ -n "${num_behind}" ]; then
        returnstr+="${RED}-${num_behind}${RESET_COLOR}"
    fi
fi
returnstr+="${BRIGHT_YELLOW})${RESET_COLOR} "
echo "${returnstr}"


# if [[ -z "$remote" ]] ; then
#     remote='.'
# fi
#
# # Nothing's been pushed yet
# if [[ -z "$upstream" ]] ; then
#     upstream='^'
# fi
