all: check

check:
	find . -type f -name "*.py" | grep -v "backup" | xargs pylint --indent-string='  ' --variable-naming-style=any --argument-naming-style=any --class-attribute-naming-style=any --disable=missing-docstring,bad-whitespace,too-many-arguments,fixme,arguments-out-of-order --max-line-length=80

test:
	python3 -B -m unittest discover test -v
