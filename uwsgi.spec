# TODO: pl desc, proper Group
Summary:	Fast WSGI server
Summary(pl.UTF-8):	Szybki serwer WSGI
Name:		uwsgi
Version:	0.9.4.3
Release:	1
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://projects.unbit.it/downloads/%{name}-%{version}.tar.gz
# Source0-md5:	5f6a7385138deccfd5f8a80f2e0dea04
URL:		http://projects.unbit.it/uwsgi/
BuildRequires:	python-devel >= 1:2.6
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
%{__make} -f Makefile.Py26

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_bindir}
install uwsgi26 $RPM_BUILD_ROOT%{_bindir}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc ChangeLog
%attr(755,root,root) %{_bindir}/uwsgi26
