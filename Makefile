all: check

check:
	find . -type f -name "*.py" | xargs pylint --indent-string='  ' --variable-naming-style=any --argument-naming-style=any --class-attribute-naming-style=any --disable=missing-docstring,bad-whitespace,fixme
