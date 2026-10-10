#include <pybind11/pybind11.h>
#include <string>
#include <tuple>
#include <iostream>

namespace py = pybind11;

class benchar;
class count_str;
class count_str_iterator;

class benchar {
public:
    int cmp_count;
    count_str create(std::string);
};

class count_str {
    benchar &parent_benchar;
    
    int min(int a, int b) const;
    int max(int a, int b) const;
    std::tuple<int, int> first_diff(std::string const &a, std::string const &b) const;

public:
    std::string const base_string;

    count_str(std::string base_string, benchar &parent_benchar);
    std::string toString() const;
    count_str getItem(int item) const;
    count_str getItem(py::slice item) const;
    count_str add(count_str const &other) const;
    count_str add(std::string const &other) const;
    count_str radd(std::string const &other) const;
    bool eq(std::string const &other) const;
    bool eq(count_str const &other) const;
    bool ne(std::string const &other) const;
    bool ne(count_str const &other) const;
    bool lt(std::string const &other) const;
    bool lt(count_str const &other) const;
    bool ge(std::string const &other) const;
    bool ge(count_str const &other) const;
    bool gt(std::string const &other) const;
    bool gt(count_str const &other) const;
    bool le(std::string const &other) const;
    bool le(count_str const &other) const;
    bool endswith(std::string const &other) const;
    bool endswith(count_str const &other) const;
    bool startswith(std::string const &other) const;
    bool startswith(count_str const &other) const;
    int hash() const;
    count_str_iterator iter() const;
    int len() const;
};

class count_str_iterator {
    int curInd;
    count_str const &parent_count_str;

public:
    count_str_iterator(count_str const &parent_count_str);
    count_str_iterator &iter();
    count_str next();
};


count_str benchar::create(std::string base_string) {
    return count_str(base_string, *this);
}

count_str::count_str(std::string base_string, benchar &parent_benchar): base_string(base_string), parent_benchar(parent_benchar) {}
int count_str::min(int a, int b) const {
    return a < b ? a : b;
}
int count_str::max(int a, int b) const {
    return a > b ? a : b;
}
std::tuple<int, int> count_str::first_diff(std::string const &a, std::string const &b) const {
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
std::string count_str::toString() const {
    return base_string;
}
count_str count_str::getItem(int item) const {
    if(item < 0) {
        item = base_string.length() - item;
    }
    return count_str(std::string(1, base_string[item]), parent_benchar);
}
count_str count_str::getItem(py::slice item) const {
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
    
    return count_str(result, parent_benchar);
}
count_str count_str::add(count_str const &other) const {
    return count_str(base_string + other.base_string, parent_benchar);
}
count_str count_str::add(std::string const &other) const {
    return count_str(base_string + other, parent_benchar);
}
count_str count_str::radd(std::string const &other) const {
    return count_str(other + base_string, parent_benchar);
}
bool count_str::eq(std::string const &other) const {
    std::tuple<int, int> diff = first_diff(base_string, other);
    parent_benchar.cmp_count += std::get<1>(diff);
    return std::get<0>(diff) == 0;
}
bool count_str::eq(count_str const &other) const {
    return eq(other.base_string);
}
bool count_str::ne(std::string const &other) const {
    return !eq(other);
}
bool count_str::ne(count_str const &other) const {
    return !eq(other);
}
bool count_str::lt(std::string const &other) const {
    std::tuple<int, int> diff = first_diff(base_string, other);
    parent_benchar.cmp_count += std::get<1>(diff);
    return std::get<0>(diff) == -1;
}
bool count_str::lt(count_str const &other) const {
    return lt(other.base_string);
}
bool count_str::ge(std::string const &other) const {
    return !lt(other);
}
bool count_str::ge(count_str const &other) const {
    return !lt(other);
}
bool count_str::gt(std::string const &other) const {
    std::tuple<int, int> diff = first_diff(base_string, other);
    parent_benchar.cmp_count += std::get<1>(diff);
    return std::get<0>(diff) == 1;
}
bool count_str::gt(count_str const &other) const {
    return lt(other.base_string);
}
bool count_str::le(std::string const &other) const {
    return !gt(other);
}
bool count_str::le(count_str const &other) const {
    return !gt(other);
}
bool count_str::endswith(std::string const &other) const {
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
bool count_str::endswith(count_str const &other) const {
    return endswith(other.base_string);
}
bool count_str::startswith(std::string const &other) const {
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
bool count_str::startswith(count_str const &other) const {
    return startswith(other.base_string);
}
int count_str::hash() const {
    return std::hash<std::string>()(base_string);
}
count_str_iterator count_str::iter() const {
    return count_str_iterator(*this);
}
int count_str::len() const {
    return base_string.length();
}

count_str_iterator::count_str_iterator(count_str const &parent_count_str): parent_count_str(parent_count_str), curInd(0) {}
count_str_iterator &count_str_iterator::iter() {
    return *this;
}
count_str count_str_iterator::next() {
    if(curInd >= parent_count_str.base_string.length()) {
        throw py::stop_iteration();
    } else {
        return parent_count_str.getItem(curInd++);
    }
}


PYBIND11_MODULE(cbenchar, handle) {
    py::class_<benchar>(
        handle, "benchar"
    )
    .def(py::init<>())
    .def("__call__", &benchar::create)
    .def_readwrite("cmp_count", &benchar::cmp_count)
    ;
    
    py::class_<count_str>(
        handle, "count_str"
    )
    .def("__str__", &count_str::toString)
    .def("__getitem__", static_cast<count_str (count_str::*)(int)const>(&count_str::getItem))
    .def("__getitem__", static_cast<count_str (count_str::*)(py::slice)const>(&count_str::getItem))
    .def("__add__", static_cast<count_str (count_str::*)(count_str const&)const>(&count_str::add))
    .def("__add__", static_cast<count_str (count_str::*)(std::string const&)const>(&count_str::add))
    .def("__radd__", static_cast<count_str (count_str::*)(std::string const&)const>(&count_str::radd))
    .def("__eq__", static_cast<bool (count_str::*)(std::string const&)const>(&count_str::eq))
    .def("__eq__", static_cast<bool (count_str::*)(count_str const&)const>(&count_str::eq))
    .def("__ne__", static_cast<bool (count_str::*)(std::string const&)const>(&count_str::ne))
    .def("__ne__", static_cast<bool (count_str::*)(count_str const&)const>(&count_str::ne))
    .def("__lt__", static_cast<bool (count_str::*)(std::string const&)const>(&count_str::lt))
    .def("__lt__", static_cast<bool (count_str::*)(count_str const&)const>(&count_str::lt))
    .def("__ge__", static_cast<bool (count_str::*)(std::string const&)const>(&count_str::ge))
    .def("__ge__", static_cast<bool (count_str::*)(count_str const&)const>(&count_str::ge))
    .def("__gt__", static_cast<bool (count_str::*)(std::string const&)const>(&count_str::gt))
    .def("__gt__", static_cast<bool (count_str::*)(count_str const&)const>(&count_str::gt))
    .def("__le__", static_cast<bool (count_str::*)(std::string const&)const>(&count_str::le))
    .def("__le__", static_cast<bool (count_str::*)(count_str const&)const>(&count_str::le))
    .def("endswith", static_cast<bool (count_str::*)(std::string const&)const>(&count_str::endswith))
    .def("endswith", static_cast<bool (count_str::*)(count_str const&)const>(&count_str::endswith))
    .def("startswith", static_cast<bool (count_str::*)(std::string const&)const>(&count_str::startswith))
    .def("startswith", static_cast<bool (count_str::*)(count_str const&)const>(&count_str::startswith))
    .def("__hash__", &count_str::hash)
    .def("__iter__", &count_str::iter)
    .def("__len__", &count_str::len)
    ;

    py::class_<count_str_iterator>(
        handle, "count_str_iterator"
    )
    .def("__iter__", &count_str_iterator::iter)
    .def("__next__", &count_str_iterator::next)
    ;
}
