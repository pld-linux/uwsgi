
%bcond_without xml
%bcond_without yaml
%bcond_without zeromq
%bcond_without ssl
%bcond_without pcre
%bcond_without routing
%bcond_without matheval
%bcond_without python2
%bcond_without python3
%bcond_without greenlet
%bcond_with json

%if %{without python2} && %{without python3}
%undefine with_greenlet
%endif

# TODO:
# - pl desc
# - apache, module?
# - 'gevent' plugin depends on python and works only after python plugin is loaded
#   this can probably be fixed by better linking

Summary:	Fast WSGI server
Summary(pl.UTF-8):	Szybki serwer WSGI
Name:		uwsgi
Version:	2.0.12
Release:	1
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://projects.unbit.it/downloads/%{name}-%{version}.tar.gz
# Source0-md5:	1451cab954bad0d7d7429e4d2c84b5df
Source1:	%{name}.init
Source2:	emperor.ini
Source3:	%{name}.tmpfiles
Source4:	%{name}.service
Patch0:		%{name}-plugin_build_dir.patch
Patch1:		shared_python.patch
URL:		http://projects.unbit.it/uwsgi/
%{?with_xml:BuildRequires:	libxml2-devel}
%{?with_yaml:BuildRequires:	yaml-devel}
%{?with_json:BuildRequires:	jansson-devel}
%{?with_zeromq:BuildRequires:	zeromq-devel}
%{?with_ssl:BuildRequires:	openssl-devel}
%{?with_matheval:BuildRequires:	libmatheval-devel}
%{!?with_matheval:BuildConflicts:	libmatheval-devel}
%if %{with pcre} || %{with routing}
BuildRequires:	pcre-devel
%endif
BuildRequires:	libcap-devel
BuildRequires:	libuuid-devel
BuildRequires:	zlib-devel
BuildRequires:	python-modules
%if %{with python2}
BuildRequires:	python-devel >= 1:2.7
%{?with_greenlet:BuildRequires:	python-greenlet-devel}
%endif
%if %{with python3}
BuildRequires:	python3-devel >= 1:2.7
%{?with_greenlet:BuildRequires:	python3-greenlet-devel}
BuildRequires:	python3-modules
%endif
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	rc-scripts >= 0.4.3.0
Requires:	systemd-units >= 38
Suggests:	uwsgi-plugin-python
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define pyver %(echo %{py_ver} | tr -d .)
%define py3ver %(echo %{py3_ver} | tr -d .)

%define _noautoprovfiles %{_libdir}/%{name}/.*

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

%package plugin-python
Summary:	Python 2.x plugin for uWSGI
Group:		Networking/Daemons
Requires:	%{name} = %{version}-%{release}

%description plugin-python
Python 2.x plugin for uWSGI.

%package plugin-python3
Summary:	Python 3.x plugin for uWSGI
Group:		Networking/Daemons
Requires:	%{name} = %{version}-%{release}

%description plugin-python3
Python 3.x plugin for uWSGI.

%prep
%setup -q

%patch0 -p1
%patch1 -p1

%build
cat >buildconf/pld.ini <<EOF
[uwsgi]
main_plugin =
embedded_plugins =
inherit = base
plugin_dir = %{_libdir}/uwsgi

xml = %{?with_xml:true}%{!?with_xml:false}
yaml = %{?with_yaml:true}%{!?with_yaml:false}
zeromq = %{?with_zeromq:true}%{!?with_zeromq:false}
ssl = %{?with_ssl:true}%{!?with_ssl:false}
pcre = %{?with_pcre:true}%{!?with_pcre:false}
routing = %{?with_routing:true}%{!?with_routing:false}
matheval = %{?with_matheval:true}%{!?with_matheval:false}
json = %{?with_json:true}%{!?with_json:false}

%{?with_xml:xml_implementation = libxml2}
EOF

%{__python} uwsgiconfig.py --build pld

# base plugin list from buildconf/base.ini
for plugin in \
	ping cache nagios rrdtool carbon rpc corerouter \
	fastrouter http ugreen signal syslog rsyslog logsocket \
	router_uwsgi router_redirect router_basicauth zergpool \
	redislog mongodblog router_rewrite router_http logfile \
	router_cache rawrouter router_static sslrouter spooler \
	cheaper_busyness symcall transformation_tofile \
	transformation_gzip transformation_chunked \
	transformation_offload router_memcached router_redis \
	router_hash router_expires router_metrics \
	transformation_template stats_pusher_socket ; do

	%{__python} uwsgiconfig.py --plugin plugins/${plugin} pld ${plugin}
done

# extra non-base plugins
for plugin in cgi ; do
	%{__python} uwsgiconfig.py --plugin plugins/${plugin} pld ${plugin}
done

%if %{with python2}
%{__python} uwsgiconfig.py --plugin plugins/python pld python%{pyver}
%{__python} uwsgiconfig.py --plugin plugins/gevent pld gevent_py%{pyver}
%{?with_greenlet:%{__python} uwsgiconfig.py --plugin plugins/greenlet pld greenlet_py%{pyver}}
%endif
%if %{with python3}
%{__python3} uwsgiconfig.py --plugin plugins/python pld python%{py3ver}
%{__python3} uwsgiconfig.py --plugin plugins/gevent pld gevent_py%{py3ver}
%{?with_greenlet:%{__python} uwsgiconfig.py --plugin plugins/greenlet pld greenlet_py%{py3ver}}
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_libdir}/%{name}} \
	$RPM_BUILD_ROOT{%{_sysconfdir}/rc.d/init.d,%{_sysconfdir}/sysconfig} \
	$RPM_BUILD_ROOT{%{_sysconfdir}/uwsgi/vassals,/var/{run/uwsgi,log}} \
	$RPM_BUILD_ROOT{%{systemdtmpfilesdir},%{systemdunitdir}}

touch $RPM_BUILD_ROOT/var/log/%{name}.log
install uwsgi $RPM_BUILD_ROOT%{_bindir}
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/uwsgi/emperor.ini
install %{SOURCE3} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/%{name}.conf
install %{SOURCE4} $RPM_BUILD_ROOT%{systemdunitdir}/%{name}.service

install *_plugin.so $RPM_BUILD_ROOT%{_libdir}/%{name}

# the symlinks must be absolute – otherwise strange things happen in strace
%if %{with python2}
ln -s %{_libdir}/%{name}/python%{pyver}_plugin.so $RPM_BUILD_ROOT%{_libdir}/%{name}/python_plugin.so
ln -s %{_libdir}/%{name}/gevent_py%{pyver}_plugin.so $RPM_BUILD_ROOT%{_libdir}/%{name}/gevent_plugin.so
%{?with_greenlet:ln -s %{_libdir}/%{name}/greenlet_py%{pyver}_plugin.so $RPM_BUILD_ROOT%{_libdir}/%{name}/greenlet_plugin.so}
%endif
%if %{with python3}
ln -s %{_libdir}/%{name}/python%{py3ver}_plugin.so $RPM_BUILD_ROOT%{_libdir}/%{name}/python3_plugin.so
ln -s %{_libdir}/%{name}/gevent_py%{py3ver}_plugin.so $RPM_BUILD_ROOT%{_libdir}/%{name}/gevent_py3_plugin.so
%{?with_greenlet:ln -s %{_libdir}/%{name}/greenlet_py%{py3ver}_plugin.so $RPM_BUILD_ROOT%{_libdir}/%{name}/greenlet_py3_plugin.so}
%endif

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
%systemd_post %{name}.service

%preun
if [ "$1" = "0" ];then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
fi
%systemd_preun %{name}.service

%postun
if [ "$1" = "0" ]; then
	%userremove %{name}
	%groupremove %{name}
fi
%systemd_reload

%triggerpostun -- %{name} < 1.9.12-1.1
UWSGI_CONFIG_FORMAT="xml"
[ -f /etc/sysconfig/uwsgi.rpmsave ] && . /etc/sysconfig/uwsgi.rpmsave || :
if [ "$UWSGI_CONFIG_FORMAT" = "xml" ] ; then
  if [ -f /etc/uwsgi/uwsgi.xml.rpmsave ] ; then
    sed -e 's/<daemonize>.*<\/daemonize>//' \
	-e 's/<uwsgi>/<uwsgi>\n<plugins>python,gevent,ping,cache,nagios,rrdtool,carbon,rpc,corerouter,fastrouter,http,ugreen,signal,syslog,rsyslog,logsocket,router_uwsgi,router_redirect,router_basicauth,zergpool,redislog,mongodblog,router_rewrite,router_http,logfile,router_cache,rawrouter<\/plugins>/' \
	< /etc/uwsgi/uwsgi.xml.rpmsave \
	> /etc/uwsgi/vassals/uwsgi.xml || :
  else
    cat >/etc/uwsgi/vassals/uwsgi.xml << 'EOF'
<uwsgi>
	<plugins>python,gevent,ping,cache,nagios,rrdtool,carbon,rpc,corerouter,fastrouter,http,ugreen,signal,syslog,rsyslog,logsocket,router_uwsgi,router_redirect,router_basicauth,zergpool,redislog,mongodblog,router_rewrite,router_http,logfile,router_cache,rawrouter</plugins>
        <pidfile>/var/run/uwsgi/uwsgi.pid</pidfile>
        <uid>uwsgi</uid>
        <gid>uwsgi</gid>
        <socket>/var/run/uwsgi/uwsgi.sock</socket>
</uwsgi>
EOF
  fi
elif [ "$UWSGI_CONFIG_FORMAT" = "ini" ] ; then
  if [ -f /etc/uwsgi/uwsgi.ini.rpmsave ] ; then
    mv /etc/uwsgi/vassals/uwsgi.ini{,.rpmorig}
    sed -e 's/[ \t]*daemonize.*//' \
	-e 's/^\[uwsgi\]/[uwsgi]\nplugins=python,gevent,ping,cache,nagios,rrdtool,carbon,rpc,corerouter,fastrouter,http,ugreen,signal,syslog,rsyslog,logsocket,router_uwsgi,router_redirect,router_basicauth,zergpool,redislog,mongodblog,router_rewrite,router_http,logfile,router_cache,rawrouter/' \
	< /etc/uwsgi/uwsgi.ini.rpmsave \
	> /etc/uwsgi/vassals/uwsgi.ini || :
  else
    cat >/etc/uwsgi/vassals/uwsgi.ini << 'EOF'
[uwsgi]
plugins = python,gevent,ping,cache,nagios,rrdtool,carbon,rpc,corerouter,fastrouter,http,ugreen,signal,syslog,rsyslog,logsocket,router_uwsgi,router_redirect,router_basicauth,zergpool,redislog,mongodblog,router_rewrite,router_http,logfile,router_cache,rawrouter
socket = /var/run/uwsgi/uwsgi.sock
uid = uwsgi
gid = uwsgi
pidfile = /var/run/uwsgi/uwsgi.pid
EOF
  fi
fi

if [ -f /var/run/uwsgi/uwsgi.pid ] ; then
  # for the service restart to work
  mv /var/run/uwsgi/uwsgi.pid /var/run/uwsgi-emperor.pid || :
fi

%banner -e %{name} << 'EOF'
uWSGI instance configuration has been moved to 
the %{_sysconfdir}/%{name}/vassals directory and
updated to be started via uWSGI emperor with loadable plugins.

The automatic configuration update might have failed, though.

You should probably install uwsgi-plugin-python too.
EOF
%service %{name} restart
%systemd_trigger %{name}.service

%files
%defattr(644,root,root,755)
%doc README
%attr(755,root,root) %{_bindir}/uwsgi
%{systemdtmpfilesdir}/%{name}.conf
%{systemdunitdir}/%{name}.service
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/uwsgi/emperor.ini
%dir %{_sysconfdir}/%{name}/vassals
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(755,uwsgi,uwsgi) %dir /var/run/uwsgi
%attr(644,uwsgi,uwsgi) %ghost /var/log/%{name}.log
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/cache_plugin.so
%{_libdir}/%{name}/carbon_plugin.so
%{_libdir}/%{name}/cgi_plugin.so
%{_libdir}/%{name}/cheaper_busyness_plugin.so
%{_libdir}/%{name}/corerouter_plugin.so
%{_libdir}/%{name}/fastrouter_plugin.so
%{_libdir}/%{name}/http_plugin.so
%{_libdir}/%{name}/logfile_plugin.so
%{_libdir}/%{name}/logsocket_plugin.so
%{_libdir}/%{name}/mongodblog_plugin.so
%{_libdir}/%{name}/nagios_plugin.so
%{_libdir}/%{name}/ping_plugin.so
%{_libdir}/%{name}/rawrouter_plugin.so
%{_libdir}/%{name}/redislog_plugin.so
%{_libdir}/%{name}/router_basicauth_plugin.so
%{_libdir}/%{name}/router_cache_plugin.so
%{_libdir}/%{name}/router_expires_plugin.so
%{_libdir}/%{name}/router_hash_plugin.so
%{_libdir}/%{name}/router_http_plugin.so
%{_libdir}/%{name}/router_memcached_plugin.so
%{_libdir}/%{name}/router_metrics_plugin.so
%{_libdir}/%{name}/router_redirect_plugin.so
%{_libdir}/%{name}/router_redis_plugin.so
%{_libdir}/%{name}/router_rewrite_plugin.so
%{_libdir}/%{name}/router_static_plugin.so
%{_libdir}/%{name}/router_uwsgi_plugin.so
%{_libdir}/%{name}/rpc_plugin.so
%{_libdir}/%{name}/rrdtool_plugin.so
%{_libdir}/%{name}/rsyslog_plugin.so
%{_libdir}/%{name}/signal_plugin.so
%{_libdir}/%{name}/spooler_plugin.so
%{_libdir}/%{name}/sslrouter_plugin.so
%{_libdir}/%{name}/stats_pusher_socket_plugin.so
%{_libdir}/%{name}/symcall_plugin.so
%{_libdir}/%{name}/syslog_plugin.so
%{_libdir}/%{name}/transformation_chunked_plugin.so
%{_libdir}/%{name}/transformation_gzip_plugin.so
%{_libdir}/%{name}/transformation_offload_plugin.so
%{_libdir}/%{name}/transformation_template_plugin.so
%{_libdir}/%{name}/transformation_tofile_plugin.so
%{_libdir}/%{name}/ugreen_plugin.so
%{_libdir}/%{name}/zergpool_plugin.so

%files plugin-python
%defattr(644,root,root,755)
%{_libdir}/%{name}/python_plugin.so
%{_libdir}/%{name}/python%{pyver}_plugin.so
%{_libdir}/%{name}/gevent_py%{pyver}_plugin.so
%{_libdir}/%{name}/gevent_plugin.so
%if %{with greenlet}
%{_libdir}/%{name}/greenlet_py%{pyver}_plugin.so
%{_libdir}/%{name}/greenlet_plugin.so
%endif

%files plugin-python3
%defattr(644,root,root,755)
%{_libdir}/%{name}/python3_plugin.so
%{_libdir}/%{name}/python%{py3ver}_plugin.so
%{_libdir}/%{name}/gevent_py%{py3ver}_plugin.so
%{_libdir}/%{name}/gevent_py3_plugin.so
%if %{with greenlet}
%{_libdir}/%{name}/greenlet_py3_plugin.so
%{_libdir}/%{name}/greenlet_py%{py3ver}_plugin.so
%endif
