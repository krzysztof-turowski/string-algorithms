all: check

check:
	find . -type f -name "*.py" | egrep -v "^(./backup/|./lib/|./text/)" | xargs pylint --indent-string='  ' --variable-naming-style=any --argument-naming-style=any --attr-naming-style=any --class-attribute-naming-style=any --disable=missing-docstring,too-many-arguments,too-many-positional-arguments,duplicate-code,fixme,arguments-out-of-order --max-line-length=80

test:
	python -B -m unittest discover test -v

.PHONY: test check
