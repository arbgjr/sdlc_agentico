#!/usr/bin/env bash
# Manages git worktrees for parallel workers
# Adapted from claude-orchestrator's wt.sh for Linux compatibility

set -euo pipefail

# Load structured logging
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../../../lib/shell/logging_utils.sh"

# Set context for logging
sdlc_set_context skill="parallel-workers" phase="5"

WORKTREE_BASE="${HOME}/.worktrees"

usage() {
    cat <<EOF
Usage: $(basename "$0") <command> [args]

Commands:
  create <project> <task-id> <base-branch>  Create new worktree
  list <project>                             List active worktrees
  remove <project> <task-id>                 Remove worktree
  prune                                      Remove stale worktrees
  status <project> <task-id>                Check worktree status

Examples:
  $(basename "$0") create my-project task-001 main
  $(basename "$0") list my-project
  $(basename "$0") remove my-project task-001
  $(basename "$0") prune

Environment:
  WORKTREE_BASE    Base directory for worktrees (default: ~/.worktrees)
EOF
    exit 1
}

create_worktree() {
    local project="$1"
    local task_id="$2"
    local base_branch="$3"

    local worktree_path="${WORKTREE_BASE}/${project}/${task_id}"
    local branch_name="feature/${task_id}"

    sdlc_log_info "Creating worktree" \
        "project=$project" \
        "task_id=$task_id" \
        "base_branch=$base_branch" \
        "worktree_path=$worktree_path"

    # Create base directory
    mkdir -p "${WORKTREE_BASE}/${project}"

    # Check if worktree already exists
    if [[ -d "$worktree_path" ]]; then
        sdlc_log_error "Worktree already exists" "path=$worktree_path"
        return 1
    fi

    # Create worktree and branch
    if git worktree add -b "$branch_name" "$worktree_path" "$base_branch" 2>&1 | \
        while IFS= read -r line; do
            sdlc_log_debug "git worktree add" "output=$line"
        done
    then
        sdlc_log_info "Worktree created successfully" \
            "branch=$branch_name" \
            "path=$worktree_path"
        echo "$worktree_path"
        return 0
    else
        sdlc_log_error "Failed to create worktree" \
            "branch=$branch_name" \
            "base=$base_branch"
        return 1
    fi
}

list_worktrees() {
    local project="$1"
    local project_path="${WORKTREE_BASE}/${project}"

    sdlc_log_debug "Listing worktrees" "project=$project"

    if [[ ! -d "$project_path" ]]; then
        sdlc_log_warn "No worktrees found for project" "project=$project"
        return 0
    fi

    # Parse git worktree list
    git worktree list --porcelain | \
    awk -v project_path="$project_path" '
        /^worktree / {
            path = substr($0, 10)
            if (index(path, project_path) == 1) {
                print path
            }
        }
    '
}

remove_worktree() {
    local project="$1"
    local task_id="$2"
    local worktree_path="${WORKTREE_BASE}/${project}/${task_id}"

    sdlc_log_info "Removing worktree" \
        "project=$project" \
        "task_id=$task_id" \
        "path=$worktree_path"

    if [[ ! -d "$worktree_path" ]]; then
        sdlc_log_warn "Worktree not found" "path=$worktree_path"
        return 0
    fi

    # Check for uncommitted changes
    if [[ -n "$(cd "$worktree_path" && git status --porcelain)" ]]; then
        sdlc_log_warn "Worktree has uncommitted changes" "path=$worktree_path"
        read -p "Force remove? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            sdlc_log_info "Removal cancelled by user"
            return 1
        fi
    fi

    # Remove worktree
    if git worktree remove "$worktree_path" --force 2>&1 | \
        while IFS= read -r line; do
            sdlc_log_debug "git worktree remove" "output=$line"
        done
    then
        sdlc_log_info "Worktree removed successfully" "path=$worktree_path"
        return 0
    else
        sdlc_log_error "Failed to remove worktree" "path=$worktree_path"
        return 1
    fi
}

prune_worktrees() {
    sdlc_log_info "Pruning stale worktrees"

    if git worktree prune --verbose 2>&1 | \
        while IFS= read -r line; do
            sdlc_log_debug "git worktree prune" "output=$line"
        done
    then
        sdlc_log_info "Worktrees pruned successfully"
        return 0
    else
        sdlc_log_error "Failed to prune worktrees"
        return 1
    fi
}

status_worktree() {
    local project="$1"
    local task_id="$2"
    local worktree_path="${WORKTREE_BASE}/${project}/${task_id}"

    if [[ ! -d "$worktree_path" ]]; then
        sdlc_log_error "Worktree not found" "path=$worktree_path"
        return 1
    fi

    sdlc_log_debug "Checking worktree status" "path=$worktree_path"

    (
        cd "$worktree_path"
        local branch=$(git branch --show-current)
        local commit=$(git rev-parse --short HEAD)
        local status=$(git status --porcelain | wc -l)

        cat <<EOF
{
  "path": "$worktree_path",
  "branch": "$branch",
  "commit": "$commit",
  "uncommitted_changes": $status,
  "exists": true
}
EOF
    )
}

# Main
if [[ $# -lt 1 ]]; then
    usage
fi

command="$1"
shift

case "$command" in
    create)
        if [[ $# -ne 3 ]]; then
            usage
        fi
        create_worktree "$1" "$2" "$3"
        ;;
    list)
        if [[ $# -ne 1 ]]; then
            usage
        fi
        list_worktrees "$1"
        ;;
    remove)
        if [[ $# -ne 2 ]]; then
            usage
        fi
        remove_worktree "$1" "$2"
        ;;
    prune)
        prune_worktrees
        ;;
    status)
        if [[ $# -ne 2 ]]; then
            usage
        fi
        status_worktree "$1" "$2"
        ;;
    *)
        sdlc_log_error "Unknown command" "command=$command"
        usage
        ;;
esac
