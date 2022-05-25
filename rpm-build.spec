%global debug_package %{nil}

Name:           acme-redirect
Version:        0.5.3
Release:        4%{?dist}
Summary:        ACME answerer & 80-to-443 redirector

License:        GPLv3
URL:            https://github.com/kpcyrd/acme-redirect
Source0:        https://github.com/kpcyrd/acme-redirect/archive/v%{version}.tar.gz

BuildRequires:  cargo make rust openssl-devel scdoc
Requires:       glibc

%description
Tiny http daemon that answers acme challenges and
redirects everything else to https

%prep
%autosetup

%build
RUSTFLAGS="-C strip=symbols" cargo build --release
make docs
target/release/acme-redirect completions bash > bash.completion
target/release/acme-redirect completions zsh > zsh.completion
target/release/acme-redirect completions fish > fish.completion

%install
# `install -D -t <dir>` does not correctly create `<dir>` on EL7
%if 0%{?el7}
    install -d \
        %{buildroot}%{_bindir} \
        %{buildroot}%{_sysconfdir} \
        %{buildroot}%{_libdir}/systemd/system \
        %{buildroot}%{_mandir}/man{1,5}
%endif

# binary
install -Dm 755 -t %{buildroot}%{_bindir} target/release/acme-redirect

# config
install -Dm 644 -t %{buildroot}%{_sysconfdir} contrib/confs/acme-redirect.conf
install -Dm 644 contrib/confs/certs.d/example.com.conf %{buildroot}%{_sysconfdir}/acme-redirect.d/example.com.conf.sample

# completion
install -Dm 644 bash.completion %{buildroot}%{_datadir}/bash-completion/completions/acme-redirect
install -Dm 644 zsh.completion %{buildroot}%{_datadir}/zsh/site-functions/_acme-redirect
install -Dm 644 fish.completion %{buildroot}%{_datadir}/fish/vendor_completions.d/acme-redirect.fish

# systemd
install -Dm 644 -t %{buildroot}%{_libdir}/systemd/system \
    contrib/systemd/acme-redirect-renew.service \
    contrib/systemd/acme-redirect-renew.timer \
    contrib/systemd/acme-redirect.service
install -Dm 644 contrib/systemd/acme-redirect.sysusers %{buildroot}%{_libdir}/sysusers.d/acme-redirect.conf
install -Dm 644 contrib/systemd/acme-redirect.tmpfiles %{buildroot}%{_libdir}/tmpfiles.d/acme-redirect.conf

# manpage
install -Dm 644 -t %{buildroot}%{_mandir}/man1 contrib/docs/acme-redirect.1
install -Dm 644 -t %{buildroot}%{_mandir}/man5 \
    contrib/docs/acme-redirect.conf.5 \
    contrib/docs/acme-redirect.d.5

%post
systemctl daemon-reload
systemd-sysusers
systemd-tmpfiles --create

if systemctl --quiet is-active acme-redirect.service; then
    systemctl restart acme-redirect.service
fi

%files
%{_bindir}/acme-redirect
%config(noreplace) %{_sysconfdir}/acme-redirect.conf
%config %{_sysconfdir}/acme-redirect.d/example.com.conf.sample
%{_datadir}/bash-completion/completions/acme-redirect
%{_datadir}/zsh/site-functions/_acme-redirect
%{_datadir}/fish/vendor_completions.d/acme-redirect.fish
%{_libdir}/systemd/system/acme-redirect-renew.service
%{_libdir}/systemd/system/acme-redirect-renew.timer
%{_libdir}/systemd/system/acme-redirect.service
%{_libdir}/sysusers.d/acme-redirect.conf
%{_libdir}/tmpfiles.d/acme-redirect.conf
%{_mandir}/man1/acme-redirect.1.gz
%{_mandir}/man5/acme-redirect.conf.5.gz
%{_mandir}/man5/acme-redirect.d.5.gz
%license LICENSE
%doc README.md

%changelog
* Mon May 16 2022 cyqsimon - 0.5.3-3
- Apply rpmlint suggestions

* Mon May 16 2022 cyqsimon - 0.5.3-2
- Install shell completions

* Tue Apr 05 2022 cyqsimon - 0.5.3-1
- Initial build
