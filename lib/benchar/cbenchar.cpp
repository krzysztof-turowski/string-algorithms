#include <pybind11/pybind11.h>
#include <string>
#include <tuple>
#include <iostream>

namespace py = pybind11;

class Benchar;
class count_string;
class count_string_iterator;

class Benchar {
public:
    int cmp_count;
    count_string create(std::string);
};

class count_string {
    Benchar &parent_benchar;
    
    int min(int a, int b) const;
    int max(int a, int b) const;
    std::tuple<int, int> first_diff(std::string const &a, std::string const &b) const;

public:
    std::string const base_string;

    count_string(std::string base_string, Benchar &parent_benchar);
    std::string toString() const;
    count_string getItem(int item) const;
    count_string getItem(py::slice item) const;
    count_string add(count_string const &other) const;
    count_string add(std::string const &other) const;
    count_string radd(std::string const &other) const;
    bool eq(std::string const &other) const;
    bool eq(count_string const &other) const;
    bool ne(std::string const &other) const;
    bool ne(count_string const &other) const;
    bool lt(std::string const &other) const;
    bool lt(count_string const &other) const;
    bool ge(std::string const &other) const;
    bool ge(count_string const &other) const;
    bool gt(std::string const &other) const;
    bool gt(count_string const &other) const;
    bool le(std::string const &other) const;
    bool le(count_string const &other) const;
    bool endswith(std::string const &other) const;
    bool endswith(count_string const &other) const;
    bool startswith(std::string const &other) const;
    bool startswith(count_string const &other) const;
    int hash() const;
    count_string_iterator iter() const;
    int len() const;
};

class count_string_iterator {
    int curInd;
    count_string const &parent_count_string;

public:
    count_string_iterator(count_string const &parent_count_string);
    count_string_iterator &iter();
    count_string next();
};


count_string Benchar::create(std::string base_string) {
    return count_string(base_string, *this);
}

count_string::count_string(std::string base_string, Benchar &parent_benchar): base_string(base_string), parent_benchar(parent_benchar) {}
int count_string::min(int a, int b) const {
    return a < b ? a : b;
}
int count_string::max(int a, int b) const {
    return a > b ? a : b;
}
std::tuple<int, int> count_string::first_diff(std::string const &a, std::string const &b) const {
    int min_length = min(a.length(), b.length());
    for(int i = 0; i < min_length; i++) {
        if(a[i] != b[i]) {
            if(a[i] < b[i]) {
                return std::tuple<int, int>{-1, i + 1};
            } else {
                return std::tuple<int, int>{1, i + 1};
            }
        }
    }
    return std::tuple<int, int>{0, min_length};;
}
std::string count_string::toString() const {
    return base_string;
}
count_string count_string::getItem(int item) const {
    if(item < 0) {
        item = base_string.length() - item;
    }
    return count_string(std::string(1, base_string[item]), parent_benchar);
}
count_string count_string::getItem(py::slice item) const {
    int start = item.attr("start").is_none() ? 0 : item.attr("start").cast<int>();
    int stop = item.attr("stop").is_none() ? base_string.length() : item.attr("stop").cast<int>();
    int step = item.attr("step").is_none() ? 1 : item.attr("step").cast<int>();
    
    start = start < 0 ? base_string.length() + start : start;
    stop = stop < 0 ? base_string.length() + stop : stop;
    start = max(start, 0);
    stop = min(stop, base_string.length());
        
    std::string result = "";
    if(step > 0) {
        for(int i = start; i < stop; i += step) {
            result += base_string[i];
        }
    } else if(step < 0) {
        for(int i = start; i > stop; i += step) {
            result += base_string[i];
        }
    }
    
    return count_string(result, parent_benchar);
}
count_string count_string::add(count_string const &other) const {
    return count_string(base_string + other.base_string, parent_benchar);
}
count_string count_string::add(std::string const &other) const {
    return count_string(base_string + other, parent_benchar);
}
count_string count_string::radd(std::string const &other) const {
    return count_string(other + base_string, parent_benchar);
}
bool count_string::eq(std::string const &other) const {
    std::tuple<int, int> diff = first_diff(base_string, other);
    parent_benchar.cmp_count += std::get<1>(diff);
    return std::get<0>(diff) == 0;
}
bool count_string::eq(count_string const &other) const {
    return eq(other.base_string);
}
bool count_string::ne(std::string const &other) const {
    return !eq(other);
}
bool count_string::ne(count_string const &other) const {
    return !eq(other);
}
bool count_string::lt(std::string const &other) const {
    std::tuple<int, int> diff = first_diff(base_string, other);
    parent_benchar.cmp_count += std::get<1>(diff);
    return std::get<0>(diff) == -1;
}
bool count_string::lt(count_string const &other) const {
    return lt(other.base_string);
}
bool count_string::ge(std::string const &other) const {
    return !lt(other);
}
bool count_string::ge(count_string const &other) const {
    return !lt(other);
}
bool count_string::gt(std::string const &other) const {
    std::tuple<int, int> diff = first_diff(base_string, other);
    parent_benchar.cmp_count += std::get<1>(diff);
    return std::get<0>(diff) == 1;
}
bool count_string::gt(count_string const &other) const {
    return lt(other.base_string);
}
bool count_string::le(std::string const &other) const {
    return !gt(other);
}
bool count_string::le(count_string const &other) const {
    return !gt(other);
}
bool count_string::endswith(std::string const &other) const {
    if(base_string.length() < other.length()) {
        return false;
    } else {
        int min_length = min(base_string.length(), other.length());
        for(int i = 0; i < min_length; i++) {
            parent_benchar.cmp_count++;
            if(base_string[base_string.length() - other.length() + i] != other[i]) {
                return false;
            }
        }
        return true;
    }
}
bool count_string::endswith(count_string const &other) const {
    return endswith(other.base_string);
}
bool count_string::startswith(std::string const &other) const {
    if(base_string.length() < other.length()) {
        return false;
    } else {
        int min_length = min(base_string.length(), other.length());
        for(int i = 0; i < min_length; i++) {
            parent_benchar.cmp_count++;
            if(base_string[i] != other[i]) {
                return false;
            }
        }
        return true;
    }
}
bool count_string::startswith(count_string const &other) const {
    return startswith(other.base_string);
}
int count_string::hash() const {
    return std::hash<std::string>()(base_string);
}
count_string_iterator count_string::iter() const {
    return count_string_iterator(*this);
}
int count_string::len() const {
    return base_string.length();
}

count_string_iterator::count_string_iterator(count_string const &parent_count_string): parent_count_string(parent_count_string), curInd(0) {}
count_string_iterator &count_string_iterator::iter() {
    return *this;
}
count_string count_string_iterator::next() {
    if(curInd >= parent_count_string.base_string.length()) {
        throw py::stop_iteration();
    } else {
        return parent_count_string.getItem(curInd++);
    }
}


PYBIND11_MODULE(cbenchar, handle) {
    py::class_<Benchar>(
        handle, "Benchar"
    )
    .def(py::init<>())
    .def("__call__", &Benchar::create)
    .def_readwrite("cmp_count", &Benchar::cmp_count)
    ;
    
    py::class_<count_string>(
        handle, "count_string"
    )
    .def("__str__", &count_string::toString)
    .def("__getitem__", static_cast<count_string (count_string::*)(int)const>(&count_string::getItem))
    .def("__getitem__", static_cast<count_string (count_string::*)(py::slice)const>(&count_string::getItem))
    .def("__add__", static_cast<count_string (count_string::*)(count_string const&)const>(&count_string::add))
    .def("__add__", static_cast<count_string (count_string::*)(std::string const&)const>(&count_string::add))
    .def("__radd__", static_cast<count_string (count_string::*)(std::string const&)const>(&count_string::radd))
    .def("__eq__", static_cast<bool (count_string::*)(std::string const&)const>(&count_string::eq))
    .def("__eq__", static_cast<bool (count_string::*)(count_string const&)const>(&count_string::eq))
    .def("__ne__", static_cast<bool (count_string::*)(std::string const&)const>(&count_string::ne))
    .def("__ne__", static_cast<bool (count_string::*)(count_string const&)const>(&count_string::ne))
    .def("__lt__", static_cast<bool (count_string::*)(std::string const&)const>(&count_string::lt))
    .def("__lt__", static_cast<bool (count_string::*)(count_string const&)const>(&count_string::lt))
    .def("__ge__", static_cast<bool (count_string::*)(std::string const&)const>(&count_string::ge))
    .def("__ge__", static_cast<bool (count_string::*)(count_string const&)const>(&count_string::ge))
    .def("__gt__", static_cast<bool (count_string::*)(std::string const&)const>(&count_string::gt))
    .def("__gt__", static_cast<bool (count_string::*)(count_string const&)const>(&count_string::gt))
    .def("__le__", static_cast<bool (count_string::*)(std::string const&)const>(&count_string::le))
    .def("__le__", static_cast<bool (count_string::*)(count_string const&)const>(&count_string::le))
    .def("endswith", static_cast<bool (count_string::*)(std::string const&)const>(&count_string::endswith))
    .def("endswith", static_cast<bool (count_string::*)(count_string const&)const>(&count_string::endswith))
    .def("startswith", static_cast<bool (count_string::*)(std::string const&)const>(&count_string::startswith))
    .def("startswith", static_cast<bool (count_string::*)(count_string const&)const>(&count_string::startswith))
    .def("__hash__", &count_string::hash)
    .def("__iter__", &count_string::iter)
    .def("__len__", &count_string::len)
    ;

    py::class_<count_string_iterator>(
        handle, "count_string_iterator"
    )
    .def("__iter__", &count_string_iterator::iter)
    .def("__next__", &count_string_iterator::next)
    ;
}
