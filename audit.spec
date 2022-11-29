Summary:            User space tools for kernel auditing
Name:               audit
Epoch:              1
Version:            3.0.1
Release:            5
License:            GPLv2+ and LGPLv2+
URL:                https://people.redhat.com/sgrubb/audit/
Source0:            https://people.redhat.com/sgrubb/audit/%{name}-%{version}.tar.gz
Source1:            https://www.gnu.org/licenses/lgpl-2.1.txt

Patch0:          bugfix-audit-support-armv7b.patch
Patch1:          bugfix-audit-userspace-missing-syscalls-for-aarm64.patch
Patch2:          bugfix-audit-reload-coredump.patch
Patch3:          backport-Fix-the-default-location-for-zos-remote.conf-171.patch
Patch4:          backport-Add-missing-call-to-free_interpretation_list.patch
Patch5:          backport-fix-2-more-issues-found-by-fuzzing.patch
Patch6:          backport-Fix-an-auparse-memory-leak-caused-in-recent-glibc.patch
Patch7:          backport-Fix-double-free-with-corrupted-logs.patch
Patch8:          backport-Fix-the-closing-timing-of-audit_fd-166.patch
Patch9:          backport-Fix-some-string-length-issues.patch
Patch10:         backport-Move-the-free_config-to-success-path.patch
Patch11:         backport-Check-for-fuzzer-induced-invalid-value.patch
Patch12:         backport-error-out-if-log-is-mangled.patch
Patch13:         backport-Dont-run-off-the-end-with-corrupt-logs.patch
Patch14:         backport-Another-hardening-measure-for-corrupted-logs.patch
Patch15:         backport-Fix-busy-loop-in-normalizer-when-logs-are-corrupt.patch
Patch16:         backport-Better-fix-for-busy-loop-in-normalizer-when-logs-are.patch
Patch17:         backport-flush-uid-gid-caches-when-user-group-added-deleted-m.patch
Patch18:         backport-In-auditd-check-if-log_file-is-valid-before-closing-.patch
Patch19:         backport-Check-ctime-return-code.patch
Patch20:         backport-When-interpreting-if-val-is-NULL-return-an-empty-str.patch
Patch21:         backport-auditd.service-Restart-on-failure-ignoring-some-exit.patch
Patch22:         backport-0001-In-auditd-close-the-logging-file-descriptor-when-log.patch
Patch23:         backport-0002-In-auditd-close-the-logging-file-descriptor-when-log.patch
Patch24:         audit-Add-sw64-architecture.patch

BuildRequires:      gcc swig libtool systemd kernel-headers >= 2.6.29
BuildRequires:      openldap-devel krb5-devel libcap-ng-devel
%ifarch %{golang_arches}
BuildRequires:      golang
%endif
Requires:           %{name}-libs = %{epoch}:%{version}-%{release}
Requires(post):     systemd coreutils
Requires(preun):    systemd
Requires(postun):   systemd coreutils

%description
The audit package contains the user space utilities for storing and searching
the audit records generated by the audit subsystem in the Linux 2.6 and later
kernels.


%package libs
Summary: Dynamic library for libaudit
License: LGPLv2+

%description libs
The audit-libs package contains the dynamic libraries needed for 
applications to use the audit framework.

%package -n audispd-plugins
Summary: Plugins for audit event dispatcher
License: GPLv2+
Requires: %{name} = %{epoch}:%{version}-%{release}
Requires: %{name}-libs = %{epoch}:%{version}-%{release}

%description -n audispd-plugins
This package provides plugins for the real-time interface to audispd.

%package -n audispd-plugins-zos
Summary: z/OS plugin for audit event dispatcher
License: GPLv2+
Requires: %{name} = %{epoch}:%{version}-%{release}
Requires: %{name}-libs = %{epoch}:%{version}-%{release}
Requires: openldap

%description -n audispd-plugins-zos
This package provides a z/OS plugin for audit event dispatcher that
will forward audit events to a configured z/OS service management facility
database.

%package devel
Summary:            Header files for libaudit
License:            LGPLv2+
Requires:           %{name}%{?_isa} = %{epoch}:%{version}-%{release}
Requires:           kernel-headers >= 2.6.29
Provides:           audit-libs-devel audit-libs-static

%description devel
The audit-libs-devel package contains the header files needed for developing
applications that need to use the audit framework libraries.

%package -n python3-audit
Summary:            Python3 bindings for libaudit
License:            LGPLv2+
BuildRequires:      python3-devel
Requires:           %{name}%{?_isa} = %{epoch}:%{version}-%{release}
Provides:           audit-libs-python3 = %{version}-%{release}
Provides:           audit-libs-python3%{?_isa} = %{version}-%{release}
Obsoletes:          audit-libs-python3 < %{version}-%{release}

%description -n python3-audit
The python3-audit package contains the bindings so that libaudit and
libauparse can be used by python3.

%package_help

%prep
%autosetup -n %{name}-%{version} -p1
cp %{SOURCE1} .
autoreconf -f -i

%build
%configure --sbindir=/sbin --libdir=/%{_lib} --with-python=no \
           --with-python3=yes \
           --enable-gssapi-krb5=yes --with-arm --with-aarch64 \
           --with-libcap-ng=yes --enable-zos-remote \
%ifarch %{golang_arches}
           --with-golang \
%endif
           --enable-systemd

make CFLAGS="%{optflags}" %{?_smp_mflags}

%install
mkdir -p $RPM_BUILD_ROOT/{sbin,etc/audit/plugins.d,etc/audit/rules.d}
mkdir -p $RPM_BUILD_ROOT/%{_mandir}/{man5,man8}
mkdir -p $RPM_BUILD_ROOT/%{_lib}
mkdir -p $RPM_BUILD_ROOT/%{_libdir}/audit
mkdir -p --mode=0700 $RPM_BUILD_ROOT/%{_var}/log/audit
mkdir -p $RPM_BUILD_ROOT/%{_var}/spool/audit
make DESTDIR=$RPM_BUILD_ROOT install

mkdir -p $RPM_BUILD_ROOT/%{_libdir}
mv $RPM_BUILD_ROOT/%{_lib}/libaudit.a $RPM_BUILD_ROOT%{_libdir}
mv $RPM_BUILD_ROOT/%{_lib}/libauparse.a $RPM_BUILD_ROOT%{_libdir}
curdir=`pwd`
cd $RPM_BUILD_ROOT/%{_libdir}
LIBNAME=`basename \`ls $RPM_BUILD_ROOT/%{_lib}/libaudit.so.1.*.*\``
ln -s ../../%{_lib}/$LIBNAME libaudit.so
LIBNAME=`basename \`ls $RPM_BUILD_ROOT/%{_lib}/libauparse.so.0.*.*\``
ln -s ../../%{_lib}/$LIBNAME libauparse.so
cd $curdir
rm -f $RPM_BUILD_ROOT/%{_lib}/libaudit.so
rm -f $RPM_BUILD_ROOT/%{_lib}/libauparse.so

find $RPM_BUILD_ROOT/%{_libdir}/python?.?/site-packages -name '*.a' -delete

mv $RPM_BUILD_ROOT/%{_lib}/pkgconfig $RPM_BUILD_ROOT%{_libdir}

touch -r ./audit.spec $RPM_BUILD_ROOT/etc/libaudit.conf
touch -r ./audit.spec $RPM_BUILD_ROOT/usr/share/man/man5/libaudit.conf.5.gz

%delete_la

%check
%ifarch %{golang_arches}
make check
%endif
rm -f rules/Makefile*

%pre
if [ -d "/etc/audisp/" ];then
    # custom plugins, copy config files from /etc/audisp/plugins.d to /etc/audit/plugins.d
    # self-plugins confile files will be overwritten when installing
    self_config_files_285=(syslog.conf au-remote.conf audispd-zos-remote.conf af_unix.conf)
    plugins_config_files=`ls /etc/audisp/plugins.d/*.conf 2>/dev/null | wc -w`
    if [ $plugins_config_files -gt 0 ];then
        if [ ! -d /etc/audit/plugins.d/ ];then
            mkdir -p /etc/audit/plugins.d/
        fi

        for file in `/usr/bin/ls /etc/audisp/plugins.d/*.conf`
        do
            if [[ " ${self_config_files_285} " =~ " `/usr/bin/basename $file` " ]];then
                continue
            else
                if [ ! -f /etc/audit/plugins.d/`/usr/bin/basename $file` ];then
                    cp $file /etc/audit/plugins.d/
                fi
            fi
        done
    fi
fi

%post
/sbin/ldconfig
files=`ls /etc/audit/rules.d/ 2>/dev/null | wc -w`
if [ "$files" -eq 0 ] ; then
	if [ -e /usr/share/doc/audit/rules/10-no-audit.rules ] ; then
	        cp /usr/share/doc/audit/rules/10-no-audit.rules /etc/audit/rules.d/audit.rules
	else
		touch /etc/audit/rules.d/audit.rules
	fi
	chmod 0600 /etc/audit/rules.d/audit.rules
fi
# merge custom changes to new file
if [ -d "/etc/audisp/" ];then
    if [ -s "/etc/audisp/plugins.d/af_unix.conf" ];then
        diffrence=`diff /etc/audisp/plugins.d/af_unix.conf /etc/audit/plugins.d/af_unix.conf`
        if [ "X$diffrence" != "X" ];then
            cp /etc/audisp/plugins.d/af_unix.conf /etc/audit/plugins.d/af_unix.conf
        fi
    fi
fi
%systemd_post auditd.service

%post -n audispd-plugins
# after installing audispd-plugins
if [ -d "/etc/audisp/" ];then
    for file in audisp-remote.conf au-remote.conf syslog.conf
    do
        # merge custom changes to new file
        if [ "$file" == "audisp-remote.conf" ];then
            if [ -s "/etc/audisp/$file" ];then
                diffrence=`diff /etc/audisp/$file /etc/audit/$file`
                if [ "X$diffrence" != "X" ];then
                    cp /etc/audisp/$file /etc/audit/$file
                    if [ "X`grep startup_failure_action /etc/audit/$file`" == "X" ];then
                        # add option in new version
                        echo "startup_failure_action = warn_once_continue" >> /etc/audit/$file
                    fi
                fi
            fi
        elif [ "$file" == "syslog.conf" ];then
            if [ -s "/etc/audisp/plugins.d/$file" ];then
                diffrence=`diff /etc/audisp/plugins.d/$file /etc/audit/plugins.d/$file`
                if [ "X$diffrence" != "X" ];then
                    cp /etc/audisp/plugins.d/syslog.conf /etc/audit/plugins.d/syslog.conf
                    # change options "path" and "type"
                    sed -i 's/path[ ]*=[ ]*builtin_syslog/path\ =\ \/sbin\/audisp-syslog/g' /etc/audit/plugins.d/syslog.conf
                    sed -i 's/type[ ]*=[ ]*builtin/type\ =\ always/g' /etc/audit/plugins.d/syslog.conf
                fi
            fi
        else
            if [ -s "/etc/audisp/plugins.d/$file" ];then
                diffrence=`diff /etc/audisp/plugins.d/$file /etc/audit/plugins.d/$file`
                if [ "X$diffrence" != "X" ];then
                    cp /etc/audisp/plugins.d/$file /etc/audit/plugins.d/$file
                fi
            fi
        fi
    done
fi

%post -n audispd-plugins-zos
# after installing audispd-plugins-zos
if [ -d "/etc/audisp/" ];then
    for file in audispd-zos-remote.conf zos-remote.conf
    do
        # merge custom changes to new file
        if [ "$file" == "zos-remote.conf" ];then
            if [ -s "/etc/audisp/$file" ];then
                diffrence=`diff /etc/audisp/$file /etc/audit/$file`
                if [ "X$diffrence" != "X" ];then
                    cp /etc/audisp/$file /etc/audit/$file
                fi
            fi
        elif [ "$file" == "audispd-zos-remote.conf" ];then
            if [ -s "/etc/audisp/plugins.d/$file" ];then
                diffrence=`diff /etc/audisp/plugins.d/$file /etc/audit/plugins.d/$file`
                if [ "X$diffrence" != "X" ];then
                    cp /etc/audisp/plugins.d/$file /etc/audit/plugins.d/$file
                    # change option "args"
                    sed -i 's/\/etc\/audisp\/zos-remote\.conf/\/etc\/audit\/zos-remote\.conf/g' /etc/audit/plugins.d/$file
                fi
            fi
        fi
    done
fi

%preun
if [ $1 -eq 0 ] && [ -x /usr/bin/systemctl ]; then 
        # Package removal, not upgrade 
        /usr/bin/systemctl --no-reload disable auditd.service || : 
fi
if [ $1 -eq 0 ]; then
        # Package removal, not upgrade 
        /sbin/service auditd stop > /dev/null 2>&1
fi

%postun
/sbin/ldconfig
if [ $1 -ge 1 ]; then
   /sbin/service auditd condrestart > /dev/null 2>&1 || :
fi

%files
%doc README
%{!?_licensedir:%global license %%doc}
%license COPYING lgpl-2.1.txt
%attr(755,root,root) /sbin/auditctl
%attr(755,root,root) /sbin/auditd
%attr(755,root,root) /sbin/ausearch
%attr(755,root,root) /sbin/aureport
%attr(750,root,root) /sbin/autrace
%attr(755,root,root) /sbin/augenrules
%attr(755,root,root) %{_bindir}/aulast
%attr(755,root,root) %{_bindir}/aulastlog
%attr(755,root,root) %{_bindir}/ausyscall
%attr(755,root,root) %{_bindir}/auvirt
%attr(644,root,root) %{_unitdir}/auditd.service
%attr(750,root,root) %dir %{_libexecdir}/initscripts/legacy-actions/auditd
%attr(750,root,root) %{_libexecdir}/initscripts/legacy-actions/auditd/condrestart
%attr(750,root,root) %{_libexecdir}/initscripts/legacy-actions/auditd/reload
%attr(750,root,root) %{_libexecdir}/initscripts/legacy-actions/auditd/restart
%attr(750,root,root) %{_libexecdir}/initscripts/legacy-actions/auditd/resume
%attr(750,root,root) %{_libexecdir}/initscripts/legacy-actions/auditd/rotate
%attr(750,root,root) %{_libexecdir}/initscripts/legacy-actions/auditd/state
%attr(750,root,root) %{_libexecdir}/initscripts/legacy-actions/auditd/stop
%ghost %{_localstatedir}/run/auditd.state
%attr(750,root,root) %dir %{_var}/log/audit
%attr(750,root,root) %dir /etc/audit
%attr(750,root,root) %dir /etc/audit/rules.d
%attr(750,root,root) %dir /etc/audit/plugins.d
%config(noreplace) %attr(640,root,root) /etc/audit/auditd.conf
%ghost %config(noreplace) %attr(600,root,root) /etc/audit/rules.d/audit.rules
%ghost %config(noreplace) %attr(640,root,root) /etc/audit/audit.rules
%config(noreplace) %attr(640,root,root) /etc/audit/audit-stop.rules
%config(noreplace) %attr(640,root,root) /etc/audit/plugins.d/af_unix.conf

%files libs
/%{_lib}/libaudit.so.1*
/%{_lib}/libauparse.*
%config(noreplace) %attr(640,root,root) /etc/libaudit.conf

%files -n audispd-plugins
%config(noreplace) %attr(640,root,root) /etc/audit/audisp-remote.conf
%config(noreplace) %attr(640,root,root) /etc/audit/plugins.d/au-remote.conf
%config(noreplace) %attr(640,root,root) /etc/audit/plugins.d/syslog.conf
%attr(750,root,root) /sbin/audisp-remote
%attr(750,root,root) /sbin/audisp-syslog
%attr(700,root,root) %dir %{_var}/spool/audit

%files -n audispd-plugins-zos
%config(noreplace) %attr(640,root,root) /etc/audit/plugins.d/audispd-zos-remote.conf
%config(noreplace) %attr(640,root,root) /etc/audit/zos-remote.conf
%attr(750,root,root) /sbin/audispd-zos-remote

%files devel
%defattr(-,root,root)
%doc contrib/plugin
%{!?_licensedir:%global license %%doc}
%license lgpl-2.1.txt
%{_libdir}/libaudit.so
%{_libdir}/libauparse.so
%ifarch %{golang_arches}
%dir %{_prefix}/lib/golang/src/pkg/redhat.com/audit
%{_prefix}/lib/golang/src/pkg/redhat.com/audit/audit.go
%endif
%{_includedir}/libaudit.h
%{_includedir}/auparse.h
%{_includedir}/auparse-defs.h
%{_datadir}/aclocal/audit.m4
%{_libdir}/pkgconfig/audit.pc
%{_libdir}/pkgconfig/auparse.pc
%{_libdir}/libaudit.a
%{_libdir}/libauparse.a

%files -n python3-audit
%attr(755,root,root) %{python3_sitearch}/*

%files help
%defattr(-,root,root)
%doc ChangeLog rules init.d/auditd.cron
%attr(644,root,root) %{_datadir}/%{name}/sample-rules/*
%attr(644,root,root) %{_mandir}/man3/*.3.gz
%attr(644,root,root) %{_mandir}/man5/*.5.gz
%attr(644,root,root) %{_mandir}/man7/*.7.gz
%attr(644,root,root) %{_mandir}/man8/*.8.gz

%changelog
* Mon Nov 14 2022 wuzx<wuzx1226@qq.com> - 3.0.1-5
- Add sw64 architecture

* Fri Oct 21 2022 zhangguangzhi <zhangguangzhi3@huawei.com> - 3.0.1-4
- change release

* Sat Feb 12 2022 yixiangzhike <yixiangzhike007@163.com> - 3.0.1-3
- Fix failure of stopping auditd before uninstalling

* Thu Dec 30 2021 yixiangzhike <yixiangzhike007@163.com> - 3.0.1-2
- drop unused patch file

* Fri Dec 10 2021 yixiangzhike <yixiangzhike007@163.com> - 3.0.1-1
- update to 3.0.1

* Tue Nov 16 2021 yixiangzhike <zhangxingliang3@huawei.com> - 3.0-3
- backport some patches
   Add missing call to free_interpretation_list
   fix 2 more issues found by fuzzing
   Fix an auparse memory leak caused in recent glibc
   Fix double free with corrupted logs
   Turn libaucommon into a libtool convenience library
   Fix the closing timing of audit_fd
   Fix some string length issues
   Move the free_config to success path
   Check for fuzzer induced invalid value
   error out if log is mangled
   Dont run off the end with corrupt logs
   Another hardening measure for corrupted logs
   Fix busy loop in normalizer when logs are corrupt
   Better fix for busy loop in normalizer when logs are corrupt
   flush uid gid caches when user group added deleted modified
   In auditd check if log_file is valid before closing handle
   Check ctime return code
   When interpreting if val is NULL return an empty string
   auditd.service Restart on failure ignoring some exit
   In auditd close the logging file descriptor when logging is suspended

* Fri May 28 2021 yixiangzhike <zhangxingliang3@huawei.com> - 3.0-2
- solve the script failure when package upgrade

* Tue May 25 2021 yixiangzhike <zhangxingliang3@huawei.com> - 3.0-1
- update to 3.0

* Mon May 24 2021 yixiangzhike <zhangxingliang3@huawei.com> - 2.8.5-4
- fix directory permissions for /etc/audisp and /etc/audisp/plugins.d

* Thu Oct 29 2020 zhangxingliang <zhangxingliang3@huawei.com> - 2.8.5-3
- remove python2 subpackage 

* Wed Aug 19 2020 wangchen <wangchen137@huawei.com> - 2.8.5-2
- add epoch for requires

* Wed Jul 29 2020 wangchen <wangchen137@huawei.com> - 2.8.5-1
- revert to 2.8.5

* Wed Jan 22 2020 openEuler Buildteam <buildteam@openeuler.org> - 3.0-5
- add subpackages

* Tue Jan 14 2020 openEuler Buildteam <buildteam@openeuler.org> - 3.0-4
- clean code

* Wed Oct 9 2019 openEuler Buildteam <buildteam@openeuler.org> - 3.0-3
- Adjust requires

* Sun Sep 29 2019 openEuler Buildteam <buildteam@openeuler.org> - 3.0-2
- Fix the auditctl error

* Sat Sep 21 2019 openEuler Buildteam <buildteam@openeuler.org> - 3.0-1
- Package init
