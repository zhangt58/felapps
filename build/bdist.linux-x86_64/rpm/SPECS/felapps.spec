%define name felapps
%define version 1.0.0
%define unmangled_version 1.0.0
%define unmangled_version 1.0.0
%define release 1

Summary: High-level applications for FEL commissioning.
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: MIT
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Tong Zhang <zhangtong@sinap.ac.cn>

%description
High-level applications created for the tunning/commissioning of the free-electron laser facilities.

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
