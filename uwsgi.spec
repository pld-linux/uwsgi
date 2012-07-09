
# TODO:
# - pl desc
# - apache, nginx, lightttpd, django modules?
Summary:	Fast WSGI server
Summary(pl.UTF-8):	Szybki serwer WSGI
Name:		uwsgi
Version:	1.2.4
Release:	1
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://projects.unbit.it/downloads/%{name}-%{version}.tar.gz
# Source0-md5:	6090367c826216f59848677a79fb7129
Source1:	%{name}.init
Source2:	%{name}.xml
Source3:	%{name}.ini
Source4:	%{name}.sysconfig
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
%{__make} 
#-f Makefile.Py27 \
#	CC="%{__cc}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_sysconfdir}/rc.d/init.d,%{_sysconfdir}/sysconfig,%{_sysconfdir}/uwsgi,/var/{run/uwsgi,log}}
touch $RPM_BUILD_ROOT/var/log/%{name}.log
install uwsgi $RPM_BUILD_ROOT%{_bindir}
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/uwsgi/
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/uwsgi/
install %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -r -g 270 %{name}
%useradd -r -u 270 -d /usr/share/empty -s /bin/false -c "uWSGI User" -g %{name} %{name}

%post
/sbin/chkconfig --add %{name}
touch /var/log/%{name}.log
chown uwsgi:uwsgi /var/log/%{name}.log
chmod 644 /var/log/%{name}.log
%service %{name} restart

%preun
if [ "$1" = "0" ];then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" = "0" ]; then
	%userremove %{name}
	%groupremove %{name}
fi

%files
%defattr(644,root,root,755)
%dir %{_sysconfdir}/%{name}
%defattr(644,root,root,755)
%doc ChangeLog
%attr(755,root,root) %{_bindir}/uwsgi
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/uwsgi
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/uwsgi/uwsgi.xml
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/uwsgi/uwsgi.ini
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(755,uwsgi,uwsgi) %dir /var/run/uwsgi
%attr(644,uwsgi,uwsgi) %ghost /var/log/%{name}.log
