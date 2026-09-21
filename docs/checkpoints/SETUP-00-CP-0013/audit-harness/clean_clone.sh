#!/bin/sh
# Re-run the mandatory validations and the suite in a fresh clone detached at the subject tag.
#
#     sh clean_clone.sh <repository-root> [checkpoint-id]
#
# Nothing of the working tree reaches the clone: the checkout is the sealed commit the subject's
# canonical tag resolves to, so a result that only holds because of workspace state cannot survive
# here.
set -u
ROOT=${1:?repository root required}
SUBJECT=${2:-SETUP-00-CP-0012}
WORK=$(mktemp -d -t cp13-clean-XXXXXX)
CLONE="$WORK/clone"

git clone --quiet --no-hardlinks "$ROOT" "$CLONE" || exit 1
cd "$CLONE" || exit 1
git checkout --quiet --detach "refs/tags/iacode-checkpoints/$SUBJECT" || exit 1

echo "CLONE_SUBJECT=$SUBJECT"
echo "CLONE_HEAD=$(git rev-parse HEAD)"
echo "CLONE_STATUS=$(git status --short | wc -l) dirty-lines"

export PYTHONDONTWRITEBYTECODE=1
for c in validate_checkpoint validate_lessons verify_integrity derive_counts \
         check_completeness derive_requirements; do
  out=$(python "scripts/development-ledger/$c.py" 2>&1 | tail -3)
  echo "CLEAN[$c] exit=$? :: $out"
done

out=$(python scripts/development-ledger/milestone_status.py --milestone M0 2>&1 | tail -3)
echo "CLEAN[milestone_status] exit=$? :: $out"
out=$(python -m compileall -q scripts tests 2>&1 | tail -3)
echo "CLEAN[compileall] exit=$? :: ${out:-ok}"
out=$(python -m unittest discover -s tests 2>&1 | tail -6)
echo "CLEAN[suite] exit=$? :: $out"

echo "CLEAN_CLONE_DONE"
rm -rf "$WORK"
