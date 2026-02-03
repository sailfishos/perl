%global perl_version    5.40.3
%global perl_epoch      4
%global perl_arch_stem -thread-multi
%global perl_archname %{_arch}-%{_os}%{perl_arch_stem}

%global multilib_64_archs aarch64 %{power64} s390x sparc64 x86_64
%global parallel_tests 1
%global tapsetdir   %{_datadir}/systemtap/tapset

# use "lib", not %%{_lib}, for privlib, sitelib, and vendorlib
# To build production version, we would need -DDEBUGGING=-g

# Perl INC path (perl -V) in search order:
# - /usr/local/share/perl5            -- for CPAN     (site lib)
# - /usr/local/lib[64]/perl5          -- for CPAN     (site arch)
# - /usr/share/perl5/vendor_perl      -- 3rd party    (vendor lib)
# - /usr/lib[64]/perl5/vendor_perl    -- 3rd party    (vendor arch)
# - /usr/share/perl5                  -- Fedora       (priv lib)
# - /usr/lib[64]/perl5                -- Fedora       (arch lib)

%global privlib     %{_prefix}/share/perl5
%global archlib     %{_libdir}/perl5

%global perl_vendorlib  %{privlib}/vendor_perl
%global perl_vendorarch %{archlib}/vendor_perl

# This overrides filters from build root (/usr/lib/rpm/macros.d/macros.perl)
# intentionally (unversioned perl(DB) is removed and versioned one is kept).
# Filter provides from *.pl files, bug #924938
%global __provides_exclude_from .*%{_docdir}
%global __provides_exclude_from %{?__provides_exclude_from:%__provides_exclude_from|}.*%{archlib}/.*\\.pl$|.*%{privlib}/.*\\.pl$
%global __requires_exclude_from %{_docdir}
%global __provides_exclude perl\\((VMS|Win32|BSD::|DB\\)$)
%global __requires_exclude perl\\((VMS|BSD::|Win32|Tk|Mac::|Your::Module::Here)
# same as we provide in /usr/lib/rpm/macros.d/macros.perl
%global perl5_testdir   %{_libexecdir}/perl5-tests

# Disabling gdbm because we don't use it and it makes boostrapping easier
%bcond_with gdbm
# We can skip %%check phase
%bcond_without test

Name:           perl
Version:        %{perl_version}
Release:        1
Epoch:          %{perl_epoch}
Summary:        Practical Extraction and Report Language
# Modules Tie::File and Getopt::Long are licenced under "GPLv2+ or Artistic,"
# we have to reflect that in the sub-package containing them.
# under UCD are unicode tables
# Public domain: ext/SDBM_File/sdbm/*, ext/Compress-Raw-Bzip2/bzip2-src/dlltest.c 
# MIT: ext/MIME-Base64/Base64.xs 
# Copyright Only: for example ext/Text-Soundex/Soundex.xs 
License:        (GPL+ or Artistic) and (GPLv2+ or Artistic) and Copyright Only and MIT and Public Domain and UCD
Url:            http://www.perl.org/
Source0:        http://www.cpan.org/src/5.0/perl-%{perl_version}.tar.xz
Source3:        macros.perl
# Systemtap tapset and example that make use of systemtap-sdt-devel
# build requirement. Written by lberk; Not yet upstream.
Source4:        perl.stp
Source5:        perl-example.stp

# Removes date check, Fedora/RHEL specific
Patch1:         perl-perlbug-tag.patch

# Fedora/RHEL only (64bit only)
Patch2:         perl-5.8.0-libdir64.patch

# Fedora/RHEL specific (use libresolv instead of libbind), bug #151127
Patch3:         perl-5.10.0-libresolv.patch

# FIXME: May need the "Fedora" references removed before upstreaming
# patches ExtUtils-MakeMaker
Patch4:         perl-USE_MM_LD_RUN_PATH.patch

# Provide maybe_command independently, bug #1129443
Patch5:         perl-5.22.1-Provide-ExtUtils-MM-methods-as-standalone-ExtUtils-M.patch

# The Fedora builders started randomly failing this futime test
# only on x86_64, so we just don't run it. Works fine on normal
# systems.
Patch6:         perl-5.10.0-x86_64-io-test-failure.patch

# switch off test, which is failing only on koji (fork)
Patch7:         perl-5.14.1-offtest.patch

# Define SONAME for libperl.so
Patch8:         perl-5.16.3-create_libperl_soname.patch

# Install libperl.so to -Dshrpdir value
Patch9:         perl-5.22.0-Install-libperl.so-to-shrpdir-on-Linux.patch

# Make *DBM_File desctructors thread-safe, bug #1107543, RT#61912
Patch10:        perl-5.34.0-Destroy-GDBM-NDBM-ODBM-SDBM-_File-objects-only-from-.patch

# Replace ExtUtils::MakeMaker dependency with ExtUtils::MM::Utils.
# This allows not to require perl-devel. Bug #1129443
Patch11:        perl-5.22.1-Replace-EU-MM-dependnecy-with-EU-MM-Utils-in-IPC-Cmd.patch

# Link XS modules to pthread library to fix linking with -z defs,
# <https://lists.fedoraproject.org/archives/list/devel@lists.fedoraproject.org/message/3RHZEHLRUHJFF2XGHI5RB6YPDNLDR4HG/>
Patch12:        perl-5.27.8-hints-linux-Add-lphtread-to-lddlflags.patch

# Pass the correct CFLAGS to dtrace
Patch13:        perl-5.28.0-Pass-CFLAGS-to-dtrace.patch

Patch100:       perl-reproducible.patch

# Link XS modules to libperl.so with EU::CBuilder on Linux, bug #960048
Patch200:       perl-5.16.3-Link-XS-modules-to-libperl.so-with-EU-CBuilder-on-Li.patch

# Link XS modules to libperl.so with EU::MM on Linux, bug #960048
Patch201:       perl-5.16.3-Link-XS-modules-to-libperl.so-with-EU-MM-on-Linux.patch

# If optimizing -O is used, add the definition to .ph files, bug #2152012
Patch202:       perl-5.36.0-Add-definition-of-OPTIMIZE-to-.ph-files.patch

# Update some of the bundled modules
# see http://fedoraproject.org/wiki/Perl/perl.spec for instructions

BuildRequires: db4-devel, bzip2-devel
BuildRequires: pkgconfig(zlib)
BuildRequires: pkgconfig(libcrypt)
%if %{with gdbm}
BuildRequires: gdbm-devel
%endif

# The long line of Perl provides.
# Compat provides
Provides: perl(:MODULE_COMPAT_5.40.3)
Provides: perl(:MODULE_COMPAT_5.16.3)
Provides: perl(:MODULE_COMPAT_5.16.1)
Provides: perl(:MODULE_COMPAT_5.16.0)
Provides: perl(:MODULE_COMPAT_5.12.1)
# Threading provides
Provides: perl(:WITH_ITHREADS)
Provides: perl(:WITH_THREADS)
# Largefile provides
Provides: perl(:WITH_LARGEFILES)
# PerlIO provides
Provides: perl(:WITH_PERLIO)
# Loaded by charnames, unicore/Name.pm does not declare unicore::Name module
Provides: perl(unicore::Name)
# File provides
Provides: perl(abbrev.pl)
Provides: perl(assert.pl)
Provides: perl(bigfloat.pl)
Provides: perl(bigint.pl)
Provides: perl(bigrat.pl)
Provides: perl(bytes_heavy.pl)
Provides: perl(cacheout.pl)
Provides: perl(complete.pl)
Provides: perl(ctime.pl)
Provides: perl(dotsh.pl)
Provides: perl(dumpvar.pl)
Provides: perl(exceptions.pl)
Provides: perl(fastcwd.pl)
Provides: perl(find.pl)
Provides: perl(finddepth.pl)
Provides: perl(flush.pl)
Provides: perl(ftp.pl)
Provides: perl(getcwd.pl)
Provides: perl(getopt.pl)
Provides: perl(getopts.pl)
Provides: perl(hostname.pl)
Provides: perl(importenv.pl)
Provides: perl(look.pl)
Provides: perl(newgetopt.pl)
Provides: perl(open2.pl)
Provides: perl(open3.pl)
Provides: perl(perl5db.pl)
Provides: perl(pwd.pl)
Provides: perl(shellwords.pl)
Provides: perl(stat.pl)
Provides: perl(syslog.pl)
Provides: perl(tainted.pl)
Provides: perl(termcap.pl)
Provides: perl(timelocal.pl)
Provides: perl(utf8_heavy.pl)
Provides: perl(validate.pl)
Provides: perl(Carp::Heavy)

# Long history in 3rd-party repositories:
Provides: perl-File-Temp = 0.22 
Obsoletes: perl-File-Temp < 0.20
Requires: perl-Scalar-List-Utils

Requires: perl-libs = %{perl_epoch}:%{perl_version}-%{release}

# We need this to break the dependency loop, and ensure that perl-libs 
# gets installed before perl.
Requires(post): perl-libs
# Same as perl-libs. We need macros in basic buildroot, where Perl is only
# because of git.
Requires(post): perl-macros


%description
Perl is a high-level programming language with roots in C, sed, awk and shell
scripting. Perl is good at handling processes and files, and is especially
good at handling text. Perl's hallmarks are practicality and efficiency.
While it is used to do a lot of different things, Perl's most common
applications are system administration utilities and web programming.

You need the perl package installed on your system so that your system can handle Perl
scripts.

Install this package if you want to program in Perl or enable your system to
handle Perl scripts.


%package libs
Summary:        The libraries for the perl runtime
License:        GPL+ or Artistic
Requires:       perl = %{perl_epoch}:%{perl_version}-%{release}

# Remove private redefinitions
# XSLoader redefines DynaLoader name space for compatibility, but it still
# loads DynaLoader.pm (though DynaLoader.xs is compiled into libperl).
%global __provides_exclude %{?__provides_exclude:%__provides_exclude|}^perl\\((charnames|DynaLoader)\\)$

%description libs
The libraries for the perl runtime


%package devel
Summary:        Header files for use in perl development
License:        GPL+ or Artistic
Requires:       perl(ExtUtils::ParseXS)
Requires:       perl = %{perl_epoch}:%{perl_version}-%{release}
Requires:       pkgconfig(libcrypt)

%description devel
This package contains header files and development modules.
Most perl packages will need to install perl-devel to build.


%package macros
Summary:        Macros for rpmbuild
License:        GPL+ or Artistic
BuildArch:      noarch
Requires:       perl = %{perl_epoch}:%{perl_version}-%{release}

%description macros
Macros for rpmbuild are needed during build of srpm in koji. This
sub-package must be installed into buildroot, so it will be needed
by perl. Perl is needed because of git.


%package tests
Summary:        The Perl test suite
License:        GPL+ or Artistic
AutoReqProv:    0
Requires:       perl = %{perl_epoch}:%{perl_version}-%{release}
# FIXME - note this will need to change when doing the core/minimal swizzle
Requires:       perl-core
Requires:       perl-parent

%description tests
This package contains the test suite included with Perl %{perl_version}.

Install this if you want to test your Perl installation (binary and core
modules).


%package Archive-Tar
Summary:        A module for Perl manipulation of .tar files
License:        GPL+ or Artistic
Version:        3.02
Requires:       perl = %{perl_epoch}:%{perl_version}
Requires:       perl(Compress::Zlib), perl(IO::Zlib)
BuildArch:      noarch

%description Archive-Tar
Archive::Tar provides an object oriented mechanism for handling tar files.  It
provides class methods for quick and easy files handling while also allowing
for the creation of tar file objects for custom manipulation.  If you have the
IO::Zlib module installed, Archive::Tar will also support compressed or
gzipped tar files.


%package Compress-Raw-Bzip2
Summary:        Low-Level Interface to bzip2 compression library
License:        GPL+ or Artistic
Version:        2.212
Requires:       perl(Exporter), perl(File::Temp)

%description Compress-Raw-Bzip2
This module provides a Perl interface to the bzip2 compression library.
It is used by IO::Compress::Bzip2.


%package Compress-Raw-Zlib
Summary:        Low-Level Interface to the zlib compression library
License:        (GPL+ or Artistic) AND Zlib
Version:        2.212
Requires:       perl = %{perl_epoch}:%{perl_version}

%description Compress-Raw-Zlib
This module provides a Perl interface to the zlib compression library.
It is used by IO::Compress::Zlib.


%package CPAN
Summary:        Query, download and build perl modules from CPAN sites
License:        GPL+ or Artistic
Version:        2.36
# CPAN encourages Digest::SHA strongly because of integrity checks
Requires:       perl(Digest::SHA)
Requires:       perl = %{perl_epoch}:%{perl_version}
Provides:       cpan = %{version}
BuildArch:      noarch

%description CPAN
Query, download and build perl modules from CPAN sites.

#%package CPAN-Meta
#Summary:        Distribution metadata for a CPAN dist
#Version:        2.150010
#License:        GPL+ or Artistic
#Requires:       perl = %{perl_epoch}:%{perl_version}
#BuildArch:      noarch

#%description CPAN-Meta
#Software distributions released to the CPAN include a META.json or, for
#older distributions, META.yml, which describes the distribution, its
#contents, and the requirements for building and installing the
#distribution. The data structure stored in the META.json file is described
#in CPAN::Meta::Spec.


%package CPAN-Meta-YAML
Version:        0.018
Summary:        Read and write a subset of YAML for CPAN Meta files
License:        GPL+ or Artistic
BuildArch:      noarch
Requires:       perl = %{perl_epoch}:%{perl_version}

%description CPAN-Meta-YAML
This module implements a subset of the YAML specification for use in reading
and writing CPAN metadata files like META.yml and MYMETA.yml. It should not be
used for any other general YAML parsing or generation task.


%package Digest
Summary:        Modules that calculate message digests
License:        GPL+ or Artistic
Version:        1.20
BuildArch:      noarch
Requires:       perl = %{perl_epoch}:%{perl_version}
Requires:       perl(MIME::Base64)

%description Digest
The Digest:: modules calculate digests, also called "fingerprints" or
"hashes", of some data, called a message. The digest is (usually)
some small/fixed size string. The actual size of the digest depend of
the algorithm used. The message is simply a sequence of arbitrary
bytes or bits.


%package Digest-SHA
Summary:        Perl extension for SHA-1/224/256/384/512
License:        GPL+ or Artistic
Version:        6.04
Requires:       perl = %{perl_epoch}:%{perl_version}
# Recommended
Requires:       perl(Digest::base)
Requires:       perl(MIME::Base64)

%description Digest-SHA
Digest::SHA is a complete implementation of the NIST Secure Hash
Standard.  It gives Perl programmers a convenient way to calculate
SHA-1, SHA-224, SHA-256, SHA-384, and SHA-512 message digests.  The
module can handle all types of input, including partial-byte data.


%package ExtUtils-CBuilder
Summary:        Compile and link C code for Perl modules
License:        GPL+ or Artistic
# real version 0.280240 https://fedoraproject.org/wiki/Perl/Tips#Dot_approach
Version:        0.28.2.40
Requires:       perl-devel
Requires:       perl = %{perl_epoch}:%{perl_version}
BuildArch:      noarch

%description ExtUtils-CBuilder
This module can build the C portions of Perl modules by invoking the
appropriate compilers and linkers in a cross-platform manner. It was motivated
by the Module::Build project, but may be useful for other purposes as well.


%package ExtUtils-Embed
Summary:        Utilities for embedding Perl in C/C++ applications
License:        GPL+ or Artistic
Version:        1.35
Requires:       perl-devel
Requires:       perl = %{perl_epoch}:%{perl_version}
BuildArch:      noarch

%description ExtUtils-Embed
Utilities for embedding Perl in C/C++ applications.


%package ExtUtils-Install
Summary:        Install files from here to there
License:        GPL+ or Artistic
Version:        2.22
Requires:       perl = %{perl_epoch}:%{perl_version}
BuildArch:      noarch

%description ExtUtils-Install
Handles the installing and uninstalling of perl modules, scripts, man
pages, etc.


%package ExtUtils-MakeMaker
Summary:        Create a module Makefile
License:        GPL+ or Artistic
Version:        7.70
Requires:       perl-devel
Requires:       perl = %{perl_epoch}:%{perl_version}
Requires:       perl(ExtUtils::Install)
Requires:       perl(ExtUtils::Manifest)
Requires:       perl(Test::Harness)
BuildArch:      noarch

# Filter false DynaLoader provides. Versioned perl(DynaLoader) keeps
# unfiltered on perl package, no need to reinject it.
%global __provides_exclude %{?__provides_exclude:%__provides_exclude|}^perl\\(DynaLoader\\)\\s*$
%global __provides_exclude %__provides_exclude|^perl\\(ExtUtils::MakeMaker::_version\\)

%description ExtUtils-MakeMaker
Create a module Makefile.


%package ExtUtils-Manifest
Summary:        Utilities to write and check a MANIFEST file
License:        GPL+ or Artistic
Version:        1.75
Requires:       perl = %{perl_epoch}:%{perl_version}
BuildArch:      noarch

%description ExtUtils-Manifest
%{summary}.


%package ExtUtils-ParseXS
Summary:        Module and a script for converting Perl XS code into C code
License:        GPL+ or Artistic
Version:        3.51
Requires:       perl-devel
Requires:       perl = %{perl_epoch}:%{perl_version}
BuildArch:      noarch

%description ExtUtils-ParseXS
ExtUtils::ParseXS will compile XS code into C code by embedding the constructs
necessary to let C functions manipulate Perl values and creates the glue
necessary to let Perl access those functions.


%package File-Fetch
Summary:        Generic file fetching mechanism
License:        GPL+ or Artistic
Version:        1.04
Requires:       perl(IPC::Cmd) >= 0.36
Requires:       perl(Module::Load::Conditional) >= 0.04
Requires:       perl(Params::Check) >= 0.07
Requires:       perl = %{perl_epoch}:%{perl_version}
BuildArch:      noarch

%description File-Fetch
File::Fetch is a generic file fetching mechanism.

# FIXME Filter-Simple? version?
%package Filter
Summary:        Perl source filters
License:        GPL+ or Artistic
Version:        1.64
Requires:       perl = %{perl_epoch}:%{perl_version}

%description Filter
Source filters alter the program text of a module before Perl sees it, much as
a C preprocessor alters the source text of a C program before the compiler
sees it.


%package IO-Compress
Summary:        IO::Compress wrapper for modules
License:        GPL+ or Artistic
Version:        2.212
Requires:       perl = %{perl_epoch}:%{perl_version}
Provides:       perl(IO::Uncompress::Bunzip2)

%description IO-Compress
This module is the base class for all IO::Compress and IO::Uncompress modules.
This module is not intended for direct use in application code. Its sole
purpose is to to be sub-classed by IO::Compress modules.


%package IO-Zlib
Summary:        Perl IO:: style interface to Compress::Zlib
License:        GPL+ or Artistic
Version:        1.15
Requires:       perl(Compress::Zlib)
Requires:       perl = %{perl_epoch}:%{perl_version}
BuildArch:      noarch

%description IO-Zlib
This modules provides an IO:: style interface to the Compress::Zlib package.
The main advantage is that you can use an IO::Zlib object in much the same way
as an IO::File object so you can have common code that doesn't know which sort
of file it is using.


%package IPC-Cmd
Summary:        Finding and running system commands made easy
License:        GPL+ or Artistic
Version:        1.04
Requires:       perl(ExtUtils::MakeMaker)
Requires:       perl = %{perl_epoch}:%{perl_version}
BuildArch:      noarch

%description IPC-Cmd
IPC::Cmd allows you to run commands, interactively if desired, in a platform
independent way, but have them still work.


%package HTTP-Tiny
Summary:        A small, simple, correct HTTP/1.1 client
License:        GPL+ or Artistic
Version:        0.088
Requires:       perl = %{perl_epoch}:%{perl_version}
Requires:       perl(IO::Socket)
BuildArch:      noarch

%description HTTP-Tiny
This is a very simple HTTP/1.1 client, designed primarily for doing simple GET 
requests without the overhead of a large framework like LWP::UserAgent.
It is more correct and more complete than HTTP::Lite. It supports proxies 
(currently only non-authenticating ones) and redirection. It also correctly 
resumes after EINTR.


%package JSON-PP
Summary:        JSON::XS compatible pure-Perl module
# 2.27150 version is a typo but we cannot fix it because it would break
# monotony
Version:        4.16
License:        GPL+ or Artistic
BuildArch:      noarch
Requires:       perl = %{perl_epoch}:%{perl_version}
Conflicts:      perl-JSON < 2.50

%description JSON-PP
JSON::XS is the fastest and most proper JSON module on CPAN. It is written by
Marc Lehmann in C, so must be compiled and installed in the used environment.
JSON::PP is a pure-Perl module and is compatible with JSON::XS.


%package Locale-Maketext-Simple
Summary:        Simple interface to Locale::Maketext::Lexicon
License:        MIT
Version:        0.21
Requires:       perl = %{perl_epoch}:%{perl_version}
BuildArch:      noarch

%description Locale-Maketext-Simple
This module is a simple wrapper around Locale::Maketext::Lexicon, designed
to alleviate the need of creating Language Classes for module authors.


%package Module-CoreList
Summary:        Perl core modules indexed by perl versions
License:        GPL+ or Artistic
Version:        5.20250803
Requires:       perl = %{perl_epoch}:%{perl_version}
Requires:       perl(version)
BuildArch:      noarch

%description Module-CoreList
Module::CoreList contains the hash of hashes %%Module::CoreList::version, this
is keyed on perl version as indicated in $].  The second level hash is module
=> version pairs.


%package Module-Load
Summary:        Runtime require of both modules and files
License:        GPL+ or Artistic
Version:        0.36
Requires:       perl = %{perl_epoch}:%{perl_version}
BuildArch:      noarch

%description Module-Load
Module::Load eliminates the need to know whether you are trying to require
either a file or a module.


%package Module-Load-Conditional
Summary:        Looking up module information / loading at runtime
License:        GPL+ or Artistic
Version:        0.74
Requires:       perl = %{perl_epoch}:%{perl_version}
BuildArch:      noarch

%description Module-Load-Conditional
Module::Load::Conditional provides simple ways to query and possibly load any
of the modules you have installed on your system during runtime.


%package Module-Loaded
Summary:        Mark modules as loaded or unloaded
License:        GPL+ or Artistic
Version:        0.08
Requires:       perl = %{perl_epoch}:%{perl_version}
BuildArch:      noarch

%description Module-Loaded
When testing applications, often you find yourself needing to provide
functionality in your test environment that would usually be provided by
external modules. Rather than munging the %INC by hand to mark these external
modules as loaded, so they are not attempted to be loaded by perl, this module
offers you a very simple way to mark modules as loaded and/or unloaded.


%package Module-Metadata
Summary:        Gather package and POD information from perl module files
Version:        1.000038
License:        GPL+ or Artistic
BuildArch:      noarch
Requires:       perl = %{perl_epoch}:%{perl_version}

%description Module-Metadata
Gather package and POD information from perl module files


%package Params-Check
Summary:        Generic input parsing/checking mechanism
License:        GPL+ or Artistic
Version:        0.38
Requires:       perl = %{perl_epoch}:%{perl_version}
BuildArch:      noarch

%description Params-Check
Params::Check is a generic input parsing/checking mechanism.


%package Parse-CPAN-Meta
Summary:        Parse META.yml and other similar CPAN metadata files
License:        GPL+ or Artistic
Version:        1.4402
Requires:       perl = %{perl_epoch}:%{perl_version}
BuildArch:      noarch
Requires:       perl(CPAN::Meta::YAML) >= 0.002
Requires:       perl(JSON::PP) >= 2.27103
# FIXME it could be removed now?
Obsoletes:      perl-Parse-CPAN-Meta < 1.40

%description Parse-CPAN-Meta 
Parse::CPAN::Meta is a parser for META.yml files, based on the parser half of
YAML::Tiny.


%package Perl-OSType
Summary:        Map Perl operating system names to generic types
Version:        1.010
License:        GPL+ or Artistic
Requires:       perl = %{perl_epoch}:%{perl_version}
BuildArch:      noarch

%description Perl-OSType
Modules that provide OS-specific behaviors often need to know if the current
operating system matches a more generic type of operating systems. For example,
'linux' is a type of 'Unix' operating system and so is 'freebsd'.
This module provides a mapping between an operating system name as given by $^O
and a more generic type. The initial version is based on the OS type mappings
provided in Module::Build and ExtUtils::CBuilder (thus, Microsoft operating
systems are given the type 'Windows' rather than 'Win32').


%package Pod-Escapes
Summary:        Perl module for resolving POD escape sequences
License:        GPL+ or Artistic
Version:        1.07
Requires:       perl = %{perl_epoch}:%{perl_version}
BuildArch:      noarch

%description Pod-Escapes
This module provides things that are useful in decoding Pod E<...> sequences.
Presumably, it should be used only by Pod parsers and/or formatters.


%package Pod-Perldoc
Summary:        Look up Perl documentation in Pod format
License:        GPL+ or Artistic
Version:        3.28.01
# Pod::Perldoc::ToMan executes roff
Requires:       perl = %{perl_epoch}:%{perl_version}
BuildArch:      noarch

%description Pod-Perldoc
perldoc looks up a piece of documentation in .pod format that is embedded
in the perl installation tree or in a perl script, and displays it via
"groff -man | $PAGER". This is primarily used for the documentation for
the perl library modules.


%package Pod-Simple
Summary:        Framework for parsing POD documentation
License:        GPL+ or Artistic
Version:        3.45
Requires:       perl = %{perl_epoch}:%{perl_version}
BuildArch:      noarch

%description Pod-Simple
Pod::Simple is a Perl library for parsing text in the Pod ("plain old
documentation") markup language that is typically used for writing
documentation for Perl and for Perl modules.


%package Scalar-List-Utils
Summary:        A selection of general-utility scalar and list subroutines
License:        GPL+ or Artistic
Version:        1.63
Requires:       perl = %{perl_epoch}:%{perl_version}

%description Scalar-List-Utils
Scalar::Util and List::Util contain a selection of subroutines that people have
expressed would be nice to have in the perl core, but the usage would not
really be high enough to warrant the use of a keyword, and the size so small
such that being individual extensions would be wasteful.


%package Test-Harness
Summary:        Run Perl standard test scripts with statistics
License:        GPL+ or Artistic
Version:        3.48
Requires:       perl = %{perl_epoch}:%{perl_version}
BuildArch:      noarch
# Use rewritten module perl-Test-Harness
Provides:       perl-TAP-Harness = 3.17
Obsoletes:      perl-TAP-Harness < 3.10

%description Test-Harness
Run Perl standard test scripts with statistics.
Use TAP::Parser, Test::Harness package was whole rewritten.


%package Test-Simple
Summary:        Basic utilities for writing tests
License:        GPL+ or Artistic
Version:        1.302199
Requires:       perl = %{perl_epoch}:%{perl_version}
#Requires:       perl(Data::Dumper)
BuildArch:      noarch

%description Test-Simple
Basic utilities for writing tests.


%package Test-Simple-tests
Summary:        Test suite for package perl-Test-Simple
License:        GPL+ or Artistic
Version:        1.302199
Requires:       perl-Test-Simple = %{epoch}:%{version}-%{release}
Requires:       /usr/bin/prove
AutoReqProv:    0
BuildArch:      noarch

%description Test-Simple-tests
This package provides the test suite for package perl-Test-Simple.


%package Time-Piece
Summary:        Time objects from localtime and gmtime
License:        GPL+ or Artistic
# real 1.20_01
Version:        1.20.1
Requires:       perl = %{perl_epoch}:%{perl_version}

%description Time-Piece
The Time::Piece module replaces the standard localtime and gmtime functions
with implementations that return objects.  It does so in a backwards compatible
manner, so that using localtime or gmtime as documented in perlfunc still
behave as expected.


%package parent
Summary:        Establish an ISA relationship with base classes at compile time
License:        GPL+ or Artistic
Version:        0.225
Requires:       perl = %{perl_epoch}:%{perl_version}
BuildArch:      noarch

%description parent
parent allows you to both load one or more modules, while setting up
inheritance from those modules at the same time. Mostly similar in effect to:

    package Baz;

    BEGIN {
        require Foo;
        require Bar; 
        
        push @ISA, qw(Foo Bar); 
    }


%package Socket
Summary:        C socket.h defines and structure manipulators
License:        GPL+ or Artistic
Version:        2.001
Requires:       perl = %{perl_epoch}:%{perl_version}

%description Socket
This module is just a translation of the C socket.h file.  Unlike the old
mechanism of requiring a translated socket.ph file, this uses the h2xs program
(see the Perl source distribution) and your native C compiler.  This means
that it has a far more likely chance of getting the numbers right.  This
includes all of the commonly used pound-defines like AF_INET, SOCK_STREAM, etc.


%package threads
Summary:        Perl interpreter-based threads
License:        GPL+ or Artistic
Version:        2.40
Requires:       perl = %{perl_epoch}:%{perl_version}

%description threads
Since Perl 5.8, thread programming has been available using a model called
interpreter threads  which provides a new Perl interpreter for each thread,
and, by default, results in no data or state information being shared between
threads.

(Prior to Perl 5.8, 5005threads was available through the Thread.pm API. This
threading model has been deprecated, and was removed as of Perl 5.10.0.)

As just mentioned, all variables are, by default, thread local. To use shared
variables, you need to also load threads::shared.


%package threads-shared
Summary:        Perl extension for sharing data structures between threads
License:        GPL+ or Artistic
Version:        1.69
Requires:       perl = %{perl_epoch}:%{perl_version}

%description threads-shared
By default, variables are private to each thread, and each newly created thread
gets a private copy of each existing variable. This module allows you to share
variables across different threads (and pseudo-forks on Win32). It is used
together with the threads module.  This module supports the sharing of the
following data types only: scalars and scalar refs, arrays and array refs, and
hashes and hash refs.


%package version
Summary:        Perl extension for Version Objects
License:        GPL+ or Artistic
# real version 0.9930
Version:        0.99.30
Requires:       perl = %{perl_epoch}:%{perl_version}
BuildArch:      noarch

%description version
Perl extension for Version Objects


%package core
Summary:        Base perl metapackage
# This rpm doesn't contain any copyrightable material.
# Nevertheless, it needs a License tag, so we'll use the generic
# "perl" license.
License:        GPL+ or Artistic
Version:        %{perl_version}
Requires:       perl = %{perl_epoch}:%{perl_version}-%{release}
Requires:       perl-libs = %{perl_epoch}:%{perl_version}-%{release}
Requires:       perl-devel = %{perl_epoch}:%{perl_version}-%{release}
Requires:       perl-macros

Requires:       perl-Archive-Tar, perl-Compress-Raw-Bzip2
Requires:       perl-Compress-Raw-Zlib, perl-CPAN,
Requires:       perl-CPAN-Meta-YAML,
Requires:       perl-Digest, perl-Digest-SHA,
Requires:       perl-ExtUtils-CBuilder, perl-ExtUtils-Embed,
Requires:       perl-ExtUtils-Install, perl-ExtUtils-MakeMaker
Requires:       perl-ExtUtils-Manifest
Requires:       perl-ExtUtils-ParseXS, perl-File-Fetch, perl-Filter,
Requires:       perl-HTTP-Tiny
Requires:       perl-IO-Zlib, perl-IPC-Cmd, perl-JSON-PP
Requires:       perl-Locale-Maketext-Simple
Requires:       perl-Module-CoreList, perl-Module-Load
Requires:       perl-Module-Load-Conditional, perl-Module-Loaded, perl-Module-Metadata
Requires:       perl-Params-Check, perl-Parse-CPAN-Meta, perl-Perl-OSType
Requires:       perl-Pod-Escapes, perl-Pod-Perldoc
Requires:       perl-Scalar-List-Utils, perl-Pod-Simple
Requires:       perl-Socket, perl-Test-Harness, perl-Test-Simple
Requires:       perl-Time-Piece, perl-version
Requires:       perl-threads, perl-threads-shared, perl-parent

%description core
A metapackage which requires all of the perl bits and modules in the upstream
tarball from perl.org.

%prep
%setup -q -n perl-%{perl_version}
%patch1 -p1
%ifarch %{multilib_64_archs}
%patch2 -p1
%endif
%ifarch %{multilib_64_archs}
%patch3 -p1
%endif
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch100 -p1
%patch200 -p1
%patch201 -p1
%patch202 -p1

#copy the example script
install -m 0644 %{SOURCE5} .

#
# Candidates for doc recoding (need case by case review):
# find . -name "*.pod" -o -name "README*" -o -name "*.pm" | xargs file -i | grep charset= | grep -v '\(us-ascii\|utf-8\)'
recode()
{
        iconv -f "${2:-iso-8859-1}" -t utf-8 < "$1" > "${1}_"
        touch -r "$1" "${1}_"
        mv -f "${1}_" "$1"
}
# TODO iconv fail on this one
##recode README.tw big5
#recode pod/perlebcdic.pod
#recode pod/perlhack.pod
#recode pod/perlhist.pod
#recode pod/perlthrtut.pod
#recode AUTHORS

find . -name \*.orig -exec rm -fv {} \;

# Configure Compress::Zlib to use system zlib
sed -i 's|BUILD_ZLIB      = True|BUILD_ZLIB      = False|
    s|INCLUDE         = ./zlib-src|INCLUDE         = %{_includedir}|
    s|LIB             = ./zlib-src|LIB             = %{_libdir}|' \
    cpan/Compress-Raw-Zlib/config.in

# Ensure that we never accidentally bundle zlib or bzip2
rm -rf cpan/Compress-Raw-Zlib/zlib-src
rm -rf cpan/Compress-Raw-Bzip2/bzip2-src
sed -i '/\(bzip2\|zlib\)-src/d' MANIFEST

#%if !%{with gdbm}
# Do not install anything requiring NDBM_File if NDBM is not available.
rm -rf 'cpan/Memoize/Memoize/NDBM_File.pm'
sed -i '\|cpan/Memoize/Memoize/NDBM_File.pm|d' MANIFEST
#%endif

%build
echo "RPM Build arch: %{_arch}"

%global perl_abi    %(echo '%{perl_version}' | sed 's/^\\([^.]*\\.[^.]*\\).*/\\1/')

# ldflags is not used when linking XS modules.
# Only ldflags is used when linking miniperl.
# Only ccflags and ldflags are used for Configure's compiler checks.
# Set optimize=none to prevent from injecting upstream's value.
/bin/sh Configure -des \
        -Doptimize="none" \
        -Dccflags="$RPM_OPT_FLAGS" \
        -Dldflags="$RPM_LD_FLAGS" \
        -Dccdlflags="-Wl,--enable-new-dtags $RPM_LD_FLAGS" \
        -Dlddlflags="-shared $RPM_LD_FLAGS" \
        -Dshrpdir="%{_libdir}" \
        -DDEBUGGING=-g \
        -Dversion=%{perl_version} \
        -Dmyhostname=localhost \
        -Dperladmin=root@localhost \
        -Dcc='%{__cc}' \
        -Dcf_by='Red Hat, Inc.' \
        -Dprefix=%{_prefix} \
        -Dman1dir="%{_mandir}/man1" \
        -Dman3dir="%{_mandir}/man3" \
        -Dvendorprefix=%{_prefix} \
        -Dsiteprefix=%{_prefix}/local \
        -Dsitelib="%{_prefix}/local/share/perl5/%{perl_abi}" \
        -Dsitearch="%{_prefix}/local/%{_lib}/perl5/%{perl_abi}" \
        -Dprivlib="%{privlib}" \
        -Dvendorlib="%{perl_vendorlib}" \
        -Darchlib="%{archlib}" \
        -Dvendorarch="%{perl_vendorarch}" \
        -Darchname=%{perl_archname} \
%ifarch %{multilib_64_archs}
        -Dlibpth="/usr/local/lib64 /lib64 %{_prefix}/lib64" \
%endif
%ifarch sparc sparcv9
        -Ud_longdbl \
%endif
        -Duseshrplib \
        -Dusethreads \
        -Duseithreads \
        -Duselargefiles \
        -Dd_semctl_semun \
        -Di_db \
%if %{with gdbm}
        -Ui_ndbm \
        -Di_gdbm \
%endif
        -Di_shadow \
        -Di_syslog \
        -Dman3ext=3pm \
        -Duseperlio \
        -Dinstallusrbinperl=n \
        -Ubincompat5005 \
        -Uversiononly \
        -Dpager='/usr/bin/less -isr' \
        -Dd_gethostent_r_proto -Ud_endhostent_r_proto -Ud_sethostent_r_proto \
        -Ud_endprotoent_r_proto -Ud_setprotoent_r_proto \
        -Ud_endservent_r_proto -Ud_setservent_r_proto \
        -Dscriptdir='%{_bindir}' \
        -Dusesitecustomize

# -Duseshrplib creates libperl.so, -Ubincompat5005 help create DSO -> libperl.so

BUILD_BZIP2=0
BZIP2_LIB=%{_libdir}
export BUILD_BZIP2 BZIP2_LIB

# Prepare a symlink from proper DSO name to libperl.so now so that new perl
# can be executed from make.
%global soname libperl.so.%{perl_abi}
test -L %soname || ln -s libperl.so %soname

%ifarch sparc64 %{arm}
make
%else
make %{?_smp_mflags}
%endif

%install
ORIG=$PWD

make install DESTDIR=$RPM_BUILD_ROOT

%global build_archlib $RPM_BUILD_ROOT%{archlib}
%global build_privlib $RPM_BUILD_ROOT%{privlib}
%global build_bindir  $RPM_BUILD_ROOT%{_bindir}
%global build_libdir  $RPM_BUILD_ROOT%{_libdir}
%global new_perl LD_PRELOAD="%{build_libdir}/libperl.so.%{perl_version}" \\\
    LD_LIBRARY_PATH="%{build_libdir}" \\\
    PERL5LIB="%{build_archlib}:%{build_privlib}" \\\
    %{build_bindir}/perl

# Make proper DSO names, move libperl to standard path.
mv "%{build_archlib}/CORE/libperl.so" \
    "$RPM_BUILD_ROOT%{_libdir}/libperl.so.%{perl_version}"
ln -s "libperl.so.%{perl_version}" "$RPM_BUILD_ROOT%{_libdir}/%{soname}"
ln -s "libperl.so.%{perl_version}" "$RPM_BUILD_ROOT%{_libdir}/libperl.so"
# XXX: Keep symlink from original location because various code glues
# $archlib/CORE/$libperl to get the DSO.
ln -s "../../libperl.so.%{perl_version}" "%{build_archlib}/CORE/libperl.so"
# XXX: Remove the soname named file from CORE directory that was created as
# a symlink in build section and installed as a regular file by perl build
# system.
rm -f "%{build_archlib}/CORE/%{soname}"

install -p -m 755 utils/pl2pm %{build_bindir}/pl2pm

# perlfunc/ioctl() recommends sys/ioctl.ph.
# perlfaq5 recommends sys/syscall.ph.
# perlfunc/syscall() recommends syscall.ph.
for i in sys/ioctl.h sys/syscall.h syscall.h
do
    %{new_perl} %{build_bindir}/h2ph -a -d %{build_archlib} $i || true
done

# vendor directories (in this case for third party rpms)
# perl doesn't create the auto subdirectory, but modules put things in it,
# so we need to own it.

mkdir -p $RPM_BUILD_ROOT%{perl_vendorarch}/auto
mkdir -p $RPM_BUILD_ROOT%{perl_vendorlib}

#
# perl RPM macros
#
mkdir -p ${RPM_BUILD_ROOT}%{_rpmmacrodir}
install -p -m 644 %{SOURCE3} ${RPM_BUILD_ROOT}%{_rpmmacrodir}

#
# Core modules removal
#
# Dual-living binaries clashes on debuginfo files between perl and standalone
# packages. Excluding is not enough, we need to remove them. This is
# a work-around for rpmbuild bug #878863.
find $RPM_BUILD_ROOT -type f -name '*.bs' -empty -delete
chmod -R u+w $RPM_BUILD_ROOT/*

# miniperl? As an interpreter? How odd. Anyway, a symlink does it:
rm %{build_privlib}/ExtUtils/xsubpp
ln -s ../../../bin/xsubpp %{build_privlib}/ExtUtils/

# Don't need the .packlist
rm %{build_archlib}/.packlist

# Local patch tracking
pushd %{build_archlib}/CORE/
%{new_perl} -x patchlevel.h \
    'Fedora Patch1: Removes date check, Fedora/RHEL specific' \
%ifarch %{multilib_64_archs}
    'Fedora Patch2: support for libdir64' \
%endif
    'Fedora Patch3: use libresolv instead of libbind' \
    'Fedora Patch4: USE_MM_LD_RUN_PATH' \
    'Fedora Patch5: Provide MM::maybe_command independently (bug #1129443)' \
    'Fedora Patch6: Dont run one io test due to random builder failures' \
    'Fedora Patch8: Define SONAME for libperl.so' \
    'Fedora Patch9: Install libperl.so to -Dshrpdir value' \
    'Fedora Patch10: Make *DBM_File desctructors thread-safe (RT#61912)' \
    'Fedora Patch11: Replace EU::MakeMaker dependency with EU::MM::Utils in IPC::Cmd (bug #1129443)' \
    'Fedora Patch12: Link XS modules to pthread library to fix linking with -z defs' \
    'Fedora Patch13: Pass the correct CFLAGS to dtrace' \
    'Fedora Patch100: Reproducible build' \
    'Fedora Patch200: Link XS modules to libperl.so with EU::CBuilder on Linux' \
    'Fedora Patch201: Link XS modules to libperl.so with EU::MM on Linux' \
    'Fedora Patch202: Add definition of OPTIMIZE to .ph files' \

rm patchlevel.bak
popd

# Local patch tracking
cd $RPM_BUILD_ROOT%{_libdir}/perl5/CORE/
%{new_perl} -x patchlevel.h 'Fedora Patch1: Removes date check, Fedora/RHEL specific'
%ifnarch sparc64
%{new_perl} -x patchlevel.h 'Fedora Patch2: Work around annoying rpath issue'
%endif
%ifarch %{multilib_64_archs}
%{new_perl} -x patchlevel.h 'Fedora Patch3: support for libdir64'
%endif

cd $ORIG
rm -rf $RPM_BUILD_ROOT/*.0

# tests -- FIXME need to validate that this all works as expected
mkdir -p %{buildroot}%{perl5_testdir}/perl-tests

# "core"
tar -cf - t/ | ( cd %{buildroot}%{perl5_testdir}/perl-tests && tar -xf - )

# "dual-lifed"
for dir in `find ext/ -type d -name t -maxdepth 2` ; do

    tar -cf - $dir | ( cd %{buildroot}%{perl5_testdir}/perl-tests/t && tar -xf - )
done

# Selected "Dual-lifed cpan" packages
pushd cpan
for package in Test-Simple; do
    for dir in `find ${package} -type d -name t -maxdepth 2` ; do
        tar -cf - $dir | ( cd %{buildroot}%{perl5_testdir} && tar -xf - )
    done
done
popd


# Systemtap tapset install
mkdir -p %{buildroot}%{tapsetdir}
%ifarch %{multilib_64_archs}
%global libperl_stp libperl%{perl_version}-64.stp
%else
%global libperl_stp libperl%{perl_version}-32.stp
%endif

sed \
  -e "s|LIBRARY_PATH|%{_libdir}/%{soname}|" \
  %{SOURCE4} \
  > %{buildroot}%{tapsetdir}/%{libperl_stp}

# TODO: Canonicalize test files (rewrite intrerpreter path, fix permissions)
# XXX: We cannot rewrite ./perl before %%check phase. Otherwise the test
# would run against system perl at build-time.
# See __spec_check_pre global macro in macros.perl.
#T_FILES=`find %%{buildroot}%%{perl5_testdir} -type f -name '*.t'`
#%%fix_shbang_line $T_FILES
#%%{__chmod} +x $T_FILES
#%%{_fixperms} %%{buildroot}%%{perl5_testdir}

%check
%if %{with test}
%if %{parallel_tests}
#    JOBS=$(printf '%%s' "%{?_smp_mflags}" | sed 's/.*-j\([0-9][0-9]*\).*/\1/')
#    LC_ALL=C TEST_JOBS=$JOBS make test_harness
%else
    LC_ALL=C make test
%endif
%endif

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%files
%doc Artistic AUTHORS Copying README Changes
%{_mandir}/man1/*.1*
%{_mandir}/man3/*.3*
%{_bindir}/*
%{privlib}
%{archlib}
%{perl_vendorlib}


# libs
%exclude %{archlib}/CORE/libperl.so
%exclude %{_libdir}/libperl.so.*
%exclude %{perl_vendorarch}

# devel
%exclude %{_bindir}/enc2xs
%exclude %{_mandir}/man1/enc2xs*
%exclude %{privlib}/Encode/
%exclude %{_bindir}/h2xs
%exclude %{_mandir}/man1/h2xs*
%exclude %{_bindir}/libnetcfg
%exclude %{_mandir}/man1/libnetcfg*
%exclude %{_bindir}/perlivp
%exclude %{_mandir}/man1/perlivp*
%exclude %{archlib}/CORE/*.h
%exclude %{_libdir}/libperl.so
%exclude %{_mandir}/man1/perlxs*

# Archive-Tar
%exclude %{_bindir}/ptar
%exclude %{_bindir}/ptardiff
%exclude %{_bindir}/ptargrep
%exclude %{privlib}/Archive/Tar/
%exclude %{privlib}/Archive/Tar.pm
%exclude %{_mandir}/man1/ptar.1*
%exclude %{_mandir}/man1/ptardiff.1*
%exclude %{_mandir}/man1/ptargrep.1*
%exclude %{_mandir}/man3/Archive::Tar*

# CPAN
%exclude %{_bindir}/cpan
%exclude %{privlib}/App/Cpan.pm
%exclude %{privlib}/CPAN/
%exclude %{privlib}/CPAN.pm
%exclude %{_mandir}/man1/cpan.1*
%exclude %{_mandir}/man3/App::Cpan.*
%exclude %{_mandir}/man3/CPAN.*
%exclude %{_mandir}/man3/CPAN:*

# CPAN-Meta-YAML
%exclude %{privlib}/CPAN/Meta/YAML.pm
%exclude %{_mandir}/man3/CPAN::Meta::YAML*

# Parse-CPAN-Meta
%exclude %dir %{privlib}/Parse/
%exclude %dir %{privlib}/Parse/CPAN/
%exclude %{privlib}/Parse/CPAN/Meta.pm
%exclude %{_mandir}/man3/Parse::CPAN::Meta.3*

# Compress-Raw-Bzip2
%exclude %dir %{archlib}/Compress
%exclude %{archlib}/Compress/Raw/Bzip2.pm
%exclude %{_mandir}/man3/Compress::Raw::Bzip2*

# Compress::Raw::Zlib
%exclude %{archlib}/Compress/Raw/
%exclude %{archlib}/auto/Compress
%exclude %{archlib}/auto/Compress/Raw/
%exclude %{archlib}/auto/Compress/Raw/Zlib/
%exclude %{_mandir}/man3/Compress::Raw::Zlib*

# Digest
%exclude %{privlib}/Digest.pm
%exclude %dir %{privlib}/Digest
%exclude %{privlib}/Digest/base.pm
%exclude %{privlib}/Digest/file.pm
%exclude %{_mandir}/man3/Digest.3*
%exclude %{_mandir}/man3/Digest::base.3*
%exclude %{_mandir}/man3/Digest::file.3*

# Digest::SHA
%exclude %{_bindir}/shasum
%exclude %{archlib}/Digest/SHA.pm
%exclude %{archlib}/auto/Digest/SHA/
%exclude %{_mandir}/man1/shasum.1*
%exclude %{_mandir}/man3/Digest::SHA.3*

# ExtUtils::CBuilder
%exclude %{privlib}/ExtUtils/CBuilder/
%exclude %{privlib}/ExtUtils/CBuilder.pm
%exclude %{_mandir}/man3/ExtUtils::CBuilder*

# ExtUtils::Embed
%exclude %{privlib}/ExtUtils/Embed.pm
%exclude %{_mandir}/man3/ExtUtils::Embed*

# ExtUtils::Install
%exclude %{privlib}/ExtUtils/Install.pm
%exclude %{privlib}/ExtUtils/Installed.pm
%exclude %{privlib}/ExtUtils/Packlist.pm
%exclude %{_mandir}/man3/ExtUtils::Install.3*
%exclude %{_mandir}/man3/ExtUtils::Installed.3*
%exclude %{_mandir}/man3/ExtUtils::Packlist.3*

# ExtUtils::Manifest
%exclude %{privlib}/ExtUtils/Manifest.pm
%exclude %{privlib}/ExtUtils/MANIFEST.SKIP
%exclude %{_mandir}/man3/ExtUtils::Manifest.3*

# ExtUtils::MakeMaker
%exclude %{_bindir}/instmodsh
%exclude %{privlib}/ExtUtils/Command/
%exclude %{privlib}/ExtUtils/Liblist/
%exclude %{privlib}/ExtUtils/Liblist.pm
%exclude %{privlib}/ExtUtils/MakeMaker/
%exclude %{privlib}/ExtUtils/MakeMaker.pm
%exclude %{privlib}/ExtUtils/MM*.pm
%exclude %{privlib}/ExtUtils/MY.pm
%exclude %{privlib}/ExtUtils/Mkbootstrap.pm
%exclude %{privlib}/ExtUtils/Mksymlists.pm
%exclude %{privlib}/ExtUtils/testlib.pm
%exclude %{_mandir}/man1/instmodsh.1*
%exclude %{_mandir}/man3/ExtUtils::Command::MM*
%exclude %{_mandir}/man3/ExtUtils::Liblist.3*
%exclude %{_mandir}/man3/ExtUtils::MM*
%exclude %{_mandir}/man3/ExtUtils::MY.3*
%exclude %{_mandir}/man3/ExtUtils::MakeMaker*
%exclude %{_mandir}/man3/ExtUtils::Mkbootstrap.3*
%exclude %{_mandir}/man3/ExtUtils::Mksymlists.3*
%exclude %{_mandir}/man3/ExtUtils::testlib.3*

# ExtUtils::ParseXS
%exclude %dir %{privlib}/ExtUtils/ParseXS/
%exclude %dir %{privlib}/ExtUtils/Typemaps/
%exclude %{privlib}/ExtUtils/ParseXS.pm
%exclude %{privlib}/ExtUtils/ParseXS.pod
%exclude %{privlib}/ExtUtils/ParseXS/Constants.pm
%exclude %{privlib}/ExtUtils/ParseXS/CountLines.pm
%exclude %{privlib}/ExtUtils/ParseXS/Utilities.pm
%exclude %{privlib}/ExtUtils/Typemaps.pm
%exclude %{privlib}/ExtUtils/Typemaps/Cmd.pm
%exclude %{privlib}/ExtUtils/Typemaps/InputMap.pm
%exclude %{privlib}/ExtUtils/Typemaps/OutputMap.pm
%exclude %{privlib}/ExtUtils/Typemaps/Type.pm
%exclude %{privlib}/ExtUtils/xsubpp
%exclude %{_bindir}/xsubpp
%exclude %{_mandir}/man1/xsubpp*
%exclude %{_mandir}/man3/ExtUtils::ParseXS.3*
%exclude %{_mandir}/man3/ExtUtils::ParseXS::Constants.3*
%exclude %{_mandir}/man3/ExtUtils::ParseXS::Utilities.3*
%exclude %{_mandir}/man3/ExtUtils::Typemaps.3*
%exclude %{_mandir}/man3/ExtUtils::Typemaps::Cmd.3*
%exclude %{_mandir}/man3/ExtUtils::Typemaps::InputMap.3*
%exclude %{_mandir}/man3/ExtUtils::Typemaps::OutputMap.3*
%exclude %{_mandir}/man3/ExtUtils::Typemaps::Type.3*

# File::Fetch
%exclude %{privlib}/File/Fetch.pm
%exclude %{_mandir}/man3/File::Fetch.3*

# Filter
%exclude %{archlib}/auto/Filter/Util
%exclude %{archlib}/Filter/Util
%exclude %{privlib}/pod/perlfilter.pod
%exclude %{_mandir}/man1/perlfilter.*
%exclude %{_mandir}/man3/Filter::Util::*

# IO-Compress
%exclude %{_bindir}/zipdetails
%exclude %{privlib}/IO/Compress/FAQ.pod
%exclude %{_mandir}/man1/zipdetails.*
%exclude %{_mandir}/man3/IO::Compress::FAQ.*
# Compress-Zlib
%exclude %{privlib}/Compress/Zlib.pm
%exclude %{_mandir}/man3/Compress::Zlib*
# IO-Compress-Base
%exclude %{privlib}/File/GlobMapper.pm
%exclude %{privlib}/IO/Compress/Base/
%exclude %{privlib}/IO/Compress/Base.pm
%exclude %{privlib}/IO/Uncompress/AnyUncompress.pm
%exclude %{privlib}/IO/Uncompress/Base.pm
%exclude %{_mandir}/man3/File::GlobMapper.*
%exclude %{_mandir}/man3/IO::Compress::Base.*
%exclude %{_mandir}/man3/IO::Uncompress::AnyUncompress.*
%exclude %{_mandir}/man3/IO::Uncompress::Base.*
# IO-Compress-Zlib
%exclude %{privlib}/IO/Compress/Adapter/
%exclude %{privlib}/IO/Compress/Deflate.pm
%exclude %{privlib}/IO/Compress/Gzip/
%exclude %{privlib}/IO/Compress/Gzip.pm
%exclude %{privlib}/IO/Compress/RawDeflate.pm
%exclude %{privlib}/IO/Compress/Bzip2.pm
%exclude %{privlib}/IO/Compress/Zip/
%exclude %{privlib}/IO/Compress/Zip.pm
%exclude %{privlib}/IO/Compress/Zlib/
%exclude %{privlib}/IO/Uncompress/Adapter/
%exclude %{privlib}/IO/Uncompress/AnyInflate.pm
%exclude %{privlib}/IO/Uncompress/Bunzip2.pm
%exclude %{privlib}/IO/Uncompress/Gunzip.pm
%exclude %{privlib}/IO/Uncompress/Inflate.pm
%exclude %{privlib}/IO/Uncompress/RawInflate.pm
%exclude %{privlib}/IO/Uncompress/Unzip.pm
%exclude %{_mandir}/man3/IO::Compress::Deflate*
%exclude %{_mandir}/man3/IO::Compress::Bzip2*
%exclude %{_mandir}/man3/IO::Compress::Gzip*
%exclude %{_mandir}/man3/IO::Compress::RawDeflate*
%exclude %{_mandir}/man3/IO::Compress::Zip*
%exclude %{_mandir}/man3/IO::Uncompress::AnyInflate*
%exclude %{_mandir}/man3/IO::Uncompress::Bunzip2*
%exclude %{_mandir}/man3/IO::Uncompress::Gunzip*
%exclude %{_mandir}/man3/IO::Uncompress::Inflate*
%exclude %{_mandir}/man3/IO::Uncompress::RawInflate*
%exclude %{_mandir}/man3/IO::Uncompress::Unzip*

# IO::Zlib
%exclude %{privlib}/IO/Zlib.pm
%exclude %{_mandir}/man3/IO::Zlib.*

# HTTP::Tiny
%exclude %{privlib}/HTTP/Tiny.pm
%exclude %{_mandir}/man3/HTTP::Tiny*

# IPC::Cmd
%exclude %{privlib}/IPC/Cmd.pm
%exclude %{_mandir}/man3/IPC::Cmd.3*

# JSON::PP
%exclude %{_bindir}/json_pp
%exclude %{privlib}/JSON/PP
%exclude %{privlib}/JSON/PP.pm
%exclude %{_mandir}/man1/json_pp.1*
%exclude %{_mandir}/man3/JSON::PP.3*
%exclude %{_mandir}/man3/JSON::PP::Boolean.3pm*

# Locale::Maketext::Simple
%exclude %{privlib}/Locale/Maketext/Simple.pm
%exclude %{_mandir}/man3/Locale::Maketext::Simple.*

# Module::Build
%exclude %{_bindir}/config_data
%exclude %{privlib}/inc/
%exclude %{privlib}/Module/Build/
%exclude %{privlib}/Module/Build.pm
%exclude %{_mandir}/man1/config_data.1*
%exclude %{_mandir}/man3/Module::Build*
%exclude %{_mandir}/man3/inc::latest.3*

# Module-CoreList
%exclude %{_bindir}/corelist
%exclude %{privlib}/Module/CoreList.pm
%exclude %{_mandir}/man1/corelist*
%exclude %{_mandir}/man3/Module::CoreList*

# Module-Load
%exclude %{privlib}/Module/Load.pm
%exclude %{_mandir}/man3/Module::Load.*

# Module-Load-Conditional
%exclude %{privlib}/Module/Load/
%exclude %{_mandir}/man3/Module::Load::Conditional*

# Module-Loaded
%exclude %{privlib}/Module/Loaded.pm
%exclude %{_mandir}/man3/Module::Loaded*

# Module-Metadata
%exclude %{privlib}/Module/Metadata.pm
%exclude %{_mandir}/man3/Module::Metadata.3pm*

# Params-Check
%exclude %{privlib}/Params/
%exclude %{_mandir}/man3/Params::Check*

# Perl-OSType
%exclude %{privlib}/Perl/OSType.pm
%exclude %{_mandir}/man3/Perl::OSType.3pm*

# parent
%exclude %{privlib}/parent.pm
%exclude %{_mandir}/man3/parent.3*

# Pod-Escapes
%exclude %{privlib}/Pod/Escapes.pm
%exclude %{_mandir}/man3/Pod::Escapes.*

# Pod-Perldoc
%exclude %{_bindir}/perldoc
%exclude %{privlib}/pod/perldoc.pod
%exclude %{privlib}/Pod/Perldoc.pm
%exclude %{privlib}/Pod/Perldoc/
%exclude %{_mandir}/man1/perldoc.1*
%exclude %{_mandir}/man3/Pod::Perldoc*

# Pod-Simple
%exclude %{privlib}/Pod/Simple/
%exclude %{privlib}/Pod/Simple.pm
%exclude %{privlib}/Pod/Simple.pod
%exclude %{_mandir}/man3/Pod::Simple*

# Scalar-List-Utils
%exclude %{archlib}/List/
%exclude %{archlib}/Scalar/
%exclude %{archlib}/auto/List/
%exclude %{_mandir}/man3/List::Util*
%exclude %{_mandir}/man3/Scalar::Util*

# Test::Harness
%exclude %{_bindir}/prove
%exclude %{privlib}/App/Prove*
%exclude %{privlib}/App
%exclude %{privlib}/TAP*
%exclude %{privlib}/Test/Harness*
%exclude %{_mandir}/man1/prove.1*
%exclude %{_mandir}/man3/App::Prove*
%exclude %{_mandir}/man3/TAP*
%exclude %{_mandir}/man3/Test::Harness*

# Test::Simple
%exclude %{privlib}/Test/More*
%exclude %{privlib}/Test/Builder*
%exclude %{privlib}/Test/Simple*
%exclude %{privlib}/Test/Tutorial*
%exclude %{_mandir}/man3/Test::More*
%exclude %{_mandir}/man3/Test::Builder*
%exclude %{_mandir}/man3/Test::Simple*
%exclude %{_mandir}/man3/Test::Tutorial*

# Time::Piece
%exclude %{archlib}/Time/Piece.pm
%exclude %{archlib}/Time/Seconds.pm
%exclude %{archlib}/auto/Time/Piece/
%exclude %{_mandir}/man3/Time::Piece.3*
%exclude %{_mandir}/man3/Time::Seconds.3*

# Socket
%exclude %dir %{archlib}/auto/Socket
%exclude %{archlib}/auto/Socket/Socket.*
%exclude %{archlib}/Socket.pm
%exclude %{_mandir}/man3/Socket.3*

# threads
%dir %exclude %{archlib}/auto/threads
%exclude %{archlib}/auto/threads/threads*
%exclude %{archlib}/threads.pm
%exclude %{_mandir}/man3/threads.3*

# threads-shared
%exclude %{archlib}/auto/threads/shared*
%exclude %dir %{archlib}/threads
%exclude %{archlib}/threads/shared*
%exclude %{_mandir}/man3/threads::shared*

# version
%exclude %{privlib}/version.pm
%exclude %{privlib}/version.pod
%exclude %{privlib}/version/
%exclude %{_mandir}/man3/version.3*
%exclude %{_mandir}/man3/version::Internals.3*

%files libs
%{archlib}/CORE/libperl.so
%{_libdir}/libperl.so.*
%dir %{archlib}
%dir %{perl_vendorarch}
%dir %{perl_vendorarch}/auto

%files devel
%{_bindir}/enc2xs
%{_mandir}/man1/enc2xs*
%{privlib}/Encode/
%{_bindir}/h2xs
%{_mandir}/man1/h2xs*
%{_bindir}/libnetcfg
%{_mandir}/man1/libnetcfg*
%{_bindir}/perlivp
%{_mandir}/man1/perlivp*
%{archlib}/CORE/*.h
%{_libdir}/libperl.so
%{_mandir}/man1/perlxs*
%{tapsetdir}/%{libperl_stp}
%doc perl-example.stp

%files macros
%{_rpmmacrodir}/macros.perl

%files tests
%{perl5_testdir}/
%exclude %{perl5_testdir}/Test-Simple

%files Archive-Tar
%{_bindir}/ptar
%{_bindir}/ptardiff
%{_bindir}/ptargrep
%dir %{privlib}/Archive
%{privlib}/Archive/Tar
%{privlib}/Archive/Tar.pm
%{_mandir}/man1/ptar.1*
%{_mandir}/man1/ptardiff.1*
%{_mandir}/man1/ptargrep.1*
%{_mandir}/man3/Archive::Tar* 

%files Compress-Raw-Bzip2
%dir %{archlib}/Compress
%dir %{archlib}/Compress/Raw
%{archlib}/Compress/Raw/Bzip2.pm
%dir %{archlib}/auto/Compress
%dir %{archlib}/auto/Compress/Raw
%{archlib}/auto/Compress/Raw/Bzip2
%{_mandir}/man3/Compress::Raw::Bzip2*

%files Compress-Raw-Zlib
%dir %{archlib}/Compress
%dir %{archlib}/Compress/Raw
%{archlib}/Compress/Raw/Zlib.pm
%dir %{archlib}/auto/Compress
%dir %{archlib}/auto/Compress/Raw
%{archlib}/auto/Compress/Raw/Zlib
%{_mandir}/man3/Compress::Raw::Zlib*

%files CPAN
%{_bindir}/cpan
%dir %{privlib}/App
%{privlib}/App/Cpan.pm
%{privlib}/CPAN
%{privlib}/CPAN.pm
%{_mandir}/man1/cpan.1*
%{_mandir}/man3/App::Cpan.*
%{_mandir}/man3/CPAN.*
%{_mandir}/man3/CPAN:*
%exclude %{privlib}/CPAN/Meta/
%exclude %{privlib}/CPAN/Meta.pm
%exclude %{_mandir}/man3/CPAN::Meta*

%files CPAN-Meta-YAML
%{privlib}/CPAN/Meta/YAML.pm
%{_mandir}/man3/CPAN::Meta::YAML*

%files Digest
%{privlib}/Digest.pm
%dir %{privlib}/Digest
%{privlib}/Digest/base.pm
%{privlib}/Digest/file.pm
%{_mandir}/man3/Digest.3*
%{_mandir}/man3/Digest::base.3*
%{_mandir}/man3/Digest::file.3*

%files Digest-SHA
%{_bindir}/shasum
%dir %{archlib}/Digest
%{archlib}/Digest/SHA.pm
%{archlib}/auto/Digest/SHA
%{_mandir}/man1/shasum.1*
%{_mandir}/man3/Digest::SHA.3*

%files ExtUtils-CBuilder
%dir %{privlib}/ExtUtils
%{privlib}/ExtUtils/CBuilder
%{privlib}/ExtUtils/CBuilder.pm
%{_mandir}/man3/ExtUtils::CBuilder*

%files ExtUtils-Embed
%dir %{privlib}/ExtUtils
%{privlib}/ExtUtils/Embed.pm
%{_mandir}/man3/ExtUtils::Embed*

%files ExtUtils-Install
%dir %{privlib}/ExtUtils
%{privlib}/ExtUtils/Install.pm
%{privlib}/ExtUtils/Installed.pm
%{privlib}/ExtUtils/Packlist.pm
%{_mandir}/man3/ExtUtils::Install.3*
%{_mandir}/man3/ExtUtils::Installed.3*
%{_mandir}/man3/ExtUtils::Packlist.3*

%files ExtUtils-Manifest
%dir %{privlib}/ExtUtils
%{privlib}/ExtUtils/Manifest.pm
%{privlib}/ExtUtils/MANIFEST.SKIP
%{_mandir}/man3/ExtUtils::Manifest.3*

%files ExtUtils-MakeMaker
%{_bindir}/instmodsh
%{privlib}/ExtUtils/Command/
%{privlib}/ExtUtils/Liblist
%{privlib}/ExtUtils/Liblist.pm
%{privlib}/ExtUtils/MakeMaker
%{privlib}/ExtUtils/MakeMaker.pm
%{privlib}/ExtUtils/MM*.pm
%{privlib}/ExtUtils/MY.pm
%{privlib}/ExtUtils/Mkbootstrap.pm
%{privlib}/ExtUtils/Mksymlists.pm
%{privlib}/ExtUtils/testlib.pm
%{_mandir}/man1/instmodsh.1*
%{_mandir}/man3/ExtUtils::Command::MM*
%{_mandir}/man3/ExtUtils::Liblist.3*
%{_mandir}/man3/ExtUtils::MM*
%{_mandir}/man3/ExtUtils::MY.3*
%{_mandir}/man3/ExtUtils::MakeMaker*
%{_mandir}/man3/ExtUtils::Mkbootstrap.3*
%{_mandir}/man3/ExtUtils::Mksymlists.3*
%{_mandir}/man3/ExtUtils::testlib.3*

%files ExtUtils-ParseXS
%dir %{privlib}/ExtUtils
%dir %{privlib}/ExtUtils/ParseXS
%{privlib}/ExtUtils/ParseXS.pm
%{privlib}/ExtUtils/ParseXS.pod
%{privlib}/ExtUtils/ParseXS/Constants.pm
%{privlib}/ExtUtils/ParseXS/CountLines.pm
%{privlib}/ExtUtils/ParseXS/Eval.pm
%{privlib}/ExtUtils/ParseXS/Utilities.pm
%dir %{privlib}/ExtUtils/Typemaps
%{privlib}/ExtUtils/Typemaps.pm
%{privlib}/ExtUtils/Typemaps/Cmd.pm
%{privlib}/ExtUtils/Typemaps/InputMap.pm
%{privlib}/ExtUtils/Typemaps/OutputMap.pm
%{privlib}/ExtUtils/Typemaps/Type.pm
%{privlib}/ExtUtils/xsubpp
%{_bindir}/xsubpp
%{_mandir}/man1/xsubpp*
%{_mandir}/man3/ExtUtils::ParseXS.3*
%{_mandir}/man3/ExtUtils::ParseXS::Constants.3*
%{_mandir}/man3/ExtUtils::ParseXS::Eval.3*
%{_mandir}/man3/ExtUtils::ParseXS::Utilities.3*
%{_mandir}/man3/ExtUtils::Typemaps.3*
%{_mandir}/man3/ExtUtils::Typemaps::Cmd.3*
%{_mandir}/man3/ExtUtils::Typemaps::InputMap.3*
%{_mandir}/man3/ExtUtils::Typemaps::OutputMap.3*
%{_mandir}/man3/ExtUtils::Typemaps::Type.3*

%files File-Fetch
%dir %{privlib}/File
%{privlib}/File/Fetch.pm
%{_mandir}/man3/File::Fetch.3*

%files Filter
%dir %{archlib}/auto/Filter
%{archlib}/auto/Filter/Util
%dir %{archlib}/Filter
%{archlib}/Filter/Util
%{privlib}/pod/perlfilter.pod
%{_mandir}/man1/perlfilter.*
%{_mandir}/man3/Filter::Util::*

%files IO-Compress
# IO-Compress
%{_bindir}/streamzip
%{_bindir}/zipdetails
%dir %{privlib}/IO
%dir %{privlib}/IO/Compress
%{privlib}/IO/Compress/FAQ.pod
%{_mandir}/man1/streamzip.*
%{_mandir}/man1/zipdetails.*
%{_mandir}/man3/IO::Compress::FAQ.*
# Compress-Zlib
%dir %{privlib}/Compress
%{privlib}/Compress/Zlib.pm
%{_mandir}/man3/Compress::Zlib*
#IO-Compress-Base
%dir %{privlib}/File
%{privlib}/File/GlobMapper.pm
%{privlib}/IO/Compress/Base
%{privlib}/IO/Compress/Base.pm
%dir %{privlib}/IO/Uncompress
%{privlib}/IO/Uncompress/AnyUncompress.pm
%{privlib}/IO/Uncompress/Base.pm
%{_mandir}/man3/File::GlobMapper.*
%{_mandir}/man3/IO::Compress::Base.*
%{_mandir}/man3/IO::Uncompress::AnyUncompress.*
%{_mandir}/man3/IO::Uncompress::Base.*

# IO-Compress-Zlib
%{privlib}/IO/Compress/Adapter
%{privlib}/IO/Compress/Deflate.pm
%{privlib}/IO/Compress/Bzip2.pm
%{privlib}/IO/Compress/Gzip
%{privlib}/IO/Compress/Gzip.pm
%{privlib}/IO/Compress/RawDeflate.pm
%{privlib}/IO/Compress/Zip
%{privlib}/IO/Compress/Zip.pm
%{privlib}/IO/Compress/Zlib
%{privlib}/IO/Uncompress/Adapter/
%{privlib}/IO/Uncompress/AnyInflate.pm
%{privlib}/IO/Uncompress/Bunzip2.pm
%{privlib}/IO/Uncompress/Gunzip.pm
%{privlib}/IO/Uncompress/Inflate.pm
%{privlib}/IO/Uncompress/RawInflate.pm
%{privlib}/IO/Uncompress/Unzip.pm
%{_mandir}/man3/IO::Compress::Deflate*
%{_mandir}/man3/IO::Compress::Gzip*
%{_mandir}/man3/IO::Compress::Bzip2*
%{_mandir}/man3/IO::Compress::RawDeflate*
%{_mandir}/man3/IO::Compress::Zip*
%{_mandir}/man3/IO::Uncompress::AnyInflate*
%{_mandir}/man3/IO::Uncompress::Bunzip2*
%{_mandir}/man3/IO::Uncompress::Gunzip*
%{_mandir}/man3/IO::Uncompress::Inflate*
%{_mandir}/man3/IO::Uncompress::RawInflate*
%{_mandir}/man3/IO::Uncompress::Unzip*

%files IO-Zlib
%{privlib}/IO/Zlib.pm
%{_mandir}/man3/IO::Zlib.*

%files HTTP-Tiny
%{privlib}/HTTP/Tiny.pm
%{_mandir}/man3/HTTP::Tiny*

%files IPC-Cmd
%{privlib}/IPC/Cmd.pm
%{_mandir}/man3/IPC::Cmd.3*

%files JSON-PP
%{_bindir}/json_pp
%{privlib}/JSON/PP
%{privlib}/JSON/PP.pm
%{_mandir}/man1/json_pp.1*
%{_mandir}/man3/JSON::PP.3*
%{_mandir}/man3/JSON::PP::Boolean.3pm*

%files Locale-Maketext-Simple
%{privlib}/Locale/Maketext/Simple.pm
%{_mandir}/man3/Locale::Maketext::Simple.*

%files Module-CoreList
%dir %{privlib}/Module
%{_bindir}/corelist
%{privlib}/Module/CoreList.pm
%{_mandir}/man1/corelist*
%{_mandir}/man3/Module::CoreList*

%files Module-Load
%{privlib}/Module/Load.pm
%{_mandir}/man3/Module::Load.*

%files Module-Load-Conditional
%{privlib}/Module/Load
%{_mandir}/man3/Module::Load::Conditional* 

%files Module-Loaded
%dir %{privlib}/Module
%{privlib}/Module/Loaded.pm
%{_mandir}/man3/Module::Loaded*

%files Module-Metadata
%{privlib}/Module/Metadata.pm
%{_mandir}/man3/Module::Metadata.3pm*

%files Params-Check
%{privlib}/Params/
%{_mandir}/man3/Params::Check*

%files Parse-CPAN-Meta
%dir %{privlib}/Parse/
%dir %{privlib}/Parse/CPAN/
%{privlib}/Parse/CPAN/Meta.pm
%{_mandir}/man3/Parse::CPAN::Meta.3*

%files parent
%{privlib}/parent.pm
%{_mandir}/man3/parent.3*

%files Perl-OSType
%{privlib}/Perl/OSType.pm
%{_mandir}/man3/Perl::OSType.3pm*

%files Pod-Escapes
%{privlib}/Pod/Escapes.pm
%{_mandir}/man3/Pod::Escapes.*

%files Pod-Perldoc
%{_bindir}/perldoc
%{privlib}/pod/perldoc.pod
%dir %{privlib}/Pod
%{privlib}/Pod/Perldoc
%{privlib}/Pod/Perldoc.pm
%{_mandir}/man1/perldoc.1*
%{_mandir}/man3/Pod::Perldoc*

%files Pod-Simple
%{privlib}/Pod/Simple
%{privlib}/Pod/Simple.pm
%{privlib}/Pod/Simple.pod
%{_mandir}/man3/Pod::Simple*

%files Scalar-List-Utils
%{archlib}/List
%{archlib}/Scalar
%{archlib}/Sub
%{archlib}/auto/List
%{_mandir}/man3/List::Util*
%{_mandir}/man3/Scalar::Util*
%{_mandir}/man3/Sub::Util*

%files Socket
%dir %{archlib}/auto/Socket
%{archlib}/auto/Socket/Socket.*
%{archlib}/Socket.pm
%{_mandir}/man3/Socket.3*

%files Test-Harness
%{_bindir}/prove
%dir %{privlib}/App
%{privlib}/App/Prove*
%{privlib}/TAP*
%dir %{privlib}/Test
%{privlib}/Test/Harness*
%{_mandir}/man1/prove.1*
%{_mandir}/man3/App::Prove*
%{_mandir}/man3/TAP*
%{_mandir}/man3/Test::Harness*

%files Test-Simple
%{privlib}/Test/More*
%{privlib}/Test/Builder*
%{privlib}/Test/Simple*
%{privlib}/Test/Tutorial*
%{_mandir}/man3/Test::More*
%{_mandir}/man3/Test::Builder*
%{_mandir}/man3/Test::Simple*
%{_mandir}/man3/Test::Tutorial*

%files Test-Simple-tests
%dir %{perl5_testdir}
%{perl5_testdir}/Test-Simple

%files Time-Piece
%dir %{archlib}/Time
%{archlib}/Time/Piece.pm 
%{archlib}/Time/Seconds.pm
%dir %{archlib}/auto/Time
%{archlib}/auto/Time/Piece
%{_mandir}/man3/Time::Piece.3*
%{_mandir}/man3/Time::Seconds.3*

%files threads
%dir %{archlib}/auto/threads
%{archlib}/auto/threads/threads*
%{archlib}/threads.pm
%{_mandir}/man3/threads.3*

%files threads-shared
%dir %{archlib}/auto/threads
%{archlib}/auto/threads/shared*
%dir %{archlib}/threads
%{archlib}/threads/shared*
%{_mandir}/man3/threads::shared*

%files version
%{privlib}/version.pm
%{privlib}/version.pod
%{privlib}/version/
%{_mandir}/man3/version.3*
%{_mandir}/man3/version::Internals.3*

%files core
# Nothing. Nada. Zilch. Zarro. Uh uh. Nope. Sorry.
