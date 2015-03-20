AC_INIT([eos-node-modules], [1.1.0])
dnl tar-pax is required instead of tar-ustar, because there are very long paths
dnl in the node_modules trees.
AM_INIT_AUTOMAKE([foreign dist-xz no-dist-gzip tar-pax -Wall])
AM_SILENT_RULES([yes])

AC_PATH_PROG([NPM], [npm], [notfound])
AS_IF([test "x$NPM" = xnotfound], [AC_MSG_ERROR([npm is required.])])
AC_PATH_PROG([APT_CACHE], [apt-cache], [notfound])
AS_IF([test "x$APT_CACHE" = xnotfound], [AC_MSG_ERROR([apt-cache is required.])])

AC_MSG_CHECKING([for node modules that have to be installed from Ubuntu repos])
AC_SUBST([eos_node_system_modules], [`$srcdir/node-pkg-info.py --format node`])
AC_MSG_RESULT([ok])

AC_CONFIG_FILES([package.json Makefile])
AC_OUTPUT
