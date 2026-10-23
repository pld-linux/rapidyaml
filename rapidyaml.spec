# TODO: unbundle c4core
#
# Conditional build:
%bcond_without	apidocs		# API documentation
#
Summary:	ryml is a C++ library to parse and emit YAML
Name:		rapidyaml
Version:	0.16.0
Release:	1
License:	MIT
Group:		Libraries
Source0:	https://github.com/biojppm/rapidyaml/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	405851934758fac31bf128b6b59bd7d8
Source10:	patch-no-download
Patch0:		653.patch
Patch1:		662.patch
Patch2:		no-c4core-doc.patch
URL:		https://github.com/biojppm/rapidyaml
BuildRequires:	cmake
BuildRequires:	ninja
#BuildRequires:	c4core
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Rapidyanl or ryml, for short is a C++ library to parse and emit YAML,
and do it fast, on everything from x64 to bare-metal chips without
operating system.

The library is fully conformant to the YAML 1.2 spec, and passes 100%
of the cases in the YAML test suite. The parser is state-machine based
and not recursive. No known vulnerabilities exist. The code is robust
and extremely tested and fuzzed.

%package devel
Summary:	Header files for %{name} library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki %{name}
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for %{name} library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki %{name}.

%package apidocs
Summary:	API documentation for %{name} library
Summary(pl.UTF-8):	Dokumentacja API biblioteki %{name}
Group:		Documentation
BuildArch:	noarch

%description apidocs
API documentation for %{name} library.

%description apidocs -l pl.UTF-8
Dokumentacja API biblioteki %{name}.

%prep
%setup -q
%patch -P0 -p1
%patch -P1 -p1
%patch -P2 -p1

# Patch out download of gtest:
%{SOURCE10} proj/c4proj/c4Project.cmake '^    if\(_GTEST\)' '^    endif'

# Patch out download of c4fs:
%{SOURCE10} ext/testbm.cmake 'c4_download_remote_proj\(c4fs' '\)$'
%{SOURCE10} ext/testbm.cmake 'c4_add_library\(c4fs' '\)$'
%{SOURCE10} ext/testbm.cmake 'ryml_testbm_link_with_c4core\(c4fs' '\)$'

# Patch out download of c4log:
%{SOURCE10} ext/testbm.cmake 'c4_download_remote_proj\(c4log' '\)$'
%{SOURCE10} ext/testbm.cmake 'c4_add_library\(c4log' '\)$'
%{SOURCE10} ext/testbm.cmake 'ryml_testbm_link_with_c4core\(c4log' '\)$'

# Patch out download of yaml-test-suite:
%{SOURCE10} test/CMakeLists.txt \
    'c4_download_remote_proj\(yaml-test-suite' '\)$'
sed --regexp-extended --in-place \
    's@([[:blank:]]*)set\(tsdir.*\).*@&\nset\(suite_dir test/extern/yaml-test-suite\)\1@' \
    'test/CMakeLists.txt'
mkdir --parents 'test/extern/'

%build
%cmake -B build \
	-G Ninja \
	-DRYML_WITH_TAB_TOKENS:BOOL=ON

%ninja_build -C build

%if %{with apidocs}
make -C doc html
%endif

%install
rm -rf $RPM_BUILD_ROOT

%ninja_install -C build

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc README.md
%{_libdir}/libryml.so.*.*.*
%ghost %{_libdir}/libryml.so.0.16

%files devel
%defattr(644,root,root,755)
%{_libdir}/libryml.so
%{_includedir}/ryml*.hpp
%{_includedir}/c4
%{_libdir}/cmake/ryml

%if %{with apidocs}
%files apidocs
%defattr(644,root,root,755)
%doc doc/_build/html/*
%endif
