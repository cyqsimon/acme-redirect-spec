%global debug_package %{nil}

Name:           acme-redirect
Version:        0.6.2
Release:        3%{?dist}
Summary:        ACME answerer & 80-to-443 redirector

License:        GPLv3
URL:            https://github.com/kpcyrd/acme-redirect
Source0:        %{url}/archive/v%{version}.tar.gz

BuildRequires:  gcc make pkgconfig(openssl) scdoc systemd-rpm-macros

%description
Tiny http daemon that answers acme challenges and
redirects everything else to https

%prep
%autosetup

# use latest stable version from rustup
curl -Lf "https://sh.rustup.rs" | sh -s -- --profile minimal -y

%build
source ~/.cargo/env
RUSTFLAGS="-C strip=symbols" cargo build --release
make docs
target/release/acme-redirect completions bash > bash.completion
target/release/acme-redirect completions zsh > zsh.completion
target/release/acme-redirect completions fish > fish.completion

%check
source ~/.cargo/env
cargo test

%install
# `install -D -t <dir>` does not correctly create `<dir>` on EL7
%if 0%{?el7}
    install -d \
        %{buildroot}%{_bindir} \
        %{buildroot}%{_sysconfdir} \
        %{buildroot}%{_unitdir} \
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
install -Dm 644 -t %{buildroot}%{_unitdir} \
    contrib/systemd/acme-redirect-renew.service \
    contrib/systemd/acme-redirect-renew.timer \
    contrib/systemd/acme-redirect.service
install -Dm 644 contrib/systemd/acme-redirect.sysusers %{buildroot}%{_sysusersdir}/acme-redirect.conf
install -Dm 644 contrib/systemd/acme-redirect.tmpfiles %{buildroot}%{_tmpfilesdir}/acme-redirect.conf

# manpage
install -Dm 644 -t %{buildroot}%{_mandir}/man1 contrib/docs/acme-redirect.1
install -Dm 644 -t %{buildroot}%{_mandir}/man5 \
    contrib/docs/acme-redirect.conf.5 \
    contrib/docs/acme-redirect.d.5

%post
systemctl daemon-reload
systemd-sysusers
systemd-tmpfiles --create

systemctl try-restart acme-redirect.service

%files
%{_bindir}/acme-redirect

%config(noreplace) %{_sysconfdir}/acme-redirect.conf
%config %{_sysconfdir}/acme-redirect.d/example.com.conf.sample

%{_datadir}/bash-completion/completions/acme-redirect
%{_datadir}/zsh/site-functions/_acme-redirect
%{_datadir}/fish/vendor_completions.d/acme-redirect.fish

%{_unitdir}/acme-redirect-renew.service
%{_unitdir}/acme-redirect-renew.timer
%{_unitdir}/acme-redirect.service
%{_sysusersdir}/acme-redirect.conf
%{_tmpfilesdir}/acme-redirect.conf

%{_mandir}/man1/acme-redirect.1.gz
%{_mandir}/man5/acme-redirect.conf.5.gz
%{_mandir}/man5/acme-redirect.d.5.gz

%license LICENSE
%doc README.md

%changelog
* Sat Mar 18 2023 cyqsimon - 0.6.2-3
- Run tests in debug mode

* Thu Feb 23 2023 cyqsimon - 0.6.2-2
- Imprv scriptlet

* Thu Jan 05 2023 cyqsimon - 0.6.2-1
- Release 0.6.2
- Use latest toolchain from rustup
- Run tests

* Thu Sep 08 2022 cyqsimon - 0.5.3-5
- Fix systemd files install location

* Wed May 25 2022 cyqsimon - 0.5.3-4
- Added post-install scriptlets

* Mon May 16 2022 cyqsimon - 0.5.3-3
- Apply rpmlint suggestions

* Mon May 16 2022 cyqsimon - 0.5.3-2
- Install shell completions

* Tue Apr 05 2022 cyqsimon - 0.5.3-1
- Initial build
