
# TODO:
# - pl desc, proper Group
# - apache, nginx, lightttpd, django modules?
# - init script
Summary:	Fast WSGI server
Summary(pl.UTF-8):	Szybki serwer WSGI
Name:		uwsgi
Version:	0.9.7
Release:	0.1
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://projects.unbit.it/downloads/%{name}-%{version}.tar.gz
# Source0-md5:	680e3edaff08f9302867aa0901abca54
#Source1:	%{name}
#Source2:	%{name}.xml
URL:		http://projects.unbit.it/uwsgi/
BuildRequires:	libxml2-devel
BuildRequires:	python-devel >= 1:2.7
BuildRequires:	python-modules
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
uWSGI is a fast (pure C), self-healing, developer-friendly WSGI
server, aimed for professional python webapps deployment and
development. Over time it has evolved in a complete stack for
networked/clustered python applications, implementing message/object
passing and process management. It uses the uwsgi (all lowercase)
protocol for all the networking/interprocess communications. From the
0.9.5 release it includes a plugin loading technology that can be used
to add support for other languages or platform. A Lua wsapi adaptor, a
PSGI handler and an Erlang message exchanger are already available.

%prep
%setup -q

%build
%{__make} -f Makefile.Py27 \
	CC="%{__cc}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_sysconfdir}/rc.d/init.d,%{_sysconfdir}/sysconfig}
install uwsgi $RPM_BUILD_ROOT%{_bindir}
#install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/
#install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc ChangeLog
%attr(755,root,root) %{_bindir}/uwsgi
#%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/uwsgi.xml
#%attr(754,root,root) %{_sysconfdir}/rc.d/init.d/uwsgi
