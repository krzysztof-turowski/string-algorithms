all: check

check:
	find . -type f -name "*.py" | grep -v "backup" | xargs pylint --indent-string='  ' --variable-naming-style=any --argument-naming-style=any --class-attribute-naming-style=any --disable=missing-docstring,bad-whitespace,fixme

CPP_DIR := backup
CPP_SRCS := $(wildcard $(CPP_DIR)/*.cpp)
CPP_EXEC := $(patsubst $(CPP_DIR)/%.cpp,$(CPP_DIR)/%.exe,$(CPP_SRCS))

backup-g++: $(CPP_EXEC)

%.exe: %.cpp
	g++ -O3 $< -o $@
